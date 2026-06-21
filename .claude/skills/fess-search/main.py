import argparse
import json
import os
from pathlib import Path

import requests

_env_path = Path(__file__).parents[3] / ".env"
if _env_path.exists():
    for _line in _env_path.read_text(encoding="utf-8").splitlines():
        if "=" in _line and not _line.startswith("#"):
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

FESS_BASE_URL = os.environ.get("FESS_BASE_URL", "http://piserver:8080")

parser = argparse.ArgumentParser()
parser.add_argument("query")
parser.add_argument("--num", type=int, default=5)
args = parser.parse_args()

resp = requests.get(
    f"{FESS_BASE_URL}/api/v1/search",
    params={"q": args.query, "start": 0, "num": args.num},
    timeout=10,
)
print(json.dumps({"status": resp.status_code, "body": resp.json()}, indent=2, ensure_ascii=False))
