# -*- coding: utf-8 -*-
"""
Stella Anki Tools - UI Module

Provides unified user interface components:
- StellaAnkiTools: Main controller with menu integration
- DeckOperationDialog: Main dialog for deck-based batch operations
- EditorIntegration: Editor buttons and shortcuts
- BatchProgressDialog: Progress UI for batch operations
- StellaSettingsDialog: Configuration dialog
"""

from .main_controller import StellaAnkiTools, get_controller, initialize
from .editor_integration import EditorIntegration, get_editor_integration, setup_editor_integration
from .progress_dialog import BatchProgressDialog, show_batch_progress
from .settings_dialog import StellaSettingsDialog, APIKeyDialog, DeckOperationDialog

__all__ = [
    "StellaAnkiTools",
    "get_controller",
    "initialize",
    "DeckOperationDialog",
    "EditorIntegration",
    "get_editor_integration",
    "setup_editor_integration",
    "BatchProgressDialog",
    "show_batch_progress",
    "StellaSettingsDialog",
    "APIKeyDialog",
]
