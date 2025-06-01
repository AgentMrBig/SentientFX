import pandas as pd
import time
import json
import os
from typing import List

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
DATA_PATH       = "../data/usdjpy_m1.csv"           # historical 1-min candles
SNAPSHOT_PATH   = "../data/market_snapshot.json"    # latest tick for the bridge
HISTORY_PATH    = "../data/market_snapshot_history.json"
ROLLING_WINDOW  = 20                                # candles to keep in memory
SLEEP_SECONDS   = 60                                # real-time delay
# ---------------------------------------------------------------------

def find_cols(cols: List[str]):
    """Return sensible names for date & time columns, whatever the CSV uses."""
    cols_lower = [c.lower().strip() for c in cols]
    date_col = next((c for c in cols_lower if c in {"date", "day"}), None)
    time_col = next((c for c in cols_lower if c in {"time", "timestamp", "datetime"}), None)
    return date_col, time_col

def load_history() -> list:
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[Simulator] Warning: history file unreadable – starting fresh.")
    return []

def main():
    # --------------------------------------------------------------
    # 1)  LOAD + CLEAN RAW DATA
    # --------------------------------------------------------------
    raw = pd.read_csv(DATA_PATH)
    raw.columns = [c.lower().strip() for c in raw.columns]           # normalise headers

    date_col, time_col = find_cols(raw.columns)
    if not time_col:
        raise ValueError("Could not locate a time/timestamp column in CSV")

    if date_col:   # separate date + time columns
        raw["timestamp"] = pd.to_datetime(
            raw[date_col].astype(str) + " " + raw[time_col].astype(str),
            errors="coerce"
        )
    else:          # timestamp/datetime column already contains full string
        raw["timestamp"] = pd.to_datetime(raw[time_col], errors="coerce")

    # Whitelist essential OHLCV fields
    df = raw[["timestamp", "open", "high", "low", "close", "volume"]].copy()
    df = df.ffill()

    # Ensure no leftover indicator columns if CSV already had them
    indicator_cols = {"ma10", "bb_upper", "bb_lower", "volatility"}
    df.drop(columns=[c for c in df.columns if c in indicator_cols], inplace=True, errors="ignore")

    print("[Simulator] Starting market data simulation…")

    history = load_history()

    # --------------------------------------------------------------
    # 2)  MAIN LOOP – one candle each minute
    # --------------------------------------------------------------
    for i in range(ROLLING_WINDOW, len(df)):
        slice_df = df.iloc[i - ROLLING_WINDOW : i].copy()

        # ----- indicator calculation -----
        slice_df["ma10"]       = slice_df["close"].rolling(10).mean()
        ma20                   = slice_df["close"].rolling(20).mean()
        std20                  = slice_df["close"].rolling(20).std()
        slice_df["bb_upper"]   = ma20 + 2 * std20
        slice_df["bb_lower"]   = ma20 - 2 * std20
        slice_df["volatility"] = std20

        latest = slice_df.iloc[-1]

        # ----- timestamp handling -----
        ts_obj = latest["timestamp"]
        if not isinstance(ts_obj, pd.Timestamp) or pd.isna(ts_obj):
            print(f"[Simulator] Bad timestamp – skipping row ({ts_obj})")
            time.sleep(1)     # tiny pause so we don't spam
            continue
        ts_str = ts_obj.strftime("%Y-%m-%d %H:%M:%S")

        # ----- snapshot build -----
        snap = {
            "timestamp" : ts_str,
            "symbol"    : "USDJPY",
            "open"      : round(latest["open"], 2),
            "high"      : round(latest["high"], 2),
            "low"       : round(latest["low"], 2),
            "close"     : round(latest["close"], 2),
            "volume"    : int(latest["volume"]),
            "ma10"      : round(latest["ma10"], 2),
            "bb_upper"  : round(latest["bb_upper"], 2),
            "bb_lower"  : round(latest["bb_lower"], 2),
            "volatility": round(latest["volatility"], 2),
            "near_sr"   : True   # TODO: future S/R detection
        }

        # ----- write current + history -----
        with open(SNAPSHOT_PATH, "w") as f:
            json.dump(snap, f, indent=2)

        history.append(snap)
        with open(HISTORY_PATH, "w") as f:
            json.dump(history, f, indent=2)

        print(f"[Simulator] Snapshot written @ {ts_str}")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
