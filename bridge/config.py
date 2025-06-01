from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")      # None if missing


# File paths
DATA_PATH = "data/market_stream.json"
ORDER_PATH = "data/orders.json"
IMAGE_CAPTURE_PATH = "data/snapshots/latest_chart.png"

# API Key (use environment variable or fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-your-api-key")

# Trade decision filtering
MIN_CONFIDENCE = {"MEDIUM", "HIGH"}

# Trade rules
MIN_LOT = 0.01
LOT_INCREMENT = 0.01
MAX_OPEN_TRADES = 4
SLIPPAGE = 3

# Loop timing
CHECK_INTERVAL_SECONDS = 10
