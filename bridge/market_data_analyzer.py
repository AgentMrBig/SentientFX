import csv

def is_trade_setup(market_data_path):
    try:
        with open(market_data_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)[-20:]  # analyze the last 20 candles

        closes = [float(row["close"]) for row in rows if row["close"]]
        if len(closes) < 2:
            return False, {}

        ma = sum(closes) / len(closes)
        current_price = closes[-1]

        if current_price > ma:
            return True, {
                "trend": "up",
                "ma": ma,
                "current_price": current_price
            }
        elif current_price < ma:
            return True, {
                "trend": "down",
                "ma": ma,
                "current_price": current_price
            }
        else:
            return False, {}

    except Exception as e:
        print(f"[Analyzer] Error: {e}")
        return False, {}
