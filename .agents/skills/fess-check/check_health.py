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
    env = load_env()
    base_url = env.get("FESS_BASE_URL", "http://piserver:8080").rstrip("/")
    session = requests.Session()
    session.trust_env = False
    response = session.get(f"{base_url}/api/v1/health", timeout=10)
    payload = response.json()
    print(json.dumps({"status": response.status_code, "body": payload}, indent=2, ensure_ascii=False))
    if response.status_code != 200 or payload.get("data", {}).get("status") != "green":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
