# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Anki Media Manager

Handles adding images to Anki's media collection and updating notes.
Uses direct Anki API (mw.col.media) instead of AnkiConnect HTTP.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, Any, List, Union
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import os
import tempfile
import hashlib
import re

if TYPE_CHECKING:
    from anki.notes import Note
    from anki.collection import Collection

from ..core.logger import get_logger
from ..core.utils import strip_html


logger = get_logger(__name__)


@dataclass
class MediaAddResult:
    """Result of adding media to Anki"""
    success: bool
    filename: str
    original_name: Optional[str] = None
    error: Optional[str] = None
    note_updated: bool = False


class AnkiMediaError(Exception):
    """Custom exception for Anki media operations"""
    pass


class AnkiMediaManager:
    """
    Manages Anki media collection operations.
    
    Uses direct Anki API (mw.col.media) for reliable media operations
    within the add-on context. Handles:
    - Adding images to media collection
    - Updating note fields with image references
    - Generating unique filenames
    - Cleanup of temporary files
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
    
    def __init__(self, collection: Optional['Collection'] = None):
        """
        Initialize media manager.
        
        Args:
            collection: Optional Anki collection. If not provided,
                       will use aqt.mw.col when needed.
        """
        self._col = collection
    
    @property
    def col(self) -> 'Collection':
        """Get the Anki collection."""
        if self._col is not None:
            return self._col
        
        try:
            from aqt import mw
            if mw and mw.col:
                return mw.col
            raise AnkiMediaError("Anki collection not available")
        except ImportError:
            raise AnkiMediaError("Cannot import aqt - not running in Anki")
    
    @property
    def media_dir(self) -> Path:
        """Get the Anki media directory path."""
        return Path(self.col.media.dir())
    
    def add_image_from_bytes(
        self,
        image_data: bytes,
        word: str,
        extension: str = ".png"
    ) -> MediaAddResult:
        """
        Add image data to Anki media collection.
        
        Args:
            image_data: Raw image bytes
            word: Word/name for the image (used in filename)
            extension: File extension (default .png)
            
        Returns:
            MediaAddResult with the final filename
        """
        try:
            if not image_data:
                return MediaAddResult(
                    success=False,
                    filename="",
                    error="Empty image data"
                )
            
            # Normalize extension
            extension = extension.lower()
            if not extension.startswith("."):
                extension = f".{extension}"
            
            if extension not in self.SUPPORTED_FORMATS:
                return MediaAddResult(
                    success=False,
                    filename="",
                    error=f"Unsupported format: {extension}"
                )
            
            # Generate unique filename
            original_name = self._generate_filename(word, extension)
            
            # Write to temp file first
            temp_path = self._write_temp_file(image_data, extension)
            
            try:
                # Add to Anki media collection
                # This copies the file to media folder and returns the final name
                final_filename = self.col.media.add_file(temp_path)
                
                logger.info(f"Added image to media: {final_filename}")
                
                return MediaAddResult(
                    success=True,
                    filename=final_filename,
                    original_name=original_name
                )
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
                
        except Exception as e:
            logger.error(f"Failed to add image to media: {e}")
            return MediaAddResult(
                success=False,
                filename="",
                error=str(e)
            )
    
    def add_image_from_file(
        self,
        file_path: Union[str, Path]
    ) -> MediaAddResult:
        """
        Add an existing image file to Anki media collection.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            MediaAddResult with the final filename
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return MediaAddResult(
                    success=False,
                    filename="",
                    error=f"File not found: {file_path}"
                )
            
            if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
                return MediaAddResult(
                    success=False,
                    filename="",
                    error=f"Unsupported format: {file_path.suffix}"
                )
            
            # Add to Anki media collection
            final_filename = self.col.media.add_file(str(file_path))
            
            logger.info(f"Added image to media: {final_filename}")
            
            return MediaAddResult(
                success=True,
                filename=final_filename,
                original_name=file_path.name
            )
            
        except Exception as e:
            logger.error(f"Failed to add image from file: {e}")
            return MediaAddResult(
                success=False,
                filename="",
                error=str(e)
            )
    
    def update_note_image_field(
        self,
        note: 'Note',
        field_name: str,
        filename: str,
        replace_existing: bool = True
    ) -> bool:
        """
        Update a note's field with an image reference.
        
        Args:
            note: The Anki note to update
            field_name: Name of the field to update
            filename: Media filename (not full path)
            replace_existing: If True, replaces existing content
            
        Returns:
            True if successful
        """
        try:
            # Verify field exists
            if field_name not in note:
                logger.error(f"Field '{field_name}' not found in note")
                return False
            
            # Build image HTML tag
            img_html = f'<img src="{filename}">'
            
            if replace_existing:
                note[field_name] = img_html
            else:
                # Append to existing content
                current = note[field_name]
                if current:
                    note[field_name] = f"{current}<br>{img_html}"
                else:
                    note[field_name] = img_html
            
            # Flush changes
            self.col.update_note(note)
            
            logger.info(f"Updated note field '{field_name}' with image: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update note field: {e}")
            return False
    
    def add_image_to_note(
        self,
        note: 'Note',
        field_name: str,
        image_data: bytes,
        word: str,
        extension: str = ".png",
        replace_existing: bool = True
    ) -> MediaAddResult:
        """
        Complete workflow: add image to media and update note.
        
        Args:
            note: The Anki note to update
            field_name: Name of the field for the image
            image_data: Raw image bytes
            word: Word for filename generation
            extension: Image file extension
            replace_existing: If True, replaces existing field content
            
        Returns:
            MediaAddResult with success status
        """
        # Add image to media collection
        result = self.add_image_from_bytes(image_data, word, extension)
        
        if not result.success:
            return result
        
        # Update note field
        updated = self.update_note_image_field(
            note=note,
            field_name=field_name,
            filename=result.filename,
            replace_existing=replace_existing
        )
        
        result.note_updated = updated
        
        if not updated:
            result.error = "Image added but note update failed"
        
        return result
    
    def _generate_filename(self, word: str, extension: str) -> str:
        """Generate a unique filename for the image."""
        # Sanitize word for filename
        safe_word = "".join(c for c in word if c.isalnum() or c in "_-").lower()
        if len(safe_word) > 30:
            safe_word = safe_word[:30]
        
        if not safe_word:
            safe_word = "image"
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"stella_{safe_word}_{timestamp}{extension}"
    
    def _write_temp_file(self, data: bytes, extension: str) -> str:
        """Write data to a temporary file."""
        fd, path = tempfile.mkstemp(suffix=extension, prefix="stella_")
        try:
            os.write(fd, data)
        finally:
            os.close(fd)
        return path
    
    def get_image_filename_in_field(self, field_content: str) -> Optional[str]:
        """
        Extract image filename from a field's HTML content.
        
        Args:
            field_content: HTML content of the field
            
        Returns:
            Image filename if found, None otherwise
        """
        if not field_content:
            return None
        
        # Match <img src="filename">
        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', field_content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def field_has_image(self, field_content: str) -> bool:
        """Check if a field contains an image."""
        return self.get_image_filename_in_field(field_content) is not None
    
    def image_exists_in_media(self, filename: str) -> bool:
        """Check if an image file exists in the media collection."""
        if not filename:
            return False
        
        image_path = self.media_dir / filename
        return image_path.exists()
    
    def get_orphaned_stella_images(self) -> List[str]:
        """
        Find Stella-generated images that are no longer referenced.
        
        Returns:
            List of filenames that may be orphaned
        """
        orphaned = []
        
        try:
            # Find all Stella-generated images
            for file_path in self.media_dir.glob("stella_*.png"):
                filename = file_path.name
                
                # Check if referenced in any note
                # Note: This is a simplified check - full check would scan all notes
                if not self._is_image_referenced(filename):
                    orphaned.append(filename)
            
            # Also check jpg
            for file_path in self.media_dir.glob("stella_*.jpg"):
                filename = file_path.name
                if not self._is_image_referenced(filename):
                    orphaned.append(filename)
                    
        except Exception as e:
            logger.error(f"Failed to find orphaned images: {e}")
        
        return orphaned
    
    def _is_image_referenced(self, filename: str) -> bool:
        """Check if image is referenced in any note (simplified check)."""
        try:
            # Use Anki's media check
            # This is a simplified check - media.check() is more comprehensive
            # but also more resource-intensive
            search = f'"{filename}"'
            note_ids = self.col.find_notes(search)
            return len(note_ids) > 0
        except Exception:
            return True  # Assume referenced if check fails
    
    def cleanup_temp_images(self, temp_dir: Optional[Union[str, Path]] = None) -> int:
        """
        Clean up temporary Stella image files.
        
        Args:
            temp_dir: Temp directory to clean (default: system temp)
            
        Returns:
            Number of files cleaned up
        """
        if temp_dir is None:
            temp_dir = Path(tempfile.gettempdir()) / "stella_anki_images"
        else:
            temp_dir = Path(temp_dir)
        
        if not temp_dir.exists():
            return 0
        
        count = 0
        for file_path in temp_dir.glob("*.png"):
            try:
                file_path.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file_path}: {e}")
        
        for file_path in temp_dir.glob("*.jpg"):
            try:
                file_path.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file_path}: {e}")
        
        if count > 0:
            logger.info(f"Cleaned up {count} temporary image files")
        
        return count
    
    def get_media_stats(self) -> Dict[str, Any]:
        """Get statistics about Stella images in media collection."""
        stats = {
            "stella_images": 0,
            "total_size_bytes": 0,
            "formats": {}
        }
        
        try:
            for ext in [".png", ".jpg", ".jpeg"]:
                pattern = f"stella_*{ext}"
                files = list(self.media_dir.glob(pattern))
                count = len(files)
                
                if count > 0:
                    stats["formats"][ext] = count
                    stats["stella_images"] += count
                    
                    for f in files:
                        stats["total_size_bytes"] += f.stat().st_size
            
            # Convert to MB
            stats["total_size_mb"] = stats["total_size_bytes"] / (1024 * 1024)
            
        except Exception as e:
            logger.error(f"Failed to get media stats: {e}")
        
        return stats
