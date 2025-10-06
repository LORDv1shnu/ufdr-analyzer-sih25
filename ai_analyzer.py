import os
import json
import base64
import time
from typing import Dict, Any
from google import genai
from google.genai.errors import APIError

class AIAnalyzer:
    """AI-powered analysis using Gemini API for UFDR data"""
    
    def __init__(self):
        # Try to get API key from multiple sources
        self.api_key = None
        
        # First, try to read from apikey.txt file
        if os.path.exists("apikey.txt"):
            try:
                with open("apikey.txt", "r", encoding="utf-8") as f:
                    self.api_key = f.read().strip()
                    if self.api_key:
                        print("✅ API key loaded from apikey.txt")
            except Exception as e:
                print(f"⚠️ Could not read apikey.txt: {e}")
        
        # If not found, try environment variable
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY")
        
        # If not in environment, try importing from config
        if not self.api_key:
            try:
                from config import GEMINI_API_KEY
                if GEMINI_API_KEY and GEMINI_API_KEY != "your_actual_api_key_here":
                    self.api_key = GEMINI_API_KEY
            except ImportError:
                pass
        
        self.client = None
        self.model_name = "gemini-2.5-flash"
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("✅ Gemini AI client initialized successfully")
            except Exception as e:
                print(f"⚠️ Gemini AI client initialization failed: {e}")
                print("💡 Please check your API key in apikey.txt, config.py, or GEMINI_API_KEY environment variable")
                self.client = None
        else:
            print("⚠️ No API key found. Please put your API key in apikey.txt file or set GEMINI_API_KEY")
    
    def is_available(self) -> bool:
        """Check if AI analysis is available"""
        return self.client is not None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to AI services"""
        if not self.is_available():
            return {
                "connected": False, 
                "error": "AI client not initialized",
                "suggestion": "Check API key configuration"
            }
        
        try:
            # Simple test request
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Test connection. Reply with 'OK'."
            )
            
            if hasattr(response, 'text') and response.text:
                return {
                    "connected": True,
                    "message": "Connection successful",
                    "response_time": "Normal"
                }
            else:
                return {
                    "connected": False,
                    "error": "No response received",
                    "suggestion": "Try again or check internet connection"
                }
                
        except (ConnectionError, OSError) as e:
            error_msg = str(e).lower()
            if "getaddrinfo failed" in error_msg:
                return {
                    "connected": False,
                    "error": "DNS resolution failed",
                    "suggestion": "Check internet connection and DNS settings"
                }
            else:
                return {
                    "connected": False,
                    "error": f"Network error: {str(e)}",
                    "suggestion": "Check internet connection"
                }
                
        except APIError as e:
            return {
                "connected": False,
                "error": f"API error: {str(e)}",
                "suggestion": "Check API key validity"
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": f"Unknown error: {str(e)}",
                "suggestion": "Contact technical support"
            }
    
    def analyze_message_content(self, message_body: str) -> Dict[str, Any]:
        """
        Analyze message content for sentiment, risk, and topics
        """
        if not self.is_available() or not message_body:
            return {
                "sentiment_score": 0.0,
                "risk_level": "unknown",
                "topics": "[]",
                "ai_summary": "AI analysis not available"
            }
        
        prompt = f"""
        Analyze this message for forensic investigation: "{message_body}"
        
        Classify the risk level:
        - "critical": explicit illegal activities (drugs, weapons, violence, fraud)
        - "high": suspicious patterns, coded language, financial irregularities
        - "medium": potentially concerning but unclear
        - "low": normal communication
        
        Determine sentiment from -1 (very negative/threatening) to 1 (very positive/friendly).
        
        Extract key topics like: drugs, weapons, money, threats, meetings, etc.
        
        Respond with JSON only:
        {{"sentiment_score": -0.3, "risk_level": "high", "topics": ["drugs", "money"], "summary": "Message discusses drug transaction with cash payment"}}
        """
        
        # Try with retry logic for network issues
        max_retries = 2  # Fewer retries for message analysis to avoid delays
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                if response.text:
                    # Try to parse JSON response
                    try:
                        result = json.loads(response.text.strip())
                        return {
                            "sentiment_score": result.get("sentiment_score", 0.0),
                            "risk_level": result.get("risk_level", "unknown"),
                            "topics": json.dumps(result.get("topics", [])),
                            "ai_summary": result.get("summary", "Analysis completed")
                        }
                    except json.JSONDecodeError:
                        # Fallback: extract information from text response
                        return self._extract_analysis_from_text(response.text, message_body)
                
            except APIError as e:
                if attempt == max_retries - 1:
                    print(f"API Error during message analysis: {e}")
                else:
                    time.sleep(1)
                    
            except (ConnectionError, OSError) as e:
                if attempt == max_retries - 1:
                    print(f"Network error during message analysis: {e}")
                else:
                    time.sleep(2)
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Error during message analysis: {e}")
                else:
                    time.sleep(1)
        
        return {
            "sentiment_score": 0.0,
            "risk_level": "unknown", 
            "topics": "[]",
            "ai_summary": "Analysis failed"
        }
    
    def _extract_analysis_from_text(self, ai_response: str, original_message: str) -> Dict[str, Any]:
        """Fallback method to extract analysis from non-JSON AI response"""
        response_lower = ai_response.lower()
        
        # Determine risk level based on keywords
        if any(word in response_lower for word in ["critical", "dangerous", "illegal", "criminal"]):
            risk_level = "critical"
        elif any(word in response_lower for word in ["high risk", "suspicious", "concerning"]):
            risk_level = "high"
        elif any(word in response_lower for word in ["medium", "moderate", "potential"]):
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Extract sentiment (simple heuristic)
        positive_words = ["positive", "good", "happy", "friendly"]
        negative_words = ["negative", "bad", "angry", "threat", "dangerous"]
        
        pos_count = sum(1 for word in positive_words if word in response_lower)
        neg_count = sum(1 for word in negative_words if word in response_lower)
        
        if neg_count > pos_count:
            sentiment = -0.5
        elif pos_count > neg_count:
            sentiment = 0.5
        else:
            sentiment = 0.0
        
        return {
            "sentiment_score": sentiment,
            "risk_level": risk_level,
            "topics": json.dumps(["general"]),
            "ai_summary": ai_response[:100] + "..." if len(ai_response) > 100 else ai_response
        }
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image content for objects, text, and potential risks
        """
        if not self.is_available():
            return {
                "ai_description": "AI analysis not available",
                "detected_objects": "[]",
                "contains_text": "",
                "faces_detected": 0,
                "risk_level": "unknown",
                "tags": "[]"
            }
        
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode()
            
            prompt = """
            Analyze this image for forensic investigation. Look for:
            
            1. Objects and items that might be relevant to criminal activity
            2. Any text visible in the image (signs, documents, messages)
            3. People/faces (count them)
            4. Weapons, drugs, cash, or other suspicious items
            5. Location indicators or identifying information
            
            Provide a JSON response with:
            - description: detailed description of what you see
            - objects: array of detected objects
            - text: any text found in the image
            - faces: number of faces detected
            - risk_level: "low", "medium", "high", or "critical"
            - tags: array of relevant tags
            
            Return only valid JSON.
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    {"text": prompt},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
                ]
            )
            
            if response.text:
                try:
                    result = json.loads(response.text.strip())
                    return {
                        "ai_description": result.get("description", "Image analyzed"),
                        "detected_objects": json.dumps(result.get("objects", [])),
                        "contains_text": result.get("text", ""),
                        "faces_detected": result.get("faces", 0),
                        "risk_level": result.get("risk_level", "low"),
                        "tags": json.dumps(result.get("tags", []))
                    }
                except json.JSONDecodeError:
                    return {
                        "ai_description": response.text[:200],
                        "detected_objects": "[]",
                        "contains_text": "",
                        "faces_detected": 0,
                        "risk_level": "unknown",
                        "tags": "[]"
                    }
        
        except Exception as e:
            print(f"Error analyzing image {image_path}: {e}")
        
        return {
            "ai_description": "Image analysis failed",
            "detected_objects": "[]",
            "contains_text": "",
            "faces_detected": 0,
            "risk_level": "unknown",
            "tags": "[]"
        }
    
    def natural_language_to_query(self, user_query: str, available_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI to interpret complex natural language queries
        This works alongside the rule-based system
        """
        if not self.is_available():
            return {"action": "ai_unavailable", "fallback": True}
        
        # Provide context about available data
        data_context = f"""
        Available data in the UFDR database:
        - Messages: {available_data.get('message_count', 0)} records
        - Contacts: {available_data.get('contact_count', 0)} records  
        - Calls: {available_data.get('call_count', 0)} records
        - Sample phone numbers: {', '.join(available_data.get('sample_phones', [])[:5])}
        - Sample contact names: {', '.join(available_data.get('sample_names', [])[:5])}
        """
        
        prompt = f"""
        You are a forensic data analyst. Convert this natural language query into a structured database query.
        
        User Query: "{user_query}"
        
        {data_context}
        
        Available actions and when to use them:
        - "suspicious_messages": for queries about illegal, drugs, weapons, suspicious content
        - "messages_from": for queries about messages from specific person/number
        - "calls_with": for queries about calls with specific person/number
        - "foreign_calls": for queries about international/foreign communications
        - "recent_messages": for queries about recent/latest messages
        - "recent_calls": for queries about recent/latest calls
        - "find_contact": for queries about finding specific contacts
        - "all_media": for queries about images, photos, media files
        - "suspicious_media": for queries about suspicious images/media
        - "media_with_faces": for queries about images with people/faces
        - "pattern_analysis": for queries about communication patterns
        - "risk_assessment": for queries about risk analysis
        - "relationship_mapping": for queries about contact relationships
        
        Respond with a simple JSON object:
        {{"action": "chosen_action", "identifier": "person_name_or_number_if_applicable"}}
        
        Examples:
        - "Find messages about drugs" → {{"action": "suspicious_messages"}}
        - "Show calls with John" → {{"action": "calls_with", "identifier": "john"}}
        - "Recent activity" → {{"action": "recent_messages"}}
        - "Images with people" → {{"action": "media_with_faces"}}
        
        Return ONLY the JSON, no other text.
        """
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name, 
                contents=prompt
            )
            
            if response.text:
                try:
                    result = json.loads(response.text.strip())
                    result["ai_processed"] = True
                    return result
                except json.JSONDecodeError:
                    pass
        
        except Exception as e:
            print(f"Error in AI query processing: {e}")
        
        return {"action": "ai_failed", "fallback": True}
    
    def investigate_analysis(self, user_query: str, analysis_content: str) -> str:
        """
        AI-powered investigation analysis for UFDR forensic reports
        Acts as a senior investigation officer analyzing evidence
        """
        if not self.is_available():
            return "❌ AI analyzer is not available. Please check your API key configuration."
        
        investigation_prompt = f"""
        You are a Senior Digital Forensic Investigation Officer. Answer the investigation query based on the forensic evidence provided.
        
        QUERY: "{user_query}"
        
        FORENSIC EVIDENCE:
        {analysis_content}
        
        INSTRUCTIONS:
        - Keep response under 200 words and highly focused
        - Provide direct answer with specific evidence (message IDs, phone numbers, dates)
        - List only the most critical findings
        - Use bullet points for clarity
        - Include threat level (Critical/High/Medium/Low) 
        - Suggest 2-3 key next steps maximum
        
        RESPONSE FORMAT:
        **FINDINGS:**
        [Brief direct answer with key evidence]
        
        **CRITICAL EVIDENCE:**
        • [Most important evidence with specific references]
        • [Second most important evidence]
        
        **THREAT LEVEL:** [Critical/High/Medium/Low]
        
        **NEXT STEPS:**
        1. [Most urgent action]
        2. [Second priority action]
        
        Keep it concise and actionable:
        """
        
        # Try with retry logic for network issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=investigation_prompt
                )
                
                if hasattr(response, 'text') and response.text:
                    return response.text
                else:
                    return "❌ No response received from AI investigation system. Please try again."
                    
            except APIError as e:
                if attempt == max_retries - 1:
                    return f"❌ AI Investigation System Error: {str(e)}\n\n💡 Troubleshooting Steps:\n• Check your API key in apikey.txt\n• Verify internet connection\n• Try again in a few moments"
                time.sleep(2)  # Wait before retry
                
            except (ConnectionError, OSError) as e:
                error_msg = str(e).lower()
                if "getaddrinfo failed" in error_msg or "network" in error_msg:
                    if attempt == max_retries - 1:
                        return """❌ Network Connection Error
                        
🔍 **Issue**: Unable to connect to Google AI services
🌐 **Cause**: Internet connectivity or DNS resolution problem

💡 **Solutions**:
• Check your internet connection
• Try refreshing the page
• Wait a moment and try again
• Verify your firewall isn't blocking the connection
• Check if Google services are accessible from your network

🔧 **If problem persists**:
• Try using a VPN or different network
• Contact your network administrator
• Verify DNS settings"""
                else:
                    if attempt == max_retries - 1:
                        return f"❌ Connection Error: {str(e)}\n\n💡 Please check your internet connection and try again."
                time.sleep(3)  # Wait longer for network issues
                
            except Exception as e:
                if attempt == max_retries - 1:
                    return f"❌ Investigation Analysis Error: {str(e)}\n\n💡 Please try again or contact technical support."
                time.sleep(1)
        
        return "❌ Unable to complete analysis after multiple attempts. Please check your connection and try again."