"""
utils/yolo_helper.py - YOLOv8 Object Detection
================================================
Downloads video frames from YouTube and runs YOLOv8 object detection.

What it does:
  1. Downloads the video using yt-dlp (video format, not audio)
  2. Uses OpenCV to extract frames at regular intervals (every N seconds)
  3. Passes each frame through YOLOv8 model
  4. Collects all detected object class names across all frames
  5. Returns a list of unique detected objects

Why YOLO for a kids video app?
  - Detects weapons, inappropriate objects → flag unsafe content
  - Detects toys, animals, letters → confirm age-appropriate content
  - Counts unique object types → contributes to "objectsUsed" score
"""

from ultralytics import YOLO
import cv2
import yt_dlp
import os
import tempfile


# Load pretrained YOLOv8 nano model (small + fast, good for CPU)
# Downloads automatically on first run (~6MB)
model = YOLO("yolov8n.pt")

# Objects that are SAFE / educational for children
SAFE_OBJECTS = {
    "teddy bear", "book", "apple", "banana", "orange", "cat", "dog",
    "bird", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "bottle", "cup", "bowl",
    "potted plant", "clock", "vase", "scissors", "toothbrush"
}

# Objects that are UNSAFE for children
UNSAFE_OBJECTS = {
    "knife", "gun", "pistol", "rifle", "sword", "bomb"
}


def download_video(video_url: str, output_path: str) -> str:
    """
    Downloads the video (not audio) using yt-dlp.
    Uses lowest quality to save bandwidth.
    """
    ydl_opts = {
        "format": "worst[ext=mp4]/worst",
        "outtmpl": os.path.join(output_path, "%(id)s.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        return os.path.join(output_path, f"{info['id']}.mp4")


def extract_frames(video_path: str, every_n_seconds: int = 10) -> list:
    """
    Extracts one frame every N seconds from the video using OpenCV.
    
    Args:
        video_path      : Path to downloaded video file
        every_n_seconds : Sampling rate (default: every 10 seconds)
    
    Returns:
        List of numpy arrays (frames/images)
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Only capture frames at the interval
        if frame_count % int(fps * every_n_seconds) == 0:
            frames.append(frame)
        frame_count += 1

    cap.release()
    return frames


def detect_objects_in_video(video_url: str) -> dict:
    """
    Main function: Downloads video and detects all objects using YOLO.
    
    Returns:
        {
            "all_objects"    : ["cat", "book", "dog", ...],
            "safe_objects"   : ["cat", "book"],
            "unsafe_objects" : [],
            "unique_count"   : 3,
            "is_safe"        : True
        }
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Download video
        video_path = download_video(video_url, tmpdir)

        # Extract frames
        frames = extract_frames(video_path, every_n_seconds=10)

        # Run YOLO on each frame
        all_detected = set()
        for frame in frames:
            results = model(frame, verbose=False)
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    all_detected.add(class_name)

        # Categorize detected objects
        safe = all_detected.intersection(SAFE_OBJECTS)
        unsafe = all_detected.intersection(UNSAFE_OBJECTS)

        return {
            "all_objects": list(all_detected),
            "safe_objects": list(safe),
            "unsafe_objects": list(unsafe),
            "unique_count": len(all_detected),
            "is_safe": len(unsafe) == 0
        }
