# -*- coding: utf-8 -*-
"""
Stella Anki Tools - API Connection Tester

Provides comprehensive API connection testing with:
- JSON schema validation
- Detailed error classification
- Support for different models

Adapted from Reference/Anki_Deck_Translater/api_tester.py
"""

from __future__ import annotations

import os
import sys
import json
import re
from typing import Tuple, Optional

# Add lib path
_addon_dir = os.path.dirname(os.path.dirname(__file__))
_lib_path = os.path.join(_addon_dir, "lib")
if _lib_path not in sys.path:
    sys.path.insert(0, _lib_path)

# Handle google namespace package - required when other addons also use google packages
try:
    if "google" in sys.modules:
        import google
        if hasattr(google, "__path__"):
            google_lib_path = os.path.join(_lib_path, "google")
            if google_lib_path not in google.__path__:
                google.__path__.append(google_lib_path)
except Exception:
    pass

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from .logger import get_logger


logger = get_logger(__name__)


def test_api_connection(
    api_key: str,
    language: str = "Korean",
    model_name: str = "gemini-2.5-flash"
) -> Tuple[bool, str]:
    """
    Test API connection with JSON schema validation.
    
    Args:
        api_key: Google AI API Key
        language: Language to test with
        model_name: Gemini model name to use
    
    Returns:
        Tuple of (success, message)
    """
    try:
        if not api_key or not api_key.strip():
            return False, "API key is empty"
        
        if not GENAI_AVAILABLE:
            return False, (
                "The Google AI SDK could not be loaded.\n\n"
                "This may happen if:\n"
                "• Another Anki addon is conflicting with this one\n"
                "• The addon's lib folder is missing or corrupted\n\n"
                "Try restarting Anki. If the problem persists, "
                "reinstall this addon from AnkiWeb."
            )
        
        logger.info(f"Starting API connection test with model: {model_name}")
        
        # Configure API key
        genai.configure(api_key=api_key)
        
        # Simple test schema
        test_schema = {
            "type": "object",
            "properties": {
                "test_response": {
                    "type": "string",
                    "description": "A simple test response"
                }
            },
            "required": ["test_response"]
        }
        
        # Create model with JSON output
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": test_schema,
                "temperature": 0.3,
                "max_output_tokens": 100,
            }
        )
        
        # Test prompt
        test_prompt = f"Please respond with a simple test message in {language}."
        
        logger.info("Sending test request to Gemini API...")
        
        # Call API
        response = model.generate_content(test_prompt)
        
        if not response:
            logger.error("API response object is None")
            return False, "API response is empty"
        
        response_text = response.text if response.text else ""
        logger.info(f"Received response (length={len(response_text)})")
        
        if not response_text or not response_text.strip():
            logger.error("API response text is empty")
            return False, "API returned empty response. The model may not support JSON schema output."
        
        # Clean and extract JSON from response
        cleaned = response_text.strip()
        
        # Remove markdown code fences
        code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', cleaned)
        if code_block_match:
            cleaned = code_block_match.group(1).strip()
        
        # Extract JSON object
        if '{' in cleaned and '}' in cleaned:
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            cleaned = cleaned[start:end]
        
        # Parse JSON
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as je:
            logger.error(f"JSON parsing failed: {je}")
            return False, f"JSON parsing error: {str(je)}\nRaw response: {response_text[:200]}"
        
        if "test_response" in data:
            logger.info("API connection test successful")
            return True, f"API connection successful: {data['test_response']}"
        else:
            logger.error(f"Invalid response format: {data}")
            return False, f"Invalid API response format. Got: {json.dumps(data)[:200]}"
            
    except Exception as e:
        return _classify_error(e, model_name)


def _classify_error(error: Exception, model_name: str) -> Tuple[bool, str]:
    """
    Classify and format API errors for user-friendly display.
    
    Args:
        error: The exception that occurred
        model_name: Model name for context
        
    Returns:
        Tuple of (False, error_message)
    """
    error_msg = str(error)
    error_type = type(error).__name__
    error_lower = error_msg.lower()
    
    logger.error(f"API test failed - Type: {error_type}, Message: {error_msg}")
    
    # Check for invalid API key first (most common issue)
    if "api key" in error_lower or "api_key" in error_lower:
        return False, "Invalid API key. Please check your API key."
    
    # Check for actual quota/rate limit errors
    if "resource exhausted" in error_lower or "quota exceeded" in error_lower:
        return False, f"API quota limit reached: {error_msg}"
    
    if "rate limit" in error_lower or "too many requests" in error_lower or "429" in error_msg:
        return False, "API rate limit reached. Please wait and try again."
    
    # Check for permission errors
    if "permission" in error_lower or "forbidden" in error_lower:
        return False, f"No API permission: {error_msg}"
    
    # Check for model-related errors
    if "model" in error_lower and ("not found" in error_lower or "does not exist" in error_lower):
        return False, f"Model not found. The model '{model_name}' may not be available."
    
    # Check for schema/parameter errors
    if "invalid" in error_lower or "bad request" in error_lower or "400" in error_msg:
        return False, f"Invalid request format or parameters: {error_msg}"
    
    # Check for network/connection errors
    if "connection" in error_lower or "timeout" in error_lower or "network" in error_lower:
        return False, f"Network connection error: {error_msg}"
    
    # Generic error with full message
    return False, f"API connection error ({error_type}): {error_msg}"


def quick_test(api_key: str) -> bool:
    """
    Quick validation of API key without full schema test.
    
    Args:
        api_key: API key to test
        
    Returns:
        True if key appears valid, False otherwise
    """
    if not api_key or not api_key.strip():
        return False
    
    # Basic format validation
    if not api_key.startswith("AIza"):
        return False
    
    if len(api_key) < 35 or len(api_key) > 50:
        return False
    
    return True
