# -*- coding: utf-8 -*-
"""
Stella Anki Tools - AI Prompts

Contains all AI prompts for translation, sentence generation, and image generation.
Centralized location for easy customization and maintenance.
"""

from __future__ import annotations

from typing import Dict, Any


# =============================================================================
# TRANSLATION PROMPTS
# =============================================================================

TRANSLATION_SYSTEM_PROMPT = """You are an expert vocabulary translator specializing in context-aware translation.

Your task is to translate vocabulary words accurately based on context provided by their definitions.

Guidelines:
1. Analyze the definition/context to understand the specific meaning intended
2. Provide the most accurate translation for that specific meaning
3. If multiple meanings exist, use the context to choose the correct one
4. Keep translations concise and natural in the target language
5. For proper nouns, provide both transliteration and meaning if applicable

Output Format:
Return ONLY the translation, nothing else. No explanations, no alternatives."""


def get_translation_prompt(
    word: str,
    definition: str,
    target_language: str,
    difficulty: str = "Normal"
) -> str:
    """
    Generate a translation prompt.
    
    Args:
        word: The word to translate
        definition: Context/definition for disambiguation
        target_language: Target language for translation
        difficulty: Translation style (Beginner, Normal, Complex)
        
    Returns:
        Formatted prompt string
    """
    difficulty_instructions = {
        "Beginner": "Use simple, common words suitable for beginners.",
        "Normal": "Use natural, everyday language.",
        "Complex": "Use precise, sophisticated vocabulary when appropriate.",
    }
    
    instruction = difficulty_instructions.get(difficulty, difficulty_instructions["Normal"])
    
    return f"""Translate the following word to {target_language}.

Word: {word}
Context/Definition: {definition}

{instruction}

Translation:"""


# =============================================================================
# SENTENCE GENERATION PROMPTS
# =============================================================================

SENTENCE_SYSTEM_PROMPT = """You are an expert language teacher creating example sentences for vocabulary learning.

Your task is to create natural, memorable example sentences that clearly demonstrate word usage.

Guidelines:
1. Create sentences that clearly show the word's meaning in context
2. Use natural, everyday language
3. Make sentences memorable and educational
4. Include both the sentence and its translation
5. The target word should be used naturally, not forced

Output Format:
Return a JSON object with exactly these fields:
{
    "translated_sentence": "The sentence in the target language",
    "translated_conjugated_word": "The word as it appears in the sentence",
    "english_sentence": "English translation of the sentence",
    "english_word": "The English word"
}"""


def get_sentence_prompt(
    word: str,
    target_language: str,
    difficulty: str = "Normal"
) -> str:
    """
    Generate a sentence creation prompt.
    
    Args:
        word: The word to create a sentence for
        target_language: Language for the sentence
        difficulty: Sentence complexity (Beginner, Normal, Complex)
        
    Returns:
        Formatted prompt string
    """
    difficulty_specs = {
        "Beginner": {
            "length": "5-8 words",
            "grammar": "simple present tense, basic structure",
            "vocab": "common, everyday words",
        },
        "Normal": {
            "length": "8-12 words",
            "grammar": "varied tenses, natural structure",
            "vocab": "natural vocabulary mix",
        },
        "Complex": {
            "length": "12-18 words",
            "grammar": "complex structures, varied tenses",
            "vocab": "sophisticated, nuanced vocabulary",
        },
    }
    
    spec = difficulty_specs.get(difficulty, difficulty_specs["Normal"])
    
    return f"""Create an example sentence for vocabulary learning.

Target Word: {word}
Language: {target_language}
Difficulty: {difficulty}

Requirements:
- Sentence length: {spec['length']}
- Grammar: {spec['grammar']}
- Vocabulary: {spec['vocab']}

Create a sentence that naturally uses "{word}" and clearly demonstrates its meaning.

Return your response as a JSON object:
{{
    "translated_sentence": "sentence in {target_language}",
    "translated_conjugated_word": "the word as used in the sentence",
    "english_sentence": "English translation",
    "english_word": "{word}"
}}"""


# =============================================================================
# IMAGE GENERATION PROMPTS
# =============================================================================

IMAGE_SYSTEM_PROMPT = """You are an expert prompt artist creating image generation prompts for vocabulary flashcards.

Your task is to transform vocabulary words into vivid, educational scene descriptions.

Guidelines:
1. Create scenes that visually represent the word's meaning
2. Focus on a single, clear main subject
3. Make the scene memorable and educational
4. Use beautiful, appealing art style descriptions
5. Avoid text, letters, or watermarks in descriptions

Output Format:
Return ONLY the scene description, no explanations or metadata."""


IMAGE_STYLE_PRESETS: Dict[str, str] = {
    "anime": """Beautiful anime style with vibrant colors, high-quality digital art, clean line art.
If a person is needed, use a cute young female anime character.""",
    
    "realistic": """Photorealistic style with natural lighting and detailed textures.
High-quality photography aesthetic with professional composition.""",
    
    "watercolor": """Soft watercolor painting style with gentle colors and artistic brush strokes.
Dreamy, ethereal quality with beautiful color blending.""",
    
    "minimalist": """Clean, minimalist design with simple shapes and limited color palette.
Modern, elegant aesthetic with clear focal point.""",
    
    "cartoon": """Bright, cheerful cartoon style with bold colors and friendly characters.
Fun, approachable aesthetic suitable for all ages.""",
}


def get_image_prompt(
    word: str,
    style_preset: str = "anime",
    custom_instructions: str = ""
) -> str:
    """
    Generate an image creation prompt.
    
    Args:
        word: The word to visualize
        style_preset: Art style preset name
        custom_instructions: Additional user instructions
        
    Returns:
        Formatted prompt string
    """
    style = IMAGE_STYLE_PRESETS.get(style_preset, IMAGE_STYLE_PRESETS["anime"])
    
    base_prompt = f"""Create a detailed scene description for an image that visually represents the word: "{word}"

**Style Requirements:**
{style}

**Scene Requirements:**
- Focus on a single main subject that clearly represents "{word}"
- Create a scene that visually demonstrates the word's meaning
- Make it educational and memorable for language learning
- No text, letters, or watermarks in the image
- Emotionally positive or neutral tone

**Instructions:**
1. Understand the core meaning of "{word}"
2. Create a scene that visually teaches this meaning
3. Include specific details about the setting, character (if any), and action
4. Make it clear and beautiful for a flashcard"""

    if custom_instructions:
        base_prompt += f"\n\n**Additional Instructions:**\n{custom_instructions}"
    
    base_prompt += f"\n\nGenerate a detailed scene description for: {word}"
    
    return base_prompt


# =============================================================================
# UNIFIED/MASTER PROMPTS
# =============================================================================

MASTER_IMAGE_PROMPT = """**Objective:** Generate a detailed, vivid, and imaginative scene description for an image that visually represents the meaning of a given word. The description will be used as a prompt for an image generation AI.

**Instructions:**
1. **Analyze the Word:** Understand the core meaning and context of the word: `{word}`.
2. **Create a Scene:** Based on the word's meaning, construct a detailed scene description. Do not just repeat the word; describe a scenario that illustrates it.
3. **Follow Style Guidelines:**

    * **Art Style:** Beautiful anime style, vibrant colors, high-quality digital art, clean line art.
    * **Character:** If a person is needed, it MUST be a cute young female anime character. No male characters.
    * **Composition:** Create a detailed, clear, and beautiful composition focusing on a single main subject that represents the word.
    * **Educational Focus:** The scene must be memorable, visually appealing, and clearly represent the word's meaning for a language-learning flashcard.
    * **Exclusions:** Avoid text, letters, or watermarks. The scene should be emotionally positive or neutral and safe for all ages.

**Example for the word "apple":**
"A cute anime-style girl with bright, curious eyes is standing in a sunlit kitchen, gently picking up a shiny red apple from a wooden table. The background is soft and slightly blurred, focusing all attention on her and the apple."

**Your Task:**
Generate a scene description for the word: `{word}`"""


# =============================================================================
# GENERATION CONFIG
# =============================================================================

def get_generation_config(task: str = "translation") -> Dict[str, Any]:
    """
    Get Gemini generation configuration for a specific task.
    
    Args:
        task: Type of task (translation, sentence, image_prompt)
        
    Returns:
        Generation config dictionary
    """
    configs = {
        "translation": {
            "temperature": 0.3,  # Lower for consistency
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 256,
        },
        "sentence": {
            "temperature": 0.7,  # Higher for creativity
            "top_p": 0.9,
            "top_k": 50,
            "max_output_tokens": 512,
        },
        "image_prompt": {
            "temperature": 0.8,  # Higher for creative descriptions
            "top_p": 0.95,
            "top_k": 60,
            "max_output_tokens": 1024,
        },
    }
    
    return configs.get(task, configs["translation"])
