"""
utils/assemblyai_helper.py - AssemblyAI NLP Integration
=========================================================
Handles audio extraction from YouTube and NLP analysis via AssemblyAI API.

What it does:
  1. Uses yt-dlp to download audio (.mp3) from a YouTube URL
  2. Uploads the audio file to AssemblyAI
  3. Requests transcription WITH content safety detection enabled
  4. Polls AssemblyAI until the job is done
  5. Returns structured NLP results (transcript, sentiment, safety labels)

AssemblyAI Content Safety Labels include:
  - "profanity", "violence", "sensitive_social_issues", "hate_speech", etc.
  - Each label has a confidence score (0.0 to 1.0)
"""

import assemblyai as aai
import yt_dlp
import os
import tempfile


# Set API key from environment variable
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY", "your_api_key_here")


def download_audio(video_url: str, output_path: str) -> str:
    """
    Downloads audio from a YouTube video using yt-dlp.
    
    Args:
        video_url   : Full YouTube URL
        output_path : Directory to save the audio file
    
    Returns:
        Path to the downloaded .mp3 file
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_path, "%(id)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        filename = os.path.join(output_path, f"{info['id']}.mp3")
        return filename


def transcribe_and_moderate(video_url: str) -> dict:
    """
    Main function: Downloads audio and runs AssemblyAI NLP analysis.
    
    Returns a dictionary with:
      - transcript     : Full text transcript
      - sentiment      : "POSITIVE" | "NEGATIVE" | "NEUTRAL"
      - safety_labels  : Dict of content safety labels with confidence scores
      - word_count     : Number of words spoken
      - has_profanity  : Boolean
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Download audio
        audio_path = download_audio(video_url, tmpdir)

        # Step 2: Configure AssemblyAI transcription with safety features
        config = aai.TranscriptionConfig(
            content_safety=True,           # Detect unsafe content
            sentiment_analysis=True,       # Analyze overall sentiment
            auto_chapters=True,            # Understand topic structure
            iab_categories=True,           # Categorize video topic
        )

        # Step 3: Transcribe
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path, config=config)

        # Step 4: Extract safety labels
        safety_labels = {}
        if transcript.content_safety_labels:
            for result in transcript.content_safety_labels.results:
                for label in result.labels:
                    label_name = label.label
                    confidence = label.confidence
                    # Keep highest confidence per label type
                    if label_name not in safety_labels or safety_labels[label_name] < confidence:
                        safety_labels[label_name] = confidence

        # Step 5: Extract overall sentiment
        sentiment = "NEUTRAL"
        if transcript.sentiment_analysis:
            sentiments = [s.sentiment for s in transcript.sentiment_analysis]
            pos = sentiments.count("POSITIVE")
            neg = sentiments.count("NEGATIVE")
            sentiment = "POSITIVE" if pos > neg else ("NEGATIVE" if neg > pos else "NEUTRAL")

        return {
            "transcript": transcript.text or "",
            "sentiment": sentiment,
            "safety_labels": safety_labels,
            "word_count": len((transcript.text or "").split()),
            "has_profanity": safety_labels.get("profanity", 0) > 0.5,
            "has_violence": safety_labels.get("violence", 0) > 0.5,
        }
