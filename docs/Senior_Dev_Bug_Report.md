# 🐛 Bug Report: Field Mapping Dropdowns Disabled (Initialization Race Condition)

**To:** Senior Developer
**From:** AI Junior Developer
**Date:** 2026-02-03
**Severity:** Critical (Core functionality blocked)

## 🚨 Issue Summary
Users cannot select fields (Source/Destination) in the "Deck Operations" dialog.
Despite successfully retrieving cards and field lists from the Anki Collection, the UI dropdowns remain disabled because the underlying Python objects are `None` at the time of the update call.

## 📉 Diagnostics & Evidence
**Log Output:**
```text
2026-02-03 14:12:22 - ... - INFO - _on_deck_changed called with deck: 'Vocabible_A_sen_img'
2026-02-03 14:12:22 - ... - INFO - Found 8 fields: ['FrontText', ... 'SentenceTranslation']
2026-02-03 14:12:22 - ... - WARNING - Translation source/dest dropdown is None!
2026-02-03 14:12:22 - ... - WARNING - Sentence dropdown is None!
```

**Root Cause Analysis:**
1. **Successful Data Fetch:** The backend logic (`_on_deck_changed`) correctly finds the deck ID, retrieves a card, and extracts field names. (Anki 25.x compatibility issue was fixed).
2. **UI Initialization Failed:** The warning `dropdown is None!` proves that `self._source_dropdown` (and others) have not been assigned to the class instance when `_on_deck_changed` executes.
3. **Race Condition / Setup Logic:** The `_on_deck_changed` method is likely being triggered (via `_load_decks` -> `setCurrentText`) **before** the tabs containing these dropdowns are fully initialized or attached to `self`.

## 🆚 Comparison with Reference Project (`Anki_Sentence_generater`)

We have a working reference project: **Anki_Sentence_generater**.

| Feature | Broken Project (`Stella Anki Tools`) | Reference Project (`Anki_Sent...`) |
| :--- | :--- | :--- |
| **File** | `ui/settings_dialog.py` | `stella_translater.py` |
| **UI Setup** | Complex multi-tab `QTabWidget` split into methods (`_create_translation_tab`, etc.) | *Unknown (Needs verification)* |
| **Trigger** | Call `_load_decks()` at the very end of `__init__` | *Likely initializes UI fully before logic* |

## 🛠 Proposed Solution Strategy
The `_on_deck_changed` signal is firing too early.

**Immediate Fix Needed:**
1. Ensure all `_create_X_tab()` methods assign widgets to `self.` instance variables **before** `_load_decks()` is called.
2. In `ui/settings_dialog.py`, verify that `self._setup_ui()` fully completes **before** any signal connection or deck loading occurs.

Please review the attached code comparison and apply the fix to `ui/settings_dialog.py`.

## 🧠 Request for Expert Analysis
While our preliminary analysis points to an initialization race condition, we defer to your superior judgment. Please do not limit your investigation to our findings. We Request a thorough and open-minded analysis of the codebase, considering all possibilities:

*   **Scope:** Look beyond the race condition hypothesis.
*   **Architecture:** Check if the lazy-loading pattern or the Singleton controller flow contributes to this state.
*   **Reference:** Utilize the working logic in `Anki_Sentence_generater` deeply to identify structural divergences we might have missed.

We trust your expertise to identify the true root cause, whether it is the one we suspected or something entirely different.
