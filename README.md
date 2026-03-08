# Age-Tailored AI Video Recommendation System

An AI-powered web application that analyzes YouTube videos for child safety and age-appropriateness using **NLP (AssemblyAI)**, **Computer Vision (YOLOv8)**, and a **Python/Flask backend** with **MongoDB** storage.

---

## Project Structure & How Everything Connects

```
kids_video_recommender/
│
├── app.py                        ← Flask server (entry point)
│
├── routes/
│   ├── video_routes.py           ← CRUD: Save/get videos from MongoDB
│   └── analyze_routes.py         ← AI pipeline: orchestrates NLP + YOLO
│
├── utils/
│   ├── assemblyai_helper.py      ← NLP: audio download + transcription + safety
│   ├── yolo_helper.py            ← CV: video download + object detection
│   └── score_calculator.py       ← Converts AI outputs → 8 safety metrics
│
├── models/
│   └── video_model.py            ← MongoDB document schema
│
├── templates/
│   └── index.html                ← HTML page (Jinja2 template served by Flask)
│
├── static/
│   ├── script.js                 ← Frontend: renders cards, calls API, filters
│   └── style.css                 ← Visual styles (hover cards, grid layout)
│
├── requirements.txt              ← Python dependencies
├── .env.example                  ← API keys template
└── .gitignore                    ← Excludes secrets and large files
```

---

## How Components Connect (Data Flow)

```
Browser (index.html + script.js)
        │
        │  POST /api/analyze { videoURL }
        ▼
app.py (Flask Server)
        │
        ├── routes/analyze_routes.py
        │         │
        │         ├── utils/assemblyai_helper.py
        │         │     ├── yt-dlp downloads AUDIO from YouTube
        │         │     └── AssemblyAI API → transcript + safety labels + sentiment
        │         │
        │         ├── utils/yolo_helper.py
        │         │     ├── yt-dlp downloads VIDEO from YouTube
        │         │     ├── OpenCV extracts frames every 10 seconds
        │         │     └── YOLOv8 detects objects in each frame
        │         │
        │         └── utils/score_calculator.py
        │               └── Combines NLP + YOLO → 8 safety metrics (JSON)
        │
        ├── MongoDB (stores video URLs + stats)
        │
        └── Returns stats JSON → browser updates the card
```

---

## AI Components Explained

### 1. AssemblyAI (NLP)
- Downloads audio track from YouTube using `yt-dlp`
- Sends `.mp3` to AssemblyAI API
- Gets back: **full transcript**, **sentiment analysis**, **content safety labels** (profanity, violence, etc.)
- Used for: `context`, `cognitive`, `storyMoral`, `musicStimulus` scores

### 2. YOLOv8 (Computer Vision)
- Downloads video using `yt-dlp`
- OpenCV samples one frame every 10 seconds
- Each frame is passed through **YOLOv8 nano model**
- Detects 80+ object types (toys, animals, weapons, etc.)
- Used for: `visualStimulus`, `objectsUsed`, content safety checks

### 3. Score Calculator
- Takes NLP + YOLO results
- Maps them to 8 standardized metrics: **context, cognitive, musicStimulus, visualStimulus, objectsUsed, habitFormingNature, storyMoral, ageGroup**

---

## Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/kids-video-recommender.git
cd kids-video-recommender
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your AssemblyAI API key
```

### 5. Start MongoDB
```bash
mongod --dbpath /data/db
```

### 6. Run the server
```bash
python app.py
```

Open http://localhost:5000 in your browser.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | HTML, CSS, JavaScript | UI, video cards, age filter |
| Styling | Bootstrap 4 | Responsive grid layout |
| Backend | Python + Flask | Web server, API routes |
| Database | MongoDB + PyMongo | Store video URLs and stats |
| NLP | AssemblyAI API | Transcription, safety labels |
| CV | YOLOv8 (Ultralytics) | Object detection in video frames |
| Video | yt-dlp + OpenCV | Download & process YouTube videos |

---

## Safety Metrics

| Metric | Description | Source |
|---|---|---|
| Context | Overall content appropriateness | NLP safety labels + YOLO unsafe objects |
| Cognitive | Educational value | Word count + transcript complexity |
| Music Stimulus | Musical engagement | Sentiment positivity |
| Visual Stimulus | Visual richness | Unique object count per frame |
| Objects Used | Prop diversity | Total distinct YOLO detections |
| Habit Forming | Engagement level | Sentiment + visual diversity |
| Story Moral | Positive messaging | Sentiment + narrative length |
| Age Group | Recommended age | Combined complexity score |

---

## API Keys Required

- **AssemblyAI**: Free tier available at [assemblyai.com](https://assemblyai.com) — 5 hours free transcription/month
- **MongoDB**: Run locally for free (no cloud account needed)
