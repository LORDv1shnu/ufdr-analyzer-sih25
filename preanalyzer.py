"""
UFDR Pre-Analyzer - Comprehensive AI Analysis System
Generates complete analysis report by sending all data to AI in bulk
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any
from sqlmodel import Session, select
from models import Message, Contact, Call, MediaFile, get_engine
from ai_analyzer import AIAnalyzer

class UFDRPreAnalyzer:
    """
    Pre-analyzes all UFDR data and creates comprehensive analysis.txt report
    """
    
    def __init__(self, analysis_file: str = "analysis.txt"):
        self.analysis_file = analysis_file
        self.ai_analyzer = AIAnalyzer()
        self.engine = get_engine()
        
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
        
        # First, add raw data to report
        report.append("### RAW DATA DUMP ###\n\n")
        
        # Add all messages
        report.append(f"=== ALL MESSAGES ({len(messages)} total) ===\n")
        if messages:
            sorted_messages = sorted(messages, key=lambda x: x.timestamp)
            for i, msg in enumerate(sorted_messages, 1):
                report.append(f"MSG_{i:03d}: [{msg.timestamp}] {msg.sender} → {msg.receiver}\n")
                report.append(f"Content: {msg.body}\n")
                report.append("-" * 40 + "\n")
        
        # Add all calls
        report.append(f"\n=== ALL CALLS ({len(calls)} total) ===\n")
        if calls:
            sorted_calls = sorted(calls, key=lambda x: x.timestamp)
            for i, call in enumerate(sorted_calls, 1):
                report.append(f"CALL_{i:03d}: [{call.timestamp}] {call.caller} → {call.callee}\n")
                report.append(f"Duration: {call.duration}s | Type: {call.type}\n")
                report.append("-" * 40 + "\n")
        
        # Add all contacts
        report.append(f"\n=== ALL CONTACTS ({len(contacts)} total) ===\n")
        if contacts:
            for i, contact in enumerate(contacts, 1):
                report.append(f"CONTACT_{i:03d}: {contact.name}\n")
                report.append(f"Phone: {contact.phone}\n")
                report.append(f"Email: {contact.email or 'No email'}\n")
                report.append(f"Notes: {contact.notes or 'No notes'}\n")
                report.append("-" * 40 + "\n")
        
        report.append("\n" + "=" * 60 + "\n\n")
        
        # Create comprehensive data summary for AI
        data_summary = self._create_comprehensive_data_summary(messages, calls, contacts)
        
        # Send to AI for analysis
        print("   🤖 Sending all data to AI for analysis...")
        
        prompt = f"""
        You are a forensic analyst examining UFDR (Universal Forensic Data Report) data for comprehensive investigation.
        
        Analyze this COMPLETE dataset and provide detailed analysis of ALL information:
        
        {data_summary}
        
        Please provide a comprehensive analysis report that includes:
        
        1. COMPLETE MESSAGE ANALYSIS - Analyze EVERY message individually and identify:
           - Content themes (money, relationships, business, personal, etc.)
           - Communication patterns
           - Any concerning or notable content
           - Financial transactions or money-related discussions
           - Meeting arrangements and locations
           - Personal relationships and social connections
        
        2. COMPLETE CALL ANALYSIS - Analyze ALL call records:
           - Call frequency patterns
           - Duration analysis
           - Communication relationships
           - Time patterns
        
        3. COMPLETE CONTACT ANALYSIS - Analyze ALL contacts:
           - Relationship mapping
           - Contact categorization
           - Network connections
        
        4. COMPREHENSIVE INSIGHTS:
           - Overall communication behavior
           - Social network structure
           - Any patterns or anomalies
           - Financial or business activities mentioned
           - Personal life insights
           - Professional connections
        
        5. DETAILED FINDINGS - Document ALL significant information found, not just suspicious items
        
        IMPORTANT: Analyze and document ALL data, including normal everyday communications, financial discussions, personal conversations, business talks, etc. Do not focus only on criminal activities - provide complete forensic documentation of all digital footprints.
        """
        
        try:
            if self.ai_analyzer.client:
                response = self.ai_analyzer.client.models.generate_content(
                    model=self.ai_analyzer.model_name,
                    contents=prompt
                )
                
                ai_analysis = response.text if hasattr(response, 'text') else str(response)
                
                report.append("### COMPREHENSIVE AI ANALYSIS OF ALL DATA ###\n\n")
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
        """Create comprehensive summary of ALL data for AI analysis"""
        summary = []
        
        # Messages analysis - Include ALL messages
        summary.append(f"=== ALL MESSAGES DATA ({len(messages)} total) ===\n")
        
        if messages:
            # Include ALL messages, not just a sample
            sorted_messages = sorted(messages, key=lambda x: x.timestamp)
            summary.append("ALL MESSAGES (chronological order):\n")
            for i, msg in enumerate(sorted_messages, 1):
                summary.append(f"MSG_{i:03d}: [{msg.timestamp}] {msg.sender} → {msg.receiver}: {msg.body}\n")
            
            # Message statistics
            senders = set(msg.sender for msg in messages)
            receivers = set(msg.receiver for msg in messages)
            summary.append(f"\nMESSAGE STATISTICS:\n")
            summary.append(f"Total Messages: {len(messages)}\n")
            summary.append(f"Unique Senders: {len(senders)}\n")
            summary.append(f"Unique Receivers: {len(receivers)}\n")
            summary.append(f"All Senders: {', '.join(sorted(senders))}\n")
            summary.append(f"All Receivers: {', '.join(sorted(receivers))}\n")
        
        summary.append("\n")
        
        # Calls analysis - Include ALL calls
        summary.append(f"=== ALL CALLS DATA ({len(calls)} total) ===\n")
        
        if calls:
            # Include ALL calls, not just a sample
            sorted_calls = sorted(calls, key=lambda x: x.timestamp)
            summary.append("ALL CALLS (chronological order):\n")
            for i, call in enumerate(sorted_calls, 1):
                summary.append(f"CALL_{i:03d}: [{call.timestamp}] {call.caller} → {call.callee} ({call.duration}s, {call.type})\n")
            
            # Call statistics
            callers = set(call.caller for call in calls)
            callees = set(call.callee for call in calls)
            total_duration = sum(call.duration for call in calls)
            summary.append(f"\nCALL STATISTICS:\n")
            summary.append(f"Total Calls: {len(calls)}\n")
            summary.append(f"Unique Callers: {len(callers)}\n")
            summary.append(f"Unique Callees: {len(callees)}\n")
            summary.append(f"Total Duration: {total_duration}s ({total_duration/60:.1f} minutes)\n")
            summary.append(f"Average Duration: {total_duration / len(calls):.1f}s\n")
            summary.append(f"All Callers: {', '.join(sorted(callers))}\n")
            summary.append(f"All Callees: {', '.join(sorted(callees))}\n")
        
        summary.append("\n")
        
        # Contacts analysis - Include ALL contacts with full details
        summary.append(f"=== ALL CONTACTS DATA ({len(contacts)} total) ===\n")
        
        if contacts:
            summary.append("COMPLETE CONTACT LIST:\n")
            for i, contact in enumerate(contacts, 1):
                summary.append(f"CONTACT_{i:03d}: {contact.name}\n")
                summary.append(f"  Phone: {contact.phone}\n")
                summary.append(f"  Email: {contact.email or 'No email'}\n")
                summary.append(f"  Notes: {contact.notes or 'No notes'}\n")
                summary.append("\n")
        
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