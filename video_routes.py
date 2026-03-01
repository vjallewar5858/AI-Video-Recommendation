"""
routes/video_routes.py - Video CRUD API Endpoints
===================================================
Handles storing and retrieving videos from MongoDB.

Routes:
  POST /api/videos  → Save a new video URL to MongoDB
  GET  /api/videos  → Retrieve all saved videos
"""

from flask import Blueprint, request, jsonify, current_app
from pymongo import MongoClient
from models.video_model import create_video_document, video_to_dict
import os

video_bp = Blueprint("video_bp", __name__)


def get_collection():
    """Helper to get the MongoDB collection from the current app context"""
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/kidswatch"))
    db = client["kidswatch"]
    return db["videos"]


@video_bp.route("/api/videos", methods=["POST"])
def add_video():
    """
    POST /api/videos
    ─────────────────
    Receives a video URL from the frontend, saves it to MongoDB.
    
    Request Body (JSON):
        { "url": "https://youtube.com/watch?v=...", "title": "..." }
    
    Response:
        { "message": "Video saved", "id": "<mongo_object_id>" }
    """
    data = request.get_json()
    url = data.get("url")
    title = data.get("title", "")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    collection = get_collection()

    # Avoid duplicate entries
    if collection.find_one({"url": url}):
        return jsonify({"message": "Video already exists"}), 200

    video_doc = create_video_document(url=url, title=title)
    result = collection.insert_one(video_doc)

    return jsonify({"message": "Video saved", "id": str(result.inserted_id)}), 201


@video_bp.route("/api/videos", methods=["GET"])
def get_videos():
    """
    GET /api/videos
    ─────────────────
    Returns all video documents stored in MongoDB.
    
    Response:
        [ { "_id": "...", "url": "...", "stats": {...} }, ... ]
    """
    collection = get_collection()
    videos = list(collection.find())
    return jsonify([video_to_dict(v) for v in videos]), 200
