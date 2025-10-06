"""
UFDR AI Investigation Interface - Streamlit App
Interactive AI-powered forensic analysis and data exploration system
"""

import streamlit as st
import os
import time
import pandas as pd
import json
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from ai_analyzer import AIAnalyzer
from models import Message, Contact, Call, MediaFile, get_engine
from datetime import datetime

class UFDRInterface:
    """Complete interface for UFDR analysis and data exploration"""
    
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        self.analysis_file = "analysis.txt"
        self.db_file = "ufdr.db"
        self.engine = None
        
        # Initialize database connection
        if os.path.exists(self.db_file):
            self.engine = get_engine()
    
    def load_analysis_report(self) -> Optional[str]:
        """Load the pre-generated analysis report"""
        if not os.path.exists(self.analysis_file):
            return None
        
        try:
            with open(self.analysis_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            st.error(f"Error reading analysis file: {e}")
            return None
    
    def query_analysis(self, user_query: str, analysis_content: str) -> str:
        """Send user query along with analysis to AI for investigation"""
        return self.ai_analyzer.investigate_analysis(user_query, analysis_content)
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        if not self.engine:
            return {}
        
        stats = {}
        try:
            with Session(self.engine) as session:
                stats['messages'] = len(session.exec(select(Message)).all())
                stats['calls'] = len(session.exec(select(Call)).all())
                stats['contacts'] = len(session.exec(select(Contact)).all())
                stats['media_files'] = len(session.exec(select(MediaFile)).all())
        except Exception as e:
            st.error(f"Error getting database stats: {e}")
        
        return stats
    
    def get_all_messages(self) -> List[Dict]:
        """Get all messages from database"""
        if not self.engine:
            return []
        
        try:
            with Session(self.engine) as session:
                messages = session.exec(select(Message)).all()
                return [
                    {
                        "ID": msg.id,
                        "Timestamp": msg.timestamp,
                        "Sender": msg.sender,
                        "Receiver": msg.receiver,
                        "Body": msg.body[:100] + "..." if msg.body and len(msg.body) > 100 else msg.body,
                        "Full Body": msg.body,
                        "Source": msg.source,
                        "Risk Level": msg.risk_level,
                        "Sentiment": msg.sentiment_score,
                        "AI Summary": msg.ai_summary
                    }
                    for msg in messages
                ]
        except Exception as e:
            st.error(f"Error loading messages: {e}")
            return []
    
    def get_all_calls(self) -> List[Dict]:
        """Get all calls from database"""
        if not self.engine:
            return []
        
        try:
            with Session(self.engine) as session:
                calls = session.exec(select(Call)).all()
                return [
                    {
                        "ID": call.id,
                        "Timestamp": call.timestamp,
                        "Caller": call.caller,
                        "Callee": call.callee,
                        "Duration (s)": call.duration,
                        "Type": call.type,
                        "Risk Level": call.risk_level,
                        "Call Pattern": call.call_pattern
                    }
                    for call in calls
                ]
        except Exception as e:
            st.error(f"Error loading calls: {e}")
            return []
    
    def get_all_contacts(self) -> List[Dict]:
        """Get all contacts from database"""
        if not self.engine:
            return []
        
        try:
            with Session(self.engine) as session:
                contacts = session.exec(select(Contact)).all()
                return [
                    {
                        "ID": contact.id,
                        "Name": contact.name,
                        "Phone": contact.phone,
                        "Email": contact.email,
                        "Notes": contact.notes
                    }
                    for contact in contacts
                ]
        except Exception as e:
            st.error(f"Error loading contacts: {e}")
            return []
    
    def get_all_media(self) -> List[Dict]:
        """Get all media files from database"""
        if not self.engine:
            return []
        
        try:
            with Session(self.engine) as session:
                media_files = session.exec(select(MediaFile)).all()
                return [
                    {
                        "ID": media.id,
                        "Filename": media.filename,
                        "Type": media.file_type,
                        "Description": media.ai_description,
                        "Objects": media.detected_objects,
                        "Text Content": media.contains_text,
                        "Faces": media.faces_detected,
                        "Risk Level": media.risk_level,
                        "Tags": media.tags
                    }
                    for media in media_files
                ]
        except Exception as e:
            st.error(f"Error loading media files: {e}")
            return []
    
    def filter_messages_by_risk(self, risk_level: str) -> List[Dict]:
        """Filter messages by risk level"""
        if not self.engine:
            return []
        
        try:
            with Session(self.engine) as session:
                messages = session.exec(
                    select(Message).where(Message.risk_level == risk_level)
                ).all()
                return [
                    {
                        "ID": msg.id,
                        "Timestamp": msg.timestamp,
                        "Sender": msg.sender,
                        "Body": msg.body,
                        "Risk Level": msg.risk_level,
                        "AI Summary": msg.ai_summary
                    }
                    for msg in messages
                ]
        except Exception as e:
            st.error(f"Error filtering messages: {e}")
            return []
    
    def search_messages(self, search_term: str) -> List[Dict]:
        """Search messages by content"""
        if not self.engine:
            return []
        
        try:
            with Session(self.engine) as session:
                messages = session.exec(select(Message)).all()
                filtered_messages = []
                
                for msg in messages:
                    if (msg.body and search_term.lower() in msg.body.lower()) or \
                       (msg.sender and search_term.lower() in msg.sender.lower()) or \
                       (msg.ai_summary and search_term.lower() in msg.ai_summary.lower()):
                        filtered_messages.append({
                            "ID": msg.id,
                            "Timestamp": msg.timestamp,
                            "Sender": msg.sender,
                            "Body": msg.body,
                            "Risk Level": msg.risk_level,
                            "AI Summary": msg.ai_summary
                        })
                
                return filtered_messages
        except Exception as e:
            st.error(f"Error searching messages: {e}")
            return []
    
    def comprehensive_word_search(self, search_term: str, case_sensitive: bool = False, exact_match: bool = False) -> Dict[str, List[Dict]]:
        """Comprehensive word search across all data types with enhanced options"""
        if not self.engine:
            return {"messages": [], "calls": [], "contacts": [], "media": []}
        
        results = {
            "messages": [],
            "calls": [],
            "contacts": [],
            "media": []
        }
        
        # Prepare search term based on options
        if case_sensitive:
            search_term_to_use = search_term
        else:
            search_term_to_use = search_term.lower()
        
        def matches_criteria(text: str, search_term: str, case_sensitive: bool, exact_match: bool) -> bool:
            """Check if text matches search criteria"""
            if not text:
                return False
            
            if not case_sensitive:
                text = text.lower()
                search_term = search_term.lower()
            
            if exact_match:
                # Split into words and check for exact word match
                words = text.split()
                return search_term in words
            else:
                # Partial match (substring)
                return search_term in text
        
        try:
            with Session(self.engine) as session:
                # Search Messages
                messages = session.exec(select(Message)).all()
                for msg in messages:
                    found_in = []
                    if matches_criteria(msg.body, search_term, case_sensitive, exact_match):
                        found_in.append("body")
                    if matches_criteria(msg.sender, search_term, case_sensitive, exact_match):
                        found_in.append("sender")
                    if matches_criteria(msg.receiver, search_term, case_sensitive, exact_match):
                        found_in.append("receiver")
                    if matches_criteria(msg.ai_summary, search_term, case_sensitive, exact_match):
                        found_in.append("ai_summary")
                    
                    if found_in:
                        results["messages"].append({
                            "id": msg.id,
                            "timestamp": msg.timestamp,
                            "sender": msg.sender,
                            "receiver": msg.receiver,
                            "body": msg.body,
                            "risk_level": msg.risk_level,
                            "ai_summary": msg.ai_summary,
                            "found_in": found_in
                        })
                
                # Search Calls
                calls = session.exec(select(Call)).all()
                for call in calls:
                    found_in = []
                    if matches_criteria(call.caller, search_term, case_sensitive, exact_match):
                        found_in.append("caller")
                    if matches_criteria(call.callee, search_term, case_sensitive, exact_match):
                        found_in.append("callee")
                    if matches_criteria(call.type, search_term, case_sensitive, exact_match):
                        found_in.append("type")
                    
                    if found_in:
                        results["calls"].append({
                            "id": call.id,
                            "timestamp": call.timestamp,
                            "caller": call.caller,
                            "callee": call.callee,
                            "duration": call.duration,
                            "type": call.type,
                            "risk_level": call.risk_level,
                            "found_in": found_in
                        })
                
                # Search Contacts
                contacts = session.exec(select(Contact)).all()
                for contact in contacts:
                    found_in = []
                    if matches_criteria(contact.name, search_term, case_sensitive, exact_match):
                        found_in.append("name")
                    if matches_criteria(contact.phone, search_term, case_sensitive, exact_match):
                        found_in.append("phone")
                    if matches_criteria(contact.email, search_term, case_sensitive, exact_match):
                        found_in.append("email")
                    if matches_criteria(contact.notes, search_term, case_sensitive, exact_match):
                        found_in.append("notes")
                    
                    if found_in:
                        results["contacts"].append({
                            "id": contact.id,
                            "name": contact.name,
                            "phone": contact.phone,
                            "email": contact.email,
                            "notes": contact.notes,
                            "found_in": found_in
                        })
                
                # Search Media Files
                media_files = session.exec(select(MediaFile)).all()
                for media in media_files:
                    found_in = []
                    if matches_criteria(media.filename, search_term, case_sensitive, exact_match):
                        found_in.append("filename")
                    if matches_criteria(media.ai_description, search_term, case_sensitive, exact_match):
                        found_in.append("ai_description")
                    if matches_criteria(media.contains_text, search_term, case_sensitive, exact_match):
                        found_in.append("contains_text")
                    if matches_criteria(media.detected_objects, search_term, case_sensitive, exact_match):
                        found_in.append("detected_objects")
                    if matches_criteria(media.tags, search_term, case_sensitive, exact_match):
                        found_in.append("tags")
                    
                    if found_in:
                        results["media"].append({
                            "id": media.id,
                            "filename": media.filename,
                            "file_type": media.file_type,
                            "ai_description": media.ai_description,
                            "contains_text": media.contains_text,
                            "detected_objects": media.detected_objects,
                            "risk_level": media.risk_level,
                            "found_in": found_in
                        })
                        
        except Exception as e:
            st.error(f"Error during comprehensive search: {e}")
        
        return results

def render_ai_query_tab(interface):
    """Render the AI Query tab"""
    st.markdown("## 🎯 AI Investigation Query")
    
    # Check if system is ready
    analysis_exists = os.path.exists(interface.analysis_file)
    ai_available = interface.ai_analyzer.is_available()
    
    if not analysis_exists:
        st.markdown("""
        <div class="error-box">
        <h4>❌ Analysis Report Not Found</h4>
        <p>The forensic analysis report (analysis.txt) is missing. Please run the pre-analyzer first:</p>
        <code>python preanalyzer.py</code>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if not ai_available:
        st.markdown("""
        <div class="error-box">
        <h4>❌ AI Engine Offline</h4>
        <p>The AI analyzer is not available. Please check your API key configuration in apikey.txt</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Sample queries in sidebar for this tab
    with st.sidebar:
        st.markdown("### 💡 Sample Investigation Queries")
        sample_queries = [
            "What are all the suspicious activities you could find?",
            "Who are the main suspects in this case?",
            "What evidence suggests criminal activity?",
            "Are there any indicators of drug-related communications?",
            "What are the most concerning findings?",
            "Who should be investigated first?",
            "What financial crimes are indicated?",
            "Are there any compromised law enforcement contacts?",
            "What are the timeline patterns of suspicious activities?",
            "What immediate actions should investigators take?"
        ]
        
        # Initialize query state if not exists
        if 'quick_query' not in st.session_state:
            st.session_state.quick_query = ""
        
        for i, query in enumerate(sample_queries):
            if st.button(f"🔍 {query[:30]}...", key=f"sample_query_{i}", help=query):
                st.session_state.quick_query = query
                st.rerun()
    
    # Query input
    default_query = st.session_state.get('quick_query', "")
    
    user_query = st.text_area(
        "Enter your investigation query:",
        value=default_query,
        height=100,
        placeholder="e.g., What are all the suspicious activities you could find in this case?",
        help="Ask specific questions about the forensic analysis. The AI will act as a senior investigation officer."
    )
    
    # Query button
    if st.button("🔍 Run Investigation Query", type="primary", disabled=not user_query.strip()):
        if user_query.strip():
            # Show progress
            progress_container = st.container()
            
            with progress_container:
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Loading analysis
                status_text.text("📄 Loading forensic analysis report...")
                progress_bar.progress(20)
                time.sleep(0.5)
                
                analysis_content = interface.load_analysis_report()
                
                if not analysis_content:
                    st.error("Failed to load analysis report")
                    return
                
                # Step 2: Preparing query
                status_text.text("🔍 Preparing investigation query...")
                progress_bar.progress(40)
                time.sleep(0.5)
                
                # Step 3: AI Analysis
                status_text.text("🤖 AI Investigation Officer analyzing evidence...")
                progress_bar.progress(60)
                time.sleep(1)
                
                # Step 4: Getting response
                status_text.text("📋 Generating investigation report...")
                progress_bar.progress(80)
                
                # Run query
                response = interface.query_analysis(user_query, analysis_content)
                
                # Step 5: Complete
                status_text.text("✅ Investigation analysis complete!")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Clear progress
                progress_container.empty()
            
            # Display results
            st.markdown("---")
            st.markdown("## 📋 Investigation Officer Analysis")
            
            # Query info
            st.markdown(f"""
            <div class="query-box">
            <strong>🔍 Investigation Query:</strong><br>
            {user_query}
            </div>
            """, unsafe_allow_html=True)
            
            # Response
            st.markdown("### 👨‍💼 Senior Investigation Officer Response:")
            st.markdown(response)
            
            # Timestamp
            st.markdown(f"*Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

def render_data_explorer_tab(interface):
    """Render the Data Explorer tab"""
    st.markdown("## 📊 Forensic Data Explorer")
    
    if not interface.engine:
        st.markdown("""
        <div class="error-box">
        <h4>❌ Database Not Found</h4>
        <p>The UFDR database is missing. Please run data ingestion first:</p>
        <code>python ingest_ufdr.py fake_ufdr</code>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Get database stats
    stats = interface.get_database_stats()
    
    if not stats:
        st.error("Unable to load database statistics")
        return
    
    # Database overview
    st.markdown("### 📈 Database Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📩 Messages", stats.get('messages', 0))
    with col2:
        st.metric("📞 Calls", stats.get('calls', 0))
    with col3:
        st.metric("👥 Contacts", stats.get('contacts', 0))
    with col4:
        st.metric("🖼️ Media Files", stats.get('media_files', 0))
    
    st.markdown("---")
    
    # Data type selector
    data_type = st.selectbox(
        "🔍 Select Data Type to Explore:",
        ["Messages", "Calls", "Contacts", "Media Files"],
        help="Choose which type of forensic data you want to explore"
    )
    
    if data_type == "Messages":
        render_messages_explorer(interface)
    elif data_type == "Calls":
        render_calls_explorer(interface)
    elif data_type == "Contacts":
        render_contacts_explorer(interface)
    elif data_type == "Media Files":
        render_media_explorer(interface)

def render_messages_explorer(interface):
    """Render messages data explorer"""
    st.markdown("### 📩 Messages Explorer")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        filter_type = st.selectbox(
            "Filter Type:",
            ["All Messages", "By Risk Level", "Search Content"],
            key="msg_filter"
        )
    
    with col2:
        if filter_type == "By Risk Level":
            risk_level = st.selectbox(
                "Risk Level:",
                ["low", "medium", "high", "critical", "unknown"],
                key="msg_risk"
            )
        elif filter_type == "Search Content":
            search_term = st.text_input(
                "Search Term:",
                placeholder="Enter search term...",
                key="msg_search"
            )
    
    # Load and filter data
    if filter_type == "All Messages":
        messages_data = interface.get_all_messages()
    elif filter_type == "By Risk Level":
        messages_data = interface.filter_messages_by_risk(risk_level)
    elif filter_type == "Search Content" and 'search_term' in locals() and search_term:
        messages_data = interface.search_messages(search_term)
    else:
        messages_data = []
    
    if messages_data:
        st.markdown(f"**Found {len(messages_data)} messages**")
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(messages_data)
        
        # Display options
        show_full_body = st.checkbox("Show Full Message Body", key="show_full_msg")
        
        if show_full_body:
            # Show full messages with expandable content
            for i, msg in enumerate(messages_data):
                with st.expander(f"Message {msg['ID']} - {msg['Sender']} → {msg['Receiver']} ({msg['Timestamp']})"):
                    st.markdown(f"**Risk Level:** {msg['Risk Level']}")
                    if msg['Sentiment']:
                        st.markdown(f"**Sentiment Score:** {msg['Sentiment']}")
                    st.markdown(f"**Full Message:**")
                    st.text_area("", value=msg['Full Body'], height=100, key=f"msg_body_{i}", disabled=True)
                    if msg['AI Summary']:
                        st.markdown(f"**AI Summary:** {msg['AI Summary']}")
        else:
            # Show table view
            display_df = df.drop(columns=['Full Body'] if 'Full Body' in df.columns else [])
            st.dataframe(display_df, width="stretch")
    else:
        st.info("No messages found with the current filter settings.")

def render_calls_explorer(interface):
    """Render calls data explorer"""
    st.markdown("### 📞 Calls Explorer")
    
    calls_data = interface.get_all_calls()
    
    if calls_data:
        st.markdown(f"**Total Calls: {len(calls_data)}**")
        
        # Convert to DataFrame
        df = pd.DataFrame(calls_data)
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            call_type_filter = st.multiselect(
                "Call Type:",
                options=df['Type'].unique().tolist() if 'Type' in df.columns else [],
                default=df['Type'].unique().tolist() if 'Type' in df.columns else [],
                key="call_type_filter"
            )
        
        with col2:
            risk_filter = st.multiselect(
                "Risk Level:",
                options=df['Risk Level'].unique().tolist() if 'Risk Level' in df.columns else [],
                default=df['Risk Level'].unique().tolist() if 'Risk Level' in df.columns else [],
                key="call_risk_filter"
            )
        
        # Apply filters
        filtered_df = df.copy()
        if call_type_filter and 'Type' in df.columns:
            filtered_df = filtered_df[filtered_df['Type'].isin(call_type_filter)]
        if risk_filter and 'Risk Level' in df.columns:
            filtered_df = filtered_df[filtered_df['Risk Level'].isin(risk_filter)]
        
        st.markdown(f"**Showing {len(filtered_df)} calls**")
        st.dataframe(filtered_df, width="stretch")
        
        # Call duration analysis
        if 'Duration (s)' in filtered_df.columns:
            st.markdown("### 📊 Call Duration Analysis")
            duration_stats = filtered_df['Duration (s)'].describe()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Duration", f"{duration_stats['mean']:.1f}s")
            with col2:
                st.metric("Max Duration", f"{duration_stats['max']:.0f}s")
            with col3:
                st.metric("Total Call Time", f"{filtered_df['Duration (s)'].sum():.0f}s")
    else:
        st.info("No calls found in the database.")

def render_contacts_explorer(interface):
    """Render contacts data explorer"""
    st.markdown("### 👥 Contacts Explorer")
    
    contacts_data = interface.get_all_contacts()
    
    if contacts_data:
        st.markdown(f"**Total Contacts: {len(contacts_data)}**")
        
        # Convert to DataFrame
        df = pd.DataFrame(contacts_data)
        
        # Search functionality
        search_contact = st.text_input(
            "Search Contacts:",
            placeholder="Search by name, phone, or email...",
            key="contact_search"
        )
        
        if search_contact:
            # Filter contacts based on search
            filtered_df = df[
                df.apply(lambda row: search_contact.lower() in str(row).lower(), axis=1)
            ]
            st.markdown(f"**Found {len(filtered_df)} matching contacts**")
        else:
            filtered_df = df
        
        # Display contacts
        if len(filtered_df) > 0:
            # Show as expandable cards for better readability
            for i, contact in filtered_df.iterrows():
                with st.expander(f"📱 {contact['Name']} - {contact['Phone']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Name:** {contact['Name']}")
                        st.markdown(f"**Phone:** {contact['Phone']}")
                    with col2:
                        st.markdown(f"**Email:** {contact['Email'] or 'N/A'}")
                        st.markdown(f"**Notes:** {contact['Notes'] or 'N/A'}")
        else:
            st.info("No contacts match your search criteria.")
    else:
        st.info("No contacts found in the database.")

def get_combined_media_data(interface):
    """Get media data by combining direct file system access with database analysis"""
    combined_data = []
    
    # Direct access to image folder
    images_folder = "fake_ufdr/media/images"
    videos_folder = "fake_ufdr/media/videos"
    
    # Get database media analysis if available
    db_media_data = {}
    if interface.engine:
        try:
            with Session(interface.engine) as session:
                media_files = session.exec(select(MediaFile)).all()
                for media in media_files:
                    db_media_data[media.filename] = {
                        'ai_description': media.ai_description or '',
                        'detected_objects': media.detected_objects or '[]',
                        'contains_text': media.contains_text or '',
                        'faces_detected': media.faces_detected or 0,
                        'risk_level': media.risk_level or 'unknown',
                        'tags': media.tags or '[]'
                    }
        except Exception as e:
            st.error(f"Error loading database analysis: {e}")
    
    # Process images
    if os.path.exists(images_folder):
        for filename in sorted(os.listdir(images_folder)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                file_path = os.path.join(images_folder, filename)
                
                # Get analysis from database if available
                analysis = db_media_data.get(filename, {})
                combined_data.append({
                    'Filename': filename,
                    'Type': 'image',
                    'File Path': file_path,
                    'Description': analysis.get('ai_description', 'No analysis available'),
                    'Objects': analysis.get('detected_objects', '[]'),
                    'Text Content': analysis.get('contains_text', ''),
                    'Faces': analysis.get('faces_detected', 0),
                    'Risk Level': analysis.get('risk_level', 'unknown'),
                    'Tags': analysis.get('tags', '[]')
                })
    
    # Process videos
    if os.path.exists(videos_folder):
        for filename in sorted(os.listdir(videos_folder)):
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.txt')):
                file_path = os.path.join(videos_folder, filename)
                
                # Get analysis from database if available
                analysis = db_media_data.get(filename, {})
                
                combined_data.append({
                    'Filename': filename,
                    'Type': 'video',
                    'File Path': file_path,
                    'Description': analysis.get('ai_description', 'No analysis available'),
                    'Objects': analysis.get('detected_objects', '[]'),
                    'Text Content': analysis.get('contains_text', ''),
                    'Faces': analysis.get('faces_detected', 0),
                    'Risk Level': analysis.get('risk_level', 'unknown'),
                    'Tags': analysis.get('tags', '[]')
                })
    
    return combined_data

def render_media_explorer(interface):
    """Render enhanced media files data explorer with image viewer and file search"""
    st.markdown("### 🖼️ Enhanced Media Files Explorer")
    
    # Get combined media data (direct from folder + database analysis)
    media_data = get_combined_media_data(interface)
    
    if media_data:
        # Enhanced search and filter controls
        st.markdown("#### 🔍 Search & Filter Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # File search by name/content
            search_query = st.text_input(
                "🔍 Search Files:",
                placeholder="Search by filename, description, or detected objects...",
                key="media_search",
                help="Search across filenames, AI descriptions, detected objects, and tags"
            )
        
        with col2:
            # Media type filter
            df = pd.DataFrame(media_data)
            media_type_filter = st.multiselect(
                "📁 Media Type:",
                options=df['Type'].unique().tolist() if 'Type' in df.columns else [],
                default=df['Type'].unique().tolist() if 'Type' in df.columns else [],
                key="media_type_filter"
            )
        
        with col3:
            # Risk level filter
            risk_filter = st.multiselect(
                "⚠️ Risk Level:",
                options=df['Risk Level'].unique().tolist() if 'Risk Level' in df.columns else [],
                default=df['Risk Level'].unique().tolist() if 'Risk Level' in df.columns else [],
                key="media_risk_filter"
            )
        
        # Advanced filters
        with st.expander("🔧 Advanced Filters"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                faces_filter = st.checkbox("🧑 Show only files with faces detected", key="faces_filter")
                text_filter = st.checkbox("📝 Show only files with text content", key="text_filter")
            
            with col2:
                objects_search = st.text_input(
                    "🎯 Search Objects:",
                    placeholder="e.g., car, person, weapon...",
                    key="objects_search"
                )
            
            with col3:
                tags_search = st.text_input(
                    "🏷️ Search Tags:",
                    placeholder="e.g., suspicious, outdoor, vehicle...",
                    key="tags_search"
                )
        
        # Apply all filters
        filtered_df = df.copy()
        
        # Text search across multiple fields
        if search_query:
            search_mask = (
                filtered_df['Filename'].str.contains(search_query, case=False, na=False) |
                filtered_df['Description'].str.contains(search_query, case=False, na=False) |
                filtered_df['Objects'].str.contains(search_query, case=False, na=False) |
                filtered_df['Tags'].str.contains(search_query, case=False, na=False) |
                filtered_df['Text Content'].str.contains(search_query, case=False, na=False)
            )
            filtered_df = filtered_df[search_mask]
        
        # Media type filter
        if media_type_filter and 'Type' in df.columns:
            filtered_df = filtered_df[filtered_df['Type'].isin(media_type_filter)]
        
        # Risk level filter
        if risk_filter and 'Risk Level' in df.columns:
            filtered_df = filtered_df[filtered_df['Risk Level'].isin(risk_filter)]
        
        # Faces filter
        if faces_filter:
            filtered_df = filtered_df[filtered_df['Faces'] > 0]
        
        # Text content filter
        if text_filter:
            filtered_df = filtered_df[filtered_df['Text Content'].notna() & (filtered_df['Text Content'] != '')]
        
        # Objects search
        if objects_search:
            objects_mask = filtered_df['Objects'].str.contains(objects_search, case=False, na=False)
            filtered_df = filtered_df[objects_mask]
        
        # Tags search
        if tags_search:
            tags_mask = filtered_df['Tags'].str.contains(tags_search, case=False, na=False)
            filtered_df = filtered_df[tags_mask]
        
        # Results summary
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Files", len(media_data))
        with col2:
            st.metric("🎯 Filtered Results", len(filtered_df))
        with col3:
            st.metric("📸 Images Found", len(filtered_df[filtered_df['Type'] == 'image']) if len(filtered_df) > 0 else 0)
        
        if len(filtered_df) > 0:
            # View mode selector
            st.markdown("#### 📋 Display Options")
            view_mode = st.radio(
                "Choose view mode:",
                ["🖼️ Image Gallery", "📋 Detailed List", "📊 Data Table"],
                horizontal=True,
                key="media_view_mode"
            )
            
            if view_mode == "🖼️ Image Gallery":
                render_image_gallery(filtered_df)
            elif view_mode == "📋 Detailed List":
                render_detailed_media_list(filtered_df)
            else:
                render_media_data_table(filtered_df)
        else:
            st.warning("🚫 No media files match the current filters.")
    else:
        st.info("No media files found in the database.")

def render_image_gallery(df):
    """Render images in a responsive gallery format"""
    st.markdown("#### 🖼️ Image Gallery View")
    
    images_df = df[df['Type'] == 'image']
    
    if len(images_df) == 0:
        st.info("📷 No images to display with current filters.")
        return
    
    # Gallery layout - 3 columns
    cols_per_row = 3
    rows = [images_df.iloc[i:i+cols_per_row] for i in range(0, len(images_df), cols_per_row)]
    
    for row in rows:
        cols = st.columns(cols_per_row)
        
        for idx, (_, media) in enumerate(row.iterrows()):
            if idx < len(cols):
                with cols[idx]:
                    # Check if image file exists
                    image_path = media.get('File Path', '')
                    if os.path.exists(image_path):
                        try:
                            # Display image with Streamlit's built-in image viewer
                            st.image(
                                image_path,
                                caption=f"� {media['Filename']}",
                                use_column_width=True
                            )
                            
                            # Image info card
                            with st.expander(f"🔍 View Details: {media['Filename']}"):
                                # Risk level with color coding
                                risk_color = {
                                    'critical': '🔴', 'high': '🟠', 
                                    'medium': '🟡', 'low': '🟢', 
                                    'unknown': '⚪'
                                }
                                risk_level = media.get('Risk Level', 'unknown').lower()
                                st.markdown(f"**Risk Level:** {risk_color.get(risk_level, '⚪')} {media.get('Risk Level', 'Unknown')}")
                                
                                if media.get('Faces', 0) > 0:
                                    st.markdown(f"**👥 Faces Detected:** {media['Faces']}")
                                
                                if media.get('Description'):
                                    st.markdown(f"**🤖 AI Analysis:**")
                                    st.write(media['Description'][:200] + "..." if len(media['Description']) > 200 else media['Description'])
                                
                                if media.get('Text Content'):
                                    st.markdown(f"**📝 Text Found:** {media['Text Content']}")
                                
                                # Display objects as badges
                                if media.get('Objects'):
                                    try:
                                        objects = json.loads(media['Objects']) if isinstance(media['Objects'], str) else media['Objects']
                                        if objects:
                                            st.markdown("**🎯 Detected Objects:**")
                                            # Create badges for objects
                                            objects_html = ""
                                            for obj in objects[:10]:  # Limit to first 10
                                                objects_html += f'<span style="background-color: #e1f5fe; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 0.8em; display: inline-block;">{obj}</span> '
                                            st.markdown(objects_html, unsafe_allow_html=True)
                                    except:
                                        pass
                                
                                # Download button for image
                                if os.path.exists(image_path):
                                    with open(image_path, "rb") as file:
                                        st.download_button(
                                            label="💾 Download Image",
                                            data=file.read(),
                                            file_name=media['Filename'],
                                            mime="image/jpeg"
                                        )
                        
                        except Exception as e:
                            st.error(f"❌ Cannot display image: {e}")
                            st.text(f"📁 File: {media['Filename']}")
                    else:
                        st.error(f"❌ Image file not found: {media['Filename']}")
                        st.text(f"📁 Expected path: {image_path}")

def render_detailed_media_list(df):
    """Render media files in detailed expandable list format"""
    st.markdown("#### 📋 Detailed Media List")
    
    for i, media in df.iterrows():
        # Color-coded risk indicator
        risk_colors = {
            'critical': '#ff1744', 'high': '#ff9800', 
            'medium': '#ffc107', 'low': '#4caf50', 
            'unknown': '#9e9e9e'
        }
        risk_level = media.get('Risk Level', 'unknown').lower()
        risk_color = risk_colors.get(risk_level, '#9e9e9e')
        
        # File type icon
        file_icon = "🖼️" if media['Type'] == 'image' else "🎥" if media['Type'] == 'video' else "📄"
        
        with st.expander(f"{file_icon} {media['Filename']} | Risk: {media.get('Risk Level', 'Unknown')} | Type: {media['Type']}", expanded=False):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Display image thumbnail if it's an image
                if media['Type'] == 'image' and os.path.exists(media.get('File Path', '')):
                    try:
                        st.image(media['File Path'], width=200, caption="Preview")
                    except:
                        st.text("📷 Image preview unavailable")
                
                # File metadata
                st.markdown(f"**📁 File:** {media['Filename']}")
                st.markdown(f"**📂 Type:** {media['Type']}")
                st.markdown(f"**⚠️ Risk:** <span style='color: {risk_color}; font-weight: bold;'>{media.get('Risk Level', 'Unknown')}</span>", unsafe_allow_html=True)
                
                if media.get('Faces', 0) > 0:
                    st.markdown(f"**👥 Faces:** {media['Faces']}")
            
            with col2:
                # AI Analysis
                if media.get('Description'):
                    st.markdown("**🤖 AI Analysis:**")
                    st.write(media['Description'])
                
                if media.get('Text Content'):
                    st.markdown("**📝 Text Content:**")
                    st.code(media['Text Content'])
                
                # Objects and Tags
                col2a, col2b = st.columns(2)
                
                with col2a:
                    if media.get('Objects'):
                        try:
                            objects = json.loads(media['Objects']) if isinstance(media['Objects'], str) else media['Objects']
                            if objects:
                                st.markdown("**🎯 Objects:**")
                                for obj in objects:
                                    st.write(f"• {obj}")
                        except:
                            pass
                
                with col2b:
                    if media.get('Tags'):
                        try:
                            tags = json.loads(media['Tags']) if isinstance(media['Tags'], str) else media['Tags']
                            if tags:
                                st.markdown("**🏷️ Tags:**")
                                for tag in tags:
                                    st.write(f"• {tag}")
                        except:
                            pass

def render_media_data_table(df):
    """Render media files in a sortable data table format"""
    st.markdown("#### 📊 Media Files Data Table")
    
    # Prepare simplified data for table view
    table_df = df[['Filename', 'Type', 'Risk Level', 'Faces', 'Description']].copy()
    
    # Truncate description for table view
    table_df['Description'] = table_df['Description'].apply(
        lambda x: x[:50] + "..." if isinstance(x, str) and len(x) > 50 else x
    )
    
    # Display interactive table
    st.dataframe(
        table_df,
        use_container_width=True,
        column_config={
            "Filename": st.column_config.TextColumn("📁 File Name", width="medium"),
            "Type": st.column_config.TextColumn("📂 Type", width="small"),
            "Risk Level": st.column_config.TextColumn("⚠️ Risk", width="small"),
            "Faces": st.column_config.NumberColumn("👥 Faces", width="small"),
            "Description": st.column_config.TextColumn("🤖 AI Analysis", width="large"),
        },
        hide_index=True
    )

def render_word_search_tab(interface):
    """Render the word-based search tab"""
    st.markdown("## 🔍 Database Search Engine")
    st.markdown("**🗄️ Direct search through ingested UFDR database - No AI required**")
    
    # Database info
    stats = interface.get_database_stats()
    if stats:
        st.info(f"🎯 **Searching in Database**: {stats.get('messages', 0)} messages, {stats.get('calls', 0)} calls, {stats.get('contacts', 0)} contacts, {stats.get('media_files', 0)} media files")
    
    if not interface.engine:
        st.markdown("""
        <div class="error-box">
        <h4>❌ Database Not Found</h4>
        <p>The UFDR database is missing. Please run data ingestion first:</p>
        <code>python ingest_ufdr.py fake_ufdr</code>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Search interface with improved layout
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Enter search term:",
            placeholder="e.g., cash, drugs, suspicious, phone numbers, names, etc.",
            help="Search across all messages, calls, contacts, and media files"
        )
    
    with col2:
        case_sensitive = st.checkbox("Case Sensitive", value=False, help="Match exact case of letters")
        exact_match = st.checkbox("Exact Match", value=False, help="Match whole words only")
        
    with col3:
        st.write("")  # Spacing
    
    # Quick search suggestions
    st.markdown("### 💡 Quick Search Suggestions")
    st.markdown("**Popular search terms**: `cash`, `weed`, `fake`, `+919`, `suspicious`, `meetup`, `burner`, `USB`")
    
    # Debug section to verify database search
    with st.expander("🔧 Debug: Verify Database Search", expanded=False):
        if st.button("🧪 Test Database Connection"):
            try:
                import sqlite3
                conn = sqlite3.connect('ufdr.db')
                cursor = conn.cursor()
                
                # Get sample data directly from database
                cursor.execute('SELECT COUNT(*) FROM message WHERE body LIKE ?', ('%cash%',))
                cash_db_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT body FROM message WHERE body LIKE ? LIMIT 2', ('%cash%',))
                samples = cursor.fetchall()
                
                conn.close()
                
                # Test our search function
                results = interface.comprehensive_word_search('cash')
                search_count = len(results['messages'])
                
                st.success(f"✅ **Database Direct Query**: {cash_db_count} messages contain 'cash'")
                st.success(f"✅ **Search Function**: {search_count} messages found")
                
                if cash_db_count == search_count:
                    st.success("🎉 **CONFIRMED**: Search function uses database correctly!")
                else:
                    st.warning("⚠️ Mismatch detected - investigating needed")
                
                st.write("**Sample database records:**")
                for i, (body,) in enumerate(samples, 1):
                    st.write(f"{i}. {body}")
                    
            except Exception as e:
                st.error(f"Debug test failed: {e}")
    
    if search_term and len(search_term.strip()) >= 2:
        # Show search progress
        with st.spinner(f"🔍 Searching for '{search_term}' across all UFDR data..."):
            # Perform comprehensive search
            results = interface.comprehensive_word_search(search_term.strip(), case_sensitive, exact_match)
            
            # Calculate totals
            total_results = (
                len(results["messages"]) + 
                len(results["calls"]) + 
                len(results["contacts"]) + 
                len(results["media"])
            )
        
        # Display results summary with improved styling
        st.markdown("---")
        st.markdown("## 📊 Search Results Summary")
        
        # Add search configuration info
        config_info = []
        if case_sensitive:
            config_info.append("Case Sensitive")
        if exact_match:
            config_info.append("Exact Match")
        if config_info:
            st.info(f"🔧 Search Configuration: {', '.join(config_info)}")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("🎯 Total Results", total_results, delta=None)
        with col2:
            msg_count = len(results["messages"])
            st.metric("📩 Messages", msg_count, delta=None)
        with col3:
            call_count = len(results["calls"])
            st.metric("📞 Calls", call_count, delta=None)
        with col4:
            contact_count = len(results["contacts"])
            st.metric("👥 Contacts", contact_count, delta=None)
        with col5:
            media_count = len(results["media"])
            st.metric("🖼️ Media", media_count, delta=None)
        
        if total_results == 0:
            st.warning(f"🔍 No results found for '{search_term}'")
            st.markdown("""
            **Suggestions:**
            - Check spelling and try different terms
            - Use simpler keywords (e.g., 'cash' instead of 'money transactions')
            - Try partial matches (e.g., 'drug' to find 'drugs')
            - Use the quick search buttons above for common terms
            """)
            return
        
        # Results display with tabs
        if total_results > 0:
            result_tabs = []
            tab_names = []
            
            if results["messages"]:
                tab_names.append(f"📩 Messages ({len(results['messages'])})")
                result_tabs.append("messages")
            if results["calls"]:
                tab_names.append(f"📞 Calls ({len(results['calls'])})")
                result_tabs.append("calls")
            if results["contacts"]:
                tab_names.append(f"👥 Contacts ({len(results['contacts'])})")
                result_tabs.append("contacts")
            if results["media"]:
                tab_names.append(f"🖼️ Media ({len(results['media'])})")
                result_tabs.append("media")
            
            # Create dynamic tabs based on results
            tabs = st.tabs(tab_names)
            
            for i, (tab, result_type) in enumerate(zip(tabs, result_tabs)):
                with tab:
                    display_search_results(results[result_type], result_type, search_term, case_sensitive)
    
    elif search_term and len(search_term.strip()) < 2:
        st.warning("⚠️ Please enter at least 2 characters to search.")
    
    # Search tips
    with st.expander("💡 Search Tips", expanded=False):
        st.markdown("""
        **Search Features:**
        - **Cross-Data Search**: Searches messages, calls, contacts, and media files simultaneously
        - **Partial Matching**: Finds partial matches within text
        - **Field-Specific Results**: Shows exactly where the term was found
        - **Offline Operation**: No internet or AI required
        
        **Search Examples (Database Fields):**
        - `cash` - Find financial transactions in message bodies
        - `drugs` or `weed` - Find drug-related communications in messages
        - `fake` - Find identity fraud mentions in message content
        - `+919` - Find Indian phone numbers in messages/calls/contacts
        - `Inspector` - Find law enforcement contacts by name
        - `suspicious` - Find flagged content in message bodies
        - `meetup` - Find meeting arrangements in message content
        - `USB` - Find data security discussions in messages
        - `burner` - Find tracking evasion attempts in messages
        
        **Note**: Search looks through actual database records, not analysis files!
        
        **Database Tables/Fields Searched:**
        - **Messages Table**: body, sender, receiver, ai_summary fields
        - **Calls Table**: caller, callee, type fields  
        - **Contacts Table**: name, phone, email, notes fields
        - **Media Table**: filename, ai_description, contains_text, detected_objects fields
        
        **🔍 This searches the SQLite database (ufdr.db), NOT the analysis.txt file!**
        """)

def display_search_results(results: List[Dict], result_type: str, search_term: str, case_sensitive: bool = False):
    """Display search results for specific data type"""
    
    if result_type == "messages":
        st.markdown(f"### 📩 Messages containing '{search_term}' ({len(results)} found)")
        
        # Add sorting options
        sort_option = st.selectbox(
            "Sort by:",
            ["Timestamp (Latest First)", "Timestamp (Oldest First)", "Risk Level", "Sender"],
            key=f"sort_messages_{search_term}"
        )
        
        # Sort results based on selection
        if sort_option == "Timestamp (Latest First)":
            results = sorted(results, key=lambda x: x['timestamp'], reverse=True)
        elif sort_option == "Timestamp (Oldest First)":
            results = sorted(results, key=lambda x: x['timestamp'])
        elif sort_option == "Risk Level":
            risk_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
            results = sorted(results, key=lambda x: risk_order.get(x['risk_level'], 0), reverse=True)
        elif sort_option == "Sender":
            results = sorted(results, key=lambda x: x['sender'] or "")
        
        for i, msg in enumerate(results, 1):
            # Create a more informative title with color coding
            risk_emoji = {"critical": "🚨", "high": "⚠️", "medium": "⚡", "low": "📝", "unknown": "❓"}
            risk_colors = {"critical": "#dc3545", "high": "#fd7e14", "medium": "#ffc107", "low": "#28a745", "unknown": "#6c757d"}
            
            title = f"{risk_emoji.get(msg['risk_level'], '📝')} Message {msg['id']}"
            subtitle = f"{msg['sender']} → {msg['receiver']}"
            risk_color = risk_colors.get(msg['risk_level'], '#6c757d')
            
            with st.expander(f"{title} | {subtitle} | {msg['timestamp']}", expanded=False):
                # Risk level indicator
                st.markdown(f"<div style='display: inline-block; background-color: {risk_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; margin-bottom: 10px;'>Risk: {msg['risk_level'].upper()}</div>", unsafe_allow_html=True)
                
                # Create columns for better layout
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Found in**: {', '.join(msg['found_in'])}")
                    if msg['body']:
                        st.markdown("**Message Content:**")
                        highlighted_body = highlight_search_term(msg['body'], search_term, case_sensitive)
                        st.markdown(f"<div class='message-content'>{highlighted_body}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**Timestamp**: {msg['timestamp']}")                    
                    # Add copy button for message content
                    if msg['body']:
                        if st.button(f"📋 Copy", key=f"copy_msg_{msg['id']}", help="Click to show copyable text"):
                            st.code(msg['body'], language=None)
                    
                    # Add message statistics
                    if msg['body']:
                        st.markdown(f"**Length**: {len(msg['body'])} chars")
                
                if msg['ai_summary']:
                    st.markdown("**AI Analysis:**")
                    st.markdown(f"<div class='ai-analysis'>{msg['ai_summary']}</div>", unsafe_allow_html=True)
    
    elif result_type == "calls":
        st.markdown(f"### 📞 Calls containing '{search_term}'")
        
        for call in results:
            with st.expander(f"Call {call['id']} - {call['caller']} ↔ {call['callee']} ({call['timestamp']})"):
                st.markdown(f"**Found in**: {', '.join(call['found_in'])}")
                st.markdown(f"**Duration**: {call['duration']} seconds")
                st.markdown(f"**Type**: {call['type']}")
                st.markdown(f"**Risk Level**: {call['risk_level']}")
    
    elif result_type == "contacts":
        st.markdown(f"### 👥 Contacts containing '{search_term}'")
        
        for contact in results:
            with st.expander(f"Contact {contact['id']} - {contact['name']} ({contact['phone']})"):
                st.markdown(f"**Found in**: {', '.join(contact['found_in'])}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Name**: {contact['name']}")
                    st.markdown(f"**Phone**: {contact['phone']}")
                with col2:
                    st.markdown(f"**Email**: {contact['email'] or 'N/A'}")
                    st.markdown(f"**Notes**: {contact['notes'] or 'N/A'}")
    
    elif result_type == "media":
        st.markdown(f"### 🖼️ Media Files containing '{search_term}'")
        
        for media in results:
            with st.expander(f"Media {media['id']} - {media['filename']} ({media['file_type']})"):
                st.markdown(f"**Found in**: {', '.join(media['found_in'])}")
                st.markdown(f"**Type**: {media['file_type']}")
                st.markdown(f"**Risk Level**: {media['risk_level']}")
                
                if media['ai_description']:
                    st.markdown(f"**AI Description**: {media['ai_description']}")
                
                if media['contains_text']:
                    st.markdown("**Text Content (OCR):**")
                    highlighted_text = highlight_search_term(media['contains_text'], search_term, case_sensitive)
                    st.markdown(highlighted_text, unsafe_allow_html=True)

def highlight_search_term(text: str, search_term: str, case_sensitive: bool = False) -> str:
    """Highlight search term in text with improved logic"""
    if not text or not search_term:
        return text
    
    import re
    
    # Escape special regex characters in search term
    escaped_term = re.escape(search_term)
    
    # Create regex pattern based on case sensitivity
    if case_sensitive:
        pattern = f"({escaped_term})"
    else:
        pattern = f"({escaped_term})"
        flags = re.IGNORECASE
    
    # Use regex to find and replace all occurrences
    def replacement(match):
        return f"<mark style='background-color: #ffd700; font-weight: bold; color: #000; padding: 2px 4px; border-radius: 3px;'>{match.group(1)}</mark>"
    
    if case_sensitive:
        highlighted = re.sub(pattern, replacement, text)
    else:
        highlighted = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return highlighted

def main():
    # Page config
    st.set_page_config(
        page_title="UFDR Investigation Interface",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        color: #1f4e79;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f4e79;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: rgba(31, 78, 121, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f4e79;
        margin: 1rem 0;
    }
    .status-box {
        background-color: rgba(40, 167, 69, 0.1);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: rgba(255, 193, 7, 0.1);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .error-box {
        background-color: rgba(220, 53, 69, 0.1);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: rgba(108, 117, 125, 0.1);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(108, 117, 125, 0.3);
        text-align: center;
    }
    .message-content {
        background-color: rgba(100, 149, 237, 0.1);
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #6495ED;
        margin: 8px 0;
    }
    .ai-analysis {
        background-color: rgba(40, 167, 69, 0.1);
        padding: 8px;
        border-radius: 3px;
        border-left: 3px solid #28a745;
        font-style: italic;
        margin: 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header with improved styling
    st.markdown('''
    <div style="text-align: center; padding: 20px 0; background: linear-gradient(90deg, #1f4e79, #4a90e2); border-radius: 10px; margin-bottom: 20px;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">🔍 UFDR Investigation & Data Explorer</h1>
        <p style="color: #e0e0e0; margin: 10px 0 0 0; font-size: 1.1rem;">Comprehensive Digital Forensic Analysis System</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize interface
    interface = UFDRInterface()
    
    # Sidebar with system status
    with st.sidebar:
        st.markdown("## 🚀 Investigation Tools")
        st.markdown("---")
        
        # Check system status
        analysis_exists = os.path.exists(interface.analysis_file)
        ai_available = interface.ai_analyzer.is_available()
        db_available = interface.engine is not None
        
        # Status indicators
        st.markdown("### System Status")
        
        if analysis_exists:
            st.markdown("✅ **Analysis Report**: Ready")
            # Show report stats
            try:
                with open(interface.analysis_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    word_count = len(content.split())
                    char_count = len(content)
                st.markdown(f"📊 Report Size: {word_count:,} words / {char_count:,} chars")
            except:
                pass
        else:
            st.markdown("❌ **Analysis Report**: Missing")
        
        if ai_available:
            st.markdown("✅ **AI Engine**: Connected")
            # Add connection test button
            if st.button("🔧 Test AI Connection", key="test_connection", help="Test connection to AI services"):
                with st.spinner("Testing connection..."):
                    test_result = interface.ai_analyzer.test_connection()
                    if test_result["connected"]:
                        st.success(f"✅ {test_result['message']}")
                    else:
                        st.error(f"❌ {test_result['error']}")
                        st.info(f"💡 {test_result['suggestion']}")
        else:
            st.markdown("❌ **AI Engine**: Offline")
        
        if db_available:
            st.markdown("✅ **Database**: Connected")
            # Show database stats
            stats = interface.get_database_stats()
            if stats:
                st.markdown(f"📊 {stats.get('messages', 0)} messages, {stats.get('calls', 0)} calls")
        else:
            st.markdown("❌ **Database**: Missing")
        
        st.markdown("---")
        
        # Quick help
        st.markdown("### 📚 Quick Help")
        st.markdown("""
        **AI Query Tab:**
        - Ask investigation questions
        - Get professional analysis
        - Evidence-based responses
        
        **Data Explorer Tab:**
        - Browse all forensic data
        - Filter and search
        - Detailed data views
        
        **Word Search Tab:**
        - Offline word-based search
        - Search across all data types
        - Fast and comprehensive
        - No AI or internet needed
        
        **Troubleshooting:**
        - Use "Test AI Connection" if queries fail
        - Check internet connectivity
        - Refresh page if needed
        """)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🤖 AI Investigation Query", "📊 Forensic Data Explorer", "🔍 Word-Based Search"])
    
    with tab1:
        render_ai_query_tab(interface)
    
    with tab2:
        render_data_explorer_tab(interface)
    
    with tab3:
        render_word_search_tab(interface)

if __name__ == "__main__":
    main()