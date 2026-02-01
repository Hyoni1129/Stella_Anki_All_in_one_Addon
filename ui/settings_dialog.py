# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Settings Dialog & Deck Operations

Provides:
- DeckOperationDialog: Main dialog for deck-based batch operations
- StellaSettingsDialog: Configuration dialog
- APIKeyDialog: API key management
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional, List, Dict, Any, Set
import threading
import time

# Get addon directory
_addon_dir = os.path.dirname(os.path.dirname(__file__))

if TYPE_CHECKING:
    from aqt.main import AnkiQt
    from ..config.settings import ConfigManager

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QComboBox, QPushButton, QCheckBox, QSpinBox,
    QProgressBar, QGroupBox, QTextEdit, QMessageBox,
    QThreadPool, Qt, QSizePolicy
)
from aqt.utils import showInfo, showWarning, askUser

from ..core.logger import get_logger
from ..core.api_key_manager import get_api_key_manager
from ..config.settings import ConfigManager
from ..sentence.progress_state import ProgressStateManager

logger = get_logger(__name__)


def format_eta(seconds: float) -> str:
    """Format seconds to human readable ETA string."""
    if seconds <= 0:
        return "calculating..."
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


class DeckOperationDialog(QDialog):
    """
    Main dialog for deck-based batch operations.
    
    Allows users to:
    - Select a deck directly (no browser required)
    - Configure field mappings
    - Run batch translation, sentence, or image generation
    - Monitor progress in real-time with ETA
    - Pause/resume operations
    - Resume interrupted batches
    """
    
    def __init__(self, parent: 'AnkiQt'):
        super().__init__(parent)
        self._mw = parent
        self._config_manager = ConfigManager()
        self._key_manager = get_api_key_manager()
        self._thread_pool = QThreadPool.globalInstance()
        self._progress_manager = ProgressStateManager(_addon_dir)
        
        # Current state
        self._current_deck = ""
        self._current_fields: List[str] = []
        self._active_worker = None
        self._cancel_event = threading.Event()
        self._pause_event = threading.Event()  # New: for pause functionality
        
        # ETA tracking
        self._start_time: float = 0
        self._items_processed: int = 0
        self._total_items: int = 0
        
        # UI elements
        self._deck_dropdown: Optional[QComboBox] = None
        self._source_dropdown: Optional[QComboBox] = None
        self._context_dropdown: Optional[QComboBox] = None
        self._dest_dropdown: Optional[QComboBox] = None
        self._sentence_field_dropdown: Optional[QComboBox] = None
        self._sentence_trans_dropdown: Optional[QComboBox] = None
        self._image_field_dropdown: Optional[QComboBox] = None
        self._language_dropdown: Optional[QComboBox] = None
        self._model_dropdown: Optional[QComboBox] = None
        self._batch_size_spin: Optional[QSpinBox] = None
        self._delay_spin: Optional[QSpinBox] = None
        self._progress_bar: Optional[QProgressBar] = None
        self._progress_label: Optional[QLabel] = None
        self._status_label: Optional[QLabel] = None
        self._eta_label: Optional[QLabel] = None
        self._error_log: Optional[QTextEdit] = None
        
        # Stats
        self._success_count = 0
        self._failure_count = 0
        
        self._setup_ui()
        self._load_decks()
        self._check_pending_operations()
        logger.info("DeckOperationDialog initialized")
    
    def _check_pending_operations(self) -> None:
        """Check for interrupted operations that can be resumed."""
        if self._progress_manager.has_pending_run():
            run_info = self._progress_manager.describe_run()
            pending = self._progress_manager.get_pending_ids()
            
            if askUser(
                f"Found interrupted operation:\n\n"
                f"Type: {run_info.get('run_type', 'unknown')}\n"
                f"Started: {run_info.get('started_at', 'unknown')}\n"
                f"Pending items: {len(pending)}\n\n"
                f"Would you like to resume?"
            ):
                self._resume_pending_operation()
            else:
                if askUser("Clear this interrupted operation?"):
                    self._progress_manager.clear()
    
    def _resume_pending_operation(self) -> None:
        """Resume an interrupted operation."""
        run_info = self._progress_manager.describe_run()
        pending_ids = self._progress_manager.get_pending_ids()
        
        if not pending_ids:
            showInfo("No pending items to process.")
            return
        
        # Get the stored run info
        run_type = run_info.get("run_type", "")
        
        if run_type == "sentence":
            self._resume_sentence_batch(pending_ids, run_info)
        elif run_type == "image":
            self._resume_image_batch(pending_ids, run_info)
        elif run_type == "translation":
            showInfo("Translation resume not yet implemented.")
        else:
            showWarning(f"Unknown operation type: {run_type}")
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.setWindowTitle("Stella Anki Tools - Deck Operations")
        self.setMinimumWidth(550)
        self.setMinimumHeight(700)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Translation Tab
        translation_tab = self._create_translation_tab()
        tab_widget.addTab(translation_tab, "🌐 Translation")
        
        # Sentence Tab
        sentence_tab = self._create_sentence_tab()
        tab_widget.addTab(sentence_tab, "✏️ Sentences")
        
        # Image Tab
        image_tab = self._create_image_tab()
        tab_widget.addTab(image_tab, "🖼️ Images")
        
        # Settings Tab
        settings_tab = self._create_settings_tab()
        tab_widget.addTab(settings_tab, "⚙️ Settings")
        
        layout.addWidget(tab_widget)
        
        # Progress section (shared)
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # Status and ETA row
        status_row = QHBoxLayout()
        self._status_label = QLabel("Ready")
        status_row.addWidget(self._status_label, 1)
        self._eta_label = QLabel("ETA: --")
        self._eta_label.setStyleSheet("color: #666;")
        status_row.addWidget(self._eta_label)
        progress_layout.addLayout(status_row)
        
        progress_row = QHBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setTextVisible(True)
        progress_row.addWidget(self._progress_bar)
        self._progress_label = QLabel("0 / 0")
        progress_row.addWidget(self._progress_label)
        progress_layout.addLayout(progress_row)
        
        # Control buttons row
        control_row = QHBoxLayout()
        self._pause_btn = QPushButton("⏸ Pause")
        self._pause_btn.setStyleSheet("background-color: #ffc107; color: black;")
        self._pause_btn.setEnabled(False)
        self._pause_btn.clicked.connect(self._toggle_pause)
        control_row.addWidget(self._pause_btn)
        
        self._global_stop_btn = QPushButton("⏹ Stop All")
        self._global_stop_btn.setStyleSheet("background-color: #dc3545; color: white;")
        self._global_stop_btn.setEnabled(False)
        self._global_stop_btn.clicked.connect(self._stop_operation)
        control_row.addWidget(self._global_stop_btn)
        
        control_row.addStretch()
        progress_layout.addLayout(control_row)
        
        # Error log (collapsible)
        self._error_log = QTextEdit()
        self._error_log.setReadOnly(True)
        self._error_log.setMaximumHeight(80)
        self._error_log.setPlaceholderText("Errors will appear here...")
        self._error_log.hide()
        progress_layout.addWidget(self._error_log)
        
        layout.addWidget(progress_group)
        
        # Bottom buttons
        button_row = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_row.addStretch()
        button_row.addWidget(close_btn)
        layout.addLayout(button_row)
    
    def _create_translation_tab(self) -> QWidget:
        """Create the translation tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header
        header = QLabel("Batch Translation")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # Deck selection
        deck_layout = QHBoxLayout()
        deck_layout.addWidget(QLabel("Deck:"))
        self._deck_dropdown = QComboBox()
        self._deck_dropdown.currentTextChanged.connect(self._on_deck_changed)
        deck_layout.addWidget(self._deck_dropdown, 1)
        layout.addLayout(deck_layout)
        
        # Field mappings
        fields_group = QGroupBox("Field Mapping")
        fields_layout = QVBoxLayout(fields_group)
        
        # Source field
        source_row = QHBoxLayout()
        source_row.addWidget(QLabel("Source Field (Word):"))
        self._source_dropdown = QComboBox()
        self._source_dropdown.setEnabled(False)
        source_row.addWidget(self._source_dropdown, 1)
        fields_layout.addLayout(source_row)
        
        # Context field
        context_row = QHBoxLayout()
        context_row.addWidget(QLabel("Context Field (Optional):"))
        self._context_dropdown = QComboBox()
        self._context_dropdown.setEnabled(False)
        context_row.addWidget(self._context_dropdown, 1)
        fields_layout.addLayout(context_row)
        
        # Destination field
        dest_row = QHBoxLayout()
        dest_row.addWidget(QLabel("Destination Field:"))
        self._dest_dropdown = QComboBox()
        self._dest_dropdown.setEnabled(False)
        dest_row.addWidget(self._dest_dropdown, 1)
        fields_layout.addLayout(dest_row)
        
        layout.addWidget(fields_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        # Language
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Target Language:"))
        self._language_dropdown = QComboBox()
        self._language_dropdown.setEditable(True)
        self._language_dropdown.addItems([
            "Korean", "Japanese", "Chinese (Simplified)", "Chinese (Traditional)",
            "Spanish", "French", "German", "Italian", "Portuguese", "Russian",
            "Vietnamese", "Thai", "Indonesian", "Arabic", "Hindi"
        ])
        self._language_dropdown.setCurrentText(
            self._config_manager.config.translation.target_language
        )
        lang_row.addWidget(self._language_dropdown, 1)
        options_layout.addLayout(lang_row)
        
        # Model
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Model:"))
        self._model_dropdown = QComboBox()
        self._model_dropdown.setEditable(True)
        self._model_dropdown.addItems([
            "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"
        ])
        self._model_dropdown.setCurrentText(
            self._config_manager.config.translation.model_name
        )
        model_row.addWidget(self._model_dropdown, 1)
        options_layout.addLayout(model_row)
        
        # Checkboxes
        self._overwrite_cb = QCheckBox("Overwrite existing translations")
        self._overwrite_cb.setChecked(self._config_manager.config.translation.overwrite_existing)
        options_layout.addWidget(self._overwrite_cb)
        
        self._skip_existing_cb = QCheckBox("Skip cards with existing translation")
        self._skip_existing_cb.setChecked(True)
        options_layout.addWidget(self._skip_existing_cb)
        
        layout.addWidget(options_group)
        
        # Batch settings
        batch_group = QGroupBox("Batch Settings")
        batch_layout = QHBoxLayout(batch_group)
        
        batch_layout.addWidget(QLabel("Batch Size:"))
        self._batch_size_spin = QSpinBox()
        self._batch_size_spin.setRange(1, 30)
        self._batch_size_spin.setValue(self._config_manager.config.translation.batch_size)
        batch_layout.addWidget(self._batch_size_spin)
        
        batch_layout.addWidget(QLabel("Delay (sec):"))
        self._delay_spin = QSpinBox()
        self._delay_spin.setRange(1, 60)
        self._delay_spin.setValue(int(self._config_manager.config.translation.batch_delay_seconds))
        batch_layout.addWidget(self._delay_spin)
        
        batch_layout.addStretch()
        layout.addWidget(batch_group)
        
        # Action buttons
        button_row = QHBoxLayout()
        
        self._translate_btn = QPushButton("▶ Start Translation")
        self._translate_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self._translate_btn.clicked.connect(self._start_translation)
        button_row.addWidget(self._translate_btn)
        
        self._stop_btn = QPushButton("⏹ Stop")
        self._stop_btn.setStyleSheet("background-color: #ff6b6b; color: white;")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_operation)
        button_row.addWidget(self._stop_btn)
        
        layout.addLayout(button_row)
        layout.addStretch()
        
        return tab
    
    def _create_sentence_tab(self) -> QWidget:
        """Create the sentence generation tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        header = QLabel("Batch Sentence Generation")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        info = QLabel("Generates example sentences for vocabulary cards.")
        info.setStyleSheet("color: gray;")
        layout.addWidget(info)
        
        # Field mappings
        fields_group = QGroupBox("Field Mapping")
        fields_layout = QVBoxLayout(fields_group)
        
        # Expression field (word)
        expr_row = QHBoxLayout()
        expr_row.addWidget(QLabel("Word Field:"))
        self._sentence_word_dropdown = QComboBox()
        self._sentence_word_dropdown.setEnabled(False)
        expr_row.addWidget(self._sentence_word_dropdown, 1)
        fields_layout.addLayout(expr_row)
        
        # Sentence field
        sent_row = QHBoxLayout()
        sent_row.addWidget(QLabel("Sentence Field:"))
        self._sentence_field_dropdown = QComboBox()
        self._sentence_field_dropdown.setEnabled(False)
        sent_row.addWidget(self._sentence_field_dropdown, 1)
        fields_layout.addLayout(sent_row)
        
        # Translation field
        trans_row = QHBoxLayout()
        trans_row.addWidget(QLabel("Translation Field:"))
        self._sentence_trans_dropdown = QComboBox()
        self._sentence_trans_dropdown.setEnabled(False)
        trans_row.addWidget(self._sentence_trans_dropdown, 1)
        fields_layout.addLayout(trans_row)
        
        layout.addWidget(fields_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        # Language
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Sentence Language:"))
        self._sentence_lang_dropdown = QComboBox()
        self._sentence_lang_dropdown.setEditable(True)
        self._sentence_lang_dropdown.addItems([
            "Korean", "Japanese", "Chinese (Simplified)", "Spanish",
            "French", "German", "Italian", "Portuguese"
        ])
        self._sentence_lang_dropdown.setCurrentText(
            self._config_manager.config.sentence.target_language
        )
        lang_row.addWidget(self._sentence_lang_dropdown, 1)
        options_layout.addLayout(lang_row)
        
        # Difficulty
        diff_row = QHBoxLayout()
        diff_row.addWidget(QLabel("Difficulty:"))
        self._difficulty_dropdown = QComboBox()
        self._difficulty_dropdown.addItems(["Beginner", "Normal", "Complex"])
        self._difficulty_dropdown.setCurrentText(
            self._config_manager.config.sentence.difficulty
        )
        diff_row.addWidget(self._difficulty_dropdown, 1)
        options_layout.addLayout(diff_row)
        
        # Highlight
        self._highlight_cb = QCheckBox("Highlight word in sentence")
        self._highlight_cb.setChecked(self._config_manager.config.sentence.highlight_word)
        options_layout.addWidget(self._highlight_cb)
        
        # Skip existing
        self._skip_sentence_cb = QCheckBox("Skip cards with existing sentences")
        self._skip_sentence_cb.setChecked(True)
        options_layout.addWidget(self._skip_sentence_cb)
        
        layout.addWidget(options_group)
        
        # Action buttons
        button_row = QHBoxLayout()
        
        self._sentence_btn = QPushButton("▶ Generate Sentences")
        self._sentence_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self._sentence_btn.clicked.connect(self._start_sentence_generation)
        button_row.addWidget(self._sentence_btn)
        
        self._stop_sentence_btn = QPushButton("⏹ Stop")
        self._stop_sentence_btn.setStyleSheet("background-color: #ff6b6b; color: white;")
        self._stop_sentence_btn.setEnabled(False)
        self._stop_sentence_btn.clicked.connect(self._stop_operation)
        button_row.addWidget(self._stop_sentence_btn)
        
        layout.addLayout(button_row)
        layout.addStretch()
        
        return tab
    
    def _create_image_tab(self) -> QWidget:
        """Create the image generation tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        header = QLabel("Batch Image Generation")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        info = QLabel("Generates images for vocabulary cards using Gemini Imagen.")
        info.setStyleSheet("color: gray;")
        layout.addWidget(info)
        
        # Field mappings
        fields_group = QGroupBox("Field Mapping")
        fields_layout = QVBoxLayout(fields_group)
        
        # Word field
        word_row = QHBoxLayout()
        word_row.addWidget(QLabel("Word Field:"))
        self._image_word_dropdown = QComboBox()
        self._image_word_dropdown.setEnabled(False)
        word_row.addWidget(self._image_word_dropdown, 1)
        fields_layout.addLayout(word_row)
        
        # Image field
        img_row = QHBoxLayout()
        img_row.addWidget(QLabel("Image Field:"))
        self._image_field_dropdown = QComboBox()
        self._image_field_dropdown.setEnabled(False)
        img_row.addWidget(self._image_field_dropdown, 1)
        fields_layout.addLayout(img_row)
        
        layout.addWidget(fields_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        # Style
        style_row = QHBoxLayout()
        style_row.addWidget(QLabel("Image Style:"))
        self._style_dropdown = QComboBox()
        self._style_dropdown.addItems([
            "realistic", "illustration", "anime", "watercolor",
            "sketch", "minimalist", "cartoon", "pixel_art"
        ])
        self._style_dropdown.setCurrentText(
            self._config_manager.config.image.style_preset
        )
        style_row.addWidget(self._style_dropdown, 1)
        options_layout.addLayout(style_row)
        
        # Skip existing
        self._skip_image_cb = QCheckBox("Skip cards with existing images")
        self._skip_image_cb.setChecked(True)
        options_layout.addWidget(self._skip_image_cb)
        
        layout.addWidget(options_group)
        
        # Action buttons
        button_row = QHBoxLayout()
        
        self._image_btn = QPushButton("▶ Generate Images")
        self._image_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self._image_btn.clicked.connect(self._start_image_generation)
        button_row.addWidget(self._image_btn)
        
        self._stop_image_btn = QPushButton("⏹ Stop")
        self._stop_image_btn.setStyleSheet("background-color: #ff6b6b; color: white;")
        self._stop_image_btn.setEnabled(False)
        self._stop_image_btn.clicked.connect(self._stop_operation)
        button_row.addWidget(self._stop_image_btn)
        
        layout.addLayout(button_row)
        layout.addStretch()
        
        return tab
    
    def _create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        header = QLabel("Settings")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # API Key section
        api_group = QGroupBox("API Keys")
        api_layout = QVBoxLayout(api_group)
        
        key_count = len(self._key_manager.get_all_keys())
        self._api_status_label = QLabel(f"API Keys configured: {key_count}")
        api_layout.addWidget(self._api_status_label)
        
        api_btn_row = QHBoxLayout()
        add_key_btn = QPushButton("Add API Key")
        add_key_btn.clicked.connect(self._add_api_key)
        api_btn_row.addWidget(add_key_btn)
        
        view_stats_btn = QPushButton("View Statistics")
        view_stats_btn.clicked.connect(self._show_api_stats)
        api_btn_row.addWidget(view_stats_btn)
        
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self._test_api_connection)
        api_btn_row.addWidget(test_btn)
        
        api_btn_row.addStretch()
        api_layout.addLayout(api_btn_row)
        
        layout.addWidget(api_group)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout(general_group)
        
        general_layout.addWidget(QLabel(
            "Additional settings can be configured via:\n"
            "Tools → Add-ons → Stella Anki Tools → Config"
        ))
        
        layout.addWidget(general_group)
        
        layout.addStretch()
        return tab
    
    # ========== Deck Management ==========
    
    def _load_decks(self) -> None:
        """Load available decks into dropdown."""
        if not mw or not mw.col:
            return
        
        deck_names = []
        for deck in mw.col.decks.all_names_and_ids():
            deck_id = mw.col.decks.id(deck.name)
            card_ids = mw.col.decks.cids(deck_id)
            if card_ids:  # Only include decks with cards
                deck_names.append(deck.name)
        
        if not deck_names:
            self._deck_dropdown.addItem("(No decks with cards)")
            return
        
        self._deck_dropdown.clear()
        self._deck_dropdown.addItems(deck_names)
        
        # Restore last selection
        saved_deck = self._config_manager.config.translation.deck
        if saved_deck and saved_deck in deck_names:
            self._deck_dropdown.setCurrentText(saved_deck)
    
    def _on_deck_changed(self, deck_name: str) -> None:
        """Handle deck selection change."""
        if not deck_name or not mw or not mw.col:
            return
        
        self._current_deck = deck_name
        
        # Get fields from first card in deck
        try:
            deck_id = mw.col.decks.id(deck_name)
            card_ids = mw.col.decks.cids(deck_id)
            
            if not card_ids:
                self._clear_field_dropdowns()
                return
            
            card = mw.col.get_card(card_ids[0])
            note = card.note()
            model = note.note_type()
            
            # Get field names
            fields = [field["name"] for field in model["flds"]]
            self._current_fields = fields
            
            # Update all field dropdowns
            self._update_field_dropdowns(fields)
            
            # Show card count
            unique_notes = len(set(mw.col.get_card(cid).nid for cid in card_ids))
            self._status_label.setText(f"Selected: {deck_name} ({unique_notes} notes)")
            
        except Exception as e:
            logger.error(f"Error loading deck fields: {e}")
            self._status_label.setText(f"Error: {e}")
    
    def _update_field_dropdowns(self, fields: List[str]) -> None:
        """Update all field dropdown menus."""
        none_option = "(None)"
        
        # Translation tab
        for dropdown in [self._source_dropdown, self._dest_dropdown]:
            if dropdown:
                dropdown.clear()
                dropdown.addItems(fields)
                dropdown.setEnabled(True)
        
        if self._context_dropdown:
            self._context_dropdown.clear()
            self._context_dropdown.addItem(none_option)
            self._context_dropdown.addItems(fields)
            self._context_dropdown.setEnabled(True)
        
        # Sentence tab
        for dropdown in [self._sentence_word_dropdown, self._sentence_field_dropdown, 
                         self._sentence_trans_dropdown]:
            if dropdown:
                dropdown.clear()
                dropdown.addItems(fields)
                dropdown.setEnabled(True)
        
        # Image tab
        for dropdown in [self._image_word_dropdown, self._image_field_dropdown]:
            if dropdown:
                dropdown.clear()
                dropdown.addItems(fields)
                dropdown.setEnabled(True)
        
        # Try to restore saved field selections
        self._restore_field_selections(fields)
    
    def _restore_field_selections(self, fields: List[str]) -> None:
        """Restore previously saved field selections."""
        config = self._config_manager.config
        
        # Translation fields
        if config.translation.source_field in fields:
            self._source_dropdown.setCurrentText(config.translation.source_field)
        if config.translation.context_field in fields:
            self._context_dropdown.setCurrentText(config.translation.context_field)
        if config.translation.destination_field in fields:
            self._dest_dropdown.setCurrentText(config.translation.destination_field)
        
        # Sentence fields
        if config.sentence.expression_field in fields:
            self._sentence_word_dropdown.setCurrentText(config.sentence.expression_field)
        if config.sentence.sentence_field in fields:
            self._sentence_field_dropdown.setCurrentText(config.sentence.sentence_field)
        if config.sentence.translation_field in fields:
            self._sentence_trans_dropdown.setCurrentText(config.sentence.translation_field)
        
        # Image fields
        if config.image.source_field in fields:
            self._image_word_dropdown.setCurrentText(config.image.source_field)
        if config.image.destination_field in fields:
            self._image_field_dropdown.setCurrentText(config.image.destination_field)
    
    def _clear_field_dropdowns(self) -> None:
        """Clear and disable all field dropdowns."""
        for dropdown in [self._source_dropdown, self._context_dropdown, self._dest_dropdown,
                         self._sentence_word_dropdown, self._sentence_field_dropdown,
                         self._sentence_trans_dropdown, self._image_word_dropdown,
                         self._image_field_dropdown]:
            if dropdown:
                dropdown.clear()
                dropdown.setEnabled(False)
    
    # ========== Note Collection ==========
    
    def _collect_notes_from_deck(
        self,
        source_field: str,
        context_field: Optional[str] = None,
        skip_if_has_content_in: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect notes from the selected deck.
        
        Args:
            source_field: Field to read word from
            context_field: Optional context field
            skip_if_has_content_in: Skip notes that have content in this field
            
        Returns:
            List of note data dictionaries
        """
        if not self._current_deck or not mw or not mw.col:
            return []
        
        try:
            deck_id = mw.col.decks.id(self._current_deck)
            card_ids = mw.col.decks.cids(deck_id)
            
            notes_data = []
            seen_notes: Set[int] = set()
            
            for card_id in card_ids:
                card = mw.col.get_card(card_id)
                note = card.note()
                
                if note.id in seen_notes:
                    continue
                seen_notes.add(note.id)
                
                # Check if should skip
                if skip_if_has_content_in and skip_if_has_content_in in note:
                    content = note[skip_if_has_content_in].strip()
                    if content and not content.startswith("<!--"):
                        continue
                
                # Get word
                if source_field not in note:
                    continue
                word = self._strip_html(note[source_field])
                if not word:
                    continue
                
                # Get context
                context = ""
                if context_field and context_field != "(None)" and context_field in note:
                    context = self._strip_html(note[context_field])
                
                notes_data.append({
                    "note": note,
                    "note_id": note.id,
                    "word": word,
                    "context": context,
                })
            
            return notes_data
            
        except Exception as e:
            logger.error(f"Error collecting notes: {e}")
            return []
    
    def _strip_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        return clean.strip()
    
    # ========== Translation Operations ==========
    
    def _start_translation(self) -> None:
        """Start batch translation."""
        # Validate
        if not self._validate_api_key():
            return
        
        source_field = self._source_dropdown.currentText()
        dest_field = self._dest_dropdown.currentText()
        context_field = self._context_dropdown.currentText()
        
        if not source_field or not dest_field:
            showWarning("Please select source and destination fields.")
            return
        
        if source_field == dest_field:
            showWarning("Source and destination fields must be different.")
            return
        
        # Collect notes
        skip_field = dest_field if self._skip_existing_cb.isChecked() else None
        notes_data = self._collect_notes_from_deck(
            source_field=source_field,
            context_field=context_field if context_field != "(None)" else None,
            skip_if_has_content_in=skip_field
        )
        
        if not notes_data:
            showInfo("No notes to translate (all may already have translations).")
            return
        
        # Confirm
        if not askUser(f"Translate {len(notes_data)} notes?\n\nThis may take a while."):
            return
        
        # Start batch worker
        self._start_batch_operation(
            operation_type="translation",
            notes_data=notes_data,
            dest_field=dest_field
        )
    
    def _start_batch_operation(
        self,
        operation_type: str,
        notes_data: List[Dict],
        dest_field: str
    ) -> None:
        """Start a batch operation with progress tracking."""
        from ..translation.batch_translator import BatchTranslator, BatchTranslationSignals
        
        # Reset state
        self._cancel_event.clear()
        self._success_count = 0
        self._failure_count = 0
        self._error_log.clear()
        self._error_log.hide()
        
        # Update UI
        total = len(notes_data)
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(0)
        self._progress_label.setText(f"0 / {total}")
        self._status_label.setText(f"Processing {operation_type}...")
        
        # Disable buttons
        self._translate_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        
        # Create worker
        worker = BatchTranslator(
            notes_data=notes_data,
            target_language=self._language_dropdown.currentText(),
            destination_field=dest_field,
            model_name=self._model_dropdown.currentText(),
            batch_size=self._batch_size_spin.value(),
            batch_delay_seconds=float(self._delay_spin.value()),
            ignore_errors=True,
            cancel_event=self._cancel_event,
        )
        
        # Connect signals
        worker.signals.progress.connect(self._on_progress)
        worker.signals.detailed_progress.connect(self._on_detailed_progress)
        worker.signals.error_detail.connect(self._on_error_detail)
        worker.signals.finished.connect(self._on_finished)
        worker.signals.error.connect(self._on_error)
        
        self._active_worker = worker
        self._thread_pool.start(worker)
    
    def _on_progress(self, processed: int, total: int) -> None:
        """Update progress bar."""
        self._progress_bar.setValue(processed)
        self._progress_label.setText(f"{processed} / {total}")
    
    def _on_detailed_progress(
        self, processed: int, total: int, success: int, failure: int
    ) -> None:
        """Update detailed progress."""
        self._success_count = success
        self._failure_count = failure
        rate = (success / processed * 100) if processed > 0 else 0
        self._status_label.setText(
            f"Processing... ✅ {success} | ❌ {failure} | Rate: {rate:.1f}%"
        )
    
    def _on_error_detail(self, error_type: str, message: str, count: int) -> None:
        """Log error details."""
        self._error_log.show()
        self._error_log.append(f"[{error_type}] {message} (x{count})")
    
    def _on_error(self, error: str) -> None:
        """Handle critical error."""
        showWarning(f"Operation error:\n{error}")
    
    def _on_finished(self, success: int, failure: int) -> None:
        """Handle operation completion."""
        self._active_worker = None
        
        # Re-enable buttons
        self._translate_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        
        # Show results
        total = success + failure
        self._status_label.setText(f"Completed: {success} success, {failure} failed")
        
        showInfo(
            f"Operation Complete!\n\n"
            f"✅ Successful: {success}\n"
            f"❌ Failed: {failure}\n"
            f"📊 Total: {total}"
        )
    
    def _stop_operation(self) -> None:
        """Stop the current operation."""
        if self._cancel_event:
            self._cancel_event.set()
            self._pause_event.set()  # Also release pause if paused
            self._status_label.setText("Stopping...")
            self._pause_btn.setEnabled(False)
            self._global_stop_btn.setEnabled(False)
    
    def _toggle_pause(self) -> None:
        """Toggle pause/resume state."""
        if self._pause_event.is_set():
            # Currently paused, resume
            self._pause_event.clear()
            self._pause_btn.setText("⏸ Pause")
            self._pause_btn.setStyleSheet("background-color: #ffc107; color: black;")
            self._status_label.setText("Resuming...")
        else:
            # Running, pause
            self._pause_event.set()
            self._pause_btn.setText("▶ Resume")
            self._pause_btn.setStyleSheet("background-color: #28a745; color: white;")
            self._status_label.setText("Paused")
    
    def _update_eta(self, processed: int, total: int) -> None:
        """Update ETA based on current progress."""
        self._items_processed = processed
        if processed <= 0 or self._start_time <= 0:
            self._eta_label.setText("ETA: calculating...")
            return
        
        elapsed = time.time() - self._start_time
        avg_time_per_item = elapsed / processed
        remaining = total - processed
        eta_seconds = avg_time_per_item * remaining
        
        self._eta_label.setText(f"ETA: {format_eta(eta_seconds)}")
    
    def _start_batch_ui(self, total: int, operation_type: str) -> None:
        """Initialize UI for batch operation."""
        self._cancel_event.clear()
        self._pause_event.clear()
        self._success_count = 0
        self._failure_count = 0
        self._start_time = time.time()
        self._total_items = total
        self._items_processed = 0
        self._error_log.clear()
        self._error_log.hide()
        
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(0)
        self._progress_label.setText(f"0 / {total}")
        self._status_label.setText(f"Starting {operation_type}...")
        self._eta_label.setText("ETA: calculating...")
        
        # Enable control buttons
        self._pause_btn.setEnabled(True)
        self._pause_btn.setText("⏸ Pause")
        self._pause_btn.setStyleSheet("background-color: #ffc107; color: black;")
        self._global_stop_btn.setEnabled(True)
    
    def _end_batch_ui(self) -> None:
        """Reset UI after batch operation ends."""
        self._pause_btn.setEnabled(False)
        self._global_stop_btn.setEnabled(False)
        self._eta_label.setText("ETA: --")
    
    # ========== Sentence Generation ==========
    
    def _start_sentence_generation(self) -> None:
        """Start batch sentence generation."""
        if not self._validate_api_key():
            return
        
        word_field = self._sentence_word_dropdown.currentText()
        sentence_field = self._sentence_field_dropdown.currentText()
        trans_field = self._sentence_trans_dropdown.currentText()
        
        if not word_field or not sentence_field:
            showWarning("Please select word and sentence fields.")
            return
        
        # Collect notes
        skip_field = sentence_field if self._skip_sentence_cb.isChecked() else None
        notes_data = self._collect_notes_from_deck(
            source_field=word_field,
            skip_if_has_content_in=skip_field
        )
        
        if not notes_data:
            showInfo("No notes to process.")
            return
        
        if not askUser(f"Generate sentences for {len(notes_data)} notes?"):
            return
        
        # Start batch (using simple loop for now)
        self._run_sentence_batch(
            notes_data=notes_data,
            word_field=word_field,
            sentence_field=sentence_field,
            trans_field=trans_field
        )
    
    def _run_sentence_batch(
        self,
        notes_data: List[Dict],
        word_field: str,
        sentence_field: str,
        trans_field: str,
        resume_ids: Optional[Set[int]] = None
    ) -> None:
        """Run sentence generation batch with pause/resume support."""
        from ..sentence.sentence_generator import SentenceGenerator
        from aqt.qt import QApplication
        
        generator = SentenceGenerator()
        total = len(notes_data)
        success = 0
        failure = 0
        
        language = self._sentence_lang_dropdown.currentText()
        difficulty = self._difficulty_dropdown.currentText()
        highlight = self._highlight_cb.isChecked()
        
        # Start batch UI
        self._start_batch_ui(total, "sentence generation")
        self._sentence_btn.setEnabled(False)
        self._stop_sentence_btn.setEnabled(True)
        
        # Initialize progress state
        note_ids = [n["note_id"] for n in notes_data]
        self._progress_manager.start_run(
            run_type="sentence",
            total_ids=note_ids,
            extra_info={
                "word_field": word_field,
                "sentence_field": sentence_field,
                "trans_field": trans_field,
                "language": language,
                "difficulty": difficulty,
                "highlight": highlight,
            }
        )
        
        for i, note_data in enumerate(notes_data):
            # Check cancel
            if self._cancel_event.is_set():
                break
            
            # Check pause (wait loop)
            while self._pause_event.is_set() and not self._cancel_event.is_set():
                QApplication.processEvents()
                time.sleep(0.1)
            
            if self._cancel_event.is_set():
                break
            
            # Skip if resuming and already done
            note_id = note_data["note_id"]
            if resume_ids and note_id not in resume_ids:
                continue
            
            note = note_data["note"]
            word = note_data["word"]
            
            # Update progress UI
            self._progress_bar.setValue(i + 1)
            self._progress_label.setText(f"{i + 1} / {total}")
            self._status_label.setText(f"Processing: {word[:20]}...")
            self._update_eta(i + 1, total)
            QApplication.processEvents()
            
            try:
                result = generator.generate_sentence_sync(
                    word=word,
                    target_language=language,
                    difficulty=difficulty,
                )
                
                sentence = result.get("translated_sentence", "")
                translation = result.get("english_sentence", "")
                
                if highlight:
                    from ..core.utils import highlight_word
                    conj = result.get("translated_conjugated_word", word)
                    eng_word = result.get("english_word", word)
                    sentence = highlight_word(sentence, conj)
                    translation = highlight_word(translation, eng_word)
                
                note[sentence_field] = sentence
                if trans_field and trans_field in note:
                    note[trans_field] = translation
                mw.col.update_note(note)
                
                success += 1
                self._progress_manager.mark_success(note_id)
                self._key_manager.record_success("sentence")
                
            except Exception as e:
                logger.error(f"Sentence generation failed for '{word}': {e}")
                failure += 1
                self._progress_manager.mark_failure(note_id, str(e))
                self._key_manager.record_failure(str(e))
            
            # Rate limiting
            time.sleep(2.0)
        
        # Cleanup
        self._sentence_btn.setEnabled(True)
        self._stop_sentence_btn.setEnabled(False)
        self._end_batch_ui()
        
        # Clear progress state if completed
        if not self._cancel_event.is_set():
            self._progress_manager.clear()
        
        self._on_finished(success, failure)
    
    def _resume_sentence_batch(self, pending_ids: List[int], run_info: Dict) -> None:
        """Resume an interrupted sentence batch."""
        extra = run_info.get("extra_info", {})
        
        # Rebuild notes_data from pending IDs
        notes_data = []
        for note_id in pending_ids:
            try:
                note = mw.col.get_note(note_id)
                word_field = extra.get("word_field", "")
                if word_field and word_field in note:
                    word = self._strip_html(note[word_field])
                    notes_data.append({
                        "note": note,
                        "note_id": note_id,
                        "word": word,
                        "context": "",
                    })
            except Exception as e:
                logger.error(f"Could not load note {note_id}: {e}")
        
        if not notes_data:
            showInfo("No pending notes could be loaded.")
            return
        
        # Restore settings
        if extra.get("language"):
            self._sentence_lang_dropdown.setCurrentText(extra["language"])
        if extra.get("difficulty"):
            self._difficulty_dropdown.setCurrentText(extra["difficulty"])
        if extra.get("highlight") is not None:
            self._highlight_cb.setChecked(extra["highlight"])
        
        # Run batch with resume
        self._run_sentence_batch(
            notes_data=notes_data,
            word_field=extra.get("word_field", ""),
            sentence_field=extra.get("sentence_field", ""),
            trans_field=extra.get("trans_field", ""),
            resume_ids=set(pending_ids)
        )
    
    # ========== Image Generation ==========
    
    def _start_image_generation(self) -> None:
        """Start batch image generation."""
        if not self._validate_api_key():
            return
        
        word_field = self._image_word_dropdown.currentText()
        image_field = self._image_field_dropdown.currentText()
        
        if not word_field or not image_field:
            showWarning("Please select word and image fields.")
            return
        
        # Collect notes
        skip_field = image_field if self._skip_image_cb.isChecked() else None
        notes_data = self._collect_notes_from_deck(
            source_field=word_field,
            skip_if_has_content_in=skip_field
        )
        
        if not notes_data:
            showInfo("No notes to process.")
            return
        
        if not askUser(f"Generate images for {len(notes_data)} notes?\n\nThis may take a long time."):
            return
        
        # Start batch
        self._run_image_batch(notes_data, word_field, image_field)
    
    def _run_image_batch(
        self,
        notes_data: List[Dict],
        word_field: str,
        image_field: str,
        resume_ids: Optional[Set[int]] = None
    ) -> None:
        """Run image generation batch with pause/resume support."""
        from ..image.image_generator import ImageGenerator
        from ..image.prompt_generator import ImagePromptGenerator
        from ..image.anki_media import AnkiMediaManager
        from aqt.qt import QApplication
        
        image_gen = ImageGenerator(self._key_manager)
        prompt_gen = ImagePromptGenerator()
        media_mgr = AnkiMediaManager()
        
        total = len(notes_data)
        success = 0
        failure = 0
        
        style = self._style_dropdown.currentText()
        
        # Start batch UI
        self._start_batch_ui(total, "image generation")
        self._image_btn.setEnabled(False)
        self._stop_image_btn.setEnabled(True)
        
        # Initialize progress state
        note_ids = [n["note_id"] for n in notes_data]
        self._progress_manager.start_run(
            run_type="image",
            total_ids=note_ids,
            extra_info={
                "word_field": word_field,
                "image_field": image_field,
                "style": style,
            }
        )
        
        for i, note_data in enumerate(notes_data):
            # Check cancel
            if self._cancel_event.is_set():
                break
            
            # Check pause (wait loop)
            while self._pause_event.is_set() and not self._cancel_event.is_set():
                QApplication.processEvents()
                time.sleep(0.1)
            
            if self._cancel_event.is_set():
                break
            
            # Skip if resuming and already done
            note_id = note_data["note_id"]
            if resume_ids and note_id not in resume_ids:
                continue
            
            note = note_data["note"]
            word = note_data["word"]
            
            # Update progress UI
            self._progress_bar.setValue(i + 1)
            self._progress_label.setText(f"{i + 1} / {total}")
            self._status_label.setText(f"Generating image: {word[:20]}...")
            self._update_eta(i + 1, total)
            QApplication.processEvents()
            
            try:
                # Generate prompt
                prompt = prompt_gen.generate_prompt_sync(
                    word=word,
                    style=style
                )
                
                # Generate image
                result = image_gen.generate_image(prompt=prompt, word=word)
                
                if result.success and result.image_data:
                    # Save to media using add_image_from_bytes
                    media_result = media_mgr.add_image_from_bytes(
                        image_data=result.image_data,
                        word=word,
                        extension=".png"
                    )
                    
                    if media_result.success and media_result.filename:
                        note[image_field] = f'<img src="{media_result.filename}">'
                        mw.col.update_note(note)
                        success += 1
                        self._progress_manager.mark_success(note_id)
                        self._key_manager.record_success("image")
                    else:
                        failure += 1
                        self._progress_manager.mark_failure(note_id, media_result.error or "Save failed")
                        logger.warning(f"Failed to save image: {media_result.error}")
                else:
                    failure += 1
                    self._progress_manager.mark_failure(note_id, result.error or "Generation failed")
                    self._key_manager.record_failure(result.error or "unknown")
                    logger.warning(f"Image generation failed: {result.error}")
                    
            except Exception as e:
                logger.error(f"Image generation failed for '{word}': {e}")
                failure += 1
                self._progress_manager.mark_failure(note_id, str(e))
                self._key_manager.record_failure(str(e))
            
            # Rate limiting (images need more time)
            time.sleep(3.0)
        
        # Cleanup
        self._image_btn.setEnabled(True)
        self._stop_image_btn.setEnabled(False)
        self._end_batch_ui()
        
        # Clear progress state if completed
        if not self._cancel_event.is_set():
            self._progress_manager.clear()
        
        self._on_finished(success, failure)
    
    def _resume_image_batch(self, pending_ids: List[int], run_info: Dict) -> None:
        """Resume an interrupted image batch."""
        extra = run_info.get("extra_info", {})
        
        # Rebuild notes_data from pending IDs
        notes_data = []
        for note_id in pending_ids:
            try:
                note = mw.col.get_note(note_id)
                word_field = extra.get("word_field", "")
                if word_field and word_field in note:
                    word = self._strip_html(note[word_field])
                    notes_data.append({
                        "note": note,
                        "note_id": note_id,
                        "word": word,
                        "context": "",
                    })
            except Exception as e:
                logger.error(f"Could not load note {note_id}: {e}")
        
        if not notes_data:
            showInfo("No pending notes could be loaded.")
            return
        
        # Restore settings
        if extra.get("style"):
            self._style_dropdown.setCurrentText(extra["style"])
        
        # Run batch with resume
        self._run_image_batch(
            notes_data=notes_data,
            word_field=extra.get("word_field", ""),
            image_field=extra.get("image_field", ""),
            resume_ids=set(pending_ids)
        )
    
    # ========== API Key Management ==========
    
    def _validate_api_key(self) -> bool:
        """Check if API key is configured."""
        if not self._key_manager.get_current_key():
            showWarning(
                "No API key configured!\n\n"
                "Please add an API key in the Settings tab."
            )
            return False
        return True
    
    def _add_api_key(self) -> None:
        """Add a new API key."""
        from aqt.utils import getText
        
        key, ok = getText("Enter Google API key:", parent=self)
        if ok and key.strip():
            self._key_manager.add_key(key.strip())
            key_count = len(self._key_manager.get_all_keys())
            self._api_status_label.setText(f"API Keys configured: {key_count}")
            showInfo("API key added successfully!")
    
    def _show_api_stats(self) -> None:
        """Show API statistics."""
        stats = self._key_manager.get_summary_stats()
        
        msg = "📊 API Key Statistics\n\n"
        msg += f"Total Keys: {stats.get('total_keys', 0)}\n"
        msg += f"Active Keys: {stats.get('active_keys', 0)}\n"
        msg += f"Total Requests: {stats.get('total_requests', 0)}\n"
        msg += f"Success Rate: {stats.get('success_rate', 0):.1f}%\n"
        
        showInfo(msg, title="API Statistics")
    
    def _test_api_connection(self) -> None:
        """
        Test API connection with comprehensive error detection.
        
        Uses JSON schema validation to properly test the API endpoint
        and provides detailed error classification for common issues.
        """
        api_key = self._key_manager.get_current_key()
        if not api_key:
            showWarning("No API key configured. Please add an API key first.")
            return
        
        self._status_label.setText("Testing API connection...")
        
        # Disable test button temporarily
        test_btn = self.sender()
        if test_btn:
            test_btn.setEnabled(False)
            test_btn.setText("Testing...")
        
        try:
            from ..core.api_tester import test_api_connection
            
            # Get current model and language settings
            model_name = self._config_manager.config.translation.model
            language = self._config_manager.config.translation.language
            
            success, message = test_api_connection(
                api_key=api_key,
                language=language,
                model_name=model_name
            )
            
            if success:
                showInfo(f"✅ {message}")
            else:
                showWarning(f"❌ API Test Failed:\n\n{message}")
                
        except ImportError:
            # Fallback to simple test if api_tester not available
            try:
                from ..core.gemini_client import get_gemini_client
                client = get_gemini_client()
                response = client.generate_text("Say 'Hello'", max_retries=1)
                
                if response:
                    showInfo("✅ API connection successful!")
                else:
                    showWarning("API returned empty response.")
            except Exception as e:
                self._handle_api_test_error(e)
                
        except Exception as e:
            self._handle_api_test_error(e)
        
        finally:
            # Re-enable test button
            if test_btn:
                test_btn.setEnabled(True)
                test_btn.setText("Test Connection")
            self._status_label.setText("Ready")
    
    def _handle_api_test_error(self, error: Exception) -> None:
        """Handle and classify API test errors with helpful messages."""
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # Classify the error for user-friendly messages
        if "api key" in error_msg or "api_key" in error_msg:
            showWarning("❌ Invalid API Key\n\nPlease check your API key is correct.")
        elif "resource exhausted" in error_msg or "quota exceeded" in error_msg:
            showWarning("❌ API Quota Exceeded\n\nYour API quota has been exhausted. "
                       "Please wait or try a different API key.")
        elif "rate limit" in error_msg or "too many requests" in error_msg or "429" in str(error):
            showWarning("❌ Rate Limit Reached\n\nPlease wait a moment and try again.")
        elif "permission" in error_msg or "forbidden" in error_msg:
            showWarning("❌ Permission Denied\n\nYour API key may not have access to this model.")
        elif "model" in error_msg and ("not found" in error_msg or "does not exist" in error_msg):
            showWarning("❌ Model Not Found\n\nThe selected model may not be available. "
                       "Try using 'gemini-2.5-flash' instead.")
        elif "connection" in error_msg or "timeout" in error_msg or "network" in error_msg:
            showWarning("❌ Network Error\n\nPlease check your internet connection.")
        elif "invalid" in error_msg or "bad request" in error_msg:
            showWarning(f"❌ Invalid Request\n\n{error}")
        else:
            showWarning(f"❌ API Test Failed ({error_type}):\n\n{error}")


# Legacy classes for backward compatibility
class StellaSettingsDialog:
    """Settings dialog - now redirects to DeckOperationDialog."""
    
    def __init__(self, parent: 'AnkiQt', config_manager: 'ConfigManager'):
        self._parent = parent
        self._config_manager = config_manager
    
    def exec(self) -> None:
        """Show the settings dialog."""
        dialog = DeckOperationDialog(self._parent)
        dialog.exec()


class APIKeyDialog:
    """API Key management dialog."""
    
    def __init__(self, parent: 'AnkiQt', key_manager):
        self._parent = parent
        self._key_manager = key_manager
    
    def exec(self) -> None:
        """Show API key management dialog."""
        try:
            from aqt.utils import getText, showInfo, askUser
            from aqt.qt import QInputDialog
            
            current_count = len(self._key_manager.get_all_keys())
            
            # Show options
            options = [
                "Add new API key",
                "View key statistics", 
                "Remove all keys",
                "Cancel"
            ]
            
            from aqt.qt import QInputDialog
            choice, ok = QInputDialog.getItem(
                self._parent,
                "Stella API Keys",
                f"Current keys: {current_count}\n\nSelect action:",
                options,
                0,
                False
            )
            
            if not ok:
                return
            
            if choice == "Add new API key":
                self._add_key()
            elif choice == "View key statistics":
                self._show_stats()
            elif choice == "Remove all keys":
                self._clear_keys()
                
        except Exception as e:
            from aqt.utils import showWarning
            showWarning(f"Error: {e}")
    
    def _add_key(self) -> None:
        """Add a new API key."""
        from aqt.utils import getText, showInfo
        
        key, ok = getText("Enter Google API key:", parent=self._parent)
        if ok and key.strip():
            self._key_manager.add_key(key.strip())
            showInfo(f"API key added!\nTotal keys: {len(self._key_manager.get_all_keys())}")
    
    def _show_stats(self) -> None:
        """Show key statistics."""
        from aqt.utils import showInfo
        
        stats = self._key_manager.get_summary_stats()
        
        msg = "📊 API Key Statistics\n\n"
        msg += f"Total Keys: {stats.get('total_keys', 0)}\n"
        msg += f"Active Keys: {stats.get('active_keys', 0)}\n"
        msg += f"Current Key Index: {stats.get('current_key_index', 0)}\n"
        msg += f"Total Requests: {stats.get('total_requests', 0)}\n"
        msg += f"Success Rate: {stats.get('success_rate', 0):.1f}%\n"
        
        showInfo(msg, title="API Statistics")
    
    def _clear_keys(self) -> None:
        """Clear all API keys."""
        from aqt.utils import askUser, showInfo
        
        if askUser("Are you sure you want to remove all API keys?"):
            # This would need a clear_all method in key_manager
            showInfo("Key clearing not yet implemented.\nPlease edit api_keys.json manually.")
