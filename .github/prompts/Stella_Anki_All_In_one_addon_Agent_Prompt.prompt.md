---
agent: agent
---
# Stella Anki Tools - Development Agent Prompt

You are an expert Python developer specializing in Anki add-on development. Your mission is to implement **Stella Anki Tools**, a unified Anki add-on that combines three existing tools into a single, polished solution.

---

## 🎯 Project Overview

**Stella Anki Tools** is a comprehensive Anki add-on that provides:
1. **AI Translation** - Context-aware vocabulary translation using Gemini AI
2. **AI Image Generation** - Visual flashcard images using Gemini Imagen
3. **AI Sentence Generation** - Example sentences for vocabulary learning

All three features share a common API key management system, unified configuration, and consistent user interface.

---

## 📚 Essential Documentation

Before making any changes, you **MUST** read and understand these documents:

| Document | Path | Purpose |
|----------|------|---------|
| **Code Analysis** | `docs/Code_Analysis.md` | Technical analysis of all three source tools |
| **Development Checklist** | `docs/Development_Checklist.md` | Detailed implementation checklist |
| **Project Goals** | `docs/Proejct.md` | Original project requirements |

### Reference Code Locations
The original implementations are in the `Reference/` folder (git-ignored):
- `Reference/Anki_Deck_Translater/` - Translation add-on source
- `Reference/Anki_Image_Gen_with_Google_Nano_Banana/` - Image generator CLI source  
- `Reference/Anki_Sentence_generater/` - Sentence generator add-on source

> [!IMPORTANT]
> Always reference the original code when implementing features. The goal is to **adapt and improve**, not reinvent.

---

## 🏗️ Target Architecture

```
stella_anki_tools/
├── __init__.py                 # Entry point
├── manifest.json               # Anki add-on manifest
├── config.json                 # Default configuration
├── meta.json                   # Anki metadata
├── core/
│   ├── __init__.py
│   ├── api_key_manager.py      # Unified multi-key system
│   ├── gemini_client.py        # Shared Gemini API interface
│   ├── logger.py               # Centralized logging
│   └── utils.py                # Common utilities
├── config/
│   ├── __init__.py
│   ├── settings.py             # Configuration management
│   └── prompts.py              # AI prompts for all features
├── translation/
│   ├── __init__.py
│   ├── translator.py           # Single-note translation
│   └── batch_translator.py     # Batch processing
├── image/
│   ├── __init__.py
│   ├── prompt_generator.py     # Image prompt creation
│   ├── image_generator.py      # Imagen API client
│   └── anki_media.py           # Media file management
├── sentence/
│   ├── __init__.py
│   ├── sentence_generator.py   # Sentence generation
│   └── progress_state.py       # Resume capability
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Settings dialog
│   ├── editor_integration.py   # Editor hooks/buttons
│   ├── progress_dialog.py      # Shared progress UI
│   ├── browser_menu.py         # Browser context menu
│   └── widgets/                # Reusable UI components
└── lib/                        # Bundled dependencies
    └── google-generativeai/    # Gemini SDK
```

---

## 🔧 Development Guidelines

### 1. Anki Add-on Best Practices

```python
# ✅ Correct: Use Anki's main window reference
from aqt import mw

# ✅ Correct: Use Anki's config system
config = mw.addonManager.getConfig(__name__)

# ✅ Correct: Modern async pattern with QueryOp
from aqt.operations import QueryOp
op = QueryOp(parent=mw, op=background_task, success=on_success)
op.with_progress("Processing...").run_in_background()

# ❌ Wrong: Don't use AnkiConnect HTTP calls (CLI pattern)
# requests.post("http://localhost:8765", ...)

# ✅ Correct: Use direct Anki API
mw.col.find_notes("deck:MyDeck")
mw.col.get_note(note_id)
mw.col.update_note(note)
```

### 2. Code Style

- **Type Hints**: Use type hints for all function parameters and returns
- **Docstrings**: Include docstrings for all classes and public methods
- **Error Handling**: Always handle exceptions with user-friendly messages
- **Logging**: Log important operations using the centralized logger

```python
from typing import Optional, List, Dict, Any

def process_notes(
    note_ids: List[int],
    config: Dict[str, Any],
    progress_callback: Optional[callable] = None
) -> Dict[str, int]:
    """
    Process multiple notes for translation/generation.
    
    Args:
        note_ids: List of Anki note IDs to process
        config: Configuration dictionary
        progress_callback: Optional callback(current, total)
        
    Returns:
        Dictionary with 'success' and 'failed' counts
    """
    pass
```

### 3. Configuration Schema

Use this unified configuration structure:

```json
{
  "version": "1.0.0",
  "api": {
    "keys": [],
    "rotation_enabled": true,
    "cooldown_hours": 24,
    "model": "gemini-2.5-flash"
  },
  "translation": {
    "enabled": true,
    "language": "Korean",
    "source_field": "Word",
    "context_field": "Definition",
    "destination_field": "Translation",
    "batch_size": 5,
    "batch_delay_seconds": 8,
    "skip_existing": true
  },
  "image": {
    "enabled": true,
    "word_field": "Word",
    "image_field": "Image",
    "style_preset": "anime",
    "max_width": 800,
    "max_height": 600
  },
  "sentence": {
    "enabled": true,
    "expression_field": "Word",
    "sentence_field": "Sentence",
    "translation_field": "SentenceTranslation",
    "difficulty": "Normal",
    "highlight_word": true
  },
  "editor": {
    "buttons_enabled": true,
    "shortcuts": {
      "translate": "Ctrl+Shift+T",
      "sentence": "Ctrl+Shift+S",
      "image": "Ctrl+Shift+I"
    }
  }
}
```

### 4. API Key Manager Requirements

Merge the best features from both existing implementations:

| Feature | Implementation Notes |
|---------|---------------------|
| Max 15 keys | From Translator |
| Encrypted storage | From Image Gen (Fernet) |
| Auto-rotation on 429 | From Translator |
| Usage statistics | Track per-key success/failure |
| 24hr cooldown | Auto-disable exhausted keys |
| Key validation | Test API connection on add |

### 5. Editor Integration

Create a **single unified** editor integration that supports all three features:

```python
# Keyboard shortcuts (distinct, no conflicts!)
SHORTCUTS = {
    "translate": "Ctrl+Shift+T",
    "sentence": "Ctrl+Shift+S", 
    "image": "Ctrl+Shift+I",
    "all": "Ctrl+Shift+A"  # Run all three
}

# Toolbar buttons
# Add 4 buttons: Translate, Sentence, Image, All
```

### 6. Image Generator Conversion

The Image Generator is currently a **CLI tool** that must be converted to an add-on:

| CLI Component | Add-on Replacement |
|--------------|-------------------|
| `requests.post("localhost:8765")` | `mw.col.find_notes()`, `mw.col.get_note()` |
| File-based images `data/images/` | `mw.col.media.add_file()` |
| SQLite database | Anki config + meta.json |
| Streamlit UI | Qt dialogs |
| `google-genai` SDK | `google-generativeai` SDK |

---

## 📋 Implementation Order

Follow this sequence for efficient development:

### Phase 1: Foundation (Priority: Critical)
1. [ ] Create directory structure
2. [ ] Implement `core/logger.py`
3. [ ] Implement `core/utils.py` (HTML stripping, error classification)
4. [ ] Implement `config/settings.py`
5. [ ] Implement `core/api_key_manager.py`
6. [ ] Implement `core/gemini_client.py`
7. [ ] Create `__init__.py` entry point
8. [ ] Create `meta.json` and `config.json`

### Phase 2: Translation Module (Priority: High)
1. [ ] Port `translation/translator.py` from Translator
2. [ ] Port `translation/batch_translator.py`
3. [ ] Add to menu and test

### Phase 3: Sentence Module (Priority: High)
1. [ ] Port `sentence/sentence_generator.py` from BunAI
2. [ ] Port `sentence/progress_state.py`
3. [ ] Add to menu and test

### Phase 4: Image Module (Priority: High, Effort: Very High)
1. [ ] Create `image/prompt_generator.py` (adapt from CLI)
2. [ ] Create `image/image_generator.py` (adapt NanoBananaClient)
3. [ ] Create `image/anki_media.py` (new, replaces AnkiConnect)
4. [ ] Add to menu and test

### Phase 5: Unified UI (Priority: High)
1. [ ] Create `ui/main_window.py` (tabbed settings)
2. [ ] Create `ui/editor_integration.py` (merged)
3. [ ] Create `ui/progress_dialog.py` (shared)
4. [ ] Create `ui/browser_menu.py`
5. [ ] Wire everything together

### Phase 6: Polish & Package
1. [ ] Bundle dependencies in `lib/`
2. [ ] Create comprehensive error handling
3. [ ] Add migration logic for old configs
4. [ ] Test with multiple Anki versions
5. [ ] Create `.ankiaddon` package

---

## ⚠️ Critical Constraints

### DO:
- ✅ Use Anki's built-in Qt widgets (QDialog, QTabWidget, etc.)
- ✅ Use `aqt.operations.QueryOp` for background tasks
- ✅ Use `mw.col.media` for storing images
- ✅ Handle all API errors gracefully with user messages
- ✅ Support Anki 2.1.50+ (min_point_version: 50)
- ✅ Test each feature independently before integration

### DON'T:
- ❌ Use AnkiConnect HTTP API (that's for external tools)
- ❌ Block the UI thread with synchronous operations
- ❌ Store sensitive data (API keys) in plain text
- ❌ Create global state that persists across add-on reloads
- ❌ Use external dependencies not bundled in `lib/`

---

## 🧪 Testing Checklist

After implementing each phase, verify:

```python
# Basic Functionality Tests
- [ ] Add-on loads without errors
- [ ] Settings dialog opens
- [ ] API key can be added and validated
- [ ] Single-note operation works in editor
- [ ] Batch operation works from browser
- [ ] Progress dialog shows correctly
- [ ] Cancel button works
- [ ] Results are saved to Anki notes

# Edge Cases
- [ ] Empty fields handled gracefully
- [ ] Unicode/special characters work
- [ ] Network timeout shows friendly error
- [ ] API quota error triggers key rotation
- [ ] Resume works after interruption
```

---

## 📝 Commit Convention

Use descriptive commits following this pattern:

```
[module] action: description

Examples:
[core] add: api_key_manager with multi-key rotation
[translation] port: batch translator from reference
[image] convert: replace AnkiConnect with direct API
[ui] create: unified settings dialog with tabs
[fix] handle: network timeout in gemini_client
```

---

## 🚀 Getting Started

1. Read `docs/Code_Analysis.md` thoroughly
2. Read `docs/Development_Checklist.md` for detailed tasks
3. Start with Phase 1 (Foundation)
4. Reference the original code in `Reference/` folder
5. Test each component before moving to the next phase
6. Commit frequently with descriptive messages

**Remember**: Quality over speed. This add-on will be used by many Anki users, so ensure robust error handling and a polished user experience.

---

## 📞 Support Files

When you need to understand how something works in the original code:

| Task | Reference File |
|------|---------------|
| API Key rotation | `Reference/Anki_Deck_Translater/api_key_manager.py` |
| Batch translation | `Reference/Anki_Deck_Translater/batch_translator.py` |
| QueryOp pattern | `Reference/Anki_Deck_Translater/stella_generator.py` |
| Editor hooks | `Reference/Anki_Deck_Translater/editor_integration.py` |
| Image prompts | `Reference/Anki_Image_Gen_with_Google_Nano_Banana/src/gemini_client.py` |
| Image generation | `Reference/Anki_Image_Gen_with_Google_Nano_Banana/src/nano_banana_client.py` |
| Sentence generation | `Reference/Anki_Sentence_generater/sentence_generator_modern.py` |
| Progress tracking | `Reference/Anki_Sentence_generater/progress_state.py` |

---

Good luck! Build something amazing. 🌟
