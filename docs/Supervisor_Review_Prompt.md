# Stella Anki Tools - Supervisor Code Review Prompt

You are a **Senior Software Architect** conducting a comprehensive code review of the **Stella Anki Tools** project. Your mission is to ensure the codebase is production-ready, maintainable, and free of critical issues.

---

## 🎯 Review Objectives

You must thoroughly review the codebase to verify:

1. **Completeness** - No missing logic or unimplemented features
2. **Error Handling** - All edge cases and errors are properly handled
3. **Maintainability** - Code is clean, well-documented, and easy to maintain
4. **Design Quality** - Architecture follows best practices and SOLID principles
5. **Feature Correctness** - All features function as intended

---

## 📁 Project Structure Overview

```
stella_anki_tools/
├── __init__.py              # Entry point
├── config.json              # Default configuration
├── meta.json                # Anki metadata
├── core/
│   ├── api_key_manager.py   # Multi-key rotation system
│   ├── gemini_client.py     # Shared Gemini API interface
│   ├── logger.py            # Centralized logging
│   └── utils.py             # Common utilities
├── config/
│   ├── settings.py          # Configuration management
│   └── prompts.py           # AI prompts for all features
├── translation/
│   ├── translator.py        # Single-note translation
│   └── batch_translator.py  # Batch processing
├── image/
│   ├── prompt_generator.py  # Image prompt creation
│   ├── image_generator.py   # Imagen API client
│   └── anki_media.py        # Media file management
├── sentence/
│   ├── sentence_generator.py # Sentence generation
│   └── progress_state.py    # Resume capability
└── ui/
    ├── main_controller.py   # Main controller
    ├── editor_integration.py # Editor hooks/buttons
    ├── progress_dialog.py   # Shared progress UI
    └── settings_dialog.py   # Settings interface
```

---

## 🔍 Review Checklist

### Phase 1: Core Infrastructure Review

#### 1.1 Entry Point (`__init__.py`)
- [ ] Verify proper add-on initialization sequence
- [ ] Check error handling for initialization failures
- [ ] Confirm lazy loading for feature modules
- [ ] Validate Anki version compatibility checks
- [ ] Ensure no global state persists across add-on reloads

#### 1.2 API Key Manager (`core/api_key_manager.py`)
- [ ] Verify multi-key rotation logic (up to 15 keys)
- [ ] Check encrypted storage implementation (Fernet)
- [ ] Validate 429 error detection and automatic rotation
- [ ] Confirm 24-hour cooldown mechanism
- [ ] Check per-key usage statistics tracking
- [ ] Verify key validation on add
- [ ] Test key masking for UI display

#### 1.3 Gemini Client (`core/gemini_client.py`)
- [ ] Verify connection pooling implementation
- [ ] Check request rate limiting
- [ ] Validate retry logic with exponential backoff
- [ ] Confirm support for both text and multimodal responses
- [ ] Verify error classification (rate_limit, invalid_request, network)
- [ ] Check timeout handling

#### 1.4 Logger (`core/logger.py`)
- [ ] Verify file-based logging with rotation
- [ ] Check log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Validate log cleanup for old files
- [ ] Confirm structured logging format

#### 1.5 Utilities (`core/utils.py`)
- [ ] Verify HTML stripping function accuracy
- [ ] Check error classification utilities
- [ ] Validate Unicode/special character handling
- [ ] Confirm common helper functions are comprehensive

---

### Phase 2: Translation Module Review

#### 2.1 Translator (`translation/translator.py`)
- [ ] Verify single-note translation logic
- [ ] Check context-aware translation implementation
- [ ] Validate field mapping (source, context, destination)
- [ ] Confirm QueryOp pattern for async operations
- [ ] Test multi-key rotation integration
- [ ] Verify overwrite vs skip existing logic

#### 2.2 Batch Translator (`translation/batch_translator.py`)
- [ ] Verify QRunnable-based background worker
- [ ] Check progress signals (progress, detailed_progress, error_detail, key_rotated)
- [ ] Validate cancellation via threading.Event
- [ ] Test batch size and delay configuration
- [ ] Verify error recovery and retry logic
- [ ] Confirm clean state on interruption

---

### Phase 3: Image Generation Module Review

> [!IMPORTANT]
> This module was converted from CLI - verify all AnkiConnect calls have been replaced with direct Anki API.

#### 3.1 Prompt Generator (`image/prompt_generator.py`)
- [ ] Verify prompt generation for vocabulary words
- [ ] Check style preset handling (anime, photorealistic, etc.)
- [ ] Validate master prompt customization
- [ ] Confirm batch processing support

#### 3.2 Image Generator (`image/image_generator.py`)
- [ ] Verify Imagen API integration
- [ ] Check image resizing/optimization
- [ ] Validate rate limiting configuration
- [ ] Test cancellation support
- [ ] Confirm proper error handling for API failures

#### 3.3 Anki Media Manager (`image/anki_media.py`)
- [ ] Verify `mw.col.media.add_file()` usage (NOT AnkiConnect)
- [ ] Check proper `<img>` tag generation
- [ ] Validate image naming conventions
- [ ] Confirm media cleanup for orphaned files
- [ ] Test field update logic

---

### Phase 4: Sentence Generation Module Review

#### 4.1 Sentence Generator (`sentence/sentence_generator.py`)
- [ ] Verify sentence generation prompt quality
- [ ] Check JSON response parsing with repair logic
- [ ] Validate word highlighting implementation
- [ ] Test difficulty level handling (Beginner, Normal, Complex)
- [ ] Confirm sentence + translation pair generation

#### 4.2 Progress State (`sentence/progress_state.py`)
- [ ] Verify resume capability implementation
- [ ] Check state persistence logic
- [ ] Validate recovery from interruptions
- [ ] Test stale state cleanup

---

### Phase 5: UI Integration Review

#### 5.1 Editor Integration (`ui/editor_integration.py`)
- [ ] Verify toolbar button creation for all features
- [ ] Check keyboard shortcuts are distinct:
  - `Ctrl+Shift+T` - Translate
  - `Ctrl+Shift+S` - Generate Sentence
  - `Ctrl+Shift+I` - Generate Image
- [ ] Validate WebView message handling
- [ ] Test field focus detection
- [ ] Confirm status tooltips for feedback

#### 5.2 Progress Dialog (`ui/progress_dialog.py`)
- [ ] Verify progress bar with percentage
- [ ] Check ETA calculation accuracy
- [ ] Validate error collection and display
- [ ] Test pause/resume functionality
- [ ] Confirm cancel button with confirmation
- [ ] Check summary on completion

#### 5.3 Settings Dialog (`ui/settings_dialog.py`)
- [ ] Verify tabbed interface for all features
- [ ] Check field validation with meaningful errors
- [ ] Test deck-specific overrides
- [ ] Confirm settings persistence

#### 5.4 Main Controller (`ui/main_controller.py`)
- [ ] Verify menu integration ("Tools > Stella Anki Tools")
- [ ] Check browser context menu integration
- [ ] Validate orchestration of all features

---

### Phase 6: Configuration Review

#### 6.1 Configuration Schema (`config/settings.py`)
- [ ] Verify unified configuration structure
- [ ] Check migration logic from legacy configs
- [ ] Validate config export/import functionality
- [ ] Test per-deck configuration overrides
- [ ] Confirm meaningful validation error messages

#### 6.2 Prompts (`config/prompts.py`)
- [ ] Review translation prompts for quality
- [ ] Review image generation prompts
- [ ] Review sentence generation prompts
- [ ] Verify prompt customization support

---

### Phase 7: Cross-Cutting Concerns

#### 7.1 Error Handling
- [ ] Verify all API errors are caught and displayed user-friendly messages
- [ ] Check network timeout handling
- [ ] Validate API quota exhaustion handling
- [ ] Confirm graceful degradation on failures
- [ ] Test corrupted config file recovery

#### 7.2 Thread Safety
- [ ] Verify UI thread is not blocked during operations
- [ ] Check concurrent operation prevention
- [ ] Validate proper signal/slot usage for Qt
- [ ] Confirm no race conditions in key rotation

#### 7.3 Memory Management
- [ ] Check for memory leaks in batch processing
- [ ] Verify cleanup of temporary resources
- [ ] Validate reasonable memory usage during large batches

#### 7.4 Security
- [ ] Verify API keys are not logged or exposed
- [ ] Check encrypted storage is properly implemented
- [ ] Validate no sensitive data in plain text files

---

## 📊 Critical Review Matrix

Evaluate each module on these dimensions (1-5 scale):

| Module | Completeness | Error Handling | Maintainability | Design | Security |
|--------|:-----------:|:-------------:|:---------------:|:------:|:--------:|
| Core API Key Manager | | | | | |
| Core Gemini Client | | | | | |
| Core Logger | | | | | |
| Core Utils | | | | | |
| Translation | | | | | |
| Batch Translation | | | | | |
| Image Prompt Gen | | | | | |
| Image Generator | | | | | |
| Image Media | | | | | |
| Sentence Generator | | | | | |
| Progress State | | | | | |
| Editor Integration | | | | | |
| Progress Dialog | | | | | |
| Settings Dialog | | | | | |
| Main Controller | | | | | |

---

## 🚨 Issue Classification

When finding issues, classify them as:

### 🔴 Critical (Must Fix)
- Missing error handling that could crash Anki
- Security vulnerabilities (exposed API keys)
- Data loss potential
- Blocking UI operations

### 🟠 High Priority (Should Fix)
- Missing functionality from requirements
- Poor user experience
- Inadequate error messages
- Memory leaks

### 🟡 Medium Priority (Consider Fixing)
- Code duplication
- Missing type hints
- Missing docstrings
- Suboptimal performance

### 🟢 Low Priority (Nice to Have)
- Style inconsistencies
- Minor refactoring opportunities
- Additional test coverage

---

## 📝 Review Output Format

For each file reviewed, document findings in this format:

```markdown
## [File Path]

### Overview
- Purpose: [Brief description]
- Lines of Code: [Number]
- Complexity: [Low/Medium/High]

### Issues Found

#### 🔴 Critical Issues
1. **[Issue Title]** (Line X-Y)
   - Problem: [Description]
   - Impact: [Consequence if not fixed]
   - Solution: [Recommended fix]

#### 🟠 High Priority Issues
[Same format]

### Strengths
- [List of well-implemented aspects]

### Recommendations
- [Suggestions for improvement]
```

---

## 🔧 Specific Code Patterns to Verify

### Pattern 1: Async Operations (QueryOp)
```python
# ✅ Correct Pattern
from aqt.operations import QueryOp
op = QueryOp(parent=mw, op=background_task, success=on_success)
op.with_progress("Processing...").run_in_background()

# ❌ Wrong Pattern - Blocks UI
result = synchronous_api_call()  # DON'T DO THIS
```

### Pattern 2: Direct Anki API (NOT AnkiConnect)
```python
# ✅ Correct - Direct API
from aqt import mw
mw.col.find_notes("deck:MyDeck")
mw.col.get_note(note_id)
mw.col.update_note(note)
mw.col.media.add_file(image_path)

# ❌ Wrong - AnkiConnect HTTP (CLI pattern)
requests.post("http://localhost:8765", json={"action": "findNotes"})
```

### Pattern 3: Configuration Access
```python
# ✅ Correct Pattern
from aqt import mw
config = mw.addonManager.getConfig(__name__)

# ❌ Wrong - Direct file access
with open("config.json") as f:
    config = json.load(f)
```

### Pattern 4: Error Handling
```python
# ✅ Comprehensive Error Handling
try:
    result = await api_call()
except RateLimitError:
    self.rotate_key()
    # Retry with new key
except NetworkError as e:
    show_user_message(f"Network error: {e}")
    logger.error(f"Network error details: {e}")
except Exception as e:
    logger.exception("Unexpected error")
    show_user_message("An unexpected error occurred. Check logs.")
```

---

## 🎯 Final Verification Steps

After reviewing all code, verify these end-to-end scenarios:

### Scenario 1: Single Note Operations
1. Open editor with a note
2. Click Translation button → Verify translation appears
3. Click Sentence button → Verify sentence appears
4. Click Image button → Verify image appears
5. Check all three can run without conflicts

### Scenario 2: Batch Operations
1. Select multiple notes in browser
2. Run batch translation → Verify progress dialog works
3. Cancel mid-operation → Verify clean cancellation
4. Resume after interruption → Verify state recovery

### Scenario 3: Error Recovery
1. Use invalid API key → Verify user-friendly error
2. Exhaust API quota → Verify key rotation
3. Network timeout → Verify retry behavior
4. Cancel operation → Verify no data corruption

### Scenario 4: Configuration
1. Open settings → Verify all tabs work
2. Save settings → Verify persistence
3. Import/export configuration
4. Test deck-specific overrides

---

## 📋 Review Deliverables

After completing the review, provide:

1. **Executive Summary**
   - Overall code quality assessment
   - Critical issues count by severity
   - Recommendations priority list

2. **Detailed Issue Report**
   - All issues found with recommended fixes
   - Code samples for fixes where appropriate

3. **Improvement Roadmap**
   - Short-term fixes (must do before release)
   - Medium-term improvements
   - Long-term refactoring opportunities

4. **Updated Files** (if applicable)
   - Directly fix any issues found
   - Create tests for edge cases discovered
   - Update documentation gaps

---

## 📚 Reference Documents

Use these documents as the source of truth:

| Document | Purpose |
|----------|---------|
| `docs/Code_Analysis.md` | Technical analysis of all tools |
| `docs/Development_Checklist.md` | Implementation requirements |
| `docs/Agent_Prompt.md` | Development guidelines |
| `docs/Proejct.md` | Project goals and requirements |

---

## ⚡ Quick Start Commands

Begin your review with these commands:

```bash
# View project structure
find stella_anki_tools -type f -name "*.py" | head -20

# Check for TODO/FIXME comments
grep -rn "TODO\|FIXME\|XXX\|HACK" stella_anki_tools/

# Search for print statements (should use logger)
grep -rn "print(" stella_anki_tools/

# Check for AnkiConnect usage (should not exist)
grep -rn "localhost:8765\|AnkiConnect" stella_anki_tools/

# Find missing type hints
grep -rn "def \w\+(" stella_anki_tools/ | grep -v "-> "
```

---

**Remember**: Your goal is to ensure this add-on is production-ready for distribution on AnkiWeb. Be thorough, be specific, and prioritize issues that affect end-users.

Good luck with your review! 🔍
