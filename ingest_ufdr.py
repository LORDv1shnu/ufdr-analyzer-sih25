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
            
        sess.commit()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ingest_ufdr.py <folder>")
        sys.exit(1)
    ingest_from_folder(sys.argv[1])
    print("Import completed!")
