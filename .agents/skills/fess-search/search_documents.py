import argparse
import json
import os
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[3]


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    values.update({k: v for k, v in os.environ.items() if k.startswith("FESS_")})
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--num", type=int, default=5)
    parser.add_argument("--label", help="Optional label value for fields.label filtering.")
    args = parser.parse_args()

    env = load_env()
    base_url = env.get("FESS_BASE_URL", "http://localhost:8080").rstrip("/")
    params: dict[str, str | int] = {"q": args.query, "start": 0, "num": args.num}
    if args.label:
        params["fields.label"] = args.label

    session = requests.Session()
    session.trust_env = False
    response = session.get(f"{base_url}/api/v1/documents", params=params, timeout=10)
    print(json.dumps({"status": response.status_code, "body": response.json()}, indent=2, ensure_ascii=False))
    if response.status_code != 200:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
