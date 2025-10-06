import re
import os
import json
from typing import List, Dict, Any
from sqlmodel import Session, select, create_engine
from sqlalchemy import or_
from models import Message, Contact, Call, MediaFile
from ai_analyzer import AIAnalyzer
from ai_preanalysis import UFDRPreAnalyzer
import pandas as pd

# Database connection
engine = create_engine("sqlite:///ufdr.db", echo=False)

# Initialize AI analyzer and pre-analyzer
ai_analyzer = AIAnalyzer()
pre_analyzer = UFDRPreAnalyzer()

def simple_parse_query(text: str) -> Dict[str, Any]:
    """
    Rule-based parser for common forensic queries.
    This handles the most common patterns investigators use.
    """
    text_lower = text.lower()
    
    # Rule: "messages from X" or "show messages from X"
    match = re.search(r"messages from ([+\d\w\s]+)", text_lower)
    if match:
        identifier = match.group(1).strip()
        return {"action": "messages_from", "identifier": identifier}
    
    # Rule: "calls with X" or "calls from/to X"
    match = re.search(r"calls (?:with|from|to) ([+\d\w\s]+)", text_lower)
    if match:
        identifier = match.group(1).strip()
        return {"action": "calls_with", "identifier": identifier}
    
    # Rule: suspicious content detection
    if any(word in text_lower for word in ["suspicious", "illegal", "drugs", "weed", "fake"]):
        return {"action": "suspicious_messages"}
    
    # Rule: foreign numbers
    if "foreign" in text_lower and ("call" in text_lower or "number" in text_lower):
        return {"action": "foreign_calls"}
    
    # Rule: recent activity
    if "recent" in text_lower:
        if "message" in text_lower:
            return {"action": "recent_messages"}
        elif "call" in text_lower:
            return {"action": "recent_calls"}
    
    # Rule: contact search
    if "contact" in text_lower and ("named" in text_lower or "name" in text_lower):
        match = re.search(r"(?:contact|person).*?(?:named|name)\s+([a-zA-Z\s]+)", text_lower)
        if match:
            name = match.group(1).strip()
            return {"action": "find_contact", "name": name}
    
    # Rule: media/image queries
    if any(word in text_lower for word in ["image", "photo", "picture", "media"]):
        if "suspicious" in text_lower:
            return {"action": "suspicious_media"}
        elif "faces" in text_lower or "people" in text_lower:
            return {"action": "media_with_faces"}
        else:
            return {"action": "all_media"}
    
    # Rule: AI-specific queries
    if "ai analysis" in text_lower or "ai summary" in text_lower or "ai insights" in text_lower:
        return {"action": "ai_insights"}
    
    # Rule: Pattern analysis queries
    if any(word in text_lower for word in ["pattern", "analyze", "analysis"]) and "communication" in text_lower:
        return {"action": "pattern_analysis"}
    
    # Rule: Risk assessment queries
    if any(word in text_lower for word in ["risk", "threat", "dangerous"]) and any(word in text_lower for word in ["assess", "evaluation", "analysis"]):
        return {"action": "risk_assessment"}
    
    # If no rule matches but contains complex terms, let AI handle it
    complex_terms = ["between", "relationship", "connection", "network", "timeline", "trend", "unusual", "anomaly"]
    if any(term in text_lower for term in complex_terms):
        return {"action": "unknown"}  # This will trigger AI
    
    # Default: unknown query
    return {"action": "unknown"}

def execute_query(parsed: Dict[str, Any]) -> pd.DataFrame:
    """
    Execute the parsed query against the database.
    """
    with Session(engine) as session:
        
        if parsed["action"] == "messages_from":
            identifier = parsed["identifier"]
            # Try to find by phone number first, then by name
            if identifier.startswith("+") or identifier.isdigit():
                # It's likely a phone number
                messages = session.exec(select(Message).where(Message.sender == identifier)).all()
            else:
                # It's likely a name - first find the contact
                contact = session.exec(
                    select(Contact).where(Contact.name.ilike(f"%{identifier}%"))
                ).first()
                if contact and contact.phone:
                    messages = session.exec(select(Message).where(Message.sender == contact.phone)).all()
                else:
                    messages = []
            
            return pd.DataFrame([msg.model_dump() for msg in messages])
        
        elif parsed["action"] == "calls_with":
            identifier = parsed["identifier"]
            if identifier.startswith("+") or identifier.isdigit():
                # Phone number
                calls = session.exec(
                    select(Call).where(
                        or_(Call.caller == identifier, Call.callee == identifier)
                    )
                ).all()
            else:
                # Name - find contact first
                contact = session.exec(
                    select(Contact).where(Contact.name.ilike(f"%{identifier}%"))
                ).first()
                if contact and contact.phone:
                    phone = contact.phone
                    calls = session.exec(
                        select(Call).where(
                            or_(Call.caller == phone, Call.callee == phone)
                        )
                    ).all()
                else:
                    calls = []
            
            return pd.DataFrame([call.model_dump() for call in calls])
        
        elif parsed["action"] == "suspicious_messages":
            # Keywords that might indicate suspicious activity
            suspicious_keywords = [
                "weed", "cannabis", "marijuana", "drugs", "powder", "pills",
                "cash", "money", "payment", "transfer",
                "fake", "forged", "illegal", "stolen",
                "delivery", "package", "drop", "pickup",
                "burner", "disposable", "anonymous"
            ]
            
            # Build a query that searches for any of these keywords in message body
            conditions = [Message.body.ilike(f"%{keyword}%") for keyword in suspicious_keywords]
            messages = session.exec(select(Message).where(or_(*conditions))).all()
            
            return pd.DataFrame([msg.model_dump() for msg in messages])
        
        elif parsed["action"] == "foreign_calls":
            # Assuming Indian numbers start with +91, everything else is foreign
            calls = session.exec(select(Call)).all()
            foreign_calls = [
                call for call in calls 
                if call.caller and not call.caller.startswith("+91") or
                   call.callee and not call.callee.startswith("+91")
            ]
            
            return pd.DataFrame([call.model_dump() for call in foreign_calls])
        
        elif parsed["action"] == "recent_messages":
            # Get the 20 most recent messages (assuming timestamp is sortable)
            messages = session.exec(
                select(Message).order_by(Message.timestamp.desc()).limit(20)
            ).all()
            
            return pd.DataFrame([msg.model_dump() for msg in messages])
        
        elif parsed["action"] == "recent_calls":
            # Get the 20 most recent calls
            calls = session.exec(
                select(Call).order_by(Call.timestamp.desc()).limit(20)
            ).all()
            
            return pd.DataFrame([call.model_dump() for call in calls])
        
        elif parsed["action"] == "find_contact":
            name = parsed["name"]
            contacts = session.exec(
                select(Contact).where(Contact.name.ilike(f"%{name}%"))
            ).all()
            
            return pd.DataFrame([contact.model_dump() for contact in contacts])
        
        elif parsed["action"] == "pattern_analysis":
            # AI-powered pattern analysis
            print("🤖 Performing AI pattern analysis...")
            # Get all messages for pattern analysis
            messages = session.exec(select(Message)).all()
            # For now, return high-risk messages, but this could be enhanced
            high_risk = [msg for msg in messages if getattr(msg, 'risk_level', 'unknown') in ['high', 'critical']]
            return pd.DataFrame([msg.model_dump() for msg in high_risk[:50]])
        
        elif parsed["action"] == "risk_assessment":
            # AI-powered risk assessment
            print("🤖 Performing AI risk assessment...")
            messages = session.exec(select(Message)).all()
            # Return messages with AI risk scores
            risky_messages = [msg for msg in messages if getattr(msg, 'risk_level', 'unknown') != 'low']
            return pd.DataFrame([msg.model_dump() for msg in risky_messages[:50]])
        
        elif parsed["action"] == "relationship_mapping":
            # AI-powered relationship analysis
            print("🤖 Analyzing communication relationships...")
            # Return contacts with their communication frequency
            contacts = session.exec(select(Contact)).all()
            return pd.DataFrame([contact.model_dump() for contact in contacts])
        
        elif parsed["action"] == "suspicious_media":
            # Find suspicious media files
            print("🖼️  Finding suspicious media files...")
            media_files = session.exec(
                select(MediaFile).where(MediaFile.risk_level.in_(["high", "critical"]))
            ).all()
            return pd.DataFrame([media.model_dump() for media in media_files])
        
        elif parsed["action"] == "media_with_faces":
            # Find media with detected faces
            print("🖼️  Finding media with faces...")
            media_files = session.exec(
                select(MediaFile).where(MediaFile.faces_detected > 0)
            ).all()
            return pd.DataFrame([media.model_dump() for media in media_files])
        
        elif parsed["action"] == "all_media":
            # Return all media files
            print("🖼️  Retrieving all media files...")
            media_files = session.exec(select(MediaFile)).all()
            return pd.DataFrame([media.model_dump() for media in media_files])
        
        elif parsed["action"] == "ai_insights":
            # Return messages with AI insights
            print("🤖 Gathering AI insights...")
            messages = session.exec(
                select(Message).where(Message.ai_summary.isnot(None))
            ).all()
            return pd.DataFrame([{
                "sender": msg.sender,
                "body": msg.body[:100] + "..." if len(msg.body or "") > 100 else msg.body,
                "risk_level": msg.risk_level,
                "sentiment_score": msg.sentiment_score,
                "ai_summary": msg.ai_summary,
                "topics": msg.topics
            } for msg in messages])
        
        elif parsed.get("ai_processed"):
            # Handle AI-interpreted queries
            print(f"🤖 Executing AI-interpreted query: {parsed.get('action')}")
            
            if parsed.get("action") == "suspicious_messages":
                # Use enhanced suspicious message detection
                conditions = [Message.body.ilike(f"%{keyword}%") for keyword in [
                    "weed", "cannabis", "marijuana", "drugs", "powder", "pills",
                    "cash", "money", "payment", "transfer", "fake", "illegal"
                ]]
                # Also include AI-flagged high-risk messages
                risk_condition = Message.risk_level.in_(["high", "critical"])
                all_conditions = conditions + [risk_condition]
                messages = session.exec(select(Message).where(or_(*all_conditions))).all()
                return pd.DataFrame([msg.model_dump() for msg in messages])
            
            elif parsed.get("action") == "pattern_analysis":
                # Enhanced pattern analysis with AI insights
                messages = session.exec(select(Message)).all()
                
                # Group by sender and analyze patterns
                sender_patterns = {}
                for msg in messages:
                    sender = msg.sender or "unknown"
                    if sender not in sender_patterns:
                        sender_patterns[sender] = {
                            "count": 0, "risk_messages": 0, "sentiment_avg": 0,
                            "recent_activity": False, "topics": set()
                        }
                    
                    pattern = sender_patterns[sender]
                    pattern["count"] += 1
                    
                    if msg.risk_level in ["high", "critical"]:
                        pattern["risk_messages"] += 1
                    
                    if msg.sentiment_score:
                        pattern["sentiment_avg"] += msg.sentiment_score
                    
                    if msg.topics:
                        try:
                            topics = json.loads(msg.topics)
                            pattern["topics"].update(topics)
                        except:
                            pass
                
                # Create summary DataFrame
                pattern_data = []
                for sender, data in sender_patterns.items():
                    if data["count"] > 0:
                        avg_sentiment = data["sentiment_avg"] / data["count"]
                        risk_ratio = data["risk_messages"] / data["count"]
                        
                        pattern_data.append({
                            "sender": sender,
                            "message_count": data["count"],
                            "risk_messages": data["risk_messages"],
                            "risk_ratio": round(risk_ratio, 2),
                            "avg_sentiment": round(avg_sentiment, 2),
                            "main_topics": ", ".join(list(data["topics"])[:3])
                        })
                
                # Sort by risk ratio
                pattern_data.sort(key=lambda x: x["risk_ratio"], reverse=True)
                return pd.DataFrame(pattern_data[:20])  # Top 20 patterns
            
            else:
                # Fallback to regular processing
                return execute_query({"action": parsed.get("action", "unknown")})
        
        else:
            # Unknown action
            return pd.DataFrame()

def query_agent(user_query: str) -> pd.DataFrame:
    """
    Hybrid AI + Rule-based query processing with pre-analysis intelligence.
    
    Args:
        user_query (str): Natural language query from the investigator
    
    Returns:
        pd.DataFrame: Results from the database query or AI analysis
    """
    print(f"🔍 Processing query: '{user_query}'")
    
    # First try rule-based parsing for simple queries
    parsed = simple_parse_query(user_query)
    print(f"📝 Rule-based parsing: {parsed['action']}")
    
    # If rule-based parsing succeeds, execute it
    if parsed['action'] != 'unknown':
        results = execute_query(parsed)
        print(f"✅ Found {len(results)} results using rule-based matching")
        return results
    
    # For complex queries, use AI with pre-analysis report
    if ai_analyzer.is_available():
        print("🤖 Using AI with comprehensive pre-analysis report...")
        
        # Get the pre-analysis report
        analysis_report = pre_analyzer.get_analysis_for_query()
        
        if "No analysis report available" in analysis_report:
            print("⚠️ No pre-analysis report found. Creating comprehensive analysis...")
            pre_analyzer.create_comprehensive_analysis()
            analysis_report = pre_analyzer.get_analysis_for_query()
        
        # Use AI to answer query based on the analysis report
        ai_response = ai_query_with_analysis(user_query, analysis_report)
        
        # Convert AI response to dataframe format
        result_df = convert_ai_response_to_dataframe(ai_response, user_query)
        print(f"✅ AI analysis complete with comprehensive insights")
        return result_df
    
    # Fallback: return empty results
    print("❌ Unable to process query - no rule match and AI unavailable")
    return pd.DataFrame([{
        "Error": "Unable to process query",
        "Reason": "No rule-based match found and AI is unavailable",
        "Query": user_query
    }])

def ai_query_with_analysis(user_query: str, analysis_report: str) -> str:
    """
    Query AI using the comprehensive pre-analysis report
    """
    if not ai_analyzer.is_available():
        return "AI not available for complex queries"
    
    prompt = f"""
    You are a forensic analyst AI with access to a comprehensive UFDR analysis report.
    
    COMPREHENSIVE ANALYSIS REPORT:
    {analysis_report}
    
    USER QUERY: {user_query}
    
    Based on the detailed analysis report above, provide a thorough answer to the user's query. Include:
    
    1. DIRECT FINDINGS: Specific information from the report that answers the query
    2. EVIDENCE DETAILS: File names, message IDs, contact names, timestamps, etc.
    3. RISK ANALYSIS: Security concerns and threat levels found
    4. PATTERNS: Communication patterns, behavioral analysis
    5. RECOMMENDATIONS: Suggested next steps for investigation
    
    Format your response with clear sections and bullet points for easy reading.
    Be specific and reference actual data from the report.
    """
    
    try:
        response = ai_analyzer.client.models.generate_content(
            model=ai_analyzer.model_name,
            contents=prompt
        )
        
        if response.text:
            return response.text.strip()
        else:
            return "AI analysis completed but no response generated"
            
    except Exception as e:
        print(f"❌ AI query failed: {e}")
        return f"AI query failed: {str(e)}"

def convert_ai_response_to_dataframe(ai_response: str, original_query: str) -> pd.DataFrame:
    """
    Convert AI response to DataFrame format for consistency with the interface
    """
    return pd.DataFrame([{
        "Query": original_query,
        "AI Comprehensive Analysis": ai_response,
        "Analysis Type": "AI Pre-Analysis Based Response",
        "Timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

def get_query_suggestions() -> List[str]:
    """
    Return a list of example queries that the agent can handle.
    """
    return [
        "Show me all messages from +919810000004",
        "Find suspicious messages",
        "Show calls with foreign numbers", 
        "Recent messages",
        "Find contact named john",
        "Messages from alice",
        "Calls with +919810000001"
    ]

def get_ai_query_suggestions() -> List[str]:
    """
    Return AI-powered query suggestions using pre-analysis.
    """
    return [
        "What are the main security threats in this data?",
        "Show me all suspicious activities found",
        "Analyze the communication patterns between contacts",
        "What evidence of illegal activities was discovered?",
        "Which contacts pose the highest risk?",
        "Summarize all high-risk findings",
        "What suspicious media files were found?",
        "Show me patterns in call behavior",
        "Which messages contain coded language?",
        "Provide a comprehensive risk assessment",
        "What connections exist between suspicious contacts?",
        "Analyze the timeline of suspicious activities"
    ]

if __name__ == "__main__":
    print("🤖 UFDR Core Agent - Interactive Mode")
    print("📋 Example queries:")
    for suggestion in get_query_suggestions():
        print(f"   • {suggestion}")
    print()
    
    while True:
        try:
            query = input("❓ Enter your query (or 'quit' to exit): ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
                
            results = query_agent(query)
            
            if len(results) > 0:
                print("\n📊 Results:")
                print(results.to_string(index=False))
                print(f"\n📈 Total: {len(results)} records")
            else:
                print("❌ No results found. Try rephrasing your query.")
                print("💡 Suggestion: Check the example queries above.")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again with a different query.")
