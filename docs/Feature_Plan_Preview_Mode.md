# Feature Development Plan: Batch Operation Preview Mode

**Target Component:** Stella Anki Tools Add-on  
**Status:** Approved for Development  
**Date:** February 4, 2026

## 1. Overview
The goal is to implement a **"Preview/Test"** workflow for all three batch operations (Sentence Generation, Translation, Image Generation). 
Users must be able to generate results for a small sample (3-5 cards) and visually verify them *before* committing to processing the entire deck. This reduces API usage anxiety and ensures quality control.

## 2. Technical Architecture

### 2.1 Core Pattern: Decoupled Generation
Currently, the worker classes often combine generation (API calls) and application (Note updates) into a single flow. We must decouple these steps.

*   **Current Flow:** `Input -> Worker -> API -> Note Update -> Save`
*   **New Preview Flow:** `Input -> Worker(preview=True) -> API -> return ResultObject -> Preview Dialog`
*   **Application Flow (Post-Preview):** `ResultObject -> Apply to Note -> Save`

### 2.2 Data Structures
We will introduce a shared data structure to standardize how results are passed from the workers to the Preview UI.

**File:** `core/preview_models.py` (New File)
```python
from dataclasses import dataclass, field
from typing import Optional, Any, Dict

@dataclass
class PreviewResult:
    """Standardized result object for previewing generated content."""
    note_id: int
    original_text: str            # The source text used for generation
    generated_content: Any        # Text string or Image Path/Bytes
    target_field: str             # The field where content will be saved
    
    # Metadata for specific features
    secondary_content: Optional[str] = None  # e.g., Translation for Sentence mode
    secondary_field: Optional[str] = None    # Field for secondary content
    
    # Image specific
    is_image: bool = False
    temp_image_path: Optional[str] = None    # Path to temp file for preview
    
    def cleanup(self):
        """Cleanup temp files if rejected."""
        import os
        if self.temp_image_path and os.path.exists(self.temp_image_path):
            try:
                os.remove(self.temp_image_path)
            except OSError:
                pass
```

### 2.3 Image Handling Strategy
*   **Preview Phase:** Images are generated and saved to the OS temporary directory (`tempfile`). They are **NOT** added to the Anki media database (`collection.media`) yet to avoid pollution.
*   **Apply Phase:** If the user accepts, the file is moved/copied from the temp folder to the Anki media folder, and the filename is written to the field.
*   **Reject Phase:** If the user cancels, `cleanup()` is called to delete the temp files.

## 3. Implementation Steps

### Phase 1: Shared Infrastructure
1.  **Create Model:** Create `core/preview_models.py` containing the `PreviewResult` dataclass.
2.  **Create UI:** Create `ui/preview_dialog.py`.
    *   **Class:** `PreviewDialog(QDialog)`
    *   **Input:** List of `PreviewResult` objects.
    *   **Layout:** A scrollable list or tabs showing "Before" (Source) vs "After" (Generated).
    *   **Controls:** "Example 1", "Example 2", "Example 3" tabs/list items.
    *   **Buttons:** 
        *   "✅ Looks Good - Start Full Batch" (Returns Accepted)
        *   "❌ Cancel" (Returns Rejected)

### Phase 2: Logic Refactoring (Worker Modules)

#### 2.1 Refactor `SentenceGenerator` (`sentence/sentence_generator.py`)
*   Add a method `generate_preview(note, ...)` that returns a `PreviewResult` instead of updating the note.
*   Ensure it performs the API call but skips the `note[field] = value` step.

#### 2.2 Refactor `Translator` (`translation/translator.py`)
*   Add `translate_preview(note, ...)` returning `PreviewResult`.

#### 2.3 Refactor `ImageGenerator` (`image/image_generator.py`)
*   Add `generate_image_preview(note, ...)` returning `PreviewResult`.
*   **Crucial:** Use `tempfile.NamedTemporaryFile` for the output path. Do not use `mw.col.media.write_data`.

### Phase 3: Main Controller & Deck Operations Integration

#### 3.1 Modify `DeckOperationDialog` (`ui/settings_dialog.py`)
*   **UI Update:** Add a "🧪 Preview (3 Cards)" button next to the "Start Processing" button.
*   **Sample Logic:** Implement `_get_sample_notes(count=3)`:
    *   Filter valid notes (ensure source field is not empty).
    *   Prefer notes where the target field is empty (to simulate real work).
    *   Randomly select 3.
*   **Preview Workflow Method:**
    1.  Show "Generating Previews..." progress dialog (modal).
    2.  Iterate through the 3 sample notes.
    3.  Call the appropriate `*_preview` method on the worker.
    4.  Collect `PreviewResult` objects.
    5.  Close progress dialog.
    6.  Open `PreviewDialog` with results.
    7.  **If User Accepts:** 
        *   Apply the preview results to the actual notes (don't waste the API calls!). 
        *   **Then** automatically trigger the full batch process configuration (or just let them click Start).
    8.  **If User Rejects:** 
        *   Call `cleanup()` on all results.

## 4. Specific Requirements & Constraints

*   **Concurrency:** Preview generation must run in a background thread (using `QThread` or `QueryOp`) to avoid freezing the UI.
*   **Rate Limiting:** The `APIKeyManager` is already robust, but ensure the preview loop respects the `request_delay` to avoid instant 429s on 3 rapid calls.
*   **Error Handling:** If 1 out of 3 previews fails, show the error in the Preview Dialog for that specific card, but display the successful ones. Do not crash the entire preview.

## 5. Definition of Done
1.  User can click "Preview" in the Deck Operations dialog.
2.  A loading bar appears while 3 items are processed.
3.  A dialog appears showing Source -> Result for the 3 items.
4.  Images render correctly in the preview.
5.  Clicking "Cancel" removes any temp images.
6.  Clicking "Start" applies those 3 changes and returns to the main dialog ready for the full run.
