"""
order_router.py  •  SentientFX Bridge
-----------------------------------------------------------
Monitors signal.json, applies basic risk rules, and appends
order tickets to orders.json for the MT4 EA.

v1 features
-----------
• Max 4 concurrent trades
• Fixed 0.10 lot size
• Skips duplicate-direction signals
• Self-heals if orders.json is empty / corrupt
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List

# ----------------------------------------------------------
# CONFIG
# ----------------------------------------------------------
SIGNAL_PATH        = "../data/signal.json"
ORDERS_PATH        = "../data/orders.json"
POLL_INTERVAL_SEC  = 2
MAX_OPEN_TRADES    = 4
FIXED_LOT          = 0.10

# ----------------------------------------------------------
# STATE
# ----------------------------------------------------------
last_signal_ts: str | None = None
open_trades: List[Dict] = []


# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------
def load_json(path: str):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_orders(orders: List[Dict]):
    with open(ORDERS_PATH, "w") as f:
        json.dump(orders, f, indent=2)


def next_order_id(snap_ts: str, action: str) -> str:
    t = datetime.strptime(snap_ts, "%Y-%m-%d %H:%M:%S")
    return f"{t:%Y%m%d-%H%M%S}-{action}"


# ----------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------
def main():
    global last_signal_ts, open_trades

    # ---------- initialise ledger ----------
    raw = load_json(ORDERS_PATH)
    orders: List[Dict]
    if isinstance(raw, list):
        orders = raw
    else:
        orders = []            # blank or corrupt file – start fresh
        save_orders(orders)

    open_trades = [o for o in orders if o.get("status") not in {"CLOSED", "EXECUTED"}]

    print("[Router] Waiting for signals…  (Ctrl-C to quit)")

    while True:
        sig = load_json(SIGNAL_PATH)
        if not sig:
            time.sleep(POLL_INTERVAL_SEC)
            continue

        sig_ts = sig["timestamp"]
        action = sig["signal"]           # BUY / SELL / HOLD
        symbol = sig["symbol"]

        # --- skip HOLDs or duplicate timestamps ---
        if action == "HOLD" or sig_ts == last_signal_ts:
            time.sleep(POLL_INTERVAL_SEC)
            continue
        last_signal_ts = sig_ts

        # --- skip if same direction as last open trade ---
        if open_trades and open_trades[-1]["action"] == action:
            print(f"[Router] Duplicate {action}; skipping.")
            time.sleep(POLL_INTERVAL_SEC)
            continue

        # --- skip if hitting max open trades ---
        if len(open_trades) >= MAX_OPEN_TRADES:
            print("[Router] Max open trades reached; skipping.")
            time.sleep(POLL_INTERVAL_SEC)
            continue

        # ---------- create order ticket ----------
        ticket = {
            "id":        next_order_id(sig_ts, action),
            "timestamp": sig_ts,
            "symbol":    symbol,
            "action":    action,
            "lot":       FIXED_LOT,
            "status":    "NEW"
        }

        orders.append(ticket)
        open_trades.append(ticket)
        save_orders(orders)

        print(f"[Router] ► Placed {action} ticket {ticket['id']}")
        time.sleep(POLL_INTERVAL_SEC)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Router] Stopped.")
