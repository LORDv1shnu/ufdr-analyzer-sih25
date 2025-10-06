"""
Demo script for UFDR Pre-Analyzer
Shows the complete workflow
"""
import os
from preanalyzer import UFDRPreAnalyzer

def demo_workflow():
    print("🎯 UFDR PRE-ANALYZER DEMO")
    print("=" * 50)
    
    # Check if database exists
    if not os.path.exists("ufdr.db"):
        print("❌ Database not found! Please run:")
        print("   python ingest_ufdr.py fake_ufdr")
        return
    
    print("✅ Database found")
    print("✅ API key configured from apikey.txt")
    
    # Show what we're going to analyze
    from sqlmodel import Session, select, create_engine
    from models import Message, Contact, Call, MediaFile
    
    engine = create_engine("sqlite:///ufdr.db", echo=False)
    
    with Session(engine) as session:
        messages = session.exec(select(Message)).all()
        calls = session.exec(select(Call)).all()
        contacts = session.exec(select(Contact)).all()
        media_files = session.exec(select(MediaFile)).all()
        images = [mf for mf in media_files if mf.file_type == "image"]
        
        print(f"\n📊 DATA TO ANALYZE:")
        print(f"   📩 Messages: {len(messages)}")
        print(f"   📞 Calls: {len(calls)}")
        print(f"   👥 Contacts: {len(contacts)}")
        print(f"   🖼️ Images: {len(images)}")
    
    print(f"\n🚀 RUNNING PRE-ANALYZER...")
    print("=" * 30)
    
    # Create analyzer instance
    analyzer = UFDRPreAnalyzer()
    
    # Run with skip images for demo (to make it faster)
    success = analyzer.run_complete_analysis(skip_images=True)
    
    if success:
        print("\n🎉 DEMO COMPLETE!")
        print("📄 Check analysis.txt for the comprehensive report")
        
        # Show file size 
        if os.path.exists("analysis.txt"):
            size = os.path.getsize("analysis.txt")
            print(f"📊 Report size: {size:,} bytes")
            
            # Show first few lines
            print("\n📖 REPORT PREVIEW:")
            print("-" * 30)
            with open("analysis.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()[:10]
                for line in lines:
                    print(line.rstrip())
            print("-" * 30)
            print(f"... and {len(lines)} more lines")
        
        print("\n🌐 NEXT STEPS:")
        print("🚀 Launch AI Investigation Interface:")
        print("   python run_streamlit.py")
        print()
        print("🔍 Or use command line queries:")
        print("   python core_agent.py")
        print()
        print("💡 Try asking: 'What are all the suspicious activities you could find?'")
    else:
        print("\n❌ Demo failed. Check your API key configuration.")

if __name__ == "__main__":
    demo_workflow()