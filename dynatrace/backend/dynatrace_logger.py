import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DYNATRACE_ENV_ID = os.getenv("DYNATRACE_ENV_ID")
DYNATRACE_API_TOKEN = os.getenv("DYNATRACE_API_TOKEN")

def send_log_to_dynatrace(content, level="INFO", service="fastapi-app", **kwargs):
    if not DYNATRACE_ENV_ID or not DYNATRACE_API_TOKEN:
        print("Missing Dynatrace credentials")
        return

    log = {
        "timestamp": int(datetime.utcnow().timestamp() * 1000),
        "content": content,
        "log.level": level,
        "service.name": service,
        **kwargs
    }

    try:
        response = requests.post(
            f"https://{DYNATRACE_ENV_ID}.live.dynatrace.com/api/v2/logs/ingest",
            headers={
                "Authorization": f"Api-Token {DYNATRACE_API_TOKEN}",
                "Content-Type": "application/json"
            },
            data=json.dumps([log])
        )
        print("Log sent:", response.status_code)
    except Exception as e:
        print("Failed to send log:", e)
