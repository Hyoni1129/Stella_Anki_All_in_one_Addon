# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Debug Utilities

Debugging functions executable in Anki Debug Console.
Provides comprehensive status checks and diagnostic tools.

Usage in Anki Debug Console:
    from Stella_Anki_All_in_one_Addon.core.debug_utils import debug_stella_status
    debug_stella_status()

Adapted from Reference implementations.
"""

from __future__ import annotations

import os
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime


def debug_stella_status() -> None:
    """
    Check overall status of Stella Anki Tools.
    
    Prints comprehensive diagnostic information about:
    - Add-on load status
    - Configuration state
    - API key status
    - Log file status
    - Hook registrations
    """
    print("=" * 60)
    print("🔍 Stella Anki Tools - Status Check")
    print("=" * 60)
    
    try:
        from aqt import mw
        
        # 1. Check Add-on Load Status
        print("\n📦 Add-on Load Status:")
        _check_addon_instances(mw)
        
        # 2. Check Configuration
        print("\n⚙️ Configuration Status:")
        _check_configuration(mw)
        
        # 3. Check API Keys
        print("\n🔑 API Key Status:")
        _check_api_keys(mw)
        
        # 4. Check Log Files
        print("\n📝 Log Status:")
        _check_logs(mw)
        
        # 5. Check Hooks
        print("\n🪝 Hook Status:")
        _check_hooks()
        
        # 6. Check Dependencies
        print("\n📚 Dependencies Status:")
        _check_dependencies()
        
    except Exception as e:
        print(f"\n❌ Error during status check: {e}")
        import traceback
        traceback.print_exc()


def _check_addon_instances(mw) -> None:
    """Check if addon instances are properly loaded."""
    if hasattr(mw, 'stella_anki_tools'):
        print("✅ mw.stella_anki_tools exists")
        print(f"   - Type: {type(mw.stella_anki_tools).__name__}")
        if hasattr(mw.stella_anki_tools, '_initialized'):
            print(f"   - Initialized: {mw.stella_anki_tools._initialized}")
    else:
        print("❌ mw.stella_anki_tools missing")
        
    if hasattr(mw, 'stella_editor'):
        print("✅ mw.stella_editor exists")
        print(f"   - Type: {type(mw.stella_editor).__name__}")
    else:
        print("❌ mw.stella_editor missing")


def _check_configuration(mw) -> None:
    """Check configuration status."""
    try:
        # Get addon name
        addon_name = "Stella_Anki_All_in_one_Addon"
        addon_dir = os.path.join(mw.pm.addonFolder(), addon_name)
        
        # Check config.json
        config_path = os.path.join(addon_dir, "config.json")
        if os.path.exists(config_path):
            print("✅ config.json exists")
            with open(config_path, 'r', encoding='utf-8') as f:
                import json
                config = json.load(f)
            print(f"   - Version: {config.get('version', 'unknown')}")
            print(f"   - Translation Language: {config.get('translation', {}).get('language', 'not set')}")
            print(f"   - Translation Model: {config.get('translation', {}).get('model_name', 'not set')}")
        else:
            print("⚠️ config.json not found (using defaults)")
        
        # Also check Anki's addon config
        anki_config = mw.addonManager.getConfig(addon_name)
        if anki_config:
            print("✅ Anki addon config loaded")
        else:
            print("⚠️ Anki addon config is empty")
            
    except Exception as e:
        print(f"❌ Config check failed: {e}")


def _check_api_keys(mw) -> None:
    """Check API key status."""
    try:
        addon_name = "Stella_Anki_All_in_one_Addon"
        addon_dir = os.path.join(mw.pm.addonFolder(), addon_name)
        
        # Check api_keys.json
        keys_path = os.path.join(addon_dir, "api_keys.json")
        if os.path.exists(keys_path):
            print("✅ api_keys.json exists")
            with open(keys_path, 'r', encoding='utf-8') as f:
                import json
                keys_data = json.load(f)
            key_count = len(keys_data.get('keys', []))
            print(f"   - Keys stored: {key_count}")
            print(f"   - Encrypted: {keys_data.get('encrypted', False)}")
            print(f"   - Current index: {keys_data.get('current_key_index', 0)}")
        else:
            print("⚠️ api_keys.json not found (no keys configured)")
        
        # Check stats
        stats_path = os.path.join(addon_dir, "api_stats.json")
        if os.path.exists(stats_path):
            print("✅ api_stats.json exists")
            with open(stats_path, 'r', encoding='utf-8') as f:
                import json
                stats = json.load(f)
            print(f"   - Keys tracked: {len(stats)}")
            total_requests = sum(s.get('total_requests', 0) for s in stats.values())
            print(f"   - Total requests: {total_requests}")
        else:
            print("⚠️ api_stats.json not found")
            
    except Exception as e:
        print(f"❌ API key check failed: {e}")


def _check_logs(mw) -> None:
    """Check log file status."""
    try:
        addon_name = "Stella_Anki_All_in_one_Addon"
        addon_dir = os.path.join(mw.pm.addonFolder(), addon_name)
        log_dir = os.path.join(addon_dir, "logs")
        
        if os.path.exists(log_dir):
            print("✅ Log directory exists")
            
            # List recent log files
            log_files = sorted(
                [f for f in os.listdir(log_dir) if f.endswith('.log')],
                reverse=True
            )
            
            if log_files:
                print(f"   - Log files: {len(log_files)}")
                print(f"   - Most recent: {log_files[0]}")
                
                # Check size of recent log
                recent_log = os.path.join(log_dir, log_files[0])
                size_kb = os.path.getsize(recent_log) / 1024
                print(f"   - Size: {size_kb:.1f} KB")
            else:
                print("   - No log files found")
        else:
            print("⚠️ Log directory missing")
            
    except Exception as e:
        print(f"❌ Log check failed: {e}")


def _check_hooks() -> None:
    """Check registered hooks."""
    try:
        from aqt import gui_hooks
        
        hooks_to_check = [
            ('editor_did_init_shortcuts', 'Editor shortcuts'),
            ('editor_did_init', 'Editor init'),
            ('webview_did_receive_js_message', 'WebView messages'),
            ('editor_did_unfocus_field', 'Field unfocus'),
        ]
        
        for hook_name, description in hooks_to_check:
            if hasattr(gui_hooks, hook_name):
                hook = getattr(gui_hooks, hook_name)
                # Try to get hook count (implementation dependent)
                if hasattr(hook, '_hooks'):
                    count = len(hook._hooks)
                    print(f"✅ {description}: {count} handler(s)")
                else:
                    print(f"✅ {description}: registered")
            else:
                print(f"⚠️ {description}: hook not available")
                
    except Exception as e:
        print(f"❌ Hook check failed: {e}")


def _check_dependencies() -> None:
    """Check if required dependencies are available."""
    dependencies = [
        ('google.generativeai', 'Google Generative AI SDK'),
        ('PIL', 'Pillow (optional, for image handling)'),
    ]
    
    for module_name, description in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {description}")
        except ImportError:
            if 'optional' in description.lower():
                print(f"⚠️ {description} - not installed")
            else:
                print(f"❌ {description} - MISSING")


def debug_api_key_manager() -> None:
    """Debug API Key Manager state."""
    print("=" * 60)
    print("🔑 API Key Manager Debug")
    print("=" * 60)
    
    try:
        from ..api_key_manager import get_api_key_manager
        
        manager = get_api_key_manager()
        
        print("\n📊 Manager State:")
        print(f"   - Total keys: {manager.get_key_count()}")
        print(f"   - Current index: {manager.get_current_key_index()}")
        print(f"   - Current key ID: {manager.get_current_key_id()}")
        
        # Get summary stats
        stats = manager.get_summary_stats()
        print("\n📈 Statistics:")
        print(f"   - Active keys: {stats.get('active_keys', 0)}")
        print(f"   - Exhausted keys: {stats.get('exhausted_keys', 0)}")
        print(f"   - Total requests: {stats.get('total_requests', 0)}")
        print(f"   - Success rate: {stats.get('success_rate', 0):.1f}%")
        print(f"   - Total rotations: {stats.get('total_rotations', 0)}")
        
        # List keys with their status
        print("\n🔐 Key Details:")
        all_stats = manager.get_all_stats()
        for key_id, key_stats in all_stats.items():
            status = "🟢 Active" if key_stats.get('is_active', True) else "🔴 Inactive"
            if key_stats.get('exhausted_at'):
                status = "🟡 Exhausted"
            failures = key_stats.get('consecutive_failures', 0)
            print(f"   - {key_id}: {status} (failures: {failures})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def debug_config() -> None:
    """Debug configuration settings."""
    print("=" * 60)
    print("⚙️ Configuration Debug")
    print("=" * 60)
    
    try:
        from ..settings import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.config
        
        print(f"\n📝 Config Version: {config.version}")
        
        print("\n🌐 Translation Settings:")
        print(f"   - Language: {config.translation.language}")
        print(f"   - Model: {config.translation.model}")
        print(f"   - Source field: {config.translation.source_field}")
        print(f"   - Dest field: {config.translation.dest_field}")
        
        print("\n✏️ Sentence Settings:")
        print(f"   - Difficulty: {config.sentence.difficulty}")
        print(f"   - Highlight word: {config.sentence.highlight_word}")
        
        print("\n🖼️ Image Settings:")
        print(f"   - Style: {config.image.style}")
        print(f"   - Size: {config.image.width}x{config.image.height}")
        
        print("\n⚡ Editor Settings:")
        print(f"   - Auto translate: {config.editor.auto_translate}")
        print(f"   - Auto sentence: {config.editor.auto_sentence}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def validate_installation() -> bool:
    """
    Validate that the addon is properly installed.
    
    Returns:
        True if installation is valid, False otherwise
    """
    issues = []
    
    try:
        from aqt import mw
        
        addon_name = "Stella_Anki_All_in_one_Addon"
        addon_dir = os.path.join(mw.pm.addonFolder(), addon_name)
        
        # Check required files
        required_files = [
            '__init__.py',
            'config.json',
            'meta.json',
        ]
        
        for filename in required_files:
            filepath = os.path.join(addon_dir, filename)
            if not os.path.exists(filepath):
                issues.append(f"Missing required file: {filename}")
        
        # Check required directories
        required_dirs = [
            'core',
            'config', 
            'ui',
            'translation',
            'sentence',
            'image',
        ]
        
        for dirname in required_dirs:
            dirpath = os.path.join(addon_dir, dirname)
            if not os.path.isdir(dirpath):
                issues.append(f"Missing required directory: {dirname}")
        
        # Check lib directory
        lib_dir = os.path.join(addon_dir, 'lib')
        if not os.path.isdir(lib_dir):
            issues.append("Missing lib directory (dependencies)")
        
        if issues:
            print("❌ Installation validation failed:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Installation validation passed")
            return True
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


# Convenience function for quick debugging
def quick_check() -> None:
    """Quick status check - minimal output."""
    try:
        from aqt import mw
        
        checks = []
        
        # Check main controller
        if hasattr(mw, 'stella_anki_tools'):
            checks.append("✅ Controller")
        else:
            checks.append("❌ Controller")
        
        # Check editor integration
        if hasattr(mw, 'stella_editor'):
            checks.append("✅ Editor")
        else:
            checks.append("❌ Editor")
        
        # Check API keys
        try:
            from .api_key_manager import get_api_key_manager
            manager = get_api_key_manager()
            if manager.get_key_count() > 0:
                checks.append(f"✅ Keys ({manager.get_key_count()})")
            else:
                checks.append("⚠️ No keys")
        except Exception:
            checks.append("❌ KeyManager")
        
        print("Stella Anki Tools: " + " | ".join(checks))
        
    except Exception as e:
        print(f"❌ Quick check failed: {e}")


if __name__ == "__main__":
    debug_stella_status()
