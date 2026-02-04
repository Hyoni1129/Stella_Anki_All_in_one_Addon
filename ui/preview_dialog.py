# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Preview Dialog

Dialog for reviewing generated content (Text/Images) before applying changes.
"""

from __future__ import annotations

import os
from typing import List, Optional

from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QWidget, QScrollArea, QFrame, QPixmap, Qt, QSizePolicy,
    QTabWidget, QTextEdit
)

from ..core.preview_models import PreviewResult
from ..core.logger import get_logger

logger = get_logger(__name__)

class PreviewItemWidget(QWidget):
    """Widget for a single preview item (Source -> Result)."""
    
    def __init__(self, result: PreviewResult, parent=None):
        super().__init__(parent)
        self.result = result
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        
        # Header: Note ID
        header = QLabel(f"<b>Note ID:</b> {self.result.note_id}")
        layout.addWidget(header)
        
        content_layout = QHBoxLayout()
        layout.addLayout(content_layout)
        
        # Left: Original Source
        left_group = self._create_group("Original Input", self.result.original_text)
        content_layout.addWidget(left_group)
        
        # Right: Generated Output
        right_container = QFrame()
        right_container.setFrameShape(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout()
        right_container.setLayout(right_layout)
        
        lbl_title = QLabel(f"<b>Generated ({self.result.target_field})</b>")
        right_layout.addWidget(lbl_title)
        
        if self.result.error:
             # Error state
            lbl_err = QLabel(f"⚠️ Error: {self.result.error}")
            lbl_err.setStyleSheet("color: red;")
            lbl_err.setWordWrap(True)
            right_layout.addWidget(lbl_err)
        
        elif self.result.is_image:
            # Image Preview
            if self.result.temp_image_path and os.path.exists(self.result.temp_image_path):
                pixmap = QPixmap(self.result.temp_image_path)
                # Scale down if too large
                if pixmap.width() > 300:
                    pixmap = pixmap.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation)
                
                lbl_img = QLabel()
                lbl_img.setPixmap(pixmap)
                lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
                right_layout.addWidget(lbl_img)
            else:
                right_layout.addWidget(QLabel("<i>Image missing or invalid</i>"))
                
        else:
            # Text Preview
            text_preview = QTextEdit()
            text_preview.setPlainText(str(self.result.generated_content))
            text_preview.setReadOnly(True)
            text_preview.setMaximumHeight(100)
            text_preview.setStyleSheet("background-color: #f0f0f0;")
            right_layout.addWidget(text_preview)
            
            # Secondary content (e.g. Translation)
            if self.result.secondary_content:
                lbl_sec = QLabel(f"<b>Secondary ({self.result.secondary_field})</b>")
                lbl_sec.setStyleSheet("margin-top: 5px;")
                right_layout.addWidget(lbl_sec)
                
                sec_preview = QTextEdit()
                sec_preview.setPlainText(str(self.result.secondary_content))
                sec_preview.setReadOnly(True)
                sec_preview.setMaximumHeight(60)
                sec_preview.setStyleSheet("background-color: #f0f0f0;")
                right_layout.addWidget(sec_preview)
        
        content_layout.addWidget(right_container)
        
        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

    def _create_group(self, title: str, content: str) -> QWidget:
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()
        container.setLayout(layout)
        
        lbl = QLabel(f"<b>{title}</b>")
        layout.addWidget(lbl)
        
        text = QTextEdit()
        text.setPlainText(content)
        text.setReadOnly(True)
        text.setMaximumHeight(100)
        # Make source look different
        text.setStyleSheet("background-color: #e6f3ff;") 
        layout.addWidget(text)
        
        return container


class PreviewDialog(QDialog):
    """
    Dialog to review batch operation previews.
    """
    
    def __init__(self, parent, results: List[PreviewResult]):
        super().__init__(parent)
        self.setWindowTitle(f"Preview Results ({len(results)} items)")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.results = results
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Instruction Label
        info_label = QLabel(
            "Review the sample generation results below.\n"
            "If satisfied, click 'Apply & Continue' to update these cards and proceed with the full batch."
        )
        info_label.setStyleSheet("font-size: 13px; margin-bottom: 10px;")
        main_layout.addWidget(info_label)
        
        # Scroll Area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        content_widget.setLayout(self.scroll_layout)
        
        # Add items
        for res in self.results:
            item = PreviewItemWidget(res)
            self.scroll_layout.addWidget(item)
            
        self.scroll_layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Button Box
        btn_layout = QHBoxLayout()
        
        self.btn_cancel = QPushButton("❌ Cancel / Discard")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_apply = QPushButton("✅ Apply & Continue")
        self.btn_apply.setStyleSheet("font-weight: bold; padding: 6px 12px;")
        self.btn_apply.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_apply)
        
        main_layout.addLayout(btn_layout)

    def reject(self):
        """Clean up and close."""
        for res in self.results:
            res.cleanup()
        super().reject()
