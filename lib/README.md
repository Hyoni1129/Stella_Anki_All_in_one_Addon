# Bundled Dependencies for Stella Anki Tools

This directory contains bundled third-party Python packages to ensure
the addon works independently of the user's Python environment.

## Currently Bundled

(None yet - using Anki's bundled packages)

## How to Bundle a Package

1. Install the package to this directory:
   ```bash
   pip install <package_name> --target="lib/"
   ```

2. Test the addon in Anki to ensure compatibility

3. Update lib/__init__.py to list the package

## Packages Available in Anki

These packages are already bundled with Anki and don't need to be bundled:
- requests
- PyQt6 (Qt bindings)
- beautifulsoup4
- markdown
- jsonschema
- send2trash

## Google Generative AI

The `google-generativeai` package is used for Gemini API access.
It requires these dependencies:
- google-ai-generativelanguage
- google-api-core
- google-auth
- proto-plus
- protobuf

For now, we install via user's Python environment or Anki's pip.
