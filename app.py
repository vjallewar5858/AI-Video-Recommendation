"""
app.py - Main Flask Backend Server
===================================
Entry point of the entire application.
- Starts the web server
- Connects to MongoDB
- Registers all API routes
- Serves the HTML frontend
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests (frontend <-> backend)

# ─── MongoDB Connection ────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/kidswatch")
client = MongoClient(MONGO_URI)
db = client["kidswatch"]
videos_collection = db["videos"]
print("✅ Connected to MongoDB")

# ─── Import route blueprints ───────────────────────────────────────────────────
from routes.video_routes import video_bp
from routes.analyze_routes import analyze_bp

app.register_blueprint(video_bp)
app.register_blueprint(analyze_bp)

# ─── Serve Frontend ────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Serve the main HTML page"""
    return render_template("index.html")

# ─── Run Server ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Server running on http://localhost:{port}")
    app.run(debug=True, port=port)
