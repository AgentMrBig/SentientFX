@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat

start "Streamer" cmd /k "cd bridge && python simulate_market_stream.py"
start "SignalGen" cmd /k "cd bridge && python signal_generator.py"
start "Router" cmd /k "cd bridge && python order_router.py"
