# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Settings Dialog (Placeholder)

Full settings dialog implementation will be added later.
For now, users can configure via Tools > Add-ons > Config.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from aqt.main import AnkiQt
    from ..config.settings import ConfigManager


# This is a placeholder - full implementation to be added
class StellaSettingsDialog:
    """Settings dialog for Stella Anki Tools."""
    
    def __init__(self, parent: 'AnkiQt', config_manager: 'ConfigManager'):
        self._parent = parent
        self._config_manager = config_manager
    
    def exec(self) -> None:
        """Show the settings dialog."""
        # For now, show simple info about using Anki's config
        try:
            from aqt.utils import showInfo
            showInfo(
                "Stella Settings\n\n"
                "Full settings dialog coming soon!\n\n"
                "For now, please configure via:\n"
                "Tools → Add-ons → Stella Anki Tools → Config\n\n"
                "Key settings:\n"
                "• API keys: Tools menu → Manage API Keys\n"
                "• Translation/Sentence/Image fields in config.json",
                title="Stella Settings"
            )
        except Exception:
            pass


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
