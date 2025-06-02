# Vision Feature: Interactive Drawing + AI Chart Interpretation
*(Documented: 2025-06-01 — for future SentientFX development)*

---

## 🎯 Feature Overview

Enable users to **interactively draw trendlines, channels, and S/R zones** directly on the custom chart. When the user is ready, they can **right-click and send the marked-up chart to ChatGPT Vision**, which will analyze the visual annotations in the context of live price action.

---

## 🧩 Components

### 1. Interactive Drawing Layer
- Users can draw:
  - Horizontal S/R lines
  - Trendlines (multi-point anchored)
  - Rectangles (zones or consolidation areas)
- Color-coded and draggable

### 2. Contextual Right-Click Menu
- Appears on canvas right-click
- Options:
  - “Send to ChatGPT for analysis”
  - “Mark as Breakout Watch”
  - “Save as Screenshot Only”

### 3. Snapshot Export with Annotations
- Captures full chart canvas (including drawn objects)
- Saves annotated image
- Calls OpenAI Vision endpoint with:
  - Image
  - Description prompt of what the user is asking for

### 4. Vision Prompt Template
Example:
> “Analyze this chart. The yellow lines are user-drawn support/resistance. The red diagonal lines are trendlines. Are there any patterns or breakouts forming?”

---

## 🧠 ChatGPT Output Possibilities
- Detects visual alignment with:
  - Head and Shoulders
  - Triangles
  - Channels
  - Fakeouts or compression zones
- Suggests:
  - Breakout bias
  - Entry point ideas
  - Whether user should wait or monitor another condition

---

## 🧱 Implementation Stack

| Component         | Tech             |
|------------------|------------------|
| Drawing Layer     | D3.js overlays or Konva.js |
| Right-click logic | JS event capture + custom context menu |
| Screenshot        | HTML2Canvas or Playwright |
| AI Interface      | OpenAI Vision (gpt-4o) |
| Future backend    | Flask server or Electron app option |

---

## 📂 File Plans

- `chart_drawing.js`
- `context_menu.js`
- `chart_analyzer.py`
- `/snapshots/` for saved images
- `vision_requests.log` for GPT instructions/responses

---

## 🔐 Considerations

- Mark images with timestamp + user ID
- Prevent accidental GPT use (confirmation popup)
- Auto-save recent chart state (annotations + last snapshot)

---

## 🗓️ Status

> ❌ Not yet implemented — this document serves as the design blueprint.
> When the base chart is fully interactive and stable, this will become **Milestone: Vision-Assisted Manual Strategy**.