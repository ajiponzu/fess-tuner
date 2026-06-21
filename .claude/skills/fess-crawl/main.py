import argparse
import json
import sys
import requests

FESS_BASE_URL = "http://piserver:8080"

parser = argparse.ArgumentParser()
parser.add_argument("--user", default="admin")
parser.add_argument("--pass", dest="password", default="admin")
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
