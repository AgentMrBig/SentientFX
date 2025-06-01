"""
signal_generator.py  •  SentientFX Bridge
-----------------------------------------------------------
Watches market_snapshot.json, evaluates simple MA-/BB-based
rules, and writes signal.json for the downstream order router.
"""

import json
import os
import time
from typing import Dict, List

# ----------------------------------------------------------
# CONFIG
# ----------------------------------------------------------
SNAPSHOT_PATH   = "../data/market_snapshot.json"   # produced by streamer
SIGNAL_PATH     = "../data/signal.json"            # published by this script
POLL_INTERVAL   = 5                                # seconds between checks

# ----------------------------------------------------------
# STATE (persisted only in memory)
# ----------------------------------------------------------
last_timestamp: str | None = None
last_above_ma: bool | None = None


# ----------------------------------------------------------
# UTILITIES
# ----------------------------------------------------------
def load_snapshot() -> Dict | None:
    try:
        with open(SNAPSHOT_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def write_signal(payload: Dict):
    with open(SIGNAL_PATH, "w") as f:
        json.dump(payload, f, indent=2)


def evaluate(snap: Dict) -> Dict:
    global last_above_ma

    close     = snap["close"]
    ma10      = snap["ma10"]
    bb_upper  = snap["bb_upper"]
    bb_lower  = snap["bb_lower"]

    reasons: List[str] = []
    signal = "HOLD"

    # --- MA10 cross rule ---
    above_ma = close > ma10
    if last_above_ma is not None and above_ma != last_above_ma:
        if above_ma:
            signal = "BUY"
            reasons.append("ma_cross_up")
        else:
            signal = "SELL"
            reasons.append("ma_cross_down")

    # --- Bollinger band touches ---
    if close <= bb_lower:
        signal = "BUY"
        reasons.append("bb_lower_touch")
    elif close >= bb_upper:
        signal = "SELL"
        reasons.append("bb_upper_touch")

    if not reasons:
        reasons.append("no_rule_triggered")

    # remember for next candle
    last_above_ma = above_ma

    return {
        "timestamp": snap["timestamp"],
        "symbol"   : snap["symbol"],
        "close"    : close,
        "ma10"     : ma10,
        "signal"   : signal,
        "reasons"  : reasons,
    }


# ----------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------
def main():
    global last_timestamp
    print("[Signal] Waiting for snapshots…  (Ctrl-C to quit)")

    while True:
        snap = load_snapshot()
        if not snap:
            time.sleep(POLL_INTERVAL)
            continue

        ts = snap["timestamp"]
        if ts == last_timestamp:
            time.sleep(POLL_INTERVAL)
            continue

        last_timestamp = ts
        payload = evaluate(snap)
        write_signal(payload)

        print(f"[Signal] {ts} → {payload['signal']:4} ({', '.join(payload['reasons'])})")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Signal] Stopped.")
