import argparse
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

parser = argparse.ArgumentParser()
parser.add_argument("--user", default=os.environ.get("FESS_ADMIN_USER", "admin"))
parser.add_argument("--pass", dest="password", default=os.environ.get("FESS_ADMIN_PASS", ""))
args = parser.parse_args()

login = requests.post(
    f"{FESS_BASE_URL}/api/admin/user/login",
    data={"username": args.user, "password": args.password},
    timeout=10,
)
if not login.ok:
    print(f"Login failed: {login.status_code}", file=sys.stderr)
    sys.exit(1)
token = login.json().get("token")

resp = requests.post(
    f"{FESS_BASE_URL}/api/admin/crawl/run",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10,
)
print(json.dumps({"status": resp.status_code, "body": resp.json()}, indent=2, ensure_ascii=False))
