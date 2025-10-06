"""
Complete UFDR Workflow Demo with Streamlit
Shows the full process from data ingestion to AI querying
"""

import os
import subprocess
import sys
import time

def run_command(command, description):
    """Run a command with description"""
    print(f"\n🚀 {description}")
    print("=" * 60)
    print(f"Running: {command}")
    print("-" * 40)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 CHECKING SYSTEM REQUIREMENTS")
    print("=" * 60)
    
    checks = []
    
    # Check Python
    print(f"✅ Python version: {sys.version}")
    
    # Check if required files exist
    required_files = [
        "requirements.txt",
        "ingest_ufdr.py", 
        "preanalyzer.py",
        "streamlit_app.py",
        "fake_ufdr"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
            checks.append(True)
        else:
            print(f"❌ {file} missing")
            checks.append(False)
    
    # Check API key
    api_key_found = False
    if os.path.exists("apikey.txt"):
        try:
            with open("apikey.txt", "r") as f:
                key = f.read().strip()
                if key and len(key) > 10:
                    print("✅ API key found in apikey.txt")
                    api_key_found = True
                else:
                    print("⚠️  apikey.txt exists but appears empty")
        except:
            print("⚠️  Could not read apikey.txt")
    
    if not api_key_found:
        print("⚠️  API key not found in apikey.txt")
        print("🔗 Get your API key from: https://aistudio.google.com/app/apikey")
        
    return all(checks) and api_key_found

def main():
    print("🎯 UFDR COMPLETE WORKFLOW DEMO")
    print("📊 From Data Ingestion to AI Investigation")
    print("=" * 60)
    
    if not check_requirements():
        print("\n❌ System requirements not met. Please fix the issues above.")
        return
    
    print("\n📋 WORKFLOW STEPS:")
    print("1. Install dependencies")
    print("2. Ingest sample UFDR data")
    print("3. Run comprehensive pre-analysis")
    print("4. Launch AI investigation interface")
    print()
    
    response = input("🚀 Start complete workflow? (y/n): ").lower().strip()
    if response != 'y':
        print("👋 Workflow cancelled")
        return
    
    # Step 1: Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return
    
    # Step 2: Ingest data
    if not run_command("python ingest_ufdr.py fake_ufdr", "Ingesting sample UFDR data"):
        return
    
    # Step 3: Pre-analysis
    print("\n📊 Running comprehensive pre-analysis...")
    print("⚠️  This may take a few minutes depending on your internet connection")
    print("🔄 The AI will analyze all messages, calls, contacts, and images")
    time.sleep(2)
    
    if not run_command("python preanalyzer.py --skip-images", "Running AI pre-analysis (skipping images for speed)"):
        print("\n💡 If this failed, try:")
        print("   - Check your API key in apikey.txt")
        print("   - Ensure you have internet connection")
        print("   - Verify your Gemini API key is valid")
        return
    
    # Check if analysis was successful
    if not os.path.exists("analysis.txt"):
        print("❌ Analysis file not generated. Please check the pre-analyzer output above.")
        return
    
    # Show analysis info
    try:
        with open("analysis.txt", "r", encoding="utf-8") as f:
            content = f.read()
            word_count = len(content.split())
            print(f"📄 Analysis report generated: {word_count:,} words")
    except:
        pass
    
    # Step 4: Launch Streamlit
    print("\n🌐 LAUNCHING AI INVESTIGATION INTERFACE")
    print("=" * 60)
    print("🎯 The Streamlit web interface will open in your browser")
    print("🔍 You can now ask AI investigation questions like:")
    print("   • 'What are all the suspicious activities you could find?'")
    print("   • 'Who are the main suspects in this case?'")
    print("   • 'What evidence suggests criminal activity?'")
    print("   • 'What are the most concerning findings?'")
    print()
    print("💡 The AI will act as a Senior Investigation Officer")
    print("📋 All responses will be based on the forensic analysis")
    print()
    print("🛑 Press Ctrl+C in the terminal to stop the server when done")
    print("=" * 60)
    
    time.sleep(3)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--theme.primaryColor", "#1f4e79",
            "--theme.backgroundColor", "#ffffff", 
            "--theme.secondaryBackgroundColor", "#f0f8ff"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 WORKFLOW COMPLETE!")
        print("🎉 You have successfully:")
        print("   ✅ Ingested UFDR data")
        print("   ✅ Generated AI analysis report")
        print("   ✅ Used the AI investigation interface")
        print()
        print("📁 Files created:")
        print("   📄 ufdr.db - Database with all forensic data")
        print("   📊 analysis.txt - Comprehensive AI analysis report")
        print()
        print("🔄 You can run 'python run_streamlit.py' anytime to restart the interface")

if __name__ == "__main__":
    main()