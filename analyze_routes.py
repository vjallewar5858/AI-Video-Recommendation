"""
routes/analyze_routes.py - AI Video Analysis API Endpoint
===========================================================
The CORE AI pipeline of the project. When a video URL is submitted:
  1. Downloads the audio from the YouTube video
  2. Sends audio to AssemblyAI for NLP transcription + content moderation
  3. Downloads video frames and runs YOLO object detection
  4. Combines both results into a unified safety score
  5. Saves the result to MongoDB and returns it to the frontend

Route:
  POST /api/analyze  → Analyze a video and return safety stats
"""

from flask import Blueprint, request, jsonify
from utils.assemblyai_helper import transcribe_and_moderate
from utils.yolo_helper import detect_objects_in_video
from utils.score_calculator import calculate_scores
from models.video_model import create_video_document, video_to_dict
from pymongo import MongoClient
import os

analyze_bp = Blueprint("analyze_bp", __name__)


def get_collection():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/kidswatch"))
    return client["kidswatch"]["videos"]


@analyze_bp.route("/api/analyze", methods=["POST"])
def analyze_video():
    """
    POST /api/analyze
    ──────────────────
    Full AI pipeline for a single YouTube video URL.

    Request Body:
        { "videoURL": "https://youtube.com/watch?v=..." }

    Response:
        {
          "context": "EXCELLENT",
          "cognitive": "GOOD",
          "musicStimulus": 9,
          "visualStimulus": 8,
          "objectsUsed": 10,
          "habitFormingNature": 9,
          "storyMoral": 8,
          "ageGroup": "2-4 years"
        }
    """
    data = request.get_json()
    video_url = data.get("videoURL")

    if not video_url:
        return jsonify({"error": "videoURL is required"}), 400

    try:
        # ── Step 1: NLP Analysis via AssemblyAI ───────────────────────────────
        # Downloads audio from YouTube, sends to AssemblyAI
        # Returns: transcript text, sentiment, content safety labels
        nlp_results = transcribe_and_moderate(video_url)

        # ── Step 2: Object Detection via YOLO ─────────────────────────────────
        # Downloads video frames, runs YOLOv8 on them
        # Returns: list of detected object class names
        detected_objects = detect_objects_in_video(video_url)

        # ── Step 3: Score Calculation ─────────────────────────────────────────
        # Combines NLP + YOLO results into the 8-metric scoring system
        stats = calculate_scores(nlp_results, detected_objects)

        # ── Step 4: Save to MongoDB ───────────────────────────────────────────
        collection = get_collection()
        doc = create_video_document(url=video_url, stats=stats)
        collection.update_one(
            {"url": video_url},
            {"$set": doc},
            upsert=True  # Insert if not exists, update if exists
        )

        return jsonify(stats), 200

    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return jsonify({"error": str(e)}), 500
