# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Core Module

Provides shared infrastructure for all features:
- API key management with multi-key rotation
- Gemini API client
- Logging system
- Common utilities
- API connection testing
- Debug utilities
"""

from .logger import StellaLogger
from .api_key_manager import APIKeyManager
from .gemini_client import GeminiClient
from .utils import strip_html, classify_error, format_error_message
from .api_tester import test_api_connection, quick_test
from .debug_utils import debug_stella_status, validate_installation, quick_check

__all__ = [
    "StellaLogger",
    "APIKeyManager", 
    "GeminiClient",
    "strip_html",
    "classify_error",
    "format_error_message",
    "test_api_connection",
    "quick_test",
    "debug_stella_status",
    "validate_installation",
    "quick_check",
]
