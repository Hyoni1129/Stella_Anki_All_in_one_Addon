# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Progress Dialog

Provides progress UI for batch operations like bulk translation,
sentence generation, and image generation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable, Dict, Any
from dataclasses import dataclass

if TYPE_CHECKING:
    from aqt.main import AnkiQt
    from PyQt6.QtWidgets import QWidget

from ..core.logger import get_logger


logger = get_logger(__name__)


@dataclass
class ProgressState:
    """State for progress tracking."""
    current: int = 0
    total: int = 0
    current_item: str = ""
    status: str = "running"  # running, paused, cancelled, completed
    errors: int = 0
    successes: int = 0


class BatchProgressDialog:
    """
    Progress dialog for batch operations.
    
    Uses Qt dialog with:
    - Progress bar
    - Current item indicator
    - Pause/Resume/Cancel buttons
    - Error summary
    """
    
    def __init__(
        self,
        parent: Optional['QWidget'] = None,
        title: str = "Processing",
        total: int = 0,
        on_cancel: Optional[Callable] = None,
        on_pause: Optional[Callable] = None
    ):
        """
        Initialize progress dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            total: Total number of items
            on_cancel: Callback when cancelled
            on_pause: Callback when paused
        """
        self._parent = parent
        self._title = title
        self._state = ProgressState(total=total)
        self._on_cancel = on_cancel
        self._on_pause = on_pause
        self._dialog = None
        self._progress_bar = None
        self._label = None
        self._status_label = None
    
    def show(self) -> None:
        """Show the progress dialog."""
        try:
            from aqt.qt import (
                QDialog, QVBoxLayout, QHBoxLayout,
                QProgressBar, QLabel, QPushButton,
                Qt
            )
            
            self._dialog = QDialog(self._parent)
            self._dialog.setWindowTitle(self._title)
            self._dialog.setMinimumWidth(400)
            self._dialog.setModal(True)
            
            layout = QVBoxLayout(self._dialog)
            
            # Title label
            title_label = QLabel(f"<b>{self._title}</b>")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            
            # Progress bar
            self._progress_bar = QProgressBar()
            self._progress_bar.setRange(0, self._state.total)
            self._progress_bar.setValue(0)
            layout.addWidget(self._progress_bar)
            
            # Current item label
            self._label = QLabel("Preparing...")
            self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self._label)
            
            # Status label
            self._status_label = QLabel("")
            self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._status_label.setStyleSheet("color: gray; font-size: 11px;")
            layout.addWidget(self._status_label)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            self._pause_btn = QPushButton("⏸ Pause")
            self._pause_btn.clicked.connect(self._toggle_pause)
            button_layout.addWidget(self._pause_btn)
            
            cancel_btn = QPushButton("✕ Cancel")
            cancel_btn.clicked.connect(self._handle_cancel)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            
            self._dialog.show()
            
        except Exception as e:
            logger.error(f"Failed to show progress dialog: {e}")
    
    def update(
        self,
        current: int,
        item_name: str = "",
        success: bool = True
    ) -> None:
        """
        Update progress.
        
        Args:
            current: Current item number (1-based)
            item_name: Name of current item
            success: Whether last item succeeded
        """
        self._state.current = current
        self._state.current_item = item_name
        
        if success:
            self._state.successes += 1
        else:
            self._state.errors += 1
        
        try:
            from aqt import mw
            
            if self._progress_bar:
                self._progress_bar.setValue(current)
            
            if self._label:
                self._label.setText(
                    f"Processing: {item_name}" if item_name else f"Item {current}/{self._state.total}"
                )
            
            if self._status_label:
                status = f"✓ {self._state.successes}"
                if self._state.errors > 0:
                    status += f"  ✗ {self._state.errors}"
                self._status_label.setText(status)
            
            # Process events to keep UI responsive
            if mw and mw.app:
                mw.app.processEvents()
                
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
    
    def set_status(self, text: str) -> None:
        """Set status text."""
        if self._status_label:
            self._status_label.setText(text)
    
    def close(self) -> None:
        """Close the dialog."""
        if self._dialog:
            self._dialog.close()
            self._dialog = None
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._state.status == "cancelled"
    
    def is_paused(self) -> bool:
        """Check if operation is paused."""
        return self._state.status == "paused"
    
    def _toggle_pause(self) -> None:
        """Toggle pause state."""
        if self._state.status == "paused":
            self._state.status = "running"
            if self._pause_btn:
                self._pause_btn.setText("⏸ Pause")
        else:
            self._state.status = "paused"
            if self._pause_btn:
                self._pause_btn.setText("▶ Resume")
        
        if self._on_pause:
            self._on_pause(self._state.status == "paused")
    
    def _handle_cancel(self) -> None:
        """Handle cancel button click."""
        self._state.status = "cancelled"
        
        if self._on_cancel:
            self._on_cancel()
        
        self.close()
    
    def get_results(self) -> Dict[str, Any]:
        """Get final results."""
        return {
            "total": self._state.total,
            "successful": self._state.successes,
            "failed": self._state.errors,
            "status": self._state.status
        }


def show_batch_progress(
    parent: 'AnkiQt',
    batch_runner,
    title: str = "Processing",
    on_complete: Optional[Callable[[Dict[str, Any]], None]] = None
) -> None:
    """
    Show progress dialog for a batch operation.
    
    Args:
        parent: Parent widget (usually mw)
        batch_runner: Batch operation runner (must have start() method)
        title: Dialog title
        on_complete: Callback with results when complete
    """
    try:
        from aqt.qt import QThreadPool, QRunnable
        
        # Get total from batch runner
        total = getattr(batch_runner, 'total', 0) or len(getattr(batch_runner, 'note_ids', []))
        
        # Create dialog
        dialog = BatchProgressDialog(
            parent=parent,
            title=title,
            total=total
        )
        
        # Connect batch runner signals if available
        if hasattr(batch_runner, 'signals'):
            signals = batch_runner.signals
            
            if hasattr(signals, 'progress'):
                signals.progress.connect(
                    lambda curr, tot, item, ok: dialog.update(curr, item, ok)
                )
            
            if hasattr(signals, 'finished'):
                signals.finished.connect(lambda results: _on_finished(dialog, results, on_complete))
            
            if hasattr(signals, 'error'):
                signals.error.connect(lambda err: logger.error(f"Batch error: {err}"))
        
        # Set cancel callback
        dialog._on_cancel = lambda: setattr(batch_runner, '_cancelled', True)
        
        # Show dialog
        dialog.show()
        
        # Start batch operation
        if isinstance(batch_runner, QRunnable):
            QThreadPool.globalInstance().start(batch_runner)
        elif hasattr(batch_runner, 'start'):
            batch_runner.start()
        elif hasattr(batch_runner, 'run'):
            batch_runner.run()
        
    except Exception as e:
        logger.error(f"Failed to show batch progress: {e}")
        if on_complete:
            on_complete({"error": str(e), "total": 0, "successful": 0, "failed": 0})


def _on_finished(
    dialog: BatchProgressDialog,
    results: Dict[str, Any],
    on_complete: Optional[Callable]
) -> None:
    """Handle batch completion."""
    dialog.close()
    
    if on_complete:
        # Merge dialog results with batch results
        final_results = dialog.get_results()
        final_results.update(results)
        on_complete(final_results)
