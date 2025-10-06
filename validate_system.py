"""
UFDR System Validation Script
Checks if all components are working correctly
"""

import os
import sys
import importlib.util

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description}")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}")
        return True
    except ImportError as e:
        print(f"❌ {description} - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {description} - {e}")
        return False

def main():
    print("🔍 UFDR SYSTEM VALIDATION")
    print("=" * 50)
    
    all_good = True
    
    # Check core files
    print("\n📁 CORE FILES:")
    files_to_check = [
        ("models.py", "Database models"),
        ("ai_analyzer.py", "AI analyzer module"),
        ("preanalyzer.py", "Pre-analyzer system"),
        ("core_agent.py", "Query processing engine"),
        ("ingest_ufdr.py", "Data ingestion script"),
        ("streamlit_app.py", "Streamlit web interface"),
        ("run_streamlit.py", "Streamlit launcher"),
        ("demo_complete.py", "Complete workflow demo"),
        ("config.py", "Configuration file"),
        ("requirements.txt", "Dependencies list"),
        ("README.md", "Documentation")
    ]
    
    for filepath, description in files_to_check:
        if not check_file(filepath, description):
            all_good = False
    
    # Check sample data
    print("\n📊 SAMPLE DATA:")
    data_files = [
        ("fake_ufdr", "Sample UFDR folder"),
        ("fake_ufdr/incidents.json", "Sample incidents"),
        ("fake_ufdr/messages/messages.json", "Sample messages"),
        ("fake_ufdr/calls/call_log.json", "Sample calls"),
        ("fake_ufdr/contacts/contacts.json", "Sample contacts"),
        ("fake_ufdr/media/images", "Sample images folder")
    ]
    
    for filepath, description in data_files:
        if not check_file(filepath, description):
            all_good = False
    
    # Check Python imports
    print("\n🐍 PYTHON MODULES:")
    modules_to_check = [
        ("sqlmodel", "SQLModel ORM"),
        ("pandas", "Pandas data analysis"),
        ("streamlit", "Streamlit web framework"),
        ("google.genai", "Google Generative AI"),
        ("PIL", "Pillow image processing"),
        ("plotly", "Plotly visualization")
    ]
    
    for module, description in modules_to_check:
        if not check_import(module, description):
            all_good = False
    
    # Check API key
    print("\n🔑 API CONFIGURATION:")
    api_key_found = False
    
    if os.path.exists("apikey.txt"):
        try:
            with open("apikey.txt", "r") as f:
                key = f.read().strip()
                if key and len(key) > 10:
                    print("✅ API key found in apikey.txt")
                    api_key_found = True
                else:
                    print("❌ apikey.txt exists but appears empty")
        except Exception as e:
            print(f"❌ Could not read apikey.txt: {e}")
    else:
        print("❌ apikey.txt not found")
    
    if not api_key_found:
        try:
            from config import GEMINI_API_KEY
            if GEMINI_API_KEY and GEMINI_API_KEY != "your_actual_api_key_here":
                print("✅ API key found in config.py")
                api_key_found = True
        except:
            pass
    
    if not api_key_found:
        print("❌ No valid API key found")
        all_good = False
    
    # Test AI analyzer
    print("\n🤖 AI SYSTEM:")
    try:
        from ai_analyzer import AIAnalyzer
        ai = AIAnalyzer()
        if ai.is_available():
            print("✅ AI analyzer initialized and ready")
        else:
            print("❌ AI analyzer initialization failed")
            all_good = False
    except Exception as e:
        print(f"❌ AI analyzer error: {e}")
        all_good = False
    
    # Check if analysis has been run
    print("\n📋 ANALYSIS STATUS:")
    if os.path.exists("ufdr.db"):
        print("✅ Database exists (data has been ingested)")
    else:
        print("⚠️  Database not found (run: python ingest_ufdr.py fake_ufdr)")
    
    if os.path.exists("analysis.txt"):
        try:
            with open("analysis.txt", "r", encoding="utf-8") as f:
                content = f.read()
                word_count = len(content.split())
                print(f"✅ Analysis report exists ({word_count:,} words)")
        except:
            print("⚠️  Analysis report exists but could not read it")
    else:
        print("⚠️  Analysis report not found (run: python preanalyzer.py)")
    
    # Final summary
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 SYSTEM VALIDATION PASSED!")
        print("🚀 Your UFDR system is ready to use!")
        print()
        print("Next steps:")
        print("1. If database missing: python ingest_ufdr.py fake_ufdr")
        print("2. If analysis missing: python preanalyzer.py")
        print("3. Launch interface: python run_streamlit.py")
    else:
        print("⚠️  SYSTEM VALIDATION ISSUES FOUND")
        print("Please fix the issues marked with ❌ above")
        print()
        print("Common fixes:")
        print("• Install dependencies: pip install -r requirements.txt")
        print("• Add API key to apikey.txt file")
        print("• Get API key from: https://aistudio.google.com/app/apikey")
    
    print("=" * 50)

if __name__ == "__main__":
    main()