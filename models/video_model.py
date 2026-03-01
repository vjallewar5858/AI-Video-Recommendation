"""
models/video_model.py - Video Data Model
==========================================
Defines the structure (schema) of a video document in MongoDB.
Python uses dictionaries + a helper class instead of Mongoose schemas.

Each video document stored in MongoDB looks like:
{
    "url": "https://youtube.com/...",
    "title": "...",
    "stats": {
        "context": "EXCELLENT",
        "cognitive": "GOOD",
        "musicStimulus": 9,
        "visualStimulus": 8,
        "objectsUsed": 10,
        "habitFormingNature": 9,
        "storyMoral": 8,
        "ageGroup": "2-4 years"
    }
}
"""

from datetime import datetime


def create_video_document(url: str, title: str = "", stats: dict = None) -> dict:
    """
    Factory function that returns a properly structured video document
    ready to be inserted into MongoDB.
    
    Args:
        url   : YouTube video URL
        title : Video title (optional, filled later by AI)
        stats : Dictionary of safety/quality scores
    
    Returns:
        A dictionary matching our MongoDB schema
    """
    return {
        "url": url,
        "title": title,
        "createdAt": datetime.utcnow(),
        "stats": stats or {
            "context": "PENDING",
            "cognitive": "PENDING",
            "musicStimulus": 0,
            "visualStimulus": 0,
            "objectsUsed": 0,
            "habitFormingNature": 0,
            "storyMoral": 0,
            "ageGroup": "Unknown"
        }
    }


def video_to_dict(video_doc) -> dict:
    """
    Converts a MongoDB document to a JSON-serializable Python dict.
    MongoDB's ObjectId is not JSON serializable by default, so we convert it.
    """
    video_doc["_id"] = str(video_doc["_id"])
    return video_doc
