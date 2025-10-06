import os
import json
from typing import List, Dict
from sqlmodel import Session, create_engine, select
from models import MediaFile, Message
from ai_analyzer import AIAnalyzer

engine = create_engine("sqlite:///ufdr.db", echo=False)

def process_media_files(ufdr_folder: str):
    """
    Process all media files in the UFDR folder and analyze them with AI
    """
    print("🖼️  Starting media file processing...")
    
    ai_analyzer = AIAnalyzer()
    media_folder = os.path.join(ufdr_folder, "media")
    
    if not os.path.exists(media_folder):
        print("❌ No media folder found")
        return
    
    processed_count = 0
    
    with Session(engine) as session:
        # Process images
        images_folder = os.path.join(media_folder, "images")
        if os.path.exists(images_folder):
            for image_file in os.listdir(images_folder):
                if image_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    image_path = os.path.join(images_folder, image_file)
                    
                    # Check if already processed
                    existing = session.exec(
                        select(MediaFile).where(MediaFile.filename == image_file)
                    ).first()
                    
                    if existing:
                        print(f"⏭️  Skipping {image_file} (already processed)")
                        continue
                    
                    print(f"🔍 Analyzing image: {image_file}")
                    
                    # AI analysis
                    analysis = ai_analyzer.analyze_image(image_path)
                    
                    # Find associated message (if any)
                    message_id = None
                    messages = session.exec(select(Message)).all()
                    for msg in messages:
                        if msg.attachments and image_file in msg.attachments:
                            message_id = msg.id
                            break
                    
                    # Create media file record
                    media_file = MediaFile(
                        filename=image_file,
                        file_path=f"media/images/{image_file}",
                        file_type="image",
                        message_id=message_id,
                        ai_description=analysis["ai_description"],
                        detected_objects=analysis["detected_objects"],
                        contains_text=analysis["contains_text"],
                        faces_detected=analysis["faces_detected"],
                        risk_level=analysis["risk_level"],
                        tags=analysis["tags"]
                    )
                    
                    session.add(media_file)
                    processed_count += 1
                    
                    # Show progress
                    if processed_count % 5 == 0:
                        print(f"✅ Processed {processed_count} images so far...")
        
        # Process videos (placeholder - would need video analysis)
        videos_folder = os.path.join(media_folder, "videos")
        if os.path.exists(videos_folder):
            for video_file in os.listdir(videos_folder):
                if video_file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    print(f"📹 Found video: {video_file} (analysis not implemented yet)")
                    
                    # Create basic record for videos
                    media_file = MediaFile(
                        filename=video_file,
                        file_path=f"media/videos/{video_file}",
                        file_type="video",
                        ai_description="Video file - analysis pending",
                        risk_level="unknown"
                    )
                    session.add(media_file)
                    processed_count += 1
        
        session.commit()
    
    print(f"✅ Media processing complete! Processed {processed_count} files")

def get_media_by_risk_level(risk_level: str) -> List[Dict]:
    """
    Get media files filtered by risk level
    """
    with Session(engine) as session:
        media_files = session.exec(
            select(MediaFile).where(MediaFile.risk_level == risk_level)
        ).all()
        
        return [
            {
                "filename": mf.filename,
                "type": mf.file_type,
                "description": mf.ai_description,
                "objects": json.loads(mf.detected_objects or "[]"),
                "text": mf.contains_text,
                "faces": mf.faces_detected,
                "risk": mf.risk_level,
                "tags": json.loads(mf.tags or "[]")
            }
            for mf in media_files
        ]

def get_suspicious_media() -> List[Dict]:
    """
    Get media files flagged as suspicious
    """
    return get_media_by_risk_level("high") + get_media_by_risk_level("critical")

def search_media_by_content(search_term: str) -> List[Dict]:
    """
    Search media files by AI description or detected text
    """
    with Session(engine) as session:
        media_files = session.exec(select(MediaFile)).all()
        
        results = []
        search_lower = search_term.lower()
        
        for mf in media_files:
            # Search in description
            if mf.ai_description and search_lower in mf.ai_description.lower():
                results.append(mf)
                continue
            
            # Search in OCR text
            if mf.contains_text and search_lower in mf.contains_text.lower():
                results.append(mf)
                continue
                
            # Search in detected objects
            if mf.detected_objects:
                try:
                    objects = json.loads(mf.detected_objects)
                    if any(search_lower in obj.lower() for obj in objects if isinstance(obj, str)):
                        results.append(mf)
                        continue
                except:
                    pass
        
        return [
            {
                "filename": mf.filename,
                "type": mf.file_type,
                "description": mf.ai_description,
                "objects": json.loads(mf.detected_objects or "[]"),
                "text": mf.contains_text,
                "risk": mf.risk_level
            }
            for mf in results
        ]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_media_files(sys.argv[1])
    else:
        print("Usage: python media_processor.py <ufdr_folder>")
        print("Example: python media_processor.py fake_ufdr")