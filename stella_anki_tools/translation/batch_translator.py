# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Batch Translator

Batch translation processing using QRunnable pattern for background execution.
Adapted from Anki_Deck_Translater/batch_translator.py.
"""

from __future__ import annotations

import os
import sys
import json
import re
import threading
import time
from typing import List, Dict, Any, Optional, Tuple

from aqt import mw
from aqt.qt import QObject, QRunnable, pyqtSignal

# Add lib path for bundled dependencies
_addon_dir = os.path.dirname(os.path.dirname(__file__))
_lib_path = os.path.join(_addon_dir, "lib")
if _lib_path not in sys.path:
    sys.path.insert(0, _lib_path)

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from ..core.logger import StellaLogger
from ..core.api_key_manager import get_api_key_manager
from ..core.utils import strip_html
from ..config.prompts import TRANSLATION_SYSTEM_PROMPT


class BatchTranslationSignals(QObject):
    """Signals emitted by BatchTranslationWorker."""
    
    progress = pyqtSignal(int, int)  # processed, total
    detailed_progress = pyqtSignal(int, int, int, int)  # processed, total, success, failure
    error_detail = pyqtSignal(str, str, int)  # error_type, message, affected_count
    error = pyqtSignal(str)
    finished = pyqtSignal(int, int)  # success_count, failure_count
    key_rotated = pyqtSignal(str, str)  # old_key_id, new_key_id


class BatchTranslator(QRunnable):
    """
    Background worker for batch translation.
    
    Processes multiple notes in batches with:
    - Rate limiting between batches
    - Automatic API key rotation on failures
    - Progress reporting via signals
    - Cancellation support
    """
    
    def __init__(
        self,
        notes_data: List[Dict[str, Any]],
        target_language: str,
        destination_field: str,
        model_name: str = "gemini-2.5-flash",
        batch_size: int = 5,
        batch_delay_seconds: float = 8.0,
        ignore_errors: bool = True,
        cancel_event: Optional[threading.Event] = None,
        addon_dir: Optional[str] = None,
    ) -> None:
        """
        Initialize batch translator.
        
        Args:
            notes_data: List of dicts with 'note_id', 'word', 'context'
            target_language: Target language for translation
            destination_field: Field to store translations
            model_name: Gemini model to use
            batch_size: Number of words per API call
            batch_delay_seconds: Delay between batches
            ignore_errors: Continue on errors if True
            cancel_event: Event to signal cancellation
            addon_dir: Add-on directory path
        """
        super().__init__()
        
        self.notes_data = notes_data
        self.target_language = target_language
        self.destination_field = destination_field
        self.model_name = model_name or "gemini-2.5-flash"
        self.batch_size = max(1, batch_size)
        self.batch_delay_seconds = max(1.0, batch_delay_seconds)
        self.ignore_errors = ignore_errors
        self.cancel_event = cancel_event or threading.Event()
        
        self._addon_dir = addon_dir or _addon_dir
        self._logger = StellaLogger.get_logger(self._addon_dir, "batch_translator")
        self._key_manager = get_api_key_manager(self._addon_dir)
        
        self.signals = BatchTranslationSignals()
        
        self._model = None
        self._current_api_key: Optional[str] = None
        self._consecutive_rate_errors = 0
    
    def run(self) -> None:
        """Execute batch translation."""
        try:
            if not self.notes_data:
                raise ValueError("No notes to translate")
            
            api_key = self._get_active_api_key()
            if not api_key:
                raise ValueError("No API key available")
            
            self._configure_api()
            self._model = self._build_model()
            
            total = len(self.notes_data)
            processed = 0
            success_count = 0
            failure_count = 0
            
            # Process in batches
            for batch in self._chunk_notes():
                if self.cancel_event.is_set():
                    self._logger.warning("Batch translation cancelled")
                    break
                
                try:
                    # Generate translations for batch
                    translations = self._translate_batch(batch)
                    
                    # Apply translations to notes
                    success, failed = self._apply_translations(batch, translations)
                    success_count += success
                    failure_count += failed
                    
                    # Record success
                    if success > 0:
                        self._key_manager.record_success(
                            operation="translation", 
                            count=success
                        )
                    
                    if failed > 0:
                        self.signals.error_detail.emit(
                            "TRANSLATION_MISSING",
                            "Some translations were empty or missing",
                            failed
                        )
                        
                except Exception as batch_error:
                    failure_count += len(batch)
                    error_type = self._classify_error(batch_error)
                    
                    self.signals.error_detail.emit(
                        error_type,
                        str(batch_error)[:200],
                        len(batch)
                    )
                    
                    # Try to rotate key on rate limit errors
                    rotated = self._handle_batch_error(batch_error, error_type)
                    
                    if self.ignore_errors:
                        self._logger.warning(f"Batch error ignored: {batch_error}")
                        if rotated:
                            self._configure_api()
                            self._model = self._build_model()
                    else:
                        self._logger.error(f"Batch translation failed: {batch_error}")
                        self.signals.error.emit(str(batch_error))
                        self.signals.finished.emit(success_count, failure_count)
                        return
                
                processed += len(batch)
                self.signals.progress.emit(processed, total)
                self.signals.detailed_progress.emit(
                    processed, total, success_count, failure_count
                )
                
                # Rate limiting delay
                if not self.cancel_event.is_set():
                    delay = self.batch_delay_seconds
                    if self._consecutive_rate_errors > 0:
                        delay = max(delay, 10.0 + (self._consecutive_rate_errors * 5.0))
                        self._logger.info(f"Extended delay: {delay:.1f}s")
                    self._interruptible_sleep(delay)
            
            self.signals.finished.emit(success_count, failure_count)
            
        except Exception as e:
            self._logger.error(f"Batch translation error: {e}")
            self.signals.error.emit(str(e))
    
    def _get_active_api_key(self) -> Optional[str]:
        """Get the current active API key."""
        if self._key_manager.get_key_count() > 0:
            key = self._key_manager.get_current_key()
            if key:
                self._current_api_key = key
                return key
        return self._current_api_key
    
    def _configure_api(self) -> None:
        """Configure Gemini API with current key."""
        if not GENAI_AVAILABLE:
            raise RuntimeError("google-generativeai not available")
        
        key = self._get_active_api_key()
        if key:
            genai.configure(api_key=key)
    
    def _build_model(self):
        """Build Gemini model instance."""
        return genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "translations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "word": {"type": "string"},
                                    "translation": {"type": "string"},
                                },
                                "required": ["word", "translation"],
                            },
                        },
                    },
                    "required": ["translations"],
                },
                "temperature": 0.3,
                "max_output_tokens": 2048,
            },
        )
    
    def _chunk_notes(self):
        """Yield batches of notes."""
        for i in range(0, len(self.notes_data), self.batch_size):
            yield self.notes_data[i:i + self.batch_size]
    
    def _translate_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Translate a batch of words.
        
        Args:
            batch: List of note data dicts
            
        Returns:
            Dictionary mapping words to translations
        """
        # Build batch prompt
        words_info = []
        for item in batch:
            word = item.get("word", "")
            context = item.get("context", "")
            if context:
                words_info.append(f'- "{word}" (context: {context})')
            else:
                words_info.append(f'- "{word}"')
        
        words_list = "\n".join(words_info)
        
        prompt = f"""{TRANSLATION_SYSTEM_PROMPT}

Translate the following words to {self.target_language}.
For each word, provide the most appropriate translation based on the given context.

Words to translate:
{words_list}

Return a JSON object with this exact structure:
{{
    "translations": [
        {{"word": "original_word", "translation": "translated_word"}},
        ...
    ]
}}"""
        
        # Call API
        max_retries = 3
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                response = self._model.generate_content(prompt)
                
                if not response or not response.text:
                    raise ValueError("Empty API response")
                
                # Parse response
                result = self._parse_batch_response(response.text, batch)
                self._consecutive_rate_errors = 0
                return result
                
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check for rate limit
                if any(x in error_str for x in ["429", "quota", "rate", "exhausted"]):
                    self._consecutive_rate_errors += 1
                    
                    rotated, new_key = self._key_manager.record_failure(str(e))
                    if rotated:
                        self._logger.info(f"Key rotated to: {new_key}")
                        self._configure_api()
                        self._model = self._build_model()
                        continue
                
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
        
        raise ValueError(f"Batch translation failed: {last_error}")
    
    def _parse_batch_response(
        self, 
        response: str, 
        batch: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Parse batch translation response."""
        cleaned = response.strip()
        
        # Extract JSON from code blocks
        code_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
        if code_match:
            cleaned = code_match.group(1).strip()
        
        # Extract JSON object
        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(0)
        
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        
        # Build result dictionary
        result = {}
        translations = data.get("translations", [])
        
        for item in translations:
            word = item.get("word", "").strip()
            translation = item.get("translation", "").strip()
            if word and translation:
                result[word.lower()] = translation
        
        return result
    
    def _apply_translations(
        self, 
        batch: List[Dict[str, Any]], 
        translations: Dict[str, str]
    ) -> Tuple[int, int]:
        """
        Apply translations to notes.
        
        Returns:
            Tuple of (success_count, failure_count)
        """
        success = 0
        failed = 0
        
        for item in batch:
            note_id = item.get("note_id")
            word = item.get("word", "").lower()
            
            translation = translations.get(word, "")
            
            if not translation:
                failed += 1
                continue
            
            try:
                # Update note
                note = mw.col.get_note(note_id)
                if note and self.destination_field in note:
                    note[self.destination_field] = translation
                    mw.col.update_note(note)
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                self._logger.error(f"Failed to update note {note_id}: {e}")
                failed += 1
        
        return success, failed
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type."""
        error_str = str(error).lower()
        
        if any(x in error_str for x in ["429", "rate limit"]):
            return "RATE_LIMIT"
        elif any(x in error_str for x in ["quota", "exhausted"]):
            return "QUOTA_EXCEEDED"
        elif any(x in error_str for x in ["401", "403", "invalid key"]):
            return "INVALID_KEY"
        elif "json" in error_str:
            return "PARSE_ERROR"
        else:
            return "UNKNOWN"
    
    def _handle_batch_error(self, error: Exception, error_type: str) -> bool:
        """Handle batch error and potentially rotate key."""
        if error_type in ("RATE_LIMIT", "QUOTA_EXCEEDED"):
            rotated, new_key = self._key_manager.record_failure(str(error))
            if rotated and new_key:
                old_key = self._key_manager._get_key_id(self._current_api_key or "")
                self.signals.key_rotated.emit(old_key, new_key)
                self._consecutive_rate_errors = 0
                return True
        
        self._key_manager.record_failure(str(error))
        return False
    
    def _interruptible_sleep(self, seconds: float) -> None:
        """Sleep that can be interrupted by cancel event."""
        interval = 0.5
        elapsed = 0.0
        while elapsed < seconds and not self.cancel_event.is_set():
            time.sleep(min(interval, seconds - elapsed))
            elapsed += interval
