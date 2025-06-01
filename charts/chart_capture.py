
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

def capture_tradingview_chart(url: str, save_path: str):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        print(f"[Chart] Navigating to {url}...")
        time.sleep(5)  # Wait for chart to fully load

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(save_path)
        print(f"[Chart] Screenshot saved to {save_path}")

        driver.quit()
    except Exception as e:
        print(f"[Chart] Failed to capture chart: {e}")
