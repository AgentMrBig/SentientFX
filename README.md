_Historical design notes and cost estimates can be found in **docs/Vision_Concept_and_Costs_2024-11.md**._





# SentientFX – System Architecture Overview  
*(technical design document – version 0.1, 2025‑06‑01)*  

---

## 1 · Context & Purpose  
SentientFX is a modular trading‐automation project that merges **rule‑based execution** with **vision‑driven pattern recognition**.  
The architecture purposely splits into two *independent but converging* tracks so that either stream can evolve or be swapped out without disrupting the other.

---

## 2 · High‑Level Data Flow  

```
                +-----------------------+
                | CSV or Live MarketFeed|
                +-----------+-----------+
                            |
                            v
                market_snapshot.json  (1‑min candles + indicators)
                            |
        +-------------------+--------------------+
        |                                        |
        v                                        v
 RULE‑BASED TRACK                        VISION TRACK (future)
 (Edge detection)                        (Chart → Image → AI)
  ─────────────────                      ─────────────────────
 simulate_market_stream.py               chart_renderer.py
     |                                   (D3 / canvas)
     v                                           |
 signal_generator.py                             |
     |                                   screenshot_grabber.py
     v                                           |
 order_router.py                                 v
     |                                  chart_analyzer.py (OpenAI Vision)
     +-------------> orders.json <--------------+
                       (tickets for MT4 EA)
```

*Both tracks consume the same **`market_snapshot.json`** feed; they publish **signals** that ultimately converge into **`orders.json`**, which the MT4 Expert Advisor executes.*

---

## 3 · Components by Track  

### 3.1 Rule‑Based Execution Stack  
| File | Role |
|------|------|
| **simulate_market_stream.py** | Replays 1‑minute USDJPY candles from CSV, writes `market_snapshot.json`. |
| **signal_generator.py** | Applies MA‑cross & Bollinger‑band rules, outputs BUY/SELL/HOLD to `signal.json`. |
| **order_router.py** | Enforces risk logic (max 4 trades, duplicate‑direction guard, fixed 0.10 lot) and appends tickets to `orders.json`. |
| **MT4 EA** (external) | Reads `orders.json`, executes trades, updates ticket status (`EXECUTED` / `CLOSED`). |

### 3.2 Vision‑Driven Analysis Stack (to‑be‑built)  
| Planned File | Role |
|--------------|------|
| **chart_renderer.py** | Replicates TradingView‑style chart (candles, MA, BB) using D3 or canvas. |
| **screenshot_grabber.py** | Uses Playwright to capture PNGs of the rendered chart at a set cadence. |
| **chart_analyzer.py** | Sends screenshots to OpenAI Vision, extracts pattern commentary or direct trade hints, optionally writes `signal.json` records. |

---

## 4 · JSON Contracts  

### `market_snapshot.json`
```json
{
  "timestamp": "2023-08-18 09:42:00",
  "symbol":    "USDJPY",
  "open":      156.50,
  "high":      156.54,
  "low":       156.48,
  "close":     156.52,
  "volume":    113,
  "ma10":      156.40,
  "bb_upper":  156.70,
  "bb_lower":  156.10,
  "volatility":0.12,
  "near_sr":   true
}
```

### `signal.json`
```json
{
  "timestamp": "2023-08-18 09:42:00",
  "symbol":    "USDJPY",
  "signal":    "BUY",
  "reasons":   ["ma_cross_up"]
}
```

### `orders.json`  (array of tickets)
```json
[
  {
    "id":        "20230818-094200-BUY",
    "timestamp": "2023-08-18 09:42:00",
    "symbol":    "USDJPY",
    "action":    "BUY",
    "lot":       0.10,
    "status":    "NEW"
  }
]
```

---

## 5 · Cold‑Boot Workflow  

| Step | Command (Git Bash) |
|------|--------------------|
| **Activate env** | `cd /c/Users/PcTech/Desktop/FOREXAI/SentientFX && source .venv/Scripts/activate` |
| **Start streamer** | `cd bridge && python simulate_market_stream.py` |
| **Start signal generator** | *new terminal* → env → `python bridge/signal_generator.py` |
| **Start router** | *third terminal* → env → `python bridge/order_router.py` |
| **Start screenshot service** | *forth terminal* (future) → env → `python bridge/screenshot_grabber.py` |
| **Launch EA** | Ensure it monitors `data/orders.json`. |

---

## 6 · Next Development Milestones  

1. **Chart Renderer** – faithful TradingView‑style D3/canvas chart.  
2. **Screenshot Pipeline** – Playwright headless capture, JPG/PNG storage.  
3. **Vision Integration** – OpenAI vision prompt engineering + response parsing.  
4. **Unified Risk Engine** – balance‑scaled lot sizing, trailing SL/TP injection.  
5. **Analytics Dashboard** – equity curve, hit‑rate, and PnL metrics.

---

## 7 · Document Metadata  

| Field | Value |
|-------|-------|
| **Document name** | **`SENTIENTFX_System_Architecture_Overview.md`** |
| **Technical doc type** | *Technical Architecture Overview* |

---
