import argparse
import json
import requests

FESS_API_BASE = "http://piserver:8080/api/v1"

parser = argparse.ArgumentParser()
parser.add_argument("query")
parser.add_argument("--num", type=int, default=5)
args = parser.parse_args()

resp = requests.get(
    f"{FESS_API_BASE}/search",
    params={"q": args.query, "start": 0, "num": args.num},
    timeout=10,
)
print(json.dumps({"status": resp.status_code, "body": resp.json()}, indent=2, ensure_ascii=False))
