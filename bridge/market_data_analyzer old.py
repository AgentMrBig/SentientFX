
def is_trade_setup(market_data):
    try:
        # Extract indicators
        price = float(market_data.get("close", 0))
        ma10 = float(market_data.get("ma10", 0))
        upper_bb = float(market_data.get("bb_upper", 0))
        lower_bb = float(market_data.get("bb_lower", 0))
        volume = float(market_data.get("volume", 0))
        sr_proximity = market_data.get("near_sr", False)
        volatility = float(market_data.get("volatility", 0))

        confluences = 0

        # Condition 1: Price above or below 10MA
        if price > ma10 or price < ma10:
            confluences += 1

        # Condition 2: Near support/resistance level
        if sr_proximity:
            confluences += 1

        # Condition 3: Bollinger Band squeeze or breakout
        bb_range = upper_bb - lower_bb
        if bb_range / price < 0.01:  # Bollinger squeeze
            confluences += 1

        # Condition 4: Volume or volatility spike
        if volatility > 0.7:  # Arbitrary threshold
            confluences += 1

        if confluences >= 2:
            return True, {
                "price": price,
                "ma10": ma10,
                "volume": volume,
                "volatility": volatility,
                "confluences": confluences,
                "sr_proximity": sr_proximity
            }

        return False, {}
    except Exception as e:
        print(f"[Analyzer] Error processing market data: {e}")
        return False, {}
