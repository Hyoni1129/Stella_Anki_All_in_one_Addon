# -*- coding: utf-8 -*-
"""
Tests for Configuration Management

Tests ConfigManager and Settings dataclasses.
"""

import unittest
import os
import tempfile
import shutil
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    ConfigManager, Config, 
    TranslationConfig, SentenceConfig, ImageConfig
)


class TestTranslationConfig(unittest.TestCase):
    """Test TranslationConfig dataclass."""
    
    def test_defaults(self):
        """Test default values."""
        config = TranslationConfig()
        
        self.assertEqual(config.target_language, "Korean")
        self.assertEqual(config.batch_size, 10)
        self.assertFalse(config.overwrite_existing)
    
    def test_to_dict(self):
        """Test serialization."""
        config = TranslationConfig(
            target_language="Japanese",
            batch_size=5,
        )
        
        data = config.to_dict()
        
        self.assertEqual(data["target_language"], "Japanese")
        self.assertEqual(data["batch_size"], 5)
    
    def test_from_dict(self):
        """Test deserialization."""
        data = {
            "target_language": "Spanish",
            "batch_size": 20,
            "model_name": "gemini-2.5-pro",
        }
        
        config = TranslationConfig.from_dict(data)
        
        self.assertEqual(config.target_language, "Spanish")
        self.assertEqual(config.batch_size, 20)
        self.assertEqual(config.model_name, "gemini-2.5-pro")


class TestSentenceConfig(unittest.TestCase):
    """Test SentenceConfig dataclass."""
    
    def test_defaults(self):
        """Test default values."""
        config = SentenceConfig()
        
        self.assertEqual(config.difficulty, "Normal")
        self.assertTrue(config.highlight_word)
    
    def test_from_dict_with_missing_keys(self):
        """Test deserialization handles missing keys."""
        data = {"difficulty": "Beginner"}
        
        config = SentenceConfig.from_dict(data)
        
        self.assertEqual(config.difficulty, "Beginner")
        self.assertTrue(config.highlight_word)  # Default


class TestImageConfig(unittest.TestCase):
    """Test ImageConfig dataclass."""
    
    def test_defaults(self):
        """Test default values."""
        config = ImageConfig()
        
        self.assertEqual(config.default_style, "realistic")
    
    def test_to_dict(self):
        """Test serialization."""
        config = ImageConfig(
            default_style="anime",
            source_field="Word",
            destination_field="Picture",
        )
        
        data = config.to_dict()
        
        self.assertEqual(data["default_style"], "anime")
        self.assertEqual(data["source_field"], "Word")


class TestConfig(unittest.TestCase):
    """Test main Config class."""
    
    def test_combined_config(self):
        """Test combined configuration."""
        config = Config(
            translation=TranslationConfig(target_language="French"),
            sentence=SentenceConfig(difficulty="Complex"),
            image=ImageConfig(default_style="watercolor"),
        )
        
        data = config.to_dict()
        
        self.assertEqual(data["translation"]["target_language"], "French")
        self.assertEqual(data["sentence"]["difficulty"], "Complex")
        self.assertEqual(data["image"]["default_style"], "watercolor")
    
    def test_from_dict(self):
        """Test deserialization."""
        data = {
            "translation": {"target_language": "German"},
            "sentence": {"difficulty": "Beginner"},
            "image": {"default_style": "sketch"},
        }
        
        config = Config.from_dict(data)
        
        self.assertEqual(config.translation.target_language, "German")
        self.assertEqual(config.sentence.difficulty, "Beginner")
        self.assertEqual(config.image.default_style, "sketch")


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality."""
    
    def setUp(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "config.json")
        
        # Reset singleton
        ConfigManager._instance = None
    
    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        ConfigManager._instance = None
    
    def test_singleton(self):
        """Test singleton pattern."""
        manager1 = ConfigManager(self.temp_dir)
        manager2 = ConfigManager()
        
        self.assertIs(manager1, manager2)
    
    def test_save_and_load(self):
        """Test saving and loading configuration."""
        manager1 = ConfigManager(self.temp_dir)
        manager1.config.translation.target_language = "Chinese"
        manager1.save()
        
        # Reset singleton
        ConfigManager._instance = None
        
        manager2 = ConfigManager(self.temp_dir)
        
        self.assertEqual(
            manager2.config.translation.target_language,
            "Chinese"
        )
    
    def test_default_config_created(self):
        """Test default config is created when file doesn't exist."""
        manager = ConfigManager(self.temp_dir)
        
        # Should have defaults
        self.assertEqual(
            manager.config.translation.target_language,
            "Korean"
        )
    
    def test_reload(self):
        """Test reloading configuration."""
        manager = ConfigManager(self.temp_dir)
        
        # Modify file directly
        with open(self.config_file, "w") as f:
            json.dump({
                "translation": {"target_language": "Italian"},
            }, f)
        
        manager.reload()
        
        self.assertEqual(
            manager.config.translation.target_language,
            "Italian"
        )


if __name__ == "__main__":
    unittest.main()
