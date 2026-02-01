# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Image Module

Provides AI-powered image generation for flashcards using Gemini Imagen.
Includes:
- ImagePromptGenerator: Creates optimized text-to-image prompts
- ImageGenerator: Generates images using Gemini Imagen model
- AnkiMediaManager: Handles adding images to Anki media collection
"""

from .prompt_generator import ImagePromptGenerator, ImagePromptResult
from .image_generator import ImageGenerator, ImageGenerationResult
from .anki_media import AnkiMediaManager, MediaAddResult

__all__ = [
    "ImagePromptGenerator",
    "ImagePromptResult",
    "ImageGenerator",
    "ImageGenerationResult",
    "AnkiMediaManager",
    "MediaAddResult",
]
