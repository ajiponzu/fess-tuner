import json
import os
from pathlib import Path
from typing import Any

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


def expect_ok(payload: dict[str, Any], context: str) -> dict[str, Any]:
    status = payload.get("response", {}).get("status")
    if status != 0:
        raise RuntimeError(f"{context} failed: {json.dumps(payload, ensure_ascii=False)}")
    return payload["response"]


def get_settings(session: requests.Session, base_url: str) -> list[dict[str, Any]]:
    response = session.get(f"{base_url}/api/admin/scheduler/settings?size=100&page=0", timeout=10)
    payload = response.json()
    if response.status_code != 200:
        raise RuntimeError(f"scheduler settings failed: HTTP {response.status_code}: {payload}")
    return list(expect_ok(payload, "get scheduler settings").get("settings") or [])


def find_crawler_scheduler_id(settings: list[dict[str, Any]]) -> str:
    for item in settings:
        text = " ".join(str(item.get(key, "")) for key in ("id", "name", "target", "script_type", "script_data", "scriptType", "scriptData"))
        if "crawler" in text.lower():
            scheduler_id = item.get("id")
            if isinstance(scheduler_id, str) and scheduler_id:
                return scheduler_id
    raise RuntimeError("crawler scheduler was not found.")


def main() -> None:
    env = load_env()
    base_url = env.get("FESS_BASE_URL", "http://piserver:8080").rstrip("/")
    token = env.get("FESS_ACCESS_TOKEN", "")
    if not token:
        raise SystemExit("FESS_ACCESS_TOKEN is not set.")

    session = requests.Session()
    session.trust_env = False
    session.headers.update({"Authorization": f"Bearer {token}"})

    scheduler_id = find_crawler_scheduler_id(get_settings(session, base_url))
    response = session.put(f"{base_url}/api/admin/scheduler/{scheduler_id}/start", timeout=10)
    payload = response.json()
    if response.status_code != 200:
        raise RuntimeError(f"crawler start failed: HTTP {response.status_code}: {payload}")
    expect_ok(payload, f"start {scheduler_id}")
    print(json.dumps({"status": response.status_code, "body": payload}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
