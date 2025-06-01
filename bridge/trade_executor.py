
import json
from pathlib import Path
from bridge.config import ORDER_PATH, MAX_OPEN_TRADES, MIN_LOT, LOT_INCREMENT

def validate_lot_size(lot):
    if lot < MIN_LOT:
        raise ValueError("Lot size below minimum allowed.")
    if round(lot / LOT_INCREMENT, 2) % 1 != 0:
        raise ValueError("Lot size must be in increments of 0.01")

def count_open_trades():
    # Placeholder: You can connect to execution log or count live positions
    return 0  # Replace with logic to track live trades

def execute_trade(decision: dict):
    try:
        if decision["decision"] not in ["BUY", "SELL"]:
            print("[Executor] No valid trade action. Skipping.")
            return

        lot = decision.get("lot", MIN_LOT)
        validate_lot_size(lot)

        if count_open_trades() >= MAX_OPEN_TRADES:
            raise ValueError("Max open trades exceeded.")

        order = {
            "symbol": "USDJPY",  # You can make this dynamic later
            "side": decision["decision"],
            "lot": lot,
            "sl": float(decision["SLLV"]),
            "tp": float(decision["TPLV1"]),
            "slippage": 3  # Configurable
        }

        Path(ORDER_PATH).write_text(json.dumps(order))
        print(f"[Executor] Trade order written to file: {order}")

    except Exception as e:
        print(f"[ERROR] Trade execution failed: {e}")
