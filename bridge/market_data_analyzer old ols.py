
def is_trade_setup(market_data: dict) -> bool:
    try:
        # Extract relevant values
        close = float(market_data.get("close"))
        ma_10 = float(market_data.get("ma_10"))
        bb_middle = float(market_data.get("bb_middle"))  # center line of BB = usually 20SMA
        bb_upper = float(market_data.get("bb_upper"))
        bb_lower = float(market_data.get("bb_lower"))
        volume = float(market_data.get("volume", 0))

        # Memory store of last MA vs BB position for crossover detection
        # In practice, you’d manage state or pass in recent values — this is a placeholder
        with open("data/prev_ma_crossover.json", "r") as f:
            prev = eval(f.read())
        prev_cross = prev.get("above_bb_center")

        current_cross = ma_10 > bb_middle

        crossover_detected = (
            prev_cross is not None and  # must have previous value
            prev_cross != current_cross  # crossover happened
        )

        price_outside_bands = close > bb_upper or close < bb_lower
        significant_volume = volume > 500  # you can tune this threshold

        # Save current state
        with open("data/prev_ma_crossover.json", "w") as f:
            f.write(str({"above_bb_center": current_cross}))

        if crossover_detected and price_outside_bands and significant_volume:
            print("[Analyzer] Confluence met: MA/BB crossover + breakout + volume")
            return True

    except Exception as e:
        print(f"[Analyzer] Error: {e}")

    return False
