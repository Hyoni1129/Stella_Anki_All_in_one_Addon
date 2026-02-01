# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Sentence Generator

Single-note sentence generation using Gemini AI with QueryOp pattern.
Adapted from Anki_Sentence_generater/sentence_generator_modern.py.
"""

from __future__ import annotations

import os
import re
import json
import time
from typing import Optional, Dict, Any, Callable, Tuple

from aqt import mw
from aqt.operations import QueryOp
from aqt.utils import showWarning
from anki.collection import Collection
from anki.notes import Note

from ..core.logger import StellaLogger
from ..core.api_key_manager import get_api_key_manager
from ..core.gemini_client import get_gemini_client, GeminiError
from ..core.utils import strip_html, classify_error, ErrorType, highlight_word
from ..config.prompts import get_sentence_prompt, SENTENCE_SYSTEM_PROMPT


class SentenceGenerator:
    """
    AI-powered example sentence generator.
    
    Features:
    - Context-aware sentence generation
    - Multi-key rotation support
    - Word highlighting in sentences
    - QueryOp async pattern
    """
    
    def __init__(self, addon_dir: Optional[str] = None) -> None:
        """
        Initialize the sentence generator.
        
        Args:
            addon_dir: Add-on directory path
        """
        self._addon_dir = addon_dir or os.path.dirname(os.path.dirname(__file__))
        self._logger = StellaLogger.get_logger(self._addon_dir, "sentence")
        self._key_manager = get_api_key_manager(self._addon_dir)
        self._gemini = get_gemini_client(self._addon_dir)
        
        self._logger.info("SentenceGenerator initialized")
    
    def generate_sentence_async(
        self,
        parent_widget,
        note: Note,
        expression_field: str,
        sentence_field: str,
        translation_field: str,
        target_language: str,
        difficulty: str = "Normal",
        highlight: bool = True,
        model_name: str = "gemini-2.5-flash",
        success_callback: Optional[Callable[[], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Generate a sentence for a note asynchronously.
        
        Args:
            parent_widget: Qt parent widget for progress
            note: Anki note to process
            expression_field: Field containing the word
            sentence_field: Field to store generated sentence
            translation_field: Field to store sentence translation
            target_language: Language for the sentence
            difficulty: Sentence complexity (Beginner, Normal, Complex)
            highlight: Whether to highlight the word in the sentence
            model_name: Gemini model to use
            success_callback: Called on success
            error_callback: Called on failure
        """
        
        def background_operation(col: Collection) -> Tuple[str, str]:
            """Background task: generate sentence."""
            # Get API key
            api_key = self._key_manager.get_current_key()
            if not api_key:
                raise GeminiError("No API key available")
            
            # Extract target word
            word = strip_html(note[expression_field]) if expression_field in note else ""
            if not word:
                raise ValueError(f"Expression field '{expression_field}' is empty")
            
            self._logger.info(f"Generating sentence for '{word}' ({target_language})")
            
            # Generate sentence
            sentence_data = self._generate_sentence(
                word=word,
                target_language=target_language,
                difficulty=difficulty,
                model_name=model_name,
            )
            
            # Apply highlighting if enabled
            sentence = sentence_data["translated_sentence"]
            translation = sentence_data["english_sentence"]
            
            if highlight:
                conjugated = sentence_data.get("translated_conjugated_word", word)
                english_word = sentence_data.get("english_word", word)
                
                sentence = self._apply_highlight(sentence, conjugated)
                translation = self._apply_highlight(translation, english_word)
            
            self._logger.info(f"Sentence generated: {sentence[:50]}...")
            return sentence, translation
        
        def on_success(result: Tuple[str, str]) -> None:
            """Success callback on main thread."""
            try:
                sentence, translation = result
                
                note[sentence_field] = sentence
                note[translation_field] = translation
                mw.col.update_note(note)
                
                self._logger.info("Note updated with sentence")
                
                if success_callback:
                    success_callback()
                    
            except Exception as e:
                error_msg = f"Failed to update note: {e}"
                self._logger.error(error_msg)
                if error_callback:
                    error_callback(error_msg)
        
        def on_failure(error: Exception) -> None:
            """Failure callback on main thread."""
            error_msg = self._format_error_message(str(error))
            self._logger.error(f"Sentence generation failed: {error_msg}")
            
            if error_callback:
                error_callback(error_msg)
            else:
                showWarning(f"Sentence generation failed:\n{error_msg}")
        
        # Execute with QueryOp
        op = QueryOp(
            parent=parent_widget,
            op=background_operation,
            success=on_success,
        ).failure(on_failure)
        
        op.with_progress("Generating sentence...").run_in_background()
    
    def generate_sentence_sync(
        self,
        word: str,
        target_language: str,
        difficulty: str = "Normal",
        model_name: str = "gemini-2.5-flash",
    ) -> Dict[str, str]:
        """
        Generate a sentence synchronously.
        
        Warning: Blocks UI thread.
        
        Args:
            word: Word to create sentence for
            target_language: Language for the sentence
            difficulty: Sentence complexity
            model_name: Gemini model to use
            
        Returns:
            Dictionary with sentence data
        """
        return self._generate_sentence(
            word=word,
            target_language=target_language,
            difficulty=difficulty,
            model_name=model_name,
        )
    
    def _generate_sentence(
        self,
        word: str,
        target_language: str,
        difficulty: str,
        model_name: str,
    ) -> Dict[str, str]:
        """
        Generate sentence using Gemini API.
        
        Args:
            word: Word to use in sentence
            target_language: Target language
            difficulty: Complexity level
            model_name: Model to use
            
        Returns:
            Dictionary with sentence data
        """
        # Build prompt with explicit JSON format request
        prompt = get_sentence_prompt(word, target_language, difficulty)
        # Add JSON format instruction with concrete example for structured response
        json_instruction = f'''

IMPORTANT: Return ONLY a valid JSON object with no markdown, no code fences, and no explanation.
Example format for word "apple" in Spanish:
{{"translated_sentence": "Me gusta comer manzanas todos los días.", "english_sentence": "I like to eat apples every day.", "translated_conjugated_word": "manzanas", "english_word": "apples"}}

Now generate for the word "{word}" in {target_language}:'''
        full_prompt = f"{SENTENCE_SYSTEM_PROMPT}\n\n{prompt}{json_instruction}"
        
        # Generation config (avoid unsupported response_mime_type for compatibility)
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 512,  # Increased to prevent JSON truncation
            "top_p": 0.9,
            "top_k": 40,
        }
        
        # Call API with retries
        max_retries = 3
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                response = self._gemini.generate_text(
                    prompt=full_prompt,
                    model_name=model_name,
                    generation_config=generation_config,
                    max_retries=1,
                )
                
                # Parse response
                data = self._parse_sentence_response(response, word)
                
                # Record success
                self._key_manager.record_success(operation="sentence", count=1)
                
                return data
                
            except Exception as e:
                last_error = e
                self._logger.warning(f"Attempt {attempt} failed: {e}")
                
                # Check for rate limit
                error_type, _ = classify_error(e)
                if error_type in (ErrorType.RATE_LIMIT, ErrorType.QUOTA_EXCEEDED):
                    rotated, new_key = self._key_manager.record_failure(str(e))
                    if rotated:
                        self._logger.info(f"Rotated to key: {new_key}")
                        continue
                
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
        
        raise GeminiError(f"Sentence generation failed: {last_error}")
    
    def _parse_sentence_response(
        self, 
        response: str, 
        word: str
    ) -> Dict[str, str]:
        """
        Parse and validate sentence API response.
        
        Args:
            response: Raw API response
            word: Target word for validation
            
        Returns:
            Parsed dictionary with sentence data
        """
        if not response or not response.strip():
            raise ValueError("Empty API response")
        
        cleaned = response.strip()
        
        # Remove code fences
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9_]*", "", cleaned)
            cleaned = cleaned.strip("`")
        
        # Extract JSON object
        if "{" in cleaned and "}" in cleaned:
            json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
        
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Try to repair malformed JSON
            data = self._repair_json(cleaned)
            if not data:
                raise ValueError(f"Invalid JSON response: {e}")
        
        # Validate required fields
        required = [
            "translated_sentence",
            "english_sentence",
            "translated_conjugated_word",
            "english_word",
        ]
        
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        return data
    
    def _repair_json(self, payload: str) -> Optional[Dict[str, str]]:
        """Attempt to repair malformed JSON."""
        candidate = payload.strip().strip("`")
        
        # Fix common quote issues
        candidate = candidate.replace(""", '"').replace(""", '"').replace("'", "'")
        
        # Fix unbalanced braces
        brace_diff = candidate.count("{") - candidate.count("}")
        if brace_diff > 0:
            candidate += "}" * brace_diff
        elif brace_diff < 0:
            candidate = "{" * (-brace_diff) + candidate
        
        # Remove trailing commas
        candidate = re.sub(r",(\s*[}\]])", r"\1", candidate)
        
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Extract key-value pairs as fallback
            kv_pairs = re.findall(r'"([^"\\]+)"\s*:\s*"([^"\\]*)"', candidate)
            if kv_pairs:
                return {k: v for k, v in kv_pairs}
            return None
    
    def _apply_highlight(self, text: str, word: str) -> str:
        """Apply highlighting to a word in text."""
        if not text or not word:
            return text
        
        highlight_style = (
            'style="background-color: rgb(255, 255, 0); '
            'color: rgb(0, 0, 0);"'
        )
        
        # Replace first occurrence only
        return text.replace(
            word,
            f'<span {highlight_style}>{word}</span>',
            1
        )
    
    def _format_error_message(self, error: str) -> str:
        """Format error message for user display."""
        error_lower = error.lower()
        
        if "json" in error_lower:
            return f"Response Error: {error}\n\nThe API response format was invalid."
        elif "api" in error_lower and "key" in error_lower:
            return f"API Key Error: {error}\n\nPlease check your API key."
        elif "quota" in error_lower:
            return f"Quota Error: {error}\n\nAPI quota exceeded."
        else:
            return f"Sentence Generation Error: {error}"


def create_sentence_generator(addon_dir: Optional[str] = None) -> SentenceGenerator:
    """Factory function to create a SentenceGenerator instance."""
    return SentenceGenerator(addon_dir)
