# Stella Anki Tools - Development Checklist

A comprehensive checklist for combining the Deck Translator, Image Generator, and Sentence Generator into a single unified Anki add-on.

**Last Updated**: 2026-02-01

---

## Table of Contents
1. [Project Setup](#1-project-setup)
2. [Core Infrastructure](#2-core-infrastructure)
3. [Translation Module](#3-translation-module)
4. [Image Generation Module](#4-image-generation-module)
5. [Sentence Generation Module](#5-sentence-generation-module)
6. [UI/UX Integration](#6-uiux-integration)
7. [API & Data Flow](#7-api--data-flow)
8. [Testing & Quality Assurance](#8-testing--quality-assurance)
9. [Packaging & Distribution](#9-packaging--distribution)
10. [Migration & Compatibility](#10-migration--compatibility)

---

## 1. Project Setup

### 1.1 Repository Structure
- [x] Create new repository for `stella_anki_tools`
- [x] Set up directory structure as per architecture plan
- [x] Initialize git with `.gitignore` for Python/Anki add-ons
- [x] Create `README.md` with project overview
- [ ] Add `LICENSE` file (decide on unified license - see note below)

> [!NOTE]
> **License Consideration**: The three tools have different licenses:
> - Translator: CC BY-NC-SA 4.0
> - Sentence Generator: AGPL-3.0
> - Image Generator: Unspecified
> 
> **Recommendation**: Use AGPL-3.0 for the unified add-on as it's the most restrictive and satisfies compatibility requirements.

### 1.2 Development Environment
- [ ] Create `requirements-dev.txt` for development dependencies
- [ ] Set up Python virtual environment
- [ ] Configure linting (flake8/pylint)
- [ ] Configure type checking (mypy)
- [ ] Set up pre-commit hooks

### 1.3 Documentation Foundation
- [x] Create `docs/` directory structure
- [ ] Add `CONTRIBUTING.md`
- [ ] Add `CHANGELOG.md`
- [ ] Create API documentation template

---

## 2. Core Infrastructure

### 2.1 Entry Point & Initialization
- [x] Create `__init__.py` with proper add-on initialization
- [x] Implement lazy loading for feature modules
- [x] Set up error handling for initialization failures
- [x] Create `meta.json` with unified add-on metadata

```python
# __init__.py structure
if __name__ != "__main__":
    try:
        from aqt import mw
        if mw:
            # Initialize core components
            from .core import initialize_core
            from .ui import initialize_ui
            # ...
    except Exception as e:
        # Handle initialization errors gracefully
        pass
```

### 2.2 Configuration System
- [x] Design unified configuration schema (see Code_Analysis.md)
- [x] Create `config/settings.py` - Settings manager class
- [ ] Implement migration logic from legacy configs
- [x] Create default `config.json`
- [x] Add config validation with meaningful error messages
- [ ] Support per-deck configuration overrides
- [ ] Implement config export/import functionality

**Unified Config Schema:**
```json
{
  "version": "1.0.0",
  "api": {
    "keys": [],
    "rotation_enabled": true,
    "cooldown_hours": 24,
    "model": "gemini-2.5-flash"
  },
  "translation": { /* ... */ },
  "image": { /* ... */ },
  "sentence": { /* ... */ },
  "editor": { /* ... */ }
}
```

### 2.3 API Key Management (Unified)
- [x] Create `core/api_key_manager.py` merging best practices from all tools
- [x] Implement encrypted storage using XOR-based encryption with PBKDF2 key derivation
- [x] Implement multi-key rotation (from Translator)
- [x] Add automatic cooldown on 429 errors
- [x] Track per-key usage statistics
- [x] Support key validation testing
- [x] Implement secure key masking for UI display
- [ ] Add key import/export functionality

**Key Features to Implement:**
| Feature | Source | Priority | Status |
|---------|--------|----------|--------|
| Max 15 keys | Translator | High | ✅ Done |
| Encrypted storage | Image Gen | High | ✅ Done |
| Auto-rotation | Translator | High | ✅ Done |
| Usage stats | Both | Medium | ✅ Done |
| 24hr cooldown | Translator | Medium | ✅ Done |
| Key validation | Both | Medium | ✅ Done |

### 2.4 Logging System
- [x] Create `core/logger.py` with unified logging
- [x] Implement file-based logging with rotation
- [x] Add log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Create log viewer in settings UI
- [ ] Implement log cleanup for old log files
- [x] Add structured logging format for debugging

### 2.5 Gemini Client (Shared)
- [x] Create `core/gemini_client.py` as shared API client
- [ ] Implement connection pooling
- [x] Add request rate limiting
- [x] Implement retry logic with exponential backoff
- [x] Support both text and multimodal responses
- [ ] Add response caching (optional, for development)

---

## 3. Translation Module

### 3.1 Core Translation Logic
- [x] Create `translation/__init__.py`
- [x] Port `StellaGenerator` to `translation/translator.py`
- [x] Port `BatchTranslationWorker` to `translation/batch_translator.py`
- [ ] Implement `TranslationManager` orchestrator class
- [x] Update prompts for translation quality
- [ ] Add context-aware translation improvements

### 3.2 Translation Features
- [x] Single-note translation (editor integration)
- [x] Batch translation for selected cards
- [x] Deck-wide translation with progress (via DeckOperationDialog)
- [x] Skip cards with existing translations (configurable)
- [x] Overwrite mode for re-translation
- [x] Field mapping with auto-detection

### 3.3 Translation Configuration
- [x] Source field selection
- [x] Context field selection (for disambiguation)
- [x] Destination field selection
- [x] Target language selection
- [x] Model selection (gemini-2.5-flash, etc.)
- [x] Batch size and delay settings

---

## 4. Image Generation Module

> [!IMPORTANT]
> This module requires the most significant refactoring as it must be converted from CLI to add-on.

### 4.1 Core Conversion from CLI
- [x] Port `GeminiClient` prompt generator → `image/prompt_generator.py`
- [x] Port `NanoBananaClient` → `image/image_generator.py`
- [x] Replace AnkiConnect HTTP calls with direct Anki API
- [x] Replace file-based image storage with `mw.col.media`
- [x] Remove CLI-specific dependencies (colorama, rich, tqdm)
- [x] Adapt SQLite workflow to Anki config system

### 4.2 Anki Media Integration
- [x] Create `image/anki_media.py` for media handling
- [x] Implement image storage via `mw.col.media.add_file()`
- [x] Generate proper `<img>` tags for card fields
- [x] Handle image naming conventions
- [ ] Implement image cleanup for orphaned media

**AnkiConnect to Direct API Mapping:**
```python
# Before (AnkiConnect)
requests.post("http://localhost:8765", json={"action": "storeMediaFile", ...})

# After (Direct Anki API)
from aqt import mw
mw.col.media.add_file(image_path)
```

### 4.3 Image Generation Features
- [x] Single-card image generation (editor)
- [x] Batch image generation for deck (via DeckOperationDialog)
- [ ] Image prompt preview before generation
- [x] Image style presets (anime, photorealistic, etc.)
- [ ] Image size optimization for Anki
- [x] Progress tracking with cancellation
- [x] Skip cards with existing images

### 4.4 Image Configuration
- [x] Word field selection
- [x] Image field selection
- [x] Style preset selection
- [ ] Master prompt customization
- [ ] Image dimensions settings
- [x] Rate limiting configuration

### 4.5 SDK Compatibility
- [x] Evaluate `google-genai` vs `google-generativeai` requirements
- [ ] Bundle necessary SDK components in `lib/`
- [x] Handle namespace conflicts with existing packages
- [ ] Test image generation with chosen SDK

---

## 5. Sentence Generation Module

### 5.1 Core Sentence Logic
- [x] Create `sentence/__init__.py`
- [x] Port `SentenceGenerator` → `sentence/sentence_generator.py`
- [x] Port `ProgressStateManager` → `sentence/progress_state.py`
- [x] Implement resume functionality for interrupted batches
- [x] Add word highlighting in generated sentences

### 5.2 Sentence Features
- [x] Single-note sentence generation (editor)
- [x] Batch sentence generation (via DeckOperationDialog)
- [x] Difficulty levels (Beginner, Normal, Complex)
- [x] Sentence + translation pair generation
- [x] Resume from last position
- [ ] Error recovery with retry queue

### 5.3 Sentence Configuration
- [x] Expression field selection
- [x] Sentence field selection
- [x] Translation field selection
- [x] Difficulty level selection
- [x] Language selection
- [ ] Auto-generate toggle

---

## 6. UI/UX Integration

### 6.1 Unified Settings Dialog (DeckOperationDialog)
- [x] Create `ui/settings_dialog.py` with tabbed interface
- [x] Tab 1: Translation Settings (deck selection, field mapping, batch)
- [x] Tab 2: Sentence Generation Settings
- [x] Tab 3: Image Generation Settings
- [x] Tab 4: Settings/API Keys Management
- [ ] Tab 5: Advanced/Debug
- [ ] Add deck-specific overrides option
- [ ] Implement settings search/filter

**Key Feature: Deck Selection Dialog**
Users can now select a deck directly from the add-on window (without browser):
- Select any deck with cards
- Auto-populate field dropdowns based on note type
- Start batch operations for Translation/Sentence/Image generation
- Real-time progress tracking with stop functionality

**UI Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Stella Anki Tools - Deck Operations                [X] │
├─────────────────────────────────────────────────────────┤
│ [Translation] [Sentences] [Images] [Settings]           │
├─────────────────────────────────────────────────────────┤
│  Deck: [▼ Select Deck________________]                  │
│                                                         │
│  ┌─Field Mapping────────────────────────────────────┐  │
│  │ Source Field:      [▼ Front___________]          │  │
│  │ Context (Optional):[▼ (None)__________]          │  │
│  │ Destination Field: [▼ Translation_____]          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─Options──────────────────────────────────────────┐  │
│  │ Target Language: [▼ Korean____________]          │  │
│  │ Model: [▼ gemini-2.5-flash___________]           │  │
│  │ ☑ Skip cards with existing translations          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  [▶ Start Translation]  [⏹ Stop]                       │
├─────────────────────────────────────────────────────────┤
│  Progress: [████████░░░░░░░] 45 / 100                  │
│  Status: Processing... ✅ 42 | ❌ 3 | Rate: 93.3%     │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Editor Integration
- [x] Create `ui/editor_integration.py` (unified from both tools)
- [x] Add toolbar buttons for each feature
- [x] Implement distinct keyboard shortcuts:
  - [x] `Ctrl+Shift+T` - Translate
  - [x] `Ctrl+Shift+S` - Generate Sentence
  - [x] `Ctrl+Shift+I` - Generate Image
- [x] Add WebView message handling for all buttons
- [ ] Implement field focus detection for auto-generation
- [ ] Add status tooltips for feedback

### 6.3 Progress Dialog
- [x] Create reusable `ui/progress_dialog.py`
- [x] Show progress bar with percentage
- [x] Display current item being processed
- [x] Show ETA calculation
- [x] List errors in expandable section
- [x] Add pause/resume functionality
- [x] Add cancel button with confirmation
- [x] Show summary on completion

### 6.4 Browser Integration
- [ ] Add context menu items in card browser:
  - [ ] "Stella: Translate Selected"
  - [ ] "Stella: Generate Images"
  - [ ] "Stella: Generate Sentences"
  - [ ] "Stella: Process All (T+I+S)"
- [ ] Show selected card count
- [ ] Add filter for cards needing processing

### 6.5 Menu Integration
- [x] Add "Stella" menu to Anki menubar
- [x] Add "📚 Deck Operations..." (primary entry point)
- [x] Add "⚙️ Settings..." submenu
- [x] Add "🔑 Manage API Keys..." submenu
- [x] Add "🧪 Test API Connection"
- [x] Add "📊 API Statistics"
- [x] Add "ℹ️ About Stella"

---

## 7. API & Data Flow

### 7.1 API Rate Limiting
- [x] Implement global rate limiter for Gemini API
- [x] Configure per-feature rate limits
- [ ] Add request queuing system
- [x] Implement batch delay between requests
- [x] Handle 429 errors gracefully with backoff

### 7.2 Data Persistence
- [x] Store settings via Anki's config API
- [x] Store API keys in JSON file (api_keys.json)
- [x] Store usage statistics in separate file (api_stats.json)
- [ ] Implement data backup functionality
- [ ] Add data export/import options

### 7.3 Progress State Management
- [x] Create `sentence/progress_state.py`
- [x] Persist batch processing state
- [x] Support resume after Anki restart
- [ ] Track per-deck processing history
- [ ] Clean up stale progress states

### 7.4 Error Handling
- [x] Create error taxonomy (API, Network, Config, etc.) in `core/utils.py`
- [x] Implement error recovery strategies per type
- [x] Add user-friendly error messages
- [x] Log detailed error info for debugging
- [ ] Collect error analytics (optional, with consent)

---

## 8. Testing & Quality Assurance

### 8.1 Unit Tests
- [x] Create `tests/` directory structure
- [x] Test configuration loading/saving
- [x] Test API key manager operations (encryption, rotation)
- [ ] Test prompt generation
- [ ] Test response parsing
- [ ] Test error handling
- [ ] Test field mapping logic

### 8.2 Integration Tests
- [ ] Test Gemini API connectivity
- [ ] Test translation end-to-end
- [ ] Test image generation end-to-end
- [ ] Test sentence generation end-to-end
- [ ] Test batch processing
- [x] Test resume functionality

### 8.3 Edge Cases
- [ ] Empty field handling
- [ ] Unicode/special characters in words
- [ ] Very long text content
- [ ] Network timeout handling
- [ ] API quota exhaustion
- [ ] Canceled operations cleanup
- [ ] Concurrent operation prevention
- [ ] Corrupted config file recovery

### 8.4 UI Testing
- [ ] Settings dialog functionality
- [ ] Progress dialog updates
- [ ] Editor button clicks
- [ ] Keyboard shortcuts work
- [ ] Menu items respond correctly
- [ ] Browser context menu integration

### 8.5 Anki Version Compatibility
- [ ] Test with Anki 2.1.50+
- [ ] Test with Anki 23.x
- [ ] Test with Anki 24.x
- [ ] Test with Anki 25.x (latest)
- [ ] Document minimum supported version

---

## 9. Packaging & Distribution

### 9.1 Dependencies Bundling
- [ ] Identify required external packages
- [ ] Bundle `google-generativeai` in `lib/`
- [ ] Bundle Pillow components if needed
- [ ] Handle namespace package conflicts
- [ ] Test with clean Anki installation

### 9.2 Package Structure
- [ ] Create proper `__init__.py` chain
- [ ] Generate `manifest.json` for AnkiWeb
- [ ] Set up `meta.json` with all fields
- [ ] Include icon file (use existing Stella icon)
- [ ] Include license file

### 9.3 Build Process
- [ ] Create build script for packaging
- [ ] Implement version numbering
- [ ] Generate `.ankiaddon` zip file
- [ ] Exclude development files from package
- [ ] Validate package structure before upload

### 9.4 Distribution Channels
- [ ] Prepare AnkiWeb submission
- [ ] Create GitHub releases
- [ ] Write installation instructions
- [ ] Create video tutorial (optional)

### 9.5 Documentation Finalization
- [ ] Complete user guide
- [ ] Add FAQ section
- [ ] Document troubleshooting steps
- [ ] Add screenshots to README
- [ ] Translate docs to target languages (optional)

---

## 10. Migration & Compatibility

### 10.1 Detect Existing Installations
- [ ] Check for existing Translator add-on
- [ ] Check for existing Sentence Generator add-on
- [ ] Check for existing Image Generator data
- [ ] Show migration prompt to user

### 10.2 Configuration Migration
- [ ] Parse old Translator `config.json`
- [ ] Parse old Sentence Generator `config.json`
- [ ] Parse old Image Generator `user_settings.json`
- [ ] Merge configurations intelligently
- [ ] Preserve API keys from all sources
- [ ] Backup old configs before migration

### 10.3 Data Migration
- [ ] Migrate multi-key state from Translator
- [ ] Migrate progress state from Sentence Generator
- [ ] Migrate image generation database (if applicable)
- [ ] Preserve usage statistics

### 10.4 Conflict Resolution
- [ ] Disable old add-ons automatically (with user consent)
- [ ] Provide instructions for manual cleanup
- [ ] Handle shortcut conflicts
- [ ] Document breaking changes

### 10.5 Rollback Support
- [ ] Keep backup of migrated configs
- [ ] Provide instructions for reverting
- [ ] Test migration reversal process

---

## Development Priority Matrix

| Phase | Tasks | Priority | Effort |
|-------|-------|----------|--------|
| Phase 1 | Core infrastructure, Config, API Key Manager | Critical | High |
| Phase 2 | Translation module (port existing) | High | Medium |
| Phase 3 | Sentence module (port existing) | High | Medium |
| Phase 4 | Image module (CLI conversion) | High | Very High |
| Phase 5 | Unified UI/UX | High | High |
| Phase 6 | Testing & QA | Critical | High |
| Phase 7 | Packaging & Distribution | High | Medium |
| Phase 8 | Migration & Compatibility | Medium | Medium |

---

## Success Criteria

### Functional Requirements
- [ ] All three features work independently
- [ ] Features can be combined in single batch
- [ ] Single API key configuration works for all features
- [ ] Editor integration works seamlessly
- [ ] Progress tracking with resume works

### Performance Requirements
- [ ] Single-note operations complete in <3 seconds
- [ ] Batch operations show real-time progress
- [ ] Memory usage stays reasonable during batches
- [ ] No UI freezing during operations

### User Experience Requirements
- [ ] Settings are intuitive and discoverable
- [ ] Error messages are helpful
- [ ] Migration from old tools is smooth
- [ ] Documentation covers all use cases

---

## Appendix: Reference Resources

### Existing Tool Locations
- **Translator**: `Reference/Anki_Deck_Translater/`
- **Image Generator**: `Reference/Anki_Image_Gen_with_Google_Nano_Banana/`
- **Sentence Generator**: `Reference/Anki_Sentence_generater/`

### Key Files to Reference
| Purpose | Translator | Image Gen | Sentence Gen |
|---------|-----------|-----------|--------------|
| Entry | `__init__.py` | `main_enhanced.py` | `__init__.py` |
| Main Class | `stella_translater.py` | `core_automation.py` | `bunai.py` |
| API Keys | `api_key_manager.py` | `api_key_manager.py` | - |
| Generator | `stella_generator.py` | `gemini_client.py` | `sentence_generator_modern.py` |
| Editor | `editor_integration.py` | - | `editor_integration.py` |
| Config | `config.json` | `config/config.py` | `config.json` |

### Anki Development Resources
- [Anki Add-on Writing Guide](https://addon-docs.ankiweb.net/)
- [Qt for Python Documentation](https://doc.qt.io/qtforpython/)
- [Anki Source Code](https://github.com/ankitects/anki)

### Google AI Resources
- [Google AI Python SDK](https://github.com/google-gemini/generative-ai-python)
- [Gemini API Documentation](https://ai.google.dev/docs)
