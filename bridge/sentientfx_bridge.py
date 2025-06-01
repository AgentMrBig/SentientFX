import os
import time
from bridge.market_data_analyzer import is_trade_setup
from bridge.vision_prompt import request_trade_decision

MARKET_DATA_PATH = "market_data.csv"
CHART_IMAGE_PATH = "chart.png"

def main_loop():
    print("[SentientFX] Vision Bridge Started...")
    while True:
        if not os.path.exists(MARKET_DATA_PATH):
            print("[Bridge] Waiting for market data...")
            time.sleep(5)
            continue

        setup_detected, context = is_trade_setup(MARKET_DATA_PATH)
        if setup_detected:
            print("[Bridge] Setup detected. Capturing chart and querying GPT-4o...")
            result = request_trade_decision(context, CHART_IMAGE_PATH)
            print("[Bridge] GPT-4o Response:", result)
        else:
            print("[Bridge] No setup detected. Waiting...")
        time.sleep(60)  # Check once per minute

if __name__ == "__main__":
    main_loop()
