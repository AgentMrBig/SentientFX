
# SentientFX: SentientFX: Vision-Based Trading with OpenAI

## Overview

This document outlines a proposed architecture for a **live, AI-driven trading system** combining:

- A MetaTrader 4 (MT4) Expert Advisor (EA)
- A headless Python middleware backend (the bridge)
- OpenAI’s API (GPT-based models)

The EA **does not execute trades**. It functions purely as a market data monitor, transmitting real-time information to the backend. The **middleware** analyzes this data, identifies potential setups, and communicates with **OpenAI**, which makes final trade decisions. The middleware then executes the trade based on OpenAI’s command.

---

## System Architecture

### 1. MetaTrader 4 Expert Advisor (EA)
- Collects real-time market data (ticks, OHLCV, indicators, etc.)
- Transmits data to the Python backend at regular intervals (e.g., every 5s or 1min)
- Logs event/state data
- Does **not** perform trade logic or execution

### 2. Python Middleware (Bridge)
- Stateless or state-aware headless backend application
- Receives and stores real-time data from the EA
- Periodically evaluates for potential trade setups
- If a setup is suspected, sends relevant context to OpenAI:
  - Simplified view of market
  - Key technical indicators
  - Nearby support/resistance levels
  - Trade history summary
- Executes trade based on OpenAI’s returned decision
- Logs all actions and results for analysis and feedback

### 3. OpenAI API
- Receives curated market context and responds with:
  - Trading decision (BUY/SELL/WAIT)
  - SL/TP/TSL parameters
  - Confidence score or reasoning (optional)
- Used via GPT-4o `/v1/chat/completions` endpoint
- Supports dynamic decision-making, adaptive strategy logic
- Can be fine-tuned or prompt-engineered based on user feedback

### 4. GPT-4o Vision Integration (Visual Analysis)
- This component is now essential to the strategy.
  - Score trade setups
  - Filter out low-quality or flat-market signals
  - Provide technical labels (e.g., consolidation, breakout, divergence)

#### Benefits:
- Reduces API costs by minimizing bad/inactive prompts
- Provides an intuitive way for OpenAI to see the market and make visual decisions

---

## System Flow

```
[MT4 EA] 
    → (Market Data) 
[Python Bridge] 
    → (Setup Detected) 
[Local ML Pre-Filter] → (Optional Scoring) 
    → (Relevant Context) 
[OpenAI API] 
    → (Decision Returned) 
[Bridge Executes Trade] 
    → (Log Result)
```

---

## Cost Estimate – OpenAI API

### Assumptions
- Model: GPT-4o (May 2025 rates)
- Token cost:
  - Input: $5.00 per 1M tokens
  - Output: $15.00 per 1M tokens
- Each request:
  - Input: ~800 tokens
  - Output: ~200 tokens
  - Total: ~1,000 tokens/request

---

### Scenario A: Moderate Activity

- **Requests/day**: 100
- **Tokens/day**: 100,000
- Input: 80,000 tokens → $0.40/day  
- Output: 20,000 tokens → $0.30/day  
**Daily Cost**: ~$0.70  
**Monthly Cost**: ~$21  

---

### Scenario B: High Frequency

- **Requests/day**: 300  
- **Tokens/day**: 300,000  
- Input: 240,000 tokens → $1.20/day  
- Output: 60,000 tokens → $0.90/day  
**Daily Cost**: ~$2.10  
**Monthly Cost**: ~$63  

---

## Summary Table

| Component        | Role                                                      |
|------------------|-----------------------------------------------------------|
| MT4 EA           | Market observer, sends data to backend                    |
| Python Bridge    | Middleware layer, handles execution and trade management  |
| OpenAI API       | Makes final trade decisions based on context and visuals  |
| GPT-4o Vision    | Analyzes chart screenshots to detect patterns and setups  |

| Metric               | Estimate (Moderate Use) |
|----------------------|-------------------------|
| API Requests/day     | 100–300                 |
| Tokens/request       | ~1,000                  |
| Daily API Cost       | ~$0.70 – $2.10          |
| Monthly Estimate     | ~$21 – $63              |

---

## Future Expansion Ideas

- Integrate **GPT-4o Vision** to analyze chart screenshots
- Use **Reinforcement Learning** or **fine-tuning** based on trade outcomes
- Implement **sentiment analysis** using news/headlines
- Design **risk-controlled feedback loops** to adjust trading confidence
- Add **live session analytics** dashboard for strategy oversight


---

## Vision Integration with GPT-4o (Chart-Based Trade Analysis)

### Purpose

Enhance trade decision-making by leveraging GPT-4o Vision to analyze **live chart screenshots** instead of processing raw data manually through complex local ML models.

### Benefits

- **Fast integration**: No training required, just send chart screenshots.
- **Context-aware**: Understands patterns, indicators, trendlines, and annotations visually.
- **Flexible prompting**: Ask trading-specific questions like "Is this a breakout?" or "Where is support forming?"
- **Reduced Dev Overhead**: Avoids custom model training and OCR pipelines.
- **Natural language output**: Receive responses like “The price is breaking below support” or “This is a bearish engulfing candle.”

### Implementation Plan

1. **Capture Chart Image**
   - Use Python (e.g., PyAutoGUI, OpenCV) to take automated screenshots from MT4 or TradingView web interface.
   - Crop or mark areas of interest (optional).

2. **Send Image to GPT-4o Vision API**
   - Use OpenAI API with `"model": "gpt-4o"` and include the screenshot in `image_url` format (base64-encoded if local).

3. **Prompt Design**
   Example Prompt:
   ```json
   {
     "model": "gpt-4o",
     "messages": [
       {"role": "system", "content": "You are a forex trading assistant."},
       {"role": "user", "content": [
         {"type": "text", "text": "This is the current USDJPY 1-min chart. Is this a valid short setup?"},
         {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}  
       ]}
     ]
   }
   ```

4. **Bridge Handles Interpretation**
   - Parses GPT-4o’s response and maps it to trade logic (e.g., execute trade, wait, confirm setup).
   - Logs decision and image for backtesting or post-analysis.

### Future Use Cases

- Visual SL/TP placement suggestions
- Pattern labeling (“triple top”, “bullish flag”)
- Risk-to-reward estimation using chart visuals



---

## Implementation Plan

This section outlines the step-by-step architecture and logic of how the trading bridge will operate, communicate with OpenAI, and make trading decisions.

### 1. Market Data Handling (from EA to Bridge)
- The MT4 EA continuously sends market data to the bridge — either per tick or per completed candle.
- This includes:
  - Timestamp
  - OHLC values
  - 10MA value
  - Bollinger Band upper/lower
  - Volume and volatility metrics
  - Custom SR levels (calculated or sent from EA)

- The bridge **writes this data to a structured file or buffer** (e.g., JSON, SQLite, or flat file) for analysis.

### 2. Setup Sampling Logic
- The bridge checks the updated market data periodically (e.g., every 10 seconds or once per candle close).
- It scans for the following **confluence conditions**:
  - Price is near support/resistance level
  - Spike in volume or volatility
  - Bollinger Band expansion/contraction
  - Price crossing or trending above/below the 10MA

- **If two or more confluences are met**, the data is flagged as a potential setup, and visual/chart analysis is initiated.

### 3. Chart Generation (or Capture)
- The bridge prepares a visual snapshot of the current market:
  - **Option A (Preferred)**: Runs a TradingView widget in a browser (headless or visible) and takes a screenshot.
  - **Option B**: Builds a D3.js or Matplotlib chart based on live data.

### ❓ Side Note: Can ChatGPT View a Web Address?
No — GPT-4o Vision cannot browse to a web address or render a live widget. You must **send it a static image** (screenshot or base64-encoded file). Therefore, capturing a **rendered chart screenshot** is the best method for vision input.

---

### 4. GPT-4o Vision Request

- The bridge constructs a message payload:
  - Prompt: “This is the current USDJPY 1m chart. Is this a good opportunity to sell? Reply only with the decision type and reasoning.”
  - Image: Chart screenshot

- The OpenAI API call includes this prompt and the image, and the model responds.

---

### 5. Shaped Response Design (for GPT-4o)

- To ensure reliability, we **train GPT-4o to respond in a strict format** the bridge can parse.

**Expected format from GPT-4o:**

```json
{
  "decision": "SELL", 
  "confidence": "HIGH", 
  "reason": "Price broke support and is trending below the 10MA."
}
```

- We will reinforce this response style through **prompt engineering and few-shot examples**.
- The bridge will validate the structure, and if malformed, discard or request retry.

---

### 6. Bridge Execution Logic

- If GPT-4o returns a valid "BUY" or "SELL" signal with acceptable confidence:
  - The bridge calculates lot size, SL, TP (if needed)
  - Executes the trade through the MT4 EA interface (e.g., command queue or file pipe)
  - Logs the trade for performance tracking and feedback

- If decision is “WAIT” or “UNSURE”:
  - No action taken
  - Log reason and store image/context for future learning

---

### Summary Flow

1. EA → Market data → Bridge
2. Bridge → Analyzes for confluence
3. Bridge → Captures chart
4. Bridge → Sends prompt + image to OpenAI
5. GPT-4o → Responds with shaped JSON
6. Bridge → Parses → Executes via EA (or ignores)



---

## Trade Decision Format Spec

To ensure reliable bridge automation and clear trade logic, GPT-4o Vision responses must follow this exact structured JSON format.

This response includes not only the trade direction, but also suggested price levels for take profit, stop loss, and nearby support/resistance zones. The structure is designed to help the bridge place and manage trades without ambiguity.

### 📤 Expected GPT-4o Response Format

```json
{
  "decision": "BUY | SELL | WAIT | UNSURE",
  "TPLV1": "target price 1",
  "TPLV2": "target price 2 (optional second TP)",
  "SLLV": "stop loss price",
  "critSupport": "important nearby support level",
  "critResistance": "important nearby resistance level",
  "confidence": "LOW | MEDIUM | HIGH",
  "reason": "Short explanation of the setup and why the decision was made"
}
```

---

### 🧠 Example Response from GPT-4o

```json
{
  "decision": "BUY",
  "TPLV1": "155.245",
  "TPLV2": "155.528",
  "SLLV": "154.763",
  "critSupport": "155.234",
  "critResistance": "155.245",
  "confidence": "MEDIUM",
  "reason": "1-minute chart shows a breakout above resistance with rising volume. 5m and 15m charts show uptrend continuation. 1-hour confirms bullish bias but near resistance, so confidence is moderate."
}
```

This response format is now the standard that the bridge will parse. GPT-4o will be guided via prompt engineering to return responses only in this form.


---

## Project Directory Structure

```
sentientfx/
├── bridge/
│   ├── __init__.py
│   ├── bridge_main.py              # Main loop to handle EA data + OpenAI call
│   ├── vision_prompt.py            # GPT-4o prompt builder + response parser
│   ├── trade_executor.py           # Handles trade execution (write to EA file)
│   ├── market_data_analyzer.py     # Confluence detection logic
│   └── config.py                   # Bridge settings (timings, thresholds)
│
├── ea/
│   └── VisionBridgeEA.mq4          # The MT4 EA that sends data and receives signals
│
├── charts/
│   ├── chart_capture.py            # Captures or builds screenshots for vision API
│   └── tradingview_widget_server/  # Web server for rendering TradingView widget
│       ├── static/
│       ├── templates/
│       ├── app.py
│       └── capture.py
│
├── logs/
│   └── trade_logs.csv              # Executed trades
│
├── data/
│   ├── market_stream.json          # Live feed from EA
│   └── snapshots/                  # Saved images sent to OpenAI
│
├── docs/
│   └── SentientFX_Architecture.md  # Full system design and strategy
│
├── README.md                       # Project overview and usage instructions
├── .env                            # OpenAI API keys and config
└── requirements.txt                # Python dependencies
```

---

This updated structure reflects the expanded scope of the SentientFX system, including the TradingView-based chart rendering server and full integration with GPT-4o Vision for multi-timeframe trade evaluation.



---

## New Logging and Data Components

The following files and utilities are used for testing, trade logging, and simulation:

### `data/market_stream.json`
Stores the latest market data sent from the EA. This is the main input used by the bridge to detect setups.

### `data/orders.json`
This file is written by the bridge (or manually during testing) and read by the EA. It contains a pending trade order in JSON format.

### `logs/trade_logs.csv`
Logs every bridge action, including trade decisions, skipped trades, or errors. The file is in CSV format for easy analysis.

### `bridge/log_utils.py`
Utility used throughout the bridge to write logs. It appends to `trade_logs.csv` with timestamps and custom messages.

```python
from bridge.log_utils import write_log

write_log("SetupDetected", "Confluence met for USDJPY")
```

---

## Development Note

The `sentientfx_bridge.py` script can be tested using these files directly. After confirming the EA executes trades correctly from `orders.json`, the entire system can be integrated for live testing.

Next Steps:
- Add `write_log()` to all major bridge steps
- Create `run_dev.py` to simulate the pipeline
- Begin preparing for Vision testing scenarios

