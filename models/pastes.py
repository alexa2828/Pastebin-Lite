# models.py
from datetime import datetime, timedelta

# Instead of a class, we can define a helper function to create paste documents
def create_paste_document(paste_id, content, ttl_seconds=3600, max_views=1):
    """
    Returns a dictionary representing a paste document for insertion into MongoDB
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=ttl_seconds) if ttl_seconds else None

    return {
        "paste_id": paste_id,
        "content": content,
        "created_at": now,
        "expires_at": expires_at,
        "max_views": max_views,
        "views": 0
    }
