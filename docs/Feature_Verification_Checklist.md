# Stella Anki All-in-One Addon - Feature Verification Checklist

## Document Purpose

This document provides a comprehensive feature-by-feature comparison between the three reference implementations and the integrated addon. The development agent should use this checklist to:

1. **Verify** each feature is correctly implemented
2. **Identify** missing functionality
3. **Ensure** logic correctness and efficiency

---

## Reference Projects Summary

| Project | Path | Primary Functionality |
|---------|------|----------------------|
| **Anki_Deck_Translater** | `Reference/Anki_Deck_Translater/` | Context-aware vocabulary translation |
| **Anki_Sentence_generater** | `Reference/Anki_Sentence_generater/` | Example sentence generation |
| **Anki_Image_Gen_with_Google_Nano_Banana** | `Reference/Anki_Image_Gen_with_Google_Nano_Banana/` | AI image generation for flashcards |

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Implemented and verified |
| ⬜ | Needs verification |
| ⚠️ | Partial/needs review |
| ❌ | Not implemented/missing |
| 🆕 | New feature (not in reference) |

---

# SECTION 1: API Key Management

## 1.1 Core Key Storage

### Reference Implementation: `Anki_Deck_Translater/api_key_manager.py`

| Feature | Lines | Integrated File | Status | Notes |
|---------|-------|-----------------|--------|-------|
| `MAX_API_KEYS = 15` constant | L38 | `core/api_key_manager.py:L28` | ✅ | Value matches (15) |
| `FAILURE_THRESHOLD = 5` constant | L41 | `core/api_key_manager.py:L29` | ✅ | Value matches (5) |
| `KEY_COOLDOWN_HOURS = 24` constant | L44 | `core/api_key_manager.py:L30` | ✅ | Value matches (24) |
| API key length validation (35-50 chars) | L47-48 | `core/api_key_manager.py:L31-32` | ✅ | MIN=35, MAX=50 verified |
| `APIKeyStats` dataclass | L71-86 | `core/api_key_manager.py:L91-130` | ✅ | All fields present + enhancements |
| `APIKeyManagerState` dataclass | L89-109 | `core/api_key_manager.py:L133-194` | ✅ | Compare fields - enhanced with encryption |
| Singleton pattern | L119-125 | `core/api_key_manager.py:L209-222` | ✅ | Thread-safe with Lock (enhanced) |

### Key Management Methods

| Method | Reference Line | Integrated | Status | Notes |
|--------|---------------|------------|--------|-------|
| `add_key(key: str)` | L168-195 | ✅ | ✅ | Validation logic verified |
| `remove_key(index: int)` | L197-217 | ✅ | ✅ | Index adjustment correct |
| `get_all_keys()` | L219-221 | ✅ | ✅ | Returns copy |
| `get_key_count()` | L223-225 | ✅ | ✅ | |
| `get_masked_keys()` | L227-229 | ✅ | ✅ | Format: `AIza...xxxx` |
| `clear_all_keys()` | L231-236 | ✅ | ✅ | |

## 1.2 Key Rotation Logic

### Reference Implementation: `Anki_Deck_Translater/api_key_manager.py`

| Feature | Reference Lines | Integrated | Status | Notes |
|---------|-----------------|------------|--------|-------|
| `get_current_key()` - skip exhausted | L240-266 | ✅ | ✅ | Loop logic verified at L418-446 |
| `_is_key_usable()` - check cooldown | L282-309 | ✅ | ✅ | Datetime comparison verified at L461-490 |
| `rotate_to_next_key()` | L311-350 | ✅ | ✅ | Circular rotation at L492-528 |
| `force_set_current_key()` | L352-357 | ✅ | ✅ | At L530-535 |
| Quota error detection | L442-444 | ✅ | ✅ | Enhanced keywords: 429, quota, rate, resource_exhausted, limit, exhausted |

### Critical Logic to Verify

```python
# Reference: api_key_manager.py:L282-309
def _is_key_usable(self, key_id: str) -> bool:
    # 1. Check if key_id exists in stats ✅
    # 2. Check is_active flag ✅
    # 3. Check exhausted_at timestamp ✅
    # 4. Compare against cooldown period ✅
    # 5. Auto-reactivate if cooldown expired ✅
```

**Verification Status**: ✅ Logic verified in integrated addon at L461-490.

## 1.3 Statistics Tracking

### Reference Implementation: `Anki_Deck_Translater/api_key_manager.py`

| Statistic | Reference | Integrated | Status |
|-----------|-----------|------------|--------|
| `total_requests` | ✅ | ✅ | ✅ |
| `successful_requests` | ✅ | ✅ | ✅ |
| `failed_requests` | ✅ | ✅ | ✅ |
| `consecutive_failures` | ✅ | ✅ | ✅ |
| `total_words_translated` | ✅ | ✅ (as `total_words_processed`) | ✅ |
| `last_used` (ISO timestamp) | ✅ | ✅ | ✅ |
| `last_failure` (ISO timestamp) | ✅ | ✅ | ✅ |
| `last_failure_reason` (sanitized) | ✅ | ✅ | ✅ |
| `exhausted_at` (ISO timestamp) | ✅ | ✅ | ✅ |
| `is_active` flag | ✅ | ✅ | ✅ |
| `total_images_generated` | ❌ | ✅ | 🆕 Enhanced |
| `total_sentences_generated` | ❌ | ✅ | 🆕 Enhanced |
| `exhausted_at` (ISO timestamp) | ✅ | ⬜ | ⬜ |
| `is_active` flag | ✅ | ⬜ | ⬜ |

### Summary Statistics

| Method | Reference | Integrated | Status |
|--------|-----------|------------|--------|
| `get_summary_stats()` | L465-505 | ✅ | ✅ L647-685 |
| `reset_stats()` | L507-521 | ✅ | ✅ L687-701 |
| `reset_key_cooldown(index)` | L523-533 | ✅ | ✅ L703-714 |

## 1.4 Persistence

| Feature | Reference | Integrated | Status | Notes |
|---------|-----------|------------|--------|-------|
| `_load_state()` | ✅ | ✅ | ✅ | Decryption verified |
| `_save_state()` | ✅ | ✅ | ✅ | Encryption verified |
| `_load_stats()` | ✅ | ✅ | ✅ | |
| `_save_stats()` | ✅ | ✅ | ✅ | |
| Error reason sanitization | ✅ | ✅ | ✅ | API key fragments removed via `_sanitize_error_reason()` |

### Encryption (New in Integrated)

| Feature | Reference | Integrated | Status |
|---------|-----------|------------|--------|
| XOR-based encryption | ❌ | ✅ | 🆕 |
| Password derivation (PBKDF2) | ❌ | ✅ | 🆕 |
| Machine-specific key | ❌ | ✅ | 🆕 |

## 1.5 New Features Added (Feb 2026)

| Feature | Status | Notes |
|---------|--------|-------|
| Thread-safe singleton with Lock | ✅ | Double-check locking pattern |
| API connection tester (`api_tester.py`) | ✅ | JSON schema validation |
| Debug utilities (`debug_utils.py`) | ✅ | Comprehensive status checks |

---

# SECTION 2: Translation Feature

## 2.1 Single Note Translation

### Reference Implementation: `Anki_Deck_Translater/stella_generator.py`

| Feature | Reference Lines | Integrated File | Status |
|---------|-----------------|-----------------|--------|
| QueryOp pattern | L48-168 | `translation/translator.py` | ✅ |
| Background operation | L54-123 | ✅ | ✅ |
| Success callback | L125-143 | ✅ | ✅ |
| Failure callback | L145-155 | ✅ | ✅ |
| HTML tag stripping | L178-183 | ✅ | ✅ via `core/utils.py` |
| JSON schema for response | L185-203 | ✅ | ✅ |
| Prompt construction | L205-224 | ✅ | ✅ via `config/prompts.py` |
| API retry logic | L226-275 | ✅ | ✅ with exponential backoff |
| Response parsing | L277-321 | ✅ | ✅ |

### Translation Prompt Template

**Reference** (`stella_generator.py:L205-224`):
```python
def _create_prompt(self, target_word: str, context: str, language: str) -> str:
    return f"""You are an expert {language} translator.

Task: Translate the word "{target_word}" into {language}.
Context: {context if context else "None provided"}

Requirements:
- Provide the most appropriate translation for the given context.
- If context is provided, use it to disambiguate the meaning.
- If no context is provided, provide the most common meaning.
- Return ONLY valid JSON in the specified format.

Word to translate: "{target_word}"
Target language: {language}"""
```

**Status**: ✅ Verified - prompt in `config/prompts.py` matches this structure.

## 2.2 Batch Translation

### Reference Implementation: `Anki_Deck_Translater/batch_translator.py`

| Feature | Reference Lines | Integrated File | Status |
|---------|-----------------|-----------------|--------|
| `BatchTranslationSignals` class | L25-34 | `translation/batch_translator.py:L40-49` | ✅ |
| `BatchTranslator` (QRunnable) | L37-70 | `translation/batch_translator.py:L52-110` | ✅ |
| Batch chunking logic | L152-163 | ✅ | ✅ |
| Build model with JSON schema | L165-191 | ✅ | ✅ |
| `_request_batch_translation()` | L193-209 | ✅ | ✅ |
| `_build_prompt()` for batch | L211-232 | ✅ | ✅ |
| `_call_model_with_retry()` | L234-299 | ✅ | ✅ |
| Rate limit detection (429) | L272-295 | ✅ | ✅ |
| `_parse_response()` | L356-388 | ✅ | ✅ |
| `_apply_translations()` | L390-419 | ✅ | ✅ |
| `_update_note_field()` | L421-432 | ✅ | ✅ |
| `_classify_error()` | L434-452 | ✅ | ✅ via `core/utils.py` |
| `_interruptible_sleep()` | L454-466 | ✅ | ✅ Implemented |

### Critical: Interruptible Sleep

**Reference** (`batch_translator.py:L454-466`):
```python
def _interruptible_sleep(self, seconds: float) -> None:
    """Sleep that can be interrupted by cancel_event."""
    elapsed = 0.0
    interval = 0.5
    while elapsed < seconds:
        if self.cancel_event.is_set():
            return
        sleep_time = min(interval, seconds - elapsed)
        time.sleep(sleep_time)
        elapsed += sleep_time
```

**Status**: ✅ Verified - implemented in integrated batch translator.

### Batch Signals

| Signal | Reference | Integrated | Status |
|--------|-----------|------------|--------|
| `progress(processed, total)` | ✅ | ✅ | ✅ |
| `detailed_progress(processed, total, success, failure)` | ✅ | ✅ | ✅ |
| `error_detail(error_type, message, affected_count)` | ✅ | ✅ | ✅ |
| `error(str)` | ✅ | ✅ | ✅ |
| `finished(success_count, failure_count)` | ✅ | ✅ | ✅ |
| `key_rotated(old_key_id, new_key_id)` | ✅ | ✅ | ✅ |

### Batch Defaults (Intentional Differences)

| Setting | Reference | Integrated | Reason |
|---------|-----------|------------|--------|
| `batch_size` | 10 | 5 | More conservative for stability |
| `batch_delay_seconds` | 5.0 | 8.0 | Longer delay for rate limit safety |

## 2.3 Translation UI

### Reference Implementation: `Anki_Deck_Translater/stella_translater.py`

| UI Element | Reference Lines | Integrated | Status |
|------------|-----------------|------------|--------|
| Deck dropdown | L165-178 | ✅ | ✅ |
| Source field dropdown | L191-193 | ✅ | ✅ |
| Context field dropdown | L194 | ✅ | ✅ |
| Destination field dropdown | L195 | ✅ | ✅ |
| Language selector (editable combo) | L197-213 | ✅ | ✅ |
| Model selector (editable combo) | L215-233 | ✅ | ✅ |
| Overwrite checkbox | L235-242 | ✅ | ✅ |
| Skip existing checkbox | L244-252 | ✅ | ✅ |
| Ignore errors checkbox | L254-262 | ✅ | ✅ |
| Batch size spinner (1-30) | L303-315 | ✅ | ✅ |
| Batch delay spinner (1-60) | L317-333 | ✅ | ✅ |
| Progress bar | L357-363 | ✅ | ✅ |
| Success/Error rate labels | L366-373 | ✅ | ✅ |
| Stop button | L382-387 | ✅ | ✅ |
| Error log section (collapsible) | L392-413 | ✅ | ✅ |

### Multi-Key UI Section

| Element | Reference Lines | Integrated | Status |
|---------|-----------------|------------|--------|
| Current key label | L432-439 | ✅ | ✅ |
| Remaining keys indicator | L441-444 | ✅ | ✅ |
| New key input field | L447-454 | ✅ | ✅ |
| Add key button | L456-458 | ✅ | ✅ |
| Key list widget | L463-466 | ✅ | ✅ via stats view |
| Remove key button | L470-472 | ✅ | ✅ |
| Set active button | L474-476 | ✅ | ✅ |
| Reset cooldown button | L478-481 | ✅ | ✅ via method |
    while elapsed < seconds:
        if self.cancel_event.is_set():
            return
        sleep_time = min(interval, seconds - elapsed)
        time.sleep(sleep_time)
        elapsed += sleep_time
```

**Action**: Verify this is implemented in integrated batch translator.

### Batch Signals

| Signal | Reference | Integrated | Status |
|--------|-----------|------------|--------|
| `progress(processed, total)` | ✅ | ⬜ | ⬜ |
| `detailed_progress(processed, total, success, failure)` | ✅ | ⬜ | ⬜ |
| `error_detail(error_type, message, affected_count)` | ✅ | ⬜ | ⬜ |
| `error(str)` | ✅ | ⬜ | ⬜ |
| `finished(success_count, failure_count)` | ✅ | ⬜ | ⬜ |
| `key_rotated(old_key_id, new_key_id)` | ✅ | ⬜ | ⬜ |

## 2.3 Translation UI

### Reference Implementation: `Anki_Deck_Translater/stella_translater.py`

| UI Element | Reference Lines | Integrated | Status |
|------------|-----------------|------------|--------|
| Deck dropdown | L165-178 | ⬜ | ⚠️ |
| Source field dropdown | L191-193 | ⬜ | ⚠️ |
| Context field dropdown | L194 | ⬜ | ⚠️ |
| Destination field dropdown | L195 | ⬜ | ⚠️ |
| Language selector (editable combo) | L197-213 | ⬜ | ⚠️ |
| Model selector (editable combo) | L215-233 | ⬜ | ⚠️ |
| Overwrite checkbox | L235-242 | ⬜ | ⚠️ |
| Skip existing checkbox | L244-252 | ⬜ | ⚠️ |
| Ignore errors checkbox | L254-262 | ⬜ | ⚠️ |
| Batch size spinner (1-30) | L303-315 | ⬜ | ⚠️ |
| Batch delay spinner (1-60) | L317-333 | ⬜ | ⚠️ |
| Progress bar | L357-363 | ⬜ | ⚠️ |
| Success/Error rate labels | L366-373 | ⬜ | ❌ |
| Stop button | L382-387 | ⬜ | ⚠️ |
| Error log section (collapsible) | L392-413 | ⬜ | ❌ |

### Multi-Key UI Section

| Element | Reference Lines | Integrated | Status |
|---------|-----------------|------------|--------|
| Current key label | L432-439 | ⬜ | ⚠️ |
| Remaining keys indicator | L441-444 | ⬜ | ⚠️ |
| New key input field | L447-454 | ⬜ | ⚠️ |
| Add key button | L456-458 | ⬜ | ⚠️ |
| Key list widget | L463-466 | ⬜ | ⚠️ |
| Remove key button | L470-472 | ⬜ | ⚠️ |
| Set active button | L474-476 | ⬜ | ⚠️ |
| Reset cooldown button | L478-481 | ⬜ | ❌ |

---

# SECTION 3: Sentence Generation Feature

## 3.1 Single Note Generation

### Reference Implementation: `Anki_Sentence_generater/sentence_generator_modern.py`

| Feature | Reference Lines | Integrated File | Status |
|---------|-----------------|-----------------|--------|
| QueryOp pattern | L62-180 | `sentence/sentence_generator.py` | ✅ |
| Background operation | L68-134 | ✅ | ✅ |
| Success callback | L136-156 | ✅ | ✅ |
| Failure callback | L158-167 | ✅ | ✅ |
| HTML stripping | L182-187 | ✅ | ✅ |
| Generation config | L189-211 | ✅ | ✅ |
| Prompt construction | L213-239 | ✅ | ✅ |
| API call with retry | L241-259 | ✅ | ✅ |
| Response parsing | L299-335 | ✅ | ✅ |
| Highlighting | L376-381 | ✅ | ✅ |

### Sentence Response Schema

**Reference** (`sentence_generator_modern.py:L189-211`):
```python
{
    "type": "object",
    "properties": {
        "translated_sentence": {"type": "string"},
        "english_sentence": {"type": "string"},
        "translated_conjugated_word": {"type": "string"},
        "english_word": {"type": "string"}
    },
    "required": [
        "translated_sentence",
        "english_sentence",
        "translated_conjugated_word",
        "english_word"
    ]
}
```

**Status**: ✅ Schema verified in integrated addon.

### Word Highlighting

**Reference** (`sentence_generator_modern.py:L376-381`):
```python
def _apply_highlighting(self, text: str, word: str) -> str:
    if not text or not word:
        return text
    highlight = f'<span style="background-color: rgb(255, 255, 0); color: rgb(0, 0, 0);">{word}</span>'
    return text.replace(word, highlight, 1)
```

**Status**: ✅ Highlighting implementation verified.

## 3.2 Batch Sentence Generation

### Reference Implementation: `Anki_Sentence_generater/bunai.py`

| Feature | Reference Lines | Integrated | Status |
|---------|-----------------|------------|--------|
| `SentenceWorker` class | `sentence_worker.py:L54-220` | ✅ | ✅ via UI dialog |
| Batch popup dialog | `bunai.py:L470-700` | ✅ | ✅ DeckOperationDialog |
| Progress tracking | ✅ | ✅ | ✅ |
| Cancel button | ✅ | ✅ | ✅ |
| Time measurement | ✅ | ✅ | ✅ via ETA calculation |

**Status**: ✅ Batch sentence generation implemented in `ui/settings_dialog.py`.

## 3.3 Progress State Manager

### Reference Implementation: `Anki_Sentence_generater/progress_state.py`

| Feature | Reference Lines | Integrated File | Status |
|---------|-----------------|-----------------|--------|
| `ProgressStateManager` class | L23-227 | `sentence/progress_state.py` | ✅ |
| Atomic write | L48-62 | ✅ | ✅ |
| Backup file | L64-69 | ✅ | ✅ |
| `start_run()` | L109-121 | ✅ | ✅ |
| `has_pending_run()` | L123-126 | ✅ | ✅ |
| `get_pending_note_ids()` | L128-132 | ✅ | ✅ |
| `get_failed_details()` | L134-139 | ✅ | ✅ |
| `update_pending()` | L141-147 | ✅ | ✅ |
| `mark_success()` | L149-160 | ✅ | ✅ |
| `mark_failure()` | L162-175 | ✅ | ✅ |
| `clear_run()` | L177-181 | ✅ | ✅ (as `clear()`) |
| `reset_failures_to_pending()` | L183-195 | ✅ | ✅ |
| `clear_missing_notes()` | L197-210 | ⚠️ | ⚠️ Not implemented |
| `operation_type` tracking | - | ✅ | 🆕 Enhanced |

---

# SECTION 4: Image Generation Feature

## 4.1 Prompt Generation

### Reference Implementation: `Anki_Image_Gen_with_Google_Nano_Banana/src/gemini_client.py`

| Feature | Reference Lines | Integrated File | Status |
|---------|-----------------|-----------------|--------|
| `GeminiClient` class | L35-75 | `image/prompt_generator.py` | ⬜ |
| `generate_single_prompt()` | L77-152 | ⬜ | ⬜ |
| `generate_image_prompts_batch()` | L154-316 | ⬜ | ⬜ |
| Safety settings | L93-112 | ⬜ | ⚠️ |
| JSON parsing with fallback | L244-296 | ⬜ | ⬜ |
| `_generate_prompts_individually()` | L318-350 | ⬜ | ⬜ |

### Master Prompt Templates

**Reference** (`config/config.py:L54-135`):
- `UNIFIED_PROMPT` - Main template
- `MASTER_PROMPTS` dictionary with presets
- `ACTIVE_MASTER_PROMPT` setting

**Action**: Compare with `config/prompts.py` in integrated addon.

## 4.2 Image Generation (Nano Banana)

### Reference Implementation: `Anki_Image_Gen_with_Google_Nano_Banana/src/nano_banana_client.py`

| Feature | Reference Lines | Integrated File | Status |
|---------|-----------------|-----------------|--------|
| `NanoBananaClient` class | L48-75 | `image/image_generator.py` | ⬜ |
| Model: `gemini-2.5-flash-image-preview` | L66 | ⬜ | ⬜ |
| New GenAI SDK | L73-77 | ⬜ | ⬜ |
| Legacy SDK fallback | L78-82 | ⬜ | ⬜ |
| `generate_image_from_prompt()` | L84-176 | ⬜ | ⬜ |
| Response extraction | L136-162 | ⬜ | ⬜ |
| PIL image handling | L164-175 | ⬜ | ⬜ |
| `generate_image_for_word()` | L178-214 | ⬜ | ⬜ |
| `generate_images_batch()` | L216-298 | ⬜ | ⬜ |

### Response Extraction

**Reference** (`nano_banana_client.py:L136-162`):
```python
candidate = response.candidates[0]
for part in candidate.content.parts:
    if hasattr(part, 'inline_data') and part.inline_data is not None:
        if hasattr(part.inline_data, 'data') and part.inline_data.data:
            image_bytes = part.inline_data.data
            break
```

**Action**: Verify this exact extraction logic in integrated addon.

## 4.3 Anki Integration

### Reference Implementation: `Anki_Image_Gen_with_Google_Nano_Banana/src/anki_connector.py`

| Feature | Reference Lines | Integrated | Status |
|---------|-----------------|------------|--------|
| `AnkiConnector` class | L30-46 | Different approach | ⚠️ |
| `anki_request()` | L48-86 | Direct Anki API | ⚠️ |
| `find_notes_without_images()` | L116-252 | ❌ | ❌ |
| `get_notes_info()` | L254-282 | ⬜ | ⬜ |
| `store_media_file()` | L284-305 | ⬜ | ⬜ |
| `update_note_fields()` | L332-352 | ⬜ | ⬜ |
| `add_image_to_note()` | L354-400 | ⬜ | ⬜ |

**Note**: The integrated addon uses direct Anki API instead of AnkiConnect. This is appropriate for an add-on but the functionality should still be equivalent.

### Missing: Find Notes Without Images

**Reference** (`anki_connector.py:L116-252`):
- Searches deck for notes with empty image field
- Uses multiple search syntaxes for compatibility
- Validates found notes
- Applies limit

**Action**: Implement equivalent functionality in integrated addon.

## 4.4 Enhanced Workflow

### Reference Implementation: `Anki_Image_Gen_with_Google_Nano_Banana/src/enhanced_workflow.py`

| Feature | Integrated | Status |
|---------|------------|--------|
| `WorkflowStep` enum | ❌ | ❌ |
| `WorkflowMetrics` dataclass | ❌ | ❌ |
| `WorkflowProgress` dataclass | ❌ | ❌ |
| `EnhancedWorkflowManager` class | ❌ | ❌ |
| Step weights for progress | ❌ | ❌ |
| Error recovery | ❌ | ❌ |
| Pause/Resume/Cancel | ❌ | ❌ |
| Estimated completion time | ❌ | ❌ |
| Workflow history | ❌ | ❌ |
| Progress callbacks | ❌ | ❌ |

**Critical**: The entire enhanced workflow system is NOT implemented.

---

# SECTION 5: Editor Integration

## 5.1 Hook Registration

### Reference Implementations:
- `Anki_Deck_Translater/editor_integration.py`
- `Anki_Sentence_generater/editor_integration.py`

| Hook | Reference | Integrated | Status |
|------|-----------|------------|--------|
| `editor_did_init_shortcuts` | ✅ | ✅ | ⬜ |
| `editor_web_view_did_init` | ✅ | ✅ | ⬜ |
| `webview_did_receive_js_message` | ✅ | ✅ | ⬜ |
| `editor_did_unfocus_field` | ✅ | ✅ | ⬜ |
| Legacy `addHook` fallback | ✅ | ✅ | ⬜ |

## 5.2 Keyboard Shortcuts

| Shortcut | Translator | Sentence | Integrated | Status |
|----------|-----------|----------|------------|--------|
| Ctrl+Shift+B | ✅ Translation | ✅ Sentence | ❓ | ⚠️ Conflict? |
| Ctrl+Shift+T | ❌ | ❌ | ✅ Translation | 🆕 |
| Ctrl+Shift+S | ❌ | ❌ | ✅ Sentence | 🆕 |
| Ctrl+Shift+I | ❌ | ❌ | ✅ Image | 🆕 |

**Note**: Reference projects both use Ctrl+Shift+B. Integrated addon uses different shortcuts.

## 5.3 Editor Button

### Reference: JavaScript Injection

Both reference projects inject a button via JavaScript. Key elements:

| Element | Reference | Integrated | Status |
|---------|-----------|------------|--------|
| Button ID (duplicate prevention) | ✅ | ⬜ | ⬜ |
| Gradient styling | ✅ | ⬜ | ⬜ |
| Hover effects | ✅ | ⬜ | ⬜ |
| pycmd integration | ✅ | ⬜ | ⬜ |
| Toolbar detection | ✅ | ⬜ | ⬜ |

## 5.4 Auto-Generation

| Feature | Reference | Integrated | Status |
|---------|-----------|------------|--------|
| Auto-generate toggle | ✅ | ✅ | ⬜ |
| Field-specific trigger | ⬜ Partial | ✅ | 🆕 |
| Feature selection (translate/sentence) | ❌ | ✅ | 🆕 |

---

# SECTION 6: Configuration

## 6.1 Config Structure

### Reference: Simple Dictionary
All reference projects use a simple dictionary loaded from `config.json`.

### Integrated: Dataclass-Based
The integrated addon uses typed dataclasses:

| Config Class | Purpose | Status |
|--------------|---------|--------|
| `APIConfig` | API key settings | 🆕 |
| `TranslationConfig` | Translation settings | 🆕 |
| `ImageConfig` | Image settings | 🆕 |
| `SentenceConfig` | Sentence settings | 🆕 |
| `EditorConfig` | Editor settings | 🆕 |
| `StellaConfig` | Root config | 🆕 |
| `ConfigManager` | Load/save manager | 🆕 |

This is an **improvement** over the reference implementations.

## 6.2 Required Config Options

| Option | Translator | Sentence | Image | Integrated | Status |
|--------|-----------|----------|-------|------------|--------|
| gemini_api_key | ✅ | ✅ | ✅ | ✅ | ⬜ |
| language | ✅ | ✅ | ❌ | ✅ | ⬜ |
| difficulty | ✅ | ✅ | ❌ | ✅ | ⬜ |
| deck | ✅ | ✅ | ✅ | ✅ | ⬜ |
| source_field | ✅ | ✅ | ✅ | ✅ | ⬜ |
| context_field | ✅ | ❌ | ❌ | ✅ | ⬜ |
| destination_field | ✅ | ✅ | ✅ | ✅ | ⬜ |
| batch_size | ✅ | ❌ | ✅ | ✅ | ⬜ |
| batch_delay_seconds | ✅ | ❌ | ✅ | ✅ | ⬜ |
| overwrite_existing | ✅ | ❌ | ❌ | ✅ | ⬜ |
| skip_existing | ✅ | ❌ | ❌ | ✅ | ⬜ |
| ignore_batch_errors | ✅ | ❌ | ❌ | ✅ | ⬜ |
| auto_generate | ✅ | ✅ | ❌ | ✅ | ⬜ |
| gemini_model | ✅ | ✅ | ✅ | ✅ | ⬜ |
| log_level | ✅ | ✅ | ✅ | ✅ | ⬜ |

---

# SECTION 7: Critical Missing Features

## 7.1 High Priority (Required for Feature Parity)

| Feature | Reference | Integrated | Action Required |
|---------|-----------|------------|-----------------|
| Batch Sentence Generation | `bunai.py:L470-700` | ❌ | Implement SentenceWorker and batch dialog |
| Interruptible Sleep | `batch_translator.py:L454-466` | ❌ | Add to batch translator |
| Find Notes Without Images | `anki_connector.py:L116-252` | ❌ | Implement deck scanning |
| Real-time Error Log UI | `stella_translater.py:L392-413` | ❌ | Add collapsible error log |
| Reset Key Cooldown | `api_key_manager.py:L523-533` | ❌ | Add to UI |
| Success/Error Rate Labels | `stella_translater.py:L366-373` | ❌ | Add to progress UI |

## 7.2 Medium Priority (Feature Completeness)

| Feature | Reference | Action Required |
|---------|-----------|-----------------|
| Image Workflow Management | `enhanced_workflow.py` | Consider implementing |
| Reset Failures to Pending | `progress_state.py:L183-195` | Add method |
| Clear Missing Notes | `progress_state.py:L197-210` | Add method |
| Average Requests Before Rotation | Statistics calculation | Add to summary stats |
| Image Preview | Image Gen UI | Consider adding |

## 7.3 Low Priority (Polish)

| Feature | Action Required |
|---------|-----------------|
| Workflow Pause/Resume | Nice to have |
| Estimated Completion Time | UX improvement |
| Manual Image Approval | Quality control |

---

# SECTION 8: Verification Procedure

## For Each Feature:

1. **Locate** the reference implementation (file and line numbers)
2. **Find** the corresponding code in integrated addon
3. **Compare** the logic line-by-line
4. **Test** the feature manually in Anki
5. **Mark** status in this checklist

## Code Review Priority Order:

1. API Key Manager (critical for all features)
2. Batch Translation (most complex)
3. Single Note Operations (foundation)
4. UI Elements (user-facing)
5. Editor Integration (convenience)

---

# SECTION 9: Testing Matrix

## 9.1 API Key Tests

| Test Case | Expected Result | Status |
|-----------|-----------------|--------|
| Add valid key (AIza...) | Key added, count +1 | ⬜ |
| Add invalid key (no AIza) | Error, rejected | ⬜ |
| Add duplicate key | Error, rejected | ⬜ |
| Remove key by index | Key removed, index adjusted | ⬜ |
| 5 consecutive failures | Auto-rotate to next key | ⬜ |
| Rate limit (429) | Immediate rotation | ⬜ |
| After 24h cooldown | Key reactivated | ⬜ |
| Manual cooldown reset | Key immediately usable | ⬜ |

## 9.2 Translation Tests

| Test Case | Expected Result | Status |
|-----------|-----------------|--------|
| Single note, empty dest | Translation added | ⬜ |
| Single note, existing dest | Follows overwrite setting | ⬜ |
| Batch 10 notes | All translated | ⬜ |
| Cancel during batch | Stops gracefully | ⬜ |
| Rate limit during batch | Rotates key, continues | ⬜ |

## 9.3 Sentence Tests

| Test Case | Expected Result | Status |
|-----------|-----------------|--------|
| Single note | Sentence + translation | ⬜ |
| Word highlighted | Yellow highlight applied | ⬜ |
| Different difficulty | Different complexity | ⬜ |
| Auto-generate | Triggers on field unfocus | ⬜ |

## 9.4 Image Tests

| Test Case | Expected Result | Status |
|-----------|-----------------|--------|
| Generate prompt | Valid prompt text | ⬜ |
| Generate image | PNG data returned | ⬜ |
| Add to Anki | File in media folder | ⬜ |
| Update note | Image tag in field | ⬜ |

---

*Document Version: 1.0*
*Created: 2026-02-01*
*Purpose: Development Agent Reference Checklist*
