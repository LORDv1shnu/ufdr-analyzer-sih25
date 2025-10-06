import json, os, sys
from sqlmodel import SQLModel, create_engine, Session
from models import Contact, Message, Call, MediaFile
from ai_analyzer import AIAnalyzer

DB_URL = "sqlite:///ufdr.db"
engine = create_engine(DB_URL, echo=False)
SQLModel.metadata.create_all(engine)

# Initialize AI analyzer
ai_analyzer = AIAnalyzer()

def ingest_from_folder(folder):
    with Session(engine) as sess:
        # Contacts
        with open(os.path.join(folder, "contacts/contacts.json")) as f:
            for c in json.load(f):
                sess.add(Contact(**{k: c.get(k) for k in ["name", "phone", "email", "notes"]}))

        # Messages with AI analysis (smart sampling to avoid API limits)
        print("📩 Processing messages with AI analysis...")
        with open(os.path.join(folder, "messages/messages.json")) as f:
            messages_data = json.load(f)
            total_messages = len(messages_data)
            
            # Process suspicious messages first, then sample others
            suspicious_keywords = ["weed", "drugs", "cash", "fake", "illegal", "burner", "delivery", "package"]
            
            analyzed_count = 0
            for i, m in enumerate(messages_data):
                message_body = m.get("body", "")
                
                # Determine if this message should get AI analysis
                should_analyze = False
                if message_body and ai_analyzer.is_available():
                    # Always analyze suspicious messages
                    if any(keyword in message_body.lower() for keyword in suspicious_keywords):
                        should_analyze = True
                    # Sample other messages (every 10th)
                    elif i % 10 == 0 and analyzed_count < 50:  # Limit to 50 AI calls total
                        should_analyze = True
                
                ai_analysis = {}
                if should_analyze:
                    analyzed_count += 1
                    print(f"🤖 AI analyzing message {analyzed_count} (#{i+1}/{total_messages})")
                    ai_analysis = ai_analyzer.analyze_message_content(message_body)
                
                message = Message(
                    timestamp=m.get("timestamp"),
                    sender=m.get("sender"),
                    receiver=m.get("receiver"),
                    body=message_body,
                    source=m.get("source"),
                    attachments=",".join(m.get("attachments", [])),
                    # AI-enhanced fields
                    sentiment_score=ai_analysis.get("sentiment_score"),
                    risk_level=ai_analysis.get("risk_level", "unknown"),
                    topics=ai_analysis.get("topics"),
                    ai_summary=ai_analysis.get("ai_summary")
                )
                sess.add(message)
            
            print(f"✅ Processed {total_messages} messages, {analyzed_count} with AI analysis")

        # Calls
        with open(os.path.join(folder, "calls/call_log.json")) as f:
            for c in json.load(f):
                sess.add(Call(
                    timestamp=c.get("timestamp"),
                    caller=c.get("caller"),
                    callee=c.get("callee"),
                    duration=c.get("duration"),
                    type=c.get("type")
                ))

        sess.commit()
        print("✅ Basic ingestion complete — ufdr.db created")
        
        # Process media files if available
        print("🖼️  Processing media files...")
        try:
            from media_processor import process_media_files
            process_media_files(folder)
        except Exception as e:
            print(f"⚠️  Media processing failed: {e}")
        
        # Create comprehensive AI pre-analysis report
        print("🤖 Creating comprehensive AI pre-analysis report...")
        try:
            from ai_preanalysis import UFDRPreAnalyzer
            pre_analyzer = UFDRPreAnalyzer()
            analysis_file = pre_analyzer.create_comprehensive_analysis()
            print(f"✅ AI pre-analysis report created: {analysis_file}")
        except Exception as e:
            print(f"⚠️  Pre-analysis creation failed: {e}")
        
        print("🎉 Complete ingestion with AI analysis and pre-analysis finished!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_ufdr.py <path_to_fake_ufdr_folder>")
        sys.exit(1)
    ingest_from_folder(sys.argv[1])
