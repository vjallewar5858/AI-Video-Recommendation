/**
 * static/script.js - Frontend Logic
 * ===================================
 * Runs entirely in the browser. Responsible for:
 *   1. Rendering video cards from the hardcoded videoData array
 *   2. Sending each video URL to the Python backend (/api/analyze)
 *   3. Updating video cards with live AI-generated stats
 *   4. Filtering cards by age group
 *
 * Connection to backend:
 *   - Uses fetch() to call Flask API at /api/analyze (POST)
 *   - Backend runs YOLO + AssemblyAI and returns stats JSON
 *   - This file then injects those stats into the card HTML
 */

// ─── Static Video Data ────────────────────────────────────────────────────────
// Preloaded stats shown BEFORE the AI finishes analyzing.
// These get REPLACED by real AI results once /api/analyze responds.
var videoData = [
  {
    url: "https://www.youtube.com/watch?v=cqya9HC8eL0",
    stats: { context: "GOOD", cognitive: "OK", musicStimulus: 8, visualStimulus: 7, objectsUsed: 9, habitFormingNature: 8, storyMoral: 6, ageGroup: "4-6 years" }
  },
  {
    url: "https://www.youtube.com/watch?v=vTlx-pmjTkM",
    stats: { context: "EXCELLENT", cognitive: "GOOD", musicStimulus: 9, visualStimulus: 8, objectsUsed: 10, habitFormingNature: 9, storyMoral: 8, ageGroup: "2-4 years" }
  },
  {
    url: "https://www.youtube.com/watch?v=itj3E4x2nR0",
    stats: { context: "GOOD", cognitive: "GOOD", musicStimulus: 7, visualStimulus: 6, objectsUsed: 8, habitFormingNature: 7, storyMoral: 5, ageGroup: "6-8 years" }
  },
  {
    url: "https://www.youtube.com/watch?v=Nwva3SQ8UTk",
    stats: { context: "OK", cognitive: "GOOD", musicStimulus: 6, visualStimulus: 7, objectsUsed: 7, habitFormingNature: 6, storyMoral: 4, ageGroup: "4-6 years" }
  },
  {
    url: "https://www.youtube.com/watch?v=t0Q2otsqC4I",
    stats: { context: "EXCELLENT", cognitive: "EXCELLENT", musicStimulus: 9, visualStimulus: 9, objectsUsed: 10, habitFormingNature: 9, storyMoral: 8, ageGroup: "2-4 years" }
  },
  {
    url: "https://www.youtube.com/watch?v=sHrHjZA-bds",
    stats: { context: "GOOD", cognitive: "OK", musicStimulus: 7, visualStimulus: 6, objectsUsed: 8, habitFormingNature: 7, storyMoral: 5, ageGroup: "4-6 years" }
  },
  {
    url: "https://www.youtube.com/watch?v=5oH9Nr3bKfw",
    stats: { context: "EXCELLENT", cognitive: "GOOD", musicStimulus: 8, visualStimulus: 9, objectsUsed: 9, habitFormingNature: 8, storyMoral: 7, ageGroup: "2-4 years" }
  }
];

// ─── Utility Functions ────────────────────────────────────────────────────────

function getVideoID(url) {
  /** Extracts YouTube video ID from a URL (e.g. "dQw4w9WgXcQ") */
  var id = url.split("v=")[1];
  if (id) {
    var amp = id.indexOf("&");
    if (amp !== -1) id = id.substring(0, amp);
  }
  return id;
}

function contextBadgeClass(value) {
  /** Returns Bootstrap badge color based on context label */
  return { EXCELLENT: "badge-success", GOOD: "badge-primary", OK: "badge-warning", POOR: "badge-danger" }[value] || "badge-secondary";
}

function buildStatsHTML(stats) {
  /** Returns the inner HTML for the stats panel shown on hover */
  return `
    <span class="badge ${contextBadgeClass(stats.context)} mb-1">Context: ${stats.context}</span>
    <span class="badge ${contextBadgeClass(stats.cognitive)} mb-1">Cognitive: ${stats.cognitive}</span>
    <p>🎵 Music Stimulus: ${stats.musicStimulus}/10</p>
    <p>👁️ Visual Stimulus: ${stats.visualStimulus}/10</p>
    <p>🧸 Objects Used: ${stats.objectsUsed}/10</p>
    <p>🔄 Habit Forming: ${stats.habitFormingNature}/10</p>
    <p>📖 Story Moral: ${stats.storyMoral}/10</p>
    <p>🧒 Age Group: ${stats.ageGroup}</p>
  `;
}

// ─── Render Video Cards ───────────────────────────────────────────────────────

function generateVideoCards() {
  /**
   * Creates a video card for each item in videoData and injects into the DOM.
   * Each card has:
   *   - A thumbnail linked to YouTube
   *   - A stats overlay (shown on hover via CSS)
   *   - A data-age attribute for filtering
   */
  var feed = document.getElementById("videoFeed");
  var html = "";

  videoData.forEach(function(data) {
    var vid = getVideoID(data.url);
    var thumb = `https://img.youtube.com/vi/${vid}/maxresdefault.jpg`;

    html += `
      <div class="col mb-4">
        <div class="video-card" data-age="${data.stats.ageGroup}" data-url="${data.url}">
          <a href="${data.url}" target="_blank">
            <div class="thumbnail">
              <img src="${thumb}" class="img-fluid" alt="Video Thumbnail"
                onerror="this.style.display='none'">
            </div>
          </a>
          <div class="video-stats">
            <div class="stats-loading">⏳ Analyzing with AI...</div>
            <div class="stats-content" style="display:none">
              ${buildStatsHTML(data.stats)}
            </div>
          </div>
        </div>
      </div>
    `;
  });

  feed.innerHTML = html;

  // Show preloaded stats immediately
  document.querySelectorAll(".video-card").forEach(function(card) {
    card.querySelector(".stats-loading").style.display = "none";
    card.querySelector(".stats-content").style.display = "block";
  });
}

// ─── AI Analysis Queue ────────────────────────────────────────────────────────

function analyzeVideos() {
  /**
   * Sends each video URL to Flask /api/analyze one at a time (queue).
   * When a response comes back, it updates that card's stats with real AI data.
   * Processing one-at-a-time prevents overwhelming the server.
   */
  var queue = videoData.map(v => v.url);

  function processNext() {
    if (queue.length === 0) return;
    var url = queue.shift();

    // Show loading state for this card
    var card = document.querySelector(`.video-card[data-url="${url}"]`);
    if (card) {
      card.querySelector(".stats-content").style.display = "none";
      card.querySelector(".stats-loading").style.display = "block";
    }

    // POST to Flask backend → Python AI pipeline
    fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ videoURL: url })
    })
    .then(res => res.json())
    .then(result => {
      updateVideoCard(url, result);
      processNext(); // Move to next in queue
    })
    .catch(err => {
      console.error("Analysis failed for", url, err);
      processNext(); // Continue even if one fails
    });
  }

  processNext();
}

function updateVideoCard(url, stats) {
  /** Finds the card by URL and replaces placeholder stats with AI results */
  var card = document.querySelector(`.video-card[data-url="${url}"]`);
  if (!card) return;

  card.querySelector(".stats-loading").style.display = "none";
  var content = card.querySelector(".stats-content");
  content.innerHTML = buildStatsHTML(stats);
  content.style.display = "block";
  card.dataset.age = stats.ageGroup; // Update age for filtering
}

// ─── Age Group Filtering ──────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll(".filter-btn").forEach(function(btn) {
    btn.addEventListener("click", function() {
      document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      this.classList.add("active");

      var selectedAge = this.dataset.age;
      document.querySelectorAll(".video-card").forEach(function(card) {
        var cardAge = card.dataset.age;
        card.closest(".col").style.display =
          (selectedAge === "all" || cardAge === selectedAge) ? "block" : "none";
      });
    });
  });
});

// ─── Initialize ───────────────────────────────────────────────────────────────
generateVideoCards();   // Step 1: Render cards with preloaded stats
analyzeVideos();        // Step 2: Trigger AI analysis in background
