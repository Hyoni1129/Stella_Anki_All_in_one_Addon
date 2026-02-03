# Stella Anki Tools - Development Status & Roadmap

**Date:** 2026-02-03
**Status:** Alpha / Near Completion (approx. 95%)

## 📊 Project Status Assessment

A comprehensive review of the codebase confirms that all core features and architecture are implemented. The current issue (disabled Field Mapping) is a specific UI/Runtime bug, not a missing feature.

| Component | Status | Implementation Details |
| :--- | :--- | :--- |
| **Core Architecture** | ✅ Complete | `StellaAnkiTools` controller, singleton pattern, and lazy loading are implemented. |
| **API Key Manager** | ✅ Complete | Multi-key rotation (`core/api_key_manager.py`) with encryption and stats is fully logic-complete. |
| **UI** | ✅ Complete | `DeckOperationDialog` and `SettingsDialog` are built. Integration with Anki's menu and editor is present. |
| **Translation** | ✅ Complete | `Translator` and `BatchTranslator` logic is present with async `QueryOp`. |
| **Sentence Gen** | ✅ Complete | `SentenceGenerator` with parsing and highlighting logic is implemented. |
| **Image Gen** | ✅ Complete | `ImageGenerator` using Imagen model is implemented. |

---

## 🐞 Critical Bug: Field Mapping Disabled

**Symptom:** The Field Mapping section remains disabled even after selecting a deck.
**Probable Cause:** Error in `DeckOperationDialog._on_deck_changed` prevented the field dropdowns from populating.

### Potential Root Causes
1.  **Anki API Compatibility:** `mw.col.decks.id(deck_name)` might carry risks in certain Anki versions or with special deck names.
2.  **Initialization Timing:** Accessing `mw.col` before the collection is fully loaded.
3.  **Empty Note Type:** The first card in the deck might belong to a note type with no fields (unlikely but possible).

---

## 📝 Immediate Action Checklist

This checklist is designed for your Development Agent to finalize the add-on and fix the current blocking bug.

### 1. 🔍 Debugging & Fixes
- [ ] **Fix `_on_deck_changed` robustness:**
    - Wrap the logic in `ui/settings_dialog.py` in a broader try-catch block that displays a `showWarning` with the specific error if it fails (currently it only logs to file).
    - Add fallback logic if `deck_id` lookup fails.
- [ ] **Verify `lib` imports:**
    - Ensure `google-generativeai` is loading correctly from the `lib/` folder.
    - Check for `ModuleNotFoundError` during startup.
- [ ] **Run Internal Diagnostics:**
    - Use the **Stella > Run Diagnostics** menu item (if accessible) to check for API Client initialization errors.

### 2. ✅ Functionality Verification
- [ ] **API Connection Test:**
    - Go to **Stella > Test API Connection**. Verify it returns "Success".
- [ ] **Single Note Translation:**
    - Open Anki Browser -> Select a Card -> Context Menu (if implemented) or Editor Button.
    - Verify translation works on a single card before batch operations.
- [ ] **Batch Processing:**
    - Once Field Mapping is fixed, test a small batch (size 1) of Translation.
    - Test Sentence Generation (parsing JSON response).
    - Test Image Generation (saving to `collection.media`).

### 3. 🚀 Polish & Release
- [ ] **User Feedback:** Improve error messages in the UI (currently some are just logged).
- [ ] **Docs:** Ensure `README.md` explains how to add API keys.

---

## 💡 Recommendation for Development Agent

**To fix the "Field Mapping Disabled" issue:**

Open `ui/settings_dialog.py` and modify `_on_deck_changed` (approx line 767).
Add explicit error reporting to the user:

```python
except Exception as e:
    logger.error(f"Error loading deck fields: {e}", exc_info=True)
    # ADD THIS:
    from aqt.utils import showWarning
    showWarning(f"Failed to load deck fields:\n{str(e)}")
    self._status_label.setText(f"Error: {e}")
```

This will immediately reveal why the fields are not loading (e.g., `AttributeError`, `KeyError`, etc.).
