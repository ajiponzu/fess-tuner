import json
import requests

FESS_API_BASE = "http://piserver:8080/api/v1"

resp = requests.get(f"{FESS_API_BASE}/health", timeout=10)
print(json.dumps({"status": resp.status_code, "body": resp.json()}, indent=2, ensure_ascii=False))
