"""
utils/score_calculator.py - Safety Score Engine
=================================================
Combines NLP (AssemblyAI) and Computer Vision (YOLO) results into
the 8 standardized safety metrics shown on the frontend cards.

Scoring Logic:
  - Each metric is scored 1–10 based on weighted inputs
  - "context" and "cognitive" are qualitative labels (EXCELLENT/GOOD/OK/POOR)
  - Numeric metrics (musicStimulus, visualStimulus, etc.) are 1–10 integers
"""


def calculate_context(nlp: dict, vision: dict) -> str:
    """
    Context = overall content appropriateness.
    Based on: safety labels, profanity, violent objects detected.
    """
    if nlp.get("has_profanity") or nlp.get("has_violence") or not vision.get("is_safe"):
        return "POOR"
    
    violence_score = nlp["safety_labels"].get("violence", 0)
    sensitive_score = nlp["safety_labels"].get("sensitive_social_issues", 0)
    
    if violence_score < 0.1 and sensitive_score < 0.1:
        return "EXCELLENT"
    elif violence_score < 0.3 and sensitive_score < 0.3:
        return "GOOD"
    else:
        return "OK"


def calculate_cognitive(nlp: dict) -> str:
    """
    Cognitive = educational value based on vocabulary and content structure.
    Based on: word count, transcript complexity, topic categories.
    """
    word_count = nlp.get("word_count", 0)
    
    if word_count > 500:
        return "EXCELLENT"
    elif word_count > 200:
        return "GOOD"
    elif word_count > 50:
        return "OK"
    else:
        return "POOR"


def calculate_music_stimulus(nlp: dict) -> int:
    """
    Music Stimulus = estimate based on word rhythm patterns and audio energy.
    Proxy: sentiment positivity often correlates with musical content.
    """
    sentiment = nlp.get("sentiment", "NEUTRAL")
    base = 5
    if sentiment == "POSITIVE":
        base += 3
    elif sentiment == "NEUTRAL":
        base += 1
    return min(10, base)


def calculate_visual_stimulus(vision: dict) -> int:
    """
    Visual Stimulus = how visually rich/engaging the video is.
    Based on: number of unique objects detected across frames.
    """
    unique_count = vision.get("unique_count", 0)
    score = min(10, 3 + unique_count)
    return score


def calculate_objects_used(vision: dict) -> int:
    """
    Objects Used = diversity of props/items shown in the video.
    Directly mapped from unique object count.
    """
    unique_count = vision.get("unique_count", 0)
    return min(10, unique_count + 2)


def calculate_habit_forming(nlp: dict, vision: dict) -> int:
    """
    Habit Forming Nature = how engaging/repetitive the content is.
    High = consistent positive sentiment + recurring visual elements.
    """
    score = 5
    if nlp.get("sentiment") == "POSITIVE":
        score += 2
    if vision.get("unique_count", 0) > 5:
        score += 2
    return min(10, score)


def calculate_story_moral(nlp: dict) -> int:
    """
    Story Moral = whether the video conveys a clear positive message.
    Based on: positive sentiment + word count (longer = more structured story).
    """
    score = 4
    if nlp.get("sentiment") == "POSITIVE":
        score += 3
    word_count = nlp.get("word_count", 0)
    if word_count > 300:
        score += 2
    elif word_count > 100:
        score += 1
    return min(10, score)


def determine_age_group(nlp: dict, vision: dict) -> str:
    """
    Determines recommended age group based on content complexity.
    """
    word_count = nlp.get("word_count", 0)
    unique_objects = vision.get("unique_count", 0)
    
    if word_count < 100 and unique_objects < 5:
        return "0-2 years"
    elif word_count < 250:
        return "2-4 years"
    elif word_count < 500:
        return "4-6 years"
    else:
        return "6-8 years"


def calculate_scores(nlp_results: dict, vision_results: dict) -> dict:
    """
    Master function that combines all individual scoring functions.
    
    Args:
        nlp_results    : Output from assemblyai_helper.transcribe_and_moderate()
        vision_results : Output from yolo_helper.detect_objects_in_video()
    
    Returns:
        Complete stats dictionary matching the frontend card format:
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
    return {
        "context": calculate_context(nlp_results, vision_results),
        "cognitive": calculate_cognitive(nlp_results),
        "musicStimulus": calculate_music_stimulus(nlp_results),
        "visualStimulus": calculate_visual_stimulus(vision_results),
        "objectsUsed": calculate_objects_used(vision_results),
        "habitFormingNature": calculate_habit_forming(nlp_results, vision_results),
        "storyMoral": calculate_story_moral(nlp_results),
        "ageGroup": determine_age_group(nlp_results, vision_results)
    }
