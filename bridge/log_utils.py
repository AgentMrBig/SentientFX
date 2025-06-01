
import csv
from datetime import datetime

LOG_PATH = "logs/trade_logs.csv"

def write_log(event: str, details: str):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, event, details])
