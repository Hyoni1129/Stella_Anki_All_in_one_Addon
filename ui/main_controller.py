# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Main Controller

Central controller that coordinates all features (Translation, Sentence, Image).
Provides unified interface for menu items, configuration, and feature access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, Any, List, Callable
import os

if TYPE_CHECKING:
    from aqt.main import AnkiQt
    from anki.notes import Note

from ..core.logger import get_logger
from ..core.api_key_manager import APIKeyManager
from ..config.settings import ConfigManager


logger = get_logger(__name__)


class StellaAnkiTools:
    """
    Main controller for Stella Anki Tools add-on.
    
    Coordinates all features and provides:
    - Menu integration
    - Settings dialog
    - API key management
    - Feature access (translation, sentence, image)
    """
    
    _instance: Optional['StellaAnkiTools'] = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, mw: Optional['AnkiQt'] = None):
        """
        Initialize main controller.
        
        Args:
            mw: Anki main window instance
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._mw = mw
        self._addon_dir = os.path.dirname(os.path.dirname(__file__))
        self._config_manager = ConfigManager()
        self._config_manager.initialize(self._addon_dir)
        self._key_manager: Optional[APIKeyManager] = None
        
        # Feature modules (lazy-loaded)
        self._translator = None
        self._sentence_generator = None
        self._image_generator = None
        self._prompt_generator = None
        
        # Menu items
        self._menu = None
        self._menu_actions: List[Any] = []
        
        self._initialized = True
        logger.info("StellaAnkiTools main controller initialized")
    
    @property
    def mw(self) -> 'AnkiQt':
        """Get Anki main window."""
        if self._mw is not None:
            return self._mw
        
        try:
            from aqt import mw
            return mw
        except ImportError:
            raise RuntimeError("Cannot access Anki main window")
    
    @property
    def config(self):
        """Get current configuration."""
        return self._config_manager.config
    
    @property
    def key_manager(self) -> APIKeyManager:
        """Get API key manager (lazy-loaded)."""
        if self._key_manager is None:
            self._key_manager = APIKeyManager(self._addon_dir)
        return self._key_manager
    
    # ========== Feature Access ==========
    
    @property
    def translator(self):
        """Get translator instance (lazy-loaded)."""
        if self._translator is None:
            from ..translation.translator import Translator
            self._translator = Translator(self._addon_dir)
        return self._translator
    
    @property
    def sentence_generator(self):
        """Get sentence generator instance (lazy-loaded)."""
        if self._sentence_generator is None:
            from ..sentence.sentence_generator import SentenceGenerator
            self._sentence_generator = SentenceGenerator(self._addon_dir)
        return self._sentence_generator
    
    @property
    def image_generator(self):
        """Get image generator instance (lazy-loaded)."""
        if self._image_generator is None:
            from ..image.image_generator import ImageGenerator
            self._image_generator = ImageGenerator(self.key_manager)
        return self._image_generator
    
    @property
    def prompt_generator(self):
        """Get image prompt generator instance (lazy-loaded)."""
        if self._prompt_generator is None:
            from ..image.prompt_generator import ImagePromptGenerator
            self._prompt_generator = ImagePromptGenerator()
        return self._prompt_generator
    
    # ========== Menu Integration ==========
    
    def setup_menu(self) -> None:
        """Set up the Stella menu in Anki."""
        try:
            from aqt.qt import QMenu, QAction
            
            # Create Stella menu
            self._menu = QMenu("&Stella", self.mw)
            self.mw.form.menubar.addMenu(self._menu)
            
            # Main deck operations dialog (PRIMARY ENTRY POINT)
            deck_ops_action = QAction("📚 Deck Operations...", self.mw)
            deck_ops_action.triggered.connect(self.show_deck_operations)
            self._menu.addAction(deck_ops_action)
            self._menu_actions.append(deck_ops_action)
            
            self._menu.addSeparator()
            
            # Settings action
            settings_action = QAction("⚙️ Settings...", self.mw)
            settings_action.triggered.connect(self.show_settings_dialog)
            self._menu.addAction(settings_action)
            self._menu_actions.append(settings_action)
            
            # API Key Management
            api_action = QAction("🔑 Manage API Keys...", self.mw)
            api_action.triggered.connect(self.show_api_key_dialog)
            self._menu.addAction(api_action)
            self._menu_actions.append(api_action)
            
            # Test API Connection
            test_action = QAction("🧪 Test API Connection", self.mw)
            test_action.triggered.connect(self.test_api_connection)
            self._menu.addAction(test_action)
            self._menu_actions.append(test_action)
            
            # Run Diagnostics
            diag_action = QAction("🕵️ Run Diagnostics", self.mw)
            diag_action.triggered.connect(self.run_diagnostics)
            self._menu.addAction(diag_action)
            self._menu_actions.append(diag_action)
            
            self._menu.addSeparator()
            
            # Statistics
            stats_action = QAction("📊 API Statistics", self.mw)
            stats_action.triggered.connect(self.show_statistics)
            self._menu.addAction(stats_action)
            self._menu_actions.append(stats_action)
            
            # About
            about_action = QAction("ℹ️ About Stella", self.mw)
            about_action.triggered.connect(self.show_about)
            self._menu.addAction(about_action)
            self._menu_actions.append(about_action)
            
            logger.info("Stella menu created")
            
        except Exception as e:
            logger.error(f"Failed to create menu: {e}")
    
    # ========== Dialogs ==========
    
    def show_deck_operations(self) -> None:
        """Show the main deck operations dialog."""
        try:
            from .settings_dialog import DeckOperationDialog
            dialog = DeckOperationDialog(self.mw)
            dialog.exec()
        except Exception as e:
            logger.error(f"Failed to show deck operations dialog: {e}")
            from aqt.utils import showWarning
            showWarning(f"Failed to open deck operations: {e}")
    
    def show_settings_dialog(self) -> None:
        """Show the settings dialog."""
        try:
            from .settings_dialog import StellaSettingsDialog
            dialog = StellaSettingsDialog(self.mw, self._config_manager)
            dialog.exec()
        except ImportError:
            # Fallback: open Anki's add-on config
            from aqt.utils import showInfo
            showInfo(
                "Settings dialog not yet implemented.\n"
                "Please use Tools → Add-ons → Stella Anki Tools → Config"
            )
        except Exception as e:
            logger.error(f"Failed to show settings dialog: {e}")
            from aqt.utils import showWarning
            showWarning(f"Failed to open settings: {e}")
    
    def show_api_key_dialog(self) -> None:
        """Show the API key management dialog."""
        try:
            from .settings_dialog import APIKeyDialog
            dialog = APIKeyDialog(self.mw, self.key_manager)
            dialog.exec()
        except ImportError:
            # Simple fallback
            from aqt.utils import getText, showInfo
            
            current_keys = len(self.key_manager.get_all_keys())
            text, ok = getText(
                f"Enter API key (currently have {current_keys} keys):",
                parent=self.mw,
                title="Add API Key"
            )
            
            if ok and text.strip():
                self.key_manager.add_key(text.strip())
                showInfo(f"API key added. Total keys: {len(self.key_manager.get_all_keys())}")
        except Exception as e:
            logger.error(f"Failed to show API key dialog: {e}")
    
    def show_statistics(self) -> None:
        """Show API usage statistics."""
        try:
            from aqt.utils import showInfo
            
            stats = self.key_manager.get_summary_stats()
            
            msg = "📊 Stella API Statistics\n\n"
            msg += f"Total Keys: {stats.get('total_keys', 0)}\n"
            msg += f"Active Keys: {stats.get('active_keys', 0)}\n"
            msg += f"Total Requests: {stats.get('total_requests', 0)}\n"
            msg += f"Successful: {stats.get('successful_requests', 0)}\n"
            msg += f"Failed: {stats.get('failed_requests', 0)}\n"
            msg += f"Success Rate: {stats.get('success_rate', 0):.1f}%\n"
            
            showInfo(msg, title="Stella Statistics")
            
        except Exception as e:
            logger.error(f"Failed to show statistics: {e}")
    
    def show_about(self) -> None:
        """Show about dialog."""
        from aqt.utils import showInfo
        
        msg = """
🌟 Stella Anki Tools

A unified AI-powered toolkit for Anki flashcards.

Features:
• 🌐 AI Translation - Translate cards to any language
• ✏️ AI Sentences - Generate example sentences
• 🖼️ AI Images - Create images from vocabulary

Powered by Google Gemini API

Version: 1.0.0
"""
        showInfo(msg, title="About Stella Anki Tools")
    
    # ========== API Testing ==========
    
    def test_api_connection(self) -> None:
        """Test API connection with current key."""
        from aqt.utils import showInfo, showWarning
        
        api_key = self.key_manager.get_current_key()
        if not api_key:
            showWarning("No API key configured. Please add an API key first.")
            return
        
        try:
            from ..core.gemini_client import GeminiClient, GENAI_AVAILABLE
            
            if not GENAI_AVAILABLE:
                showWarning(
                    "❌ API Test Error:\n"
                    "The google-generativeai package is not available.\n\n"
                    "This addon requires the Google Generative AI SDK.\n"
                    "Please install it via pip:\n\n"
                    "pip install google-generativeai"
                )
                return
            
            client = GeminiClient(api_key=api_key)
            success, message = client.test_connection()
            
            if success:
                showInfo(
                    f"✅ API Connection Successful!\n\n"
                    f"{message}",
                    title="API Test"
                )
            else:
                showWarning(f"❌ API Test Failed:\n{message}")
                
        except Exception as e:
            showWarning(f"❌ API Test Error:\n{e}")
    
    def run_diagnostics(self) -> None:
        """Run the self-diagnosis suite."""
        try:
            from ..tests.diagnostics import StellaDiagnostics
            from aqt.utils import showInfo, showText
            
            # Run diagnostics
            diag = StellaDiagnostics()
            results = diag.run_all()
            
            status = results.get("final_status", "UNKNOWN")
            
            # Format report for display
            import json
            report_str = json.dumps(results, indent=2, ensure_ascii=False)
            
            if status == "SUCCESS":
                showInfo(
                    "✅ Diagnostics Passed!\n\n"
                    "All systems appear to be functioning correctly.\n"
                    "See detailed report for more info.",
                    title="Stella Diagnostics"
                )
            else:
                reason = results.get("error", "Unknown error")
                showInfo(
                    f"⚠️ Diagnostics Failed: {status}\n\n"
                    f"Reason: {reason}\n\n"
                    "Please check the log file or share the report.",
                    title="Stella Diagnostics"
                )
            
            # Show detailed report
            showText(report_str, title="Diagnostic Report")
            
        except Exception as e:
            logger.error(f"Failed to run diagnostics: {e}")
            from aqt.utils import showWarning
            showWarning(f"Failed to run diagnostics: {e}")
    
    # ========== Cleanup ==========
    
    def cleanup(self) -> None:
        """Clean up resources on unload."""
        try:
            # Save any pending state
            if self._key_manager:
                self._key_manager.save_state()
            
            self._config_manager.save()
            
            logger.info("StellaAnkiTools cleanup complete")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Module-level access
_controller: Optional[StellaAnkiTools] = None


def get_controller() -> StellaAnkiTools:
    """Get the main controller singleton."""
    global _controller
    if _controller is None:
        _controller = StellaAnkiTools()
    return _controller


def initialize(mw: 'AnkiQt') -> StellaAnkiTools:
    """Initialize the main controller with Anki main window."""
    global _controller
    _controller = StellaAnkiTools(mw)
    _controller.setup_menu()
    return _controller
