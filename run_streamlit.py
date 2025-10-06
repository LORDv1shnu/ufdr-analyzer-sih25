"""
UFDR Streamlit App Launcher
Easy way to start the forensic analysis web interface
"""

import subprocess
import sys
import os

def main():
    print("🚀 UFDR AI Investigation Interface")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("streamlit_app.py"):
        print("❌ streamlit_app.py not found!")
        print("Make sure you're running this from the ufdr_mvp directory")
        return
    
    # Check if analysis.txt exists
    if not os.path.exists("analysis.txt"):
        print("⚠️  Warning: analysis.txt not found!")
        print("Run 'python preanalyzer.py' first to generate the analysis report")
        print()
        
        response = input("Continue anyway? (y/n): ").lower().strip()
        if response != 'y':
            print("Exiting...")
            return
    
    print("🌐 Starting Streamlit web interface...")
    print("📱 The app will open in your browser automatically")
    print("🔍 Ready for AI-powered forensic investigation queries!")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--theme.primaryColor", "#1f4e79",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f8ff",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit server stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        print("💡 Try running manually: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()