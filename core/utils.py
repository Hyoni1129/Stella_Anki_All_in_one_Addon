# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Common Utilities

Provides shared utility functions:
- HTML stripping for card content
- Error classification and formatting
- Text processing helpers
"""

from __future__ import annotations

import re
from typing import Tuple, Optional
from enum import Enum


class ErrorType(Enum):
    """Classification of API and processing errors."""
    RATE_LIMIT = "rate_limit"
    QUOTA_EXCEEDED = "quota_exceeded"
    INVALID_KEY = "invalid_key"
    NETWORK = "network"
    TIMEOUT = "timeout"
    CONTENT_FILTER = "content_filter"
    INVALID_RESPONSE = "invalid_response"
    FIELD_ERROR = "field_error"
    UNKNOWN = "unknown"


def strip_html(html_content: str) -> str:
    """
    Remove HTML tags and decode entities from card content.
    
    Args:
        html_content: Raw HTML string from Anki card
        
    Returns:
        Clean text content
    """
    if not html_content:
        return ""
    
    # Remove script and style elements entirely
    text = re.sub(r"<script[^>]*>.*?</script>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    
    # Replace <br> tags with newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    
    # Replace </p>, </div> with newlines
    text = re.sub(r"</(?:p|div)>", "\n", text, flags=re.IGNORECASE)
    
    # Remove all remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # Decode common HTML entities
    html_entities = {
        "&nbsp;": " ",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&apos;": "'",
        "&#39;": "'",
        "&ndash;": "–",
        "&mdash;": "—",
        "&hellip;": "…",
    }
    for entity, char in html_entities.items():
        text = text.replace(entity, char)
    
    # Decode numeric HTML entities
    text = re.sub(
        r"&#(\d+);",
        lambda m: chr(int(m.group(1))),
        text
    )
    text = re.sub(
        r"&#x([0-9a-fA-F]+);",
        lambda m: chr(int(m.group(1), 16)),
        text
    )
    
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces/tabs to single space
    text = re.sub(r"\n{3,}", "\n\n", text)  # Limit consecutive newlines
    
    return text.strip()


def clean_filename(text: str) -> str:
    """
    Clean text for use in filenames.
    Removes invalid characters and spaces.
    """
    # Replace spaces with underscores
    text = text.replace(" ", "_")
    # Keep only alphanumeric, underscores, hyphens
    text = re.sub(r'[^a-zA-Z0-9_\-]', '', text)
    return text[:50]  # Limit length


def classify_error(error: Exception) -> Tuple[ErrorType, str]:
    """
    Classify an exception into an error type.
    
    Args:
        error: The exception to classify
        
    Returns:
        Tuple of (ErrorType, user-friendly message)
    """
    error_str = str(error).lower()
    
    # Rate limit / Quota errors (need key rotation)
    if any(x in error_str for x in ["429", "rate limit", "quota", "resource exhausted"]):
        if "quota" in error_str or "resource exhausted" in error_str:
            return ErrorType.QUOTA_EXCEEDED, "API quota exceeded. Rotating to next key..."
        return ErrorType.RATE_LIMIT, "Rate limit reached. Waiting before retry..."
    
    # Invalid API key
    if any(x in error_str for x in ["401", "403", "invalid api key", "api key not valid"]):
        return ErrorType.INVALID_KEY, "Invalid API key. Please check your key."
    
    # Network errors
    if any(x in error_str for x in ["connection", "network", "refused", "unreachable"]):
        return ErrorType.NETWORK, "Network error. Please check your internet connection."
    
    # Timeout
    if "timeout" in error_str:
        return ErrorType.TIMEOUT, "Request timed out. Please try again."
    
    # Content filter
    if any(x in error_str for x in ["safety", "blocked", "content filter", "harm"]):
        return ErrorType.CONTENT_FILTER, "Content was blocked by safety filters."
    
    # Invalid response format
    if any(x in error_str for x in ["json", "parse", "decode", "format"]):
        return ErrorType.INVALID_RESPONSE, "Invalid response from API. Please retry."
    
    return ErrorType.UNKNOWN, f"An error occurred: {str(error)[:100]}"


def format_error_message(error: Exception, operation: str = "operation") -> str:
    """
    Format an error message for user display.
    
    Args:
        error: The exception
        operation: Name of the operation that failed
        
    Returns:
        User-friendly error message
    """
    _, message = classify_error(error)  # SonarQube fix: S1481 - use _ for unused variable
    return f"Failed to {operation}: {message}"


def should_rotate_key(error: Exception) -> bool:
    """
    Determine if an error should trigger API key rotation.
    
    Args:
        error: The exception to check
        
    Returns:
        True if key rotation is recommended
    """
    error_type, _ = classify_error(error)
    return error_type in (ErrorType.RATE_LIMIT, ErrorType.QUOTA_EXCEEDED, ErrorType.INVALID_KEY)


def sanitize_api_key(key: str) -> str:
    """
    Mask an API key for safe logging/display.
    
    Args:
        key: The full API key
        
    Returns:
        Masked key (e.g., "AIza...xyz")
    """
    if not key or len(key) < 10:
        return "invalid"
    return f"{key[:4]}...{key[-4:]}"


def validate_api_key_format(key: str) -> Tuple[bool, str]:
    """
    Validate Google API key format.
    
    Args:
        key: API key to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    key = key.strip()
    
    if not key:
        return False, "API key cannot be empty."
    
    if not key.startswith("AIza"):
        return False, "Invalid Google AI API key format (must start with 'AIza')."
    
    if len(key) < 35 or len(key) > 50:
        return False, "Invalid API key length."
    
    # Check for invalid characters
    if not re.match(r"^[A-Za-z0-9_-]+$", key):
        return False, "API key contains invalid characters."
    
    return True, ""


def highlight_word(text: str, word: str, tag: str = "b") -> str:
    """
    Highlight a word in text with HTML tags.
    
    Args:
        text: The text containing the word
        word: The word to highlight
        tag: HTML tag to use (default: "b" for bold)
        
    Returns:
        Text with word wrapped in HTML tags
    """
    if not text or not word:
        return text
    
    # Case-insensitive replacement preserving original case
    pattern = re.compile(re.escape(word), re.IGNORECASE)
    return pattern.sub(f"<{tag}>\\g<0></{tag}>", text)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: String to append if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_json_from_response(text: str) -> Optional[str]:
    """
    Extract JSON object from a text response that may contain markdown.
    
    Args:
        text: Response text that may contain ```json blocks
        
    Returns:
        Extracted JSON string or None
    """
    if not text:
        return None
    
    # Try to find JSON in code blocks (SonarQube fix: avoid reluctant quantifier)
    json_match = re.search(r"```(?:json)?\s*(\{[^`]*\})\s*```", text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    
    # Try to find raw JSON object
    json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return None
