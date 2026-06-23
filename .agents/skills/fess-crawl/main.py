import json
import os
import sys
from pathlib import Path

import requests

_env_path = Path(__file__).parents[3] / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

FESS_BASE_URL = os.environ.get("FESS_BASE_URL", "http://piserver:8080")
ACCESS_TOKEN = os.environ.get("FESS_ACCESS_TOKEN", "")

if not ACCESS_TOKEN:
    print("Error: FESS_ACCESS_TOKEN is not set in .env", file=sys.stderr)
    sys.exit(1)

HEADERS = {"Authorization": ACCESS_TOKEN}

resp = requests.put(
    f"{FESS_BASE_URL}/api/admin/scheduler/default_crawler/start",
    headers=HEADERS,
    timeout=10,
)
print(json.dumps({"status": resp.status_code, "body": resp.json()}, indent=2, ensure_ascii=False))
