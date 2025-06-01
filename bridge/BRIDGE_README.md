# SentientFX — **Bridge Module Documentation**
*(last updated 2025‑06‑01)*  

---

## 1. Purpose of the Bridge
The **bridge** stitches three worlds together:

| World | Direction | Exchange Format |
|-------|-----------|-----------------|
| **Historical CSV / live feed** | → | `market_snapshot.json` |
| **Signal logic** (edge detection) | ↔ | `signal.json` |
| **Execution layer** (MT4 EA) | ←→ | `orders.json` |

It lets you swap in new data sources, trading rules, or execution platforms without rewriting everything.

---

## 2. Bridge Directory Layout
```text
SentientFX/
├── .venv/                       (# virtual environment)
├── bridge/
│   ├── simulate_market_stream.py
│   ├── signal_generator.py
│   └── order_router.py
└── data/
    ├── usdjpy_m1.csv            (# raw historical feed)
    ├── market_snapshot.json     (# latest candle + indicators)
    ├── market_snapshot_history.json
    ├── signal.json              (# latest trading signal)
    └── orders.json              (# order tickets for EA)
```

---

## 3. File‑by‑File Breakdown

| File | Role | Why it exists |
|------|------|---------------|
| **`simulate_market_stream.py`** | Streams 1‑min candles from `usdjpy_m1.csv` → **`market_snapshot.json`** every 60 s. | Replays history in real‑time so the rest of the stack can work unmodified. |
| **`signal_generator.py`** | Polls snapshots, applies MA‑cross & Bollinger‑band rules, writes **`signal.json`** (BUY/SELL/HOLD + reasons). | Encapsulates strategy logic so you can iterate without touching execution code. |
| **`order_router.py`** | Watches signals, enforces risk limits (max 4 open trades, duplicate‑direction guard, fixed 0.10 lot v1), appends **`orders.json`** for the MT4 EA. | Decouples risk & trade management from signal detection; keeps EA stateless. |

---

## 4. JSON Schemas

### 4.1 `market_snapshot.json`
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

### 4.2 `signal.json`
```json
{
  "timestamp": "2023-08-18 09:42:00",
  "symbol":    "USDJPY",
  "close":     156.52,
  "ma10":      156.40,
  "signal":    "BUY",
  "reasons":   ["ma_cross_up"]
}
```

### 4.3 `orders.json`
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

## 5. Cold‑Boot Sequence
| Step | Command (Git Bash) |
|------|--------------------|
| Activate env | `cd /c/Users/PcTech/Desktop/FOREXAI/SentientFX`<br>`source .venv/Scripts/activate` |
| Start streamer | `cd bridge && python simulate_market_stream.py` |
| Start signal generator | **new terminal** → same env → `python bridge/signal_generator.py` |
| Start router | **third terminal** → same env → `python bridge/order_router.py` |
| Launch EA | Ensure it watches `data/orders.json` and updates ticket status. |

---

## 6. Future Enhancements
| Area | Planned upgrade |
|------|-----------------|
| Risk engine | ATR‑scaled lot sizing, SL/TP, equity draw‑down guard |
| S/R detection | Populate `near_sr` + zone strength, feed into signals |
| Order lifecycle | Router marks tickets CLOSED when EA exits trades |
| Analytics | Equity curve, PnL dashboard |
| Live feed | Swap CSV replay for broker WebSocket or REST |

---

## 7. Changelog
| Date | Change |
|------|--------|
| 2025‑06‑01 | Initial stable trio (`simulate_market_stream.py`, `signal_generator.py`, `order_router.py`). |
