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
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

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
                "image": {"status": "skipped"}
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
                self._check_translation_feature()
                self._check_sentence_feature()
                self._check_image_feature()
            else:
                self._log("Skipping feature tests due to API connection failure.")
                self.results["final_status"] = "WARNING"
                
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
            from translation.translator import Translator
            translator = Translator()
            
            # Test direct generation
            word = "apple"
            context = "fruit"
            target_lang = "Spanish"
            
            self._log(f"Translating '{word}' to {target_lang}...")
            result = translator.translate_text(word, context, target_lang)
            
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
            from sentence.sentence_generator import SentenceGenerator
            generator = SentenceGenerator()
            
            # Test generation
            word = "run"
            target_lang = "French"
            
            self._log(f"Generating sentence for '{word}' in {target_lang}...")
            result = generator.generate_sentences(word, target_lang)
            
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
            from image.prompt_generator import ImagePromptGenerator
            generator = ImagePromptGenerator()
            
            word = "ocean"
            
            self._log(f"Generating image prompt for '{word}'...")
            result = generator.generate_prompt(word)
            
            if result and len(result) > 10:
                status["status"] = "success"
                status["prompt_preview"] = result[:50] + "..."
                self._log("Image prompt generation success")
            else:
                status["status"] = "failure"
                status["reason"] = "Empty or short response"
                
        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)
            self._log(f"Image error: {e}")
            
        self.results["features"]["image"] = status

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
