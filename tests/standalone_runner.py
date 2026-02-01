import sys
import os
import json
from unittest.mock import MagicMock

# ==========================================
# 1. Mock Anki Environment (Must be first)
# ==========================================
# This allows us to import modules that depend on 'aqt' or 'anki'
# without actually running inside Anki.

mock_aqt = MagicMock()
mock_anki = MagicMock()

# Define structure for aqt.mw.addonManager.getConfig
mock_config = {"gemini_api_key": "test_key"}
mock_mw = MagicMock()
mock_mw.addonManager.getConfig.return_value = mock_config
mock_mw.app.version = "2.1.66-mock"
mock_mw.version = "2.1.66-mock" # Some addons check this

mock_aqt.mw = mock_mw

sys.modules['aqt'] = mock_aqt
sys.modules['aqt.qt'] = MagicMock()
sys.modules['aqt.utils'] = MagicMock()
sys.modules['aqt.operations'] = MagicMock()
sys.modules['anki'] = mock_anki
sys.modules['anki.collection'] = MagicMock()
sys.modules['anki.notes'] = MagicMock()

# ==========================================
# 2. Setup Paths
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
addon_dir = os.path.dirname(current_dir)

# Add addon root to path
if addon_dir not in sys.path:
    sys.path.insert(0, addon_dir)

# Add lib to path (extremely important for google-generativeai)
lib_dir = os.path.join(addon_dir, 'lib')
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

# Handle google namespace
try:
    import google
    # If google is already imported, we might need to extend its path
    # But usually adding lib_dir to sys.path covers it for a fresh run
    pass 
except ImportError:
    pass

# ==========================================
# 3. Run Diagnostics
# ==========================================
if __name__ == "__main__":
    print(f"🚀 Starting Standalone Diagnostics...")
    print(f"📂 Addon Directory: {addon_dir}")
    
    try:
        from tests.diagnostics import StellaDiagnostics
        
        diag = StellaDiagnostics()
        results = diag.run_all()
        
        print("\n" + "="*50)
        print(f"📊 Final Status: {results.get('final_status')}")
        print("="*50)
        
        if results.get('final_status') == 'SUCCESS':
            print("\n✅ All systems go! The internal logic is working correctly.")
            print("Summary:")
            print(f"- Environment: OK")
            print(f"- API Connection: {results['components'].get('connection_message', 'OK')}")
            print(f"- Translation: {results['features']['translation'].get('status')}")
            print(f"- Sentence: {results['features']['sentence'].get('status')}")
            print(f"- Image: {results['features']['image'].get('status')}")
        else:
            print(f"\n❌ Failure Detected: {results.get('error')}")
            print("\nDetailed breakdown:")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("This usually means a dependency is missing from the 'lib' folder.")
        print(f"sys.path: {sys.path}")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
