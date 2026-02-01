# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Self-Diagnostics Module

This module provides a comprehensive self-test for the add-on.
It can be run from within Anki to verify that all components are functioning correctly.
"""

import logging
import os
import sys
import traceback
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Ensure we can import from the addon
addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
addon_name = os.path.basename(addon_dir)

if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

# Try to import using package-relative style first (when run via standalone_runner)
# Fall back to direct imports if that fails (when run directly in Anki)
try:
    # Check if addon package is set up in sys.modules
    if addon_name in sys.modules:
        # Import through the package hierarchy
        import importlib
        core_logger = importlib.import_module(f"{addon_name}.core.logger")
        get_logger = core_logger.get_logger
        
        core_api = importlib.import_module(f"{addon_name}.core.api_key_manager")
        APIKeyManager = core_api.APIKeyManager
        
        core_gemini = importlib.import_module(f"{addon_name}.core.gemini_client")
        GeminiClient = core_gemini.GeminiClient
        GENAI_AVAILABLE = core_gemini.GENAI_AVAILABLE
    else:
        # Direct import (when run within Anki context)
        from core.logger import get_logger
        from core.api_key_manager import APIKeyManager
        from core.gemini_client import GeminiClient, GENAI_AVAILABLE
except Exception as e:
    # Fallback to direct import
    from core.logger import get_logger
    from core.api_key_manager import APIKeyManager
    from core.gemini_client import GeminiClient, GENAI_AVAILABLE

# We mock objects if running outside Anki, but this is designed to run IN Anki
try:
    from aqt import mw
    from anki.notes import Note
    IN_ANKI = True
except ImportError:
    IN_ANKI = False
    mw = None

logger = get_logger("diagnostics")

class StellaDiagnostics:
    """
    Runs diagnostic tests for Stella Anki Tools.
    """
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": {},
            "components": {},
            "components": {},
            "features": {
                "translation": {"status": "skipped"},
                "sentence": {"status": "skipped"},
                "image": {"status": "skipped"},
                "ui_init": {"status": "skipped"}
            },
            "final_status": "UNKNOWN"
        }
        self.report_path = os.path.join(addon_dir, "logs", "diagnostic_report.json")
        self.log_path = os.path.join(addon_dir, "logs", "diagnostic_log.txt")
        
        # Ensure log dir exists
        os.makedirs(os.path.dirname(self.report_path), exist_ok=True)

    def run_all(self) -> Dict[str, Any]:
        """Run all diagnostic checks."""
        self._log("Starting Stella Diagnostics...")
        
        try:
            self._check_environment()
            self._check_api_connectivity()
            
            if self.results["components"].get("api_connection", False):
                self._check_sentence_feature()
                self._check_image_feature()
            else:
                self._log("Skipping feature tests due to API connection failure.")
                self.results["final_status"] = "WARNING"
            
            # UI Init check should run regardless of API status
            self._check_ui_init()
                
            if self.results["final_status"] == "UNKNOWN":
                self.results["final_status"] = "SUCCESS"
                
            self._log(f"Diagnostics completed with status: {self.results['final_status']}")
            
        except Exception as e:
            self.results["final_status"] = "ERROR"
            self.results["error"] = str(e)
            self.results["traceback"] = traceback.format_exc()
            self._log(f"Diagnostics failed: {e}")
            self._log(traceback.format_exc())
            
        self._save_report()
        return self.results

    def _log(self, msg: str):
        """Log to console and file."""
        print(f"[StellaDiag] {msg}")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%H:%M:%S')} - {msg}\n")

    def _check_environment(self):
        """Check Python and Anki environment."""
        self._log("Checking environment...")
        env = {
            "python_version": sys.version,
            "addon_dir": addon_dir,
            "in_anki": IN_ANKI,
            "genai_installed": GENAI_AVAILABLE
        }
        
        if IN_ANKI:
            env["anki_version"] = mw.app.version
            env["qt_version"] = "Qt6" # Simplified, can be more specific
            
        self.results["environment"] = env
        self._log(f"Environment: In Anki={IN_ANKI}, GenAI={GENAI_AVAILABLE}")

    def _check_api_connectivity(self):
        """Check API Key and Gemini connection."""
        self._log("Checking API connectivity...")
        
        key_manager = APIKeyManager()
        current_key = key_manager.get_current_key()
        
        comp = {
            "has_api_key": bool(current_key),
            "key_count": len(key_manager.get_all_keys()),
            "api_connection": False
        }
        
        if current_key and GENAI_AVAILABLE:
            try:
                client = GeminiClient()
                success, msg = client.test_connection()
                comp["api_connection"] = success
                comp["connection_message"] = msg
                self._log(f"API Test: {msg}")
            except Exception as e:
                comp["api_connection"] = False
                comp["error"] = str(e)
                self._log(f"API Test Failed: {e}")
        
        self.results["components"].update(comp)

    def _check_translation_feature(self):
        """Check Translation logic."""
        self._log("Testing Translation Feature...")
        status = {"status": "skipped"}
        
        try:
            # Import using package-relative path
            if addon_name in sys.modules:
                import importlib
                translator_module = importlib.import_module(f"{addon_name}.translation.translator")
                Translator = translator_module.Translator
            else:
                from translation.translator import Translator
            translator = Translator()
            
            # Test direct generation
            word = "apple"
            context = "fruit"
            target_lang = "Spanish"
            
            self._log(f"Translating '{word}' to {target_lang}...")
            # Use _generate_translation for direct testing (no Note object needed)
            result = translator._generate_translation(word, context, target_lang, "gemini-2.5-flash")
            
            if result and len(result) > 0:
                status["status"] = "success"
                status["output"] = result
                self._log(f"Translation success: {result}")
            else:
                status["status"] = "failure"
                status["reason"] = "Empty response"
                
        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)
            self._log(f"Translation error: {e}")
            
        self.results["features"]["translation"] = status

    def _check_sentence_feature(self):
        """Check Sentence Generation logic."""
        self._log("Testing Sentence Feature...")
        status = {"status": "skipped"}
        
        try:
            # Import using package-relative path
            if addon_name in sys.modules:
                import importlib
                sentence_module = importlib.import_module(f"{addon_name}.sentence.sentence_generator")
                SentenceGenerator = sentence_module.SentenceGenerator
            else:
                from sentence.sentence_generator import SentenceGenerator
            generator = SentenceGenerator()
            
            # Test generation
            word = "run"
            target_lang = "French"
            
            self._log(f"Generating sentence for '{word}' in {target_lang}...")
            # Use generate_sentence_sync for direct testing (no Note object needed)
            result = generator.generate_sentence_sync(word, target_lang)
            
            if result:
                status["status"] = "success"
                status["output_keys"] = list(result.keys())
                self._log("Sentence generation success")
            else:
                status["status"] = "failure"
                status["reason"] = "Empty response"
                
        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)
            self._log(f"Sentence error: {e}")
            
        self.results["features"]["sentence"] = status

    def _check_image_feature(self):
        """Check Image Prompt logic (not actual image download to save bandwidth)."""
        self._log("Testing Image Feature (Prompt only)...")
        status = {"status": "skipped"}
        
        try:
            # Import using package-relative path
            if addon_name in sys.modules:
                import importlib
                image_module = importlib.import_module(f"{addon_name}.image.prompt_generator")
                ImagePromptGenerator = image_module.ImagePromptGenerator
            else:
                from image.prompt_generator import ImagePromptGenerator
            generator = ImagePromptGenerator()
            
            word = "ocean"
            
            self._log(f"Generating image prompt for '{word}'...")
            result = generator.generate_prompt(word)
            
            # result is an ImagePromptResult object, check success and prompt length
            if result and result.success and len(result.prompt) > 10:
                status["status"] = "success"
                status["prompt_preview"] = result.prompt[:50] + "..."
                self._log("Image prompt generation success")
            else:
                status["status"] = "failure"
                status["reason"] = result.error if result and result.error else "Empty or short response"
                
        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)
            self._log(f"Image error: {e}")
            
        self.results["features"]["image"] = status

    def _check_ui_init(self):
        """Check if UI classes can be instantiated (catches config/attribute errors)."""
        self._log("Testing UI Initialization...")
        status = {"status": "skipped"}
        
        try:
            # Import using package-relative path
            if addon_name in sys.modules:
                import importlib
                ui_module = importlib.import_module(f"{addon_name}.ui.settings_dialog")
                DeckOperationDialog = ui_module.DeckOperationDialog
            else:
                from ui.settings_dialog import DeckOperationDialog
            
            # We need to mock parent widget (AnkiQt)
            if IN_ANKI:
                parent = mw
            else:
                from unittest.mock import MagicMock
                parent = MagicMock()
            
            # Attempt instantiation
            # This triggers __init__ -> _setup_ui -> accessing config settings
            print(f"DEBUG: Instantiating DeckOperationDialog with parent {parent}")
            dialog = DeckOperationDialog(parent)
            print("DEBUG: Instantiation complete")
            
            # Verify the config object is real
            cfg = dialog._config_manager.config
            print(f"DEBUG: Config object: {type(cfg)}")
            print(f"DEBUG: Image Config: {type(cfg.image)}")
            print(f"DEBUG: Image Config vars: {vars(cfg.image)}")
            
            status["status"] = "success"
            self._log("UI Initialization success")
                
        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)
            status["traceback"] = traceback.format_exc()
            self._log(f"UI Initialization error: {e}")
            self._log(traceback.format_exc())
            
        self.results["features"]["ui_init"] = status

    def _save_report(self):
        """Save results to JSON."""
        try:
            with open(self.report_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            self._log(f"Report saved to {self.report_path}")
        except Exception as e:
            self._log(f"Failed to save report: {e}")

if __name__ == "__main__":
    # If run directly as a script
    diag = StellaDiagnostics()
    diag.run_all()
    print(f"Report path: {diag.report_path}")
