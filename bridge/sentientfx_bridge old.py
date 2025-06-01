
import time
import json
from pathlib import Path
from bridge.market_data_analyzer import is_trade_setup
from bridge.vision_prompt import request_trade_decision
from bridge.trade_executor import execute_trade
from charts.chart_capture import capture_tradingview_chart
from bridge.config import (
    DATA_PATH,
    CHECK_INTERVAL_SECONDS,
    MIN_CONFIDENCE,
    IMAGE_CAPTURE_PATH,
)

def load_latest_market_data():
    try:
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read market data: {e}")
        return None

def main_loop():
    print("[SentientFX] Vision Bridge Started...")
    while True:
        market_data = load_latest_market_data()
        if not market_data:
            time.sleep(CHECK_INTERVAL_SECONDS)
            continue

        setup_detected, context = is_trade_setup(market_data)
        if setup_detected:
            print("[Bridge] Setup detected. Capturing chart and querying GPT-4o...")
            capture_tradingview_chart("http://localhost:5000", IMAGE_CAPTURE_PATH)
            decision = request_trade_decision(context, IMAGE_CAPTURE_PATH)
            if decision:
                if decision.get("confidence", "").upper() in MIN_CONFIDENCE:
                    print(f"[Bridge] Trade decision: {decision['decision']} (confidence: {decision['confidence']})")
                    execute_trade(decision)
                else:
                    print("[Bridge] Low confidence. Skipping trade.")
            else:
                print("[Bridge] GPT-4o did not return a decision.")
        else:
            print("[Bridge] No valid setup at this time.")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main_loop()
