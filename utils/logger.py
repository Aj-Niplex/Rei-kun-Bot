from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

LOG_FILE = Path("logs/bot_logs.txt")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log_event(text: str):
    indian_time = datetime.now(ZoneInfo("Asia/Kolkata"))
    timestamp = indian_time.strftime("%Y-%m-%d %I:%M:%S %p IST")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")
