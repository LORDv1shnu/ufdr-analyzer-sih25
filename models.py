from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
import sqlalchemy

# Ensure we only create the metadata once
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine("sqlite:///ufdr.db", echo=False)
    return _engine

class Contact(SQLModel, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    notes: Optional[str]

class Message(SQLModel, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: Optional[str]
    sender: Optional[str]
    receiver: Optional[str]
    body: Optional[str]
    source: Optional[str]
    attachments: Optional[str]
    # AI-enhanced fields
    sentiment_score: Optional[float] = Field(default=None)  # -1 to 1 (negative to positive)
    risk_level: Optional[str] = Field(default="unknown")    # low, medium, high, critical
    topics: Optional[str] = Field(default=None)             # JSON string of extracted topics
    ai_summary: Optional[str] = Field(default=None)         # AI-generated summary

class Call(SQLModel, table=True, extend_existing=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: Optional[str]
    caller: Optional[str]
    callee: Optional[str]
    duration: Optional[int]
    type: Optional[str]
    # AI-enhanced fields
    risk_level: Optional[str] = Field(default="unknown")
    call_pattern: Optional[str] = Field(default=None)  # frequent, suspicious, normal

class MediaFile(SQLModel, table=True, extend_existing=True):
    """New table for media analysis"""
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: Optional[str]
    file_path: Optional[str]
    file_type: Optional[str]  # image, video, audio, document
    message_id: Optional[int] = Field(default=None, foreign_key="message.id")
    
    # AI analysis fields
    ai_description: Optional[str] = Field(default=None)      # AI-generated description
    detected_objects: Optional[str] = Field(default=None)    # JSON list of detected objects
    contains_text: Optional[str] = Field(default=None)       # OCR extracted text
    faces_detected: Optional[int] = Field(default=0)         # Number of faces
    risk_level: Optional[str] = Field(default="unknown")     # Based on content analysis
    tags: Optional[str] = Field(default=None)                # JSON list of tags
