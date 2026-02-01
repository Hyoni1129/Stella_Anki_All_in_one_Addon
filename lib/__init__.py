# -*- coding: utf-8 -*-
"""
Stella Anki Tools - Bundled Dependencies

This folder contains bundled third-party libraries to ensure
compatibility with the Anki environment.

Bundled libraries:
- (Add libraries here as needed)

To bundle a new dependency:
1. pip install <package> --target=./lib
2. Test in Anki environment
3. Add to this list

Note: Prefer using packages already bundled with Anki when possible:
- requests (bundled with Anki)
- PyQt6/PyQt5 (bundled with Anki)
"""

import sys
import os

# Add lib folder to path for imports
lib_path = os.path.dirname(os.path.abspath(__file__))
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

# Track what's available
BUNDLED_PACKAGES = []

def ensure_package(package_name: str) -> bool:
    """
    Ensure a package is available for import.
    
    First checks if the package is already available in Anki's environment,
    then falls back to bundled version if available.
    
    Returns True if package is available.
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        # Try from bundled
        if package_name in BUNDLED_PACKAGES:
            try:
                __import__(package_name)
                return True
            except ImportError:
                pass
        return False
