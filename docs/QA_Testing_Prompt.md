# Stella Anki Tools - QA Testing Guide

You are a QA engineer tasked with thoroughly testing **Stella Anki Tools**, a comprehensive Anki add-on that provides AI-powered Translation, Sentence Generation, and Image Generation features. Your goal is to identify bugs, usability issues, and edge cases before release.

---

## 📋 Test Environment Setup

### Prerequisites
| Requirement | Specification |
|-------------|---------------|
| Anki Version | 2.1.50+ (test on 2.1.54, 2.1.60, 23.10+) |
| Operating Systems | Windows 10/11, macOS 12+, Ubuntu 22.04 |
| Python | Bundled with Anki (3.9+) |
| API Keys | 2-3 valid Google Gemini API keys |
| Test Deck | Vocabulary deck with 100+ notes |

### Test Deck Structure
Create a test deck with these fields:
```
Note Type: "Stella Test Card"
Fields:
- Word (front)
- Definition  
- Translation (target for translation)
- Sentence (target for sentences)
- SentenceTranslation
- Image (target for images)
```

### Sample Test Data
```
| Word | Definition |
|------|------------|
| ephemeral | lasting for a very short time |
| serendipity | finding something good without looking for it |
| ubiquitous | present everywhere at the same time |
| eloquent | fluent or persuasive speaking |
| 猫 | Japanese word for cat |
| Schmetterling | German word for butterfly |
| café | French loanword with accent |
| 🎉 | emoji character |
| <b>bold</b> | HTML in field |
| word with "quotes" | special characters |
```

---

## 🔧 Phase 1: Installation & Initialization Tests

### T1.1 - Fresh Installation
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Copy `stella_anki_tools` folder to Anki add-ons | Folder appears in add-ons directory | |
| 2 | Start Anki | Anki launches without errors | |
| 3 | Check Tools menu | "Stella" menu appears | |
| 4 | Open Tools → Add-ons | Stella Anki Tools listed with correct name | |
| 5 | Check Anki console (debug) | No Python errors on startup | |

### T1.2 - Configuration Loading
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Check config.json exists | Default config created on first run | |
| 2 | Open Tools → Add-ons → Config | JSON config editor opens | |
| 3 | Modify a setting and save | Setting persists after restart | |
| 4 | Delete config.json and restart | Default config recreated | |
| 5 | Corrupt config.json with invalid JSON | Graceful error, defaults restored | |

### T1.3 - Dependency Check
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Verify `lib/` folder exists | google-generativeai bundled | |
| 2 | Import test: `import google.generativeai` | No ImportError in Anki console | |
| 3 | Check for namespace conflicts | No warnings about google.* | |

---

## 🔑 Phase 2: API Key Management Tests

### T2.1 - Adding API Keys
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Stella → Manage API Keys | API Key dialog opens | |
| 2 | Add valid API key | Key added, count updated | |
| 3 | Add same key again | Duplicate warning shown | |
| 4 | Add invalid key (random string) | Validation fails with message | |
| 5 | Add 15 keys | All keys accepted | |
| 6 | Add 16th key | "Maximum keys reached" error | |
| 7 | Close dialog and reopen | Keys persist | |

### T2.2 - API Connection Test
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Stella → Test API Connection (no keys) | "No API key configured" warning | |
| 2 | Add valid key, then Test Connection | "Connection Successful" with response | |
| 3 | Test with invalid key | "Authentication failed" error | |
| 4 | Disconnect internet, test | "Network error" message | |

### T2.3 - Key Rotation
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Add 3 keys, exhaust quota on first | Auto-rotates to second key | |
| 2 | Verify in statistics | First key shows "cooldown" status | |
| 3 | Wait or mock 24hr cooldown | Key becomes active again | |
| 4 | All keys exhausted | "All API keys exhausted" error | |

### T2.4 - Statistics
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Stella → API Statistics | Statistics dialog shows | |
| 2 | After 10 API calls | Request count increases | |
| 3 | After failed call | Failure count increases | |
| 4 | Token usage | Token count reasonable | |

---

## 🌐 Phase 3: Translation Feature Tests

### T3.1 - Single Note Translation (Editor)
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Open note editor | Stella buttons visible in toolbar | |
| 2 | Click 🌐 Translate button | Translation runs with progress | |
| 3 | Check Translation field | Korean translation appears | |
| 4 | Use Ctrl+Shift+T shortcut | Same result as button | |
| 5 | Translate already-translated note | Skips or overwrites per config | |

### T3.2 - Batch Translation (Browser)
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Open card browser | Browser window opens | |
| 2 | Select 10 notes | Notes highlighted | |
| 3 | Stella → Translate Selected Notes | Progress dialog appears | |
| 4 | Watch progress | Count updates correctly | |
| 5 | Click Cancel mid-process | Operation stops, partial results saved | |
| 6 | Check results | Completed notes have translations | |

### T3.3 - Translation Edge Cases
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Translate empty Word field | Graceful skip with warning | |
| 2 | Translate `<b>bold text</b>` | HTML stripped, text translated | |
| 3 | Translate Japanese word "猫" | Korean translation appears | |
| 4 | Translate German "Schmetterling" | Korean translation appears | |
| 5 | Translate emoji "🎉" | Handled gracefully (skip or describe) | |
| 6 | Very long word (100+ chars) | Truncated or handled | |
| 7 | Word with "quotes" and 'apostrophes' | No JSON parsing errors | |

### T3.4 - Translation Quality
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Translate "ephemeral" | Context-aware Korean (덧없는, 일시적인) | |
| 2 | Check for Natural Korean | No awkward Google Translate style | |
| 3 | Verify formatting | Clean text, no markdown artifacts | |

---

## ✏️ Phase 4: Sentence Generation Tests

### T4.1 - Single Sentence Generation (Editor)
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Click ✏️ Sentence button | Generation runs with progress | |
| 2 | Check Sentence field | English sentence with word appears | |
| 3 | Check SentenceTranslation | Korean translation appears | |
| 4 | Verify word highlighting | Target word is **bold** or highlighted | |
| 5 | Use Ctrl+Shift+S shortcut | Same result as button | |

### T4.2 - Batch Sentence Generation
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Select 10 notes in browser | Notes selected | |
| 2 | Stella → Generate Sentences | Progress dialog appears | |
| 3 | Pause operation | Operation pauses, resumes correctly | |
| 4 | Cancel operation | Partial results saved | |

### T4.3 - Sentence Edge Cases
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Generate for empty field | Graceful skip | |
| 2 | Word is a phrase "kick the bucket" | Sentence uses full idiom | |
| 3 | Word with special chars | Sentence handles correctly | |
| 4 | Generate for same word twice | Different sentence each time | |

### T4.4 - Sentence Quality
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Check grammar | Sentence is grammatically correct | |
| 2 | Check difficulty level | Matches configured level (Normal) | |
| 3 | Check context usage | Word used in natural context | |
| 4 | Translation accuracy | Korean translation is natural | |

---

## 🖼️ Phase 5: Image Generation Tests

### T5.1 - Single Image Generation (Editor)
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Click 🖼️ Image button | Generation runs (may take 5-10s) | |
| 2 | Check Image field | `<img src="filename.png">` appears | |
| 3 | Preview card | Image displays correctly | |
| 4 | Use Ctrl+Shift+I shortcut | Same result as button | |
| 5 | Check media folder | Image file exists | |

### T5.2 - Image Quality
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Image dimensions | Within 800x600 or configured max | |
| 2 | File size | Reasonable (<2MB) | |
| 3 | Visual relevance | Image represents the word | |
| 4 | Style consistency | Matches configured preset | |

### T5.3 - Image Edge Cases
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Generate for abstract word "ephemeral" | Creative visual representation | |
| 2 | Generate for concrete word "cat" | Clear cat image | |
| 3 | Generate for offensive word (test blocked) | API refuses, graceful error | |
| 4 | Regenerate for same word | Different image generated | |
| 5 | Empty word field | Graceful skip with message | |

### T5.4 - Media Management
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Check filename format | `stella_word_YYYYMMDD.png` | |
| 2 | Duplicate word same day | `stella_word_YYYYMMDD_2.png` | |
| 3 | Check media folder cleanup | Old temp files removed | |
| 4 | Sync with AnkiWeb | Images sync correctly | |

---

## 🎛️ Phase 6: UI & UX Tests

### T6.1 - Editor Toolbar
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Open Add note window | Stella buttons appear | |
| 2 | Open Edit note window | Stella buttons appear | |
| 3 | Hover over buttons | Tooltips show shortcuts | |
| 4 | Click ⚙️ menu button | Quick menu appears | |

### T6.2 - Keyboard Shortcuts
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Ctrl+Shift+T | Translate triggers | |
| 2 | Ctrl+Shift+S | Sentence triggers | |
| 3 | Ctrl+Shift+I | Image triggers | |
| 4 | Check for conflicts | No conflict with Anki defaults | |

### T6.3 - Progress Dialog
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Start batch operation | Progress dialog shows | |
| 2 | Progress bar | Updates smoothly | |
| 3 | Current item display | Shows current word | |
| 4 | Success/failure counters | Update correctly | |
| 5 | Pause button | Pauses, changes to Resume | |
| 6 | Cancel button | Cancels, dialog closes | |
| 7 | Complete | Dialog closes, results shown | |

### T6.4 - Menu Structure
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Stella menu exists | Menu visible in menubar | |
| 2 | All menu items work | Each item triggers correctly | |
| 3 | Menu icons | Emojis display correctly | |
| 4 | About dialog | Version info displays | |

---

## ⚡ Phase 7: Performance Tests

### T7.1 - Startup Performance
| Metric | Target | Actual | Pass/Fail |
|--------|--------|--------|-----------|
| Add-on load time | < 2 seconds | | |
| Menu creation | < 500ms | | |
| No UI freeze | Yes | | |

### T7.2 - Batch Operation Performance
| Operation | Notes | Target Time | Actual | Pass/Fail |
|-----------|-------|-------------|--------|-----------|
| Translate | 10 | < 30 seconds | | |
| Translate | 100 | < 5 minutes | | |
| Sentences | 10 | < 30 seconds | | |
| Images | 10 | < 2 minutes | | |

### T7.3 - Memory Usage
| Test | Expected | Actual | Pass/Fail |
|------|----------|--------|-----------|
| Baseline (no operation) | < 50MB added | | |
| During batch (100 notes) | < 200MB peak | | |
| After operation complete | Returns to baseline | | |

---

## 🛡️ Phase 8: Error Handling Tests

### T8.1 - Network Errors
| Scenario | Expected Behavior | Pass/Fail |
|----------|-------------------|-----------|
| Internet disconnected | "Network error" message, no crash | |
| API timeout (slow connection) | Retry or timeout message | |
| API returns 500 error | Friendly error message | |

### T8.2 - API Errors
| Scenario | Expected Behavior | Pass/Fail |
|----------|-------------------|-----------|
| Invalid API key | "Authentication failed" | |
| Rate limit (429) | Key rotation, retry | |
| Quota exceeded | Key rotation or "quota" message | |
| Safety filter triggered | "Content blocked" message | |

### T8.3 - Data Errors
| Scenario | Expected Behavior | Pass/Fail |
|----------|-------------------|-----------|
| Malformed API response | Graceful fallback | |
| Empty response | Skip with warning | |
| Unicode issues | Handle all Unicode | |
| JSON parsing error | Fallback, no crash | |

### T8.4 - User Errors
| Scenario | Expected Behavior | Pass/Fail |
|----------|-------------------|-----------|
| No notes selected | "Please select notes" message | |
| Field doesn't exist | "Field not found" message | |
| No API key configured | Prompt to add key | |

---

## 🔄 Phase 9: Integration Tests

### T9.1 - All Features Together
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Translate, then Sentence, then Image | All three work sequentially | |
| 2 | Run all three on batch | Each feature completes | |
| 3 | Undo operations (Ctrl+Z) | Changes can be undone | |

### T9.2 - Anki Operations
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Sync to AnkiWeb | All data syncs correctly | |
| 2 | Check database | No corruption | |
| 3 | Export deck with images | Images included | |
| 4 | Import on another device | Everything works | |

### T9.3 - Add-on Compatibility
| Test | Expected | Pass/Fail |
|------|----------|-----------|
| With Review Heatmap | No conflicts | |
| With Image Occlusion | No conflicts | |
| With AwesomeTTS | No conflicts | |
| With AnkiConnect | No conflicts | |

---

## 🔁 Phase 10: Regression Tests

### T10.1 - After Configuration Change
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Change target language | New translations use new language | |
| 2 | Change field mappings | Features use new fields | |
| 3 | Disable a feature | Feature button/shortcut disabled | |

### T10.2 - After Anki Restart
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Restart Anki | Add-on loads correctly | |
| 2 | Check API keys | Keys persist | |
| 3 | Check statistics | Stats persist | |
| 4 | Run operations | All features work | |

### T10.3 - After Update
| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Update add-on files | No errors on restart | |
| 2 | Config migration | Old config upgraded | |
| 3 | Data preserved | Previous translations remain | |

---

## 📊 Test Results Summary

### Overall Status
| Phase | Tests | Passed | Failed | Blocked |
|-------|-------|--------|--------|---------|
| Installation | | | | |
| API Keys | | | | |
| Translation | | | | |
| Sentences | | | | |
| Images | | | | |
| UI/UX | | | | |
| Performance | | | | |
| Error Handling | | | | |
| Integration | | | | |
| Regression | | | | |
| **TOTAL** | | | | |

### Critical Bugs Found
| ID | Description | Severity | Status |
|----|-------------|----------|--------|
| | | | |

### Recommendations
- [ ] 
- [ ] 
- [ ] 

---

## 🔧 Test Environment Notes

```
Anki Version: 
OS: 
Date: 
Tester: 
Add-on Version: 
```

---

## 📝 Bug Report Template

When reporting bugs, include:

```markdown
## Bug Report

**Environment:**
- Anki Version: 
- OS: 
- Stella Version: 

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Result:**


**Actual Result:**


**Error Message (if any):**
```

**Screenshots:**
(attach if applicable)

**Console Logs:**
```
(paste from Anki debug console)
```

**Severity:** Critical / High / Medium / Low

**Reproducibility:** Always / Sometimes / Rarely
```

---

## ✅ Sign-off Checklist

Before release, all items must be checked:

- [ ] All critical and high-severity bugs fixed
- [ ] All Phase 1-10 tests pass
- [ ] Performance targets met
- [ ] Documentation updated
- [ ] Tested on Windows, macOS, Linux
- [ ] Tested on Anki 2.1.50, 2.1.60, 23.10+
- [ ] User guide created
- [ ] Release notes prepared

**QA Sign-off:** _________________ Date: _________

**Developer Sign-off:** _________________ Date: _________

---

*This QA testing guide ensures comprehensive coverage of Stella Anki Tools functionality before release.*
