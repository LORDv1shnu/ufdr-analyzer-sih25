import json, os, sys
from sqlmodel import SQLModel, Session
from models import Contact, Message, Call, MediaFile, get_engine

engine = get_engine()
SQLModel.metadata.create_all(engine)

def ingest_from_folder(folder):
    with Session(engine) as sess:
        # Contacts
        try:
            with open(os.path.join(folder, "contacts/contacts.json")) as f:
                contacts = json.load(f)
            for c in contacts:
                sess.add(Contact(name=c.get("name"), phone=c.get("phone"), email=c.get("email")))
            print(f"Imported {len(contacts)} contacts")
        except Exception as e:
            print(f"Contacts error: {e}")
        
        # Messages  
        try:
            with open(os.path.join(folder, "messages/messages.json")) as f:
                messages = json.load(f)
            for m in messages:
                sess.add(Message(timestamp=m.get("timestamp"), sender=m.get("sender"), receiver=m.get("receiver"), body=m.get("body")))
            print(f"Imported {len(messages)} messages")
        except Exception as e:
            print(f"Messages error: {e}")
            
        # Calls
        try:
            with open(os.path.join(folder, "calls/call_log.json")) as f:
                calls = json.load(f)
            for c in calls:
                sess.add(Call(timestamp=c.get("timestamp"), caller=c.get("caller"), callee=c.get("callee"), duration=c.get("duration", 0)))
            print(f"Imported {len(calls)} calls")
        except Exception as e:
            print(f"Calls error: {e}")
            
        # Media Files (Images and Videos)
        try:
            media_count = 0
            media_dir = os.path.join(folder, "media")
            
            if os.path.exists(media_dir):
                # Import images
                images_dir = os.path.join(media_dir, "images")
                if os.path.exists(images_dir):
                    for filename in os.listdir(images_dir):
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                            file_path = os.path.join(images_dir, filename)
                            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                            media_file = MediaFile(
                                filename=filename,
                                file_type="image",
                                file_path=file_path,
                                size=file_size
                            )
                            sess.add(media_file)
                            media_count += 1
                
                # Import videos
                videos_dir = os.path.join(media_dir, "videos")
                if os.path.exists(videos_dir):
                    for filename in os.listdir(videos_dir):
                        if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.txt')):  # .txt for video placeholders
                            file_path = os.path.join(videos_dir, filename)
                            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                            media_file = MediaFile(
                                filename=filename,
                                file_type="video",
                                file_path=file_path,
                                size=file_size
                            )
                            sess.add(media_file)
                            media_count += 1
                            
                print(f"Imported {media_count} media files")
            else:
                print("No media directory found")
        except Exception as e:
            print(f"Media files error: {e}")
            
        sess.commit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ingest_ufdr.py <folder>")
        sys.exit(1)
    ingest_from_folder(sys.argv[1])
    print("Import completed!")
