"""
UFDR Pre-Analyzer - Comprehensive AI Analysis System
Generates complete analysis report by sending all data to AI in bulk
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any
from sqlmodel import Session, select, create_engine
from models import Message, Contact, Call, MediaFile
from ai_analyzer import AIAnalyzer

class UFDRPreAnalyzer:
    """
    Pre-analyzes all UFDR data and creates comprehensive analysis.txt report
    """
    
    def __init__(self, analysis_file: str = "analysis.txt"):
        self.analysis_file = analysis_file
        self.ai_analyzer = AIAnalyzer()
        self.engine = create_engine("sqlite:///ufdr.db", echo=False)
        
    def run_complete_analysis(self, skip_images: bool = False):
        """
        Run complete analysis of all UFDR data
        """
        print("🚀 UFDR PRE-ANALYZER - Starting Complete Analysis")
        print("=" * 60)
        
        if not self.ai_analyzer.is_available():
            print("❌ AI Analyzer not available! Please configure your Gemini API key in config.py")
            print("   Get your API key from: https://aistudio.google.com/app/apikey")
            return False
        
        # Initialize analysis report
        report_lines = []
        report_lines.append("=== UFDR COMPREHENSIVE AI ANALYSIS REPORT ===\n")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("=" * 60 + "\n\n")
        
        with Session(self.engine) as session:
            # Step 1: Analyze ALL text data at once
            print("📊 Step 1: Analyzing ALL text data with AI...")
            report_lines.extend(self._analyze_all_text_data(session))
            
            # Step 2: Ask user about image analysis if not specified
            if not skip_images:
                # Check how many images we have
                media_files = session.exec(select(MediaFile)).all()
                image_files = [mf for mf in media_files if mf.file_type == "image"]
                
                if image_files:
                    print(f"\n🖼️ Found {len(image_files)} images for analysis.")
                    print("⚠️ Image analysis may take time and API calls...")
                    
                    while True:
                        user_choice = input("Do you want to proceed with image analysis? (y/n): ").lower().strip()
                        if user_choice in ['y', 'yes']:
                            print("🖼️ Step 2: Analyzing images individually...")
                            report_lines.extend(self._analyze_all_images(session))
                            break
                        elif user_choice in ['n', 'no']:
                            print("⏭️ Step 2: Skipping image analysis (user choice)")
                            report_lines.append("### IMAGE ANALYSIS ###\n")
                            report_lines.append("Image analysis was skipped by user choice.\n\n")
                            break
                        else:
                            print("Please enter 'y' for yes or 'n' for no.")
                else:
                    print("⏭️ Step 2: No images found to analyze")
                    report_lines.append("### IMAGE ANALYSIS ###\n")
                    report_lines.append("No image files found in database.\n\n")
            else:
                print("⏭️ Step 2: Skipping image analysis (command line flag)")
                report_lines.append("### IMAGE ANALYSIS ###\n")
                report_lines.append("Image analysis was skipped by command line flag.\n\n")
        
        # Write complete report to analysis.txt
        report_content = "".join(report_lines)
        
        try:
            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ Complete analysis saved to: {self.analysis_file}")
            print(f"📄 Report size: {len(report_content):,} characters")
            return True
            
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False
    
    def _analyze_all_text_data(self, session) -> List[str]:
        """Send ALL text data to AI for comprehensive bulk analysis"""
        report = []
        
        # Get all data
        messages = session.exec(select(Message)).all()
        calls = session.exec(select(Call)).all()
        contacts = session.exec(select(Contact)).all()
        
        print(f"   📩 Messages: {len(messages)}")
        print(f"   📞 Calls: {len(calls)}")
        print(f"   👥 Contacts: {len(contacts)}")
        
        # Create comprehensive data summary for AI
        data_summary = self._create_comprehensive_data_summary(messages, calls, contacts)
        
        # Send to AI for analysis
        print("   🤖 Sending all data to AI for analysis...")
        
        prompt = f"""
        You are a forensic analyst examining UFDR (Universal Forensic Data Report) data for criminal investigation.
        
        Analyze this complete dataset and provide comprehensive forensic insights:
        
        {data_summary}
        
        Please provide a detailed forensic analysis report including:
        
        1. EXECUTIVE SUMMARY - Key findings and overall assessment
        2. CRIMINAL ACTIVITY INDICATORS - Any signs of illegal activities
        3. COMMUNICATION PATTERNS - Suspicious communication behaviors
        4. NETWORK ANALYSIS - Key players and relationships
        5. TEMPORAL ANALYSIS - Time-based patterns and anomalies
        6. RISK ASSESSMENT - Overall threat level and concerns
        7. EVIDENCE HIGHLIGHTS - Most significant findings
        8. INVESTIGATIVE RECOMMENDATIONS - Next steps for investigation
        
        Focus on forensic value and criminal investigation aspects.
        """
        
        try:
            if self.ai_analyzer.client:
                response = self.ai_analyzer.client.models.generate_content(
                    model=self.ai_analyzer.model_name,
                    contents=prompt
                )
                
                ai_analysis = response.text if hasattr(response, 'text') else str(response)
                
                report.append("### COMPREHENSIVE AI ANALYSIS OF ALL TEXT DATA ###\n\n")
                report.append(ai_analysis)
                report.append("\n\n" + "=" * 60 + "\n\n")
                
                print("   ✅ AI analysis complete!")
                
        except Exception as e:
            print(f"   ❌ AI analysis failed: {e}")
            report.append("### COMPREHENSIVE AI ANALYSIS ###\n\n")
            report.append(f"AI analysis failed: {e}\n\n")
            report.append("=" * 60 + "\n\n")
        
        return report
    
    def _analyze_all_images(self, session) -> List[str]:
        """Analyze each image individually and append to report"""
        report = []
        
        # Get all media files
        media_files = session.exec(select(MediaFile)).all()
        image_files = [mf for mf in media_files if mf.file_type == "image"]
        
        print(f"   🖼️ Found {len(image_files)} images to analyze")
        
        report.append("### INDIVIDUAL IMAGE ANALYSIS ###\n\n")
        
        if not image_files:
            report.append("No image files found in database.\n\n")
            return report
        
        analyzed_count = 0
        
        for i, media_file in enumerate(image_files, 1):
            print(f"   📸 Analyzing image {i}/{len(image_files)}: {media_file.filename}")
            
            # Image file info
            report.append(f"--- IMAGE {i}: {media_file.filename} ---\n")
            report.append(f"File Path: {media_file.file_path}\n")
            report.append(f"File Type: {media_file.file_type}\n")
            
            # Check if file actually exists
            full_path = os.path.join("fake_ufdr", media_file.file_path)
            if os.path.exists(full_path):
                # Analyze with AI
                try:
                    analysis = self.ai_analyzer.analyze_image(full_path)
                    
                    report.append(f"AI Description: {analysis.get('ai_description', 'N/A')}\n")
                    report.append(f"Detected Objects: {analysis.get('detected_objects', '[]')}\n")
                    report.append(f"Contains Text: {analysis.get('contains_text', 'N/A')}\n")
                    report.append(f"Faces Detected: {analysis.get('faces_detected', 0)}\n")
                    report.append(f"Risk Level: {analysis.get('risk_level', 'unknown')}\n")
                    report.append(f"Tags: {analysis.get('tags', '[]')}\n")
                    
                    analyzed_count += 1
                    
                except Exception as e:
                    report.append(f"Analysis Error: {e}\n")
            else:
                report.append("File Status: File not found on disk\n")
            
            report.append("\n")
        
        report.append(f"📊 IMAGE ANALYSIS SUMMARY: {analyzed_count}/{len(image_files)} images successfully analyzed\n\n")
        report.append("=" * 60 + "\n\n")
        
        print(f"   ✅ Image analysis complete! {analyzed_count}/{len(image_files)} analyzed")
        
        return report
    
    def _create_comprehensive_data_summary(self, messages, calls, contacts) -> str:
        """Create comprehensive summary of all data for AI analysis"""
        summary = []
        
        # Messages analysis
        summary.append(f"=== MESSAGES DATA ({len(messages)} total) ===\n")
        
        if messages:
            # Sample recent messages
            recent_messages = sorted(messages, key=lambda x: x.timestamp, reverse=True)[:20]
            summary.append("RECENT MESSAGES SAMPLE:\n")
            for msg in recent_messages:
                summary.append(f"[{msg.timestamp}] {msg.sender} → {msg.receiver}: {msg.body}\n")
            
            # Message statistics
            senders = set(msg.sender for msg in messages)
            summary.append(f"\nMESSAGE STATISTICS:\n")
            summary.append(f"Total Messages: {len(messages)}\n")
            summary.append(f"Unique Senders: {len(senders)}\n")
            summary.append(f"Top Senders: {', '.join(list(senders)[:10])}\n")
        
        summary.append("\n")
        
        # Calls analysis
        summary.append(f"=== CALLS DATA ({len(calls)} total) ===\n")
        
        if calls:
            # Sample recent calls
            recent_calls = sorted(calls, key=lambda x: x.timestamp, reverse=True)[:20]
            summary.append("RECENT CALLS SAMPLE:\n")
            for call in recent_calls:
                summary.append(f"[{call.timestamp}] {call.caller} → {call.callee} ({call.duration}s, {call.type})\n")
            
            # Call statistics
            callers = set(call.caller for call in calls)
            summary.append(f"\nCALL STATISTICS:\n")
            summary.append(f"Total Calls: {len(calls)}\n")
            summary.append(f"Unique Callers: {len(callers)}\n")
            summary.append(f"Average Duration: {sum(call.duration for call in calls) / len(calls):.1f}s\n")
        
        summary.append("\n")
        
        # Contacts analysis
        summary.append(f"=== CONTACTS DATA ({len(contacts)} total) ===\n")
        
        if contacts:
            summary.append("CONTACT LIST:\n")
            for contact in contacts:
                summary.append(f"{contact.name} - {contact.phone} ({contact.email or 'No email'})\n")
        
        summary.append("\n")
        
        return "".join(summary)

def main():
    """Main function with command line interface"""
    print("🚀 UFDR PRE-ANALYZER")
    print("=" * 40)
    
    # Check for skip images flag
    skip_images = "--skip-images" in sys.argv
    
    if skip_images:
        print("⚠️ Image analysis will be SKIPPED")
    
    # Check if database exists
    if not os.path.exists("ufdr.db"):
        print("❌ Database not found! Please run data ingestion first:")
        print("   python ingest_ufdr.py fake_ufdr")
        return
    
    # Run analysis
    analyzer = UFDRPreAnalyzer()
    success = analyzer.run_complete_analysis(skip_images=skip_images)
    
    if success:
        print("\n🎉 PRE-ANALYSIS COMPLETE!")
        print(f"📄 Full report saved to: analysis.txt")
        print("💡 You can now use this comprehensive analysis for any queries!")
    else:
        print("\n❌ Analysis failed. Please check your API key configuration.")

if __name__ == "__main__":
    main()