# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Configuration Module

Provides settings management and AI prompts.
"""

from .settings import (
    ConfigManager,
    StellaConfig,
    APIConfig,
    TranslationConfig,
    ImageConfig,
    SentenceConfig,
    EditorConfig,
    config_manager,
    get_config,
)

from .prompts import (
    TRANSLATION_SYSTEM_PROMPT,
    SENTENCE_SYSTEM_PROMPT,
    IMAGE_SYSTEM_PROMPT,
    IMAGE_STYLE_PRESETS,
    MASTER_IMAGE_PROMPT,
    get_translation_prompt,
    get_sentence_prompt,
    get_image_prompt,
    get_generation_config,
)

__all__ = [
    # Settings
    "ConfigManager",
    "StellaConfig",
    "APIConfig",
    "TranslationConfig",
    "ImageConfig",
    "SentenceConfig",
    "EditorConfig",
    "config_manager",
    "get_config",
    # Prompts
    "TRANSLATION_SYSTEM_PROMPT",
    "SENTENCE_SYSTEM_PROMPT",
    "IMAGE_SYSTEM_PROMPT",
    "IMAGE_STYLE_PRESETS",
    "MASTER_IMAGE_PROMPT",
    "get_translation_prompt",
    "get_sentence_prompt",
    "get_image_prompt",
    "get_generation_config",
]
