import json
import os
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[3]
DOCS_PATTERN = r".*(/docs/|/sessions/|/record/|/temps/|README\.md$|\.md$|\.pdf$).*"
SOURCE_PATTERN = (
    r".*(/src/|/include/|/examples/|/tests/|CMakeLists\.txt$|"
    r"\.(rs|cpp|hpp|h|c|cc|cxx|py|js|ts|tsx|jsx|toml|ya?ml|json|cmake|glsl|wgsl)$).*"
)


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


ENV = load_env()
BASE_URL = ENV.get("FESS_BASE_URL", "http://piserver:8080").rstrip("/")
TOKEN = ENV.get("FESS_ACCESS_TOKEN", "")

if not TOKEN:
    raise SystemExit("FESS_ACCESS_TOKEN is not set.")

SESSION = requests.Session()
SESSION.trust_env = False
SESSION.headers.update({"Authorization": f"Bearer {TOKEN}"})


def api_request(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    response = SESSION.request(method, url, timeout=30, **kwargs)
    try:
        payload = response.json()
    except ValueError:
        payload = {"raw": response.text}
    if not response.ok:
        raise RuntimeError(f"{method} {path} failed: HTTP {response.status_code}: {payload}")
    return payload


def expect_ok(payload: dict[str, Any], context: str) -> dict[str, Any]:
    status = payload.get("response", {}).get("status")
    if status != 0:
        raise RuntimeError(f"{context} failed: {json.dumps(payload, ensure_ascii=False)}")
    return payload["response"]


def get_settings(path: str) -> list[dict[str, Any]]:
    payload = api_request("GET", f"{path}?size=200&page=0")
    response = expect_ok(payload, f"GET {path}")
    return list(response.get("settings") or [])


def index_by_string_field(items: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        value = item.get(field)
        if isinstance(value, str) and value:
            indexed[value] = item
    return indexed


def create_labeltypes() -> dict[str, dict[str, Any]]:
    any_project = r".*/var/www/(elpix|pandolabo)/.*"
    desired = [
        {"value": "elpix", "name": "project: elpix", "sortOrder": 10, "includedPaths": r".*/var/www/elpix/.*", "excludedPaths": ""},
        {
            "value": "pandolabo",
            "name": "project: pandolabo",
            "sortOrder": 20,
            "includedPaths": r".*/var/www/pandolabo/.*",
            "excludedPaths": "",
        },
        {"value": "docs", "name": "content_type: docs", "sortOrder": 110, "includedPaths": DOCS_PATTERN, "excludedPaths": ""},
        {"value": "source", "name": "content_type: source", "sortOrder": 120, "includedPaths": SOURCE_PATTERN, "excludedPaths": DOCS_PATTERN},
        {
            "value": "other",
            "name": "content_type: other",
            "sortOrder": 130,
            "includedPaths": any_project,
            "excludedPaths": f"{DOCS_PATTERN}\n{SOURCE_PATTERN}",
        },
    ]
    existing = index_by_string_field(get_settings("/api/admin/labeltype/settings"), "value")
    for item in desired:
        body = {
            "name": item["name"],
            "value": item["value"],
            "includedPaths": item["includedPaths"],
            "included_paths": item["includedPaths"],
            "excludedPaths": item["excludedPaths"],
            "excluded_paths": item["excludedPaths"],
            "permissions": "{role}guest",
            "virtualHost": "",
            "virtual_host": "",
            "sortOrder": item["sortOrder"],
            "sort_order": item["sortOrder"],
        }
        if item["value"] in existing:
            detail = expect_ok(
                api_request("GET", f"/api/admin/labeltype/setting/{existing[item['value']]['id']}"),
                f"get labeltype {item['value']}",
            )["setting"]
            body["id"] = existing[item["value"]]["id"]
            version = detail.get("versionNo", detail.get("version_no"))
            body["versionNo"] = version
            body["version_no"] = version
            response = expect_ok(
                api_request("PUT", "/api/admin/labeltype/setting", json=body),
                f"update labeltype {item['value']}",
            )
            print(f"labeltype updated: {item['value']} ({response.get('id')})")
        else:
            response = expect_ok(
                api_request("POST", "/api/admin/labeltype/setting", json=body),
                f"create labeltype {item['value']}",
            )
            print(f"labeltype created: {item['value']} ({response.get('id')})")
    labels = index_by_string_field(get_settings("/api/admin/labeltype/settings"), "value")
    missing = [item["value"] for item in desired if item["value"] not in labels]
    if missing:
        raise RuntimeError(f"missing labeltypes after create: {missing}")
    return labels


def fileconfig_body(
    name: str,
    path: str,
    included: str,
    excluded: str,
    label_ids: list[str],
    sort_order: int,
) -> dict[str, Any]:
    return {
        "name": name,
        "description": "fess-tuner managed label config",
        "paths": path,
        "includedPaths": included,
        "included_paths": included,
        "excludedPaths": excluded,
        "excluded_paths": excluded,
        "includedDocPaths": "",
        "included_doc_paths": "",
        "excludedDocPaths": "",
        "excluded_doc_paths": "",
        "configParameter": "",
        "config_parameter": "",
        "depth": 0,
        "maxAccessCount": 10000,
        "max_access_count": 10000,
        "numOfThread": 1,
        "num_of_thread": 1,
        "intervalTime": 1000,
        "interval_time": 1000,
        "boost": 1.0,
        "available": "true",
        "sortOrder": sort_order,
        "sort_order": sort_order,
        "permissions": "{role}guest",
        "virtualHosts": "",
        "virtual_hosts": "",
        "labelTypeIds": label_ids,
        "label_type_ids": label_ids,
    }


def upsert_fileconfig(name: str, body: dict[str, Any], existing: dict[str, Any] | None) -> None:
    if not existing:
        response = expect_ok(
            api_request("POST", "/api/admin/fileconfig/setting", json=body),
            f"create fileconfig {name}",
        )
        print(f"fileconfig created: {name} ({response.get('id')})")
        return

    detail = expect_ok(
        api_request("GET", f"/api/admin/fileconfig/setting/{existing['id']}"),
        f"get fileconfig {existing['id']}",
    )["setting"]
    update_body = dict(body)
    update_body["id"] = existing["id"]
    version = detail.get("versionNo", detail.get("version_no"))
    update_body["versionNo"] = version
    update_body["version_no"] = version
    response = expect_ok(
        api_request("PUT", "/api/admin/fileconfig/setting", json=update_body),
        f"update fileconfig {name}",
    )
    print(f"fileconfig updated: {name} ({response.get('id')})")


def create_fileconfigs(labels: dict[str, dict[str, Any]]) -> None:
    existing = index_by_string_field(get_settings("/api/admin/fileconfig/settings"), "name")
    projects = [
        ("elpix", "file:///var/www/elpix", 1000),
        ("pandolabo", "file:///var/www/pandolabo", 2000),
    ]
    content_types = [
        ("docs", DOCS_PATTERN, "", 10),
        ("source", SOURCE_PATTERN, DOCS_PATTERN, 20),
        ("other", "", f"{DOCS_PATTERN}\n{SOURCE_PATTERN}", 30),
    ]
    for project, root_path, sort_base in projects:
        for content_type, included, excluded, sort_offset in content_types:
            name = f"{project}-{content_type}"
            body = fileconfig_body(
                name=name,
                path=root_path,
                included=included,
                excluded=excluded,
                label_ids=[labels[project]["id"], labels[content_type]["id"]],
                sort_order=sort_base + sort_offset,
            )
            try:
                upsert_fileconfig(name, body, existing.get(name))
            except RuntimeError:
                print(f"failed body for {name}: {json.dumps(body, ensure_ascii=False, indent=2)}")
                raise


def disable_old_var_www() -> None:
    settings = get_settings("/api/admin/fileconfig/settings")
    disabled = []
    for item in settings:
        if item.get("name") != "var-www" or item.get("paths") != "file:///var/www":
            continue
        if str(item.get("available")).lower() != "true":
            continue
        detail = expect_ok(
            api_request("GET", f"/api/admin/fileconfig/setting/{item['id']}"),
            f"get fileconfig {item['id']}",
        )["setting"]

        def first(*keys: str, default: Any = None) -> Any:
            for key in keys:
                if key in detail and detail[key] is not None:
                    return detail[key]
            return default

        body = {
            "id": detail["id"],
            "name": detail["name"],
            "description": detail.get("description") or "",
            "paths": detail["paths"],
            "includedPaths": detail.get("includedPaths") or "",
            "excludedPaths": detail.get("excludedPaths") or "",
            "includedDocPaths": detail.get("includedDocPaths") or "",
            "excludedDocPaths": detail.get("excludedDocPaths") or "",
            "configParameter": detail.get("configParameter") or "",
            "depth": first("depth", default=0),
            "maxAccessCount": first("maxAccessCount", "max_access_count", default=10000),
            "numOfThread": first("numOfThread", "num_of_thread", default=1),
            "num_of_thread": first("numOfThread", "num_of_thread", default=1),
            "intervalTime": first("intervalTime", "interval_time", default=1000),
            "interval_time": first("intervalTime", "interval_time", default=1000),
            "boost": first("boost", default=1.0),
            "available": "false",
            "sortOrder": first("sortOrder", "sort_order", default=9000),
            "sort_order": first("sortOrder", "sort_order", default=9000),
            "permissions": detail.get("permissions") or "{role}guest",
            "virtualHosts": detail.get("virtualHosts") or "",
            "labelTypeIds": detail.get("labelTypeIds") or [],
            "versionNo": first("versionNo", "version_no"),
            "version_no": first("versionNo", "version_no"),
        }
        response = expect_ok(
            api_request("PUT", "/api/admin/fileconfig/setting", json=body),
            f"disable fileconfig {item['id']}",
        )
        disabled.append(response.get("id") or item["id"])
    for item_id in disabled:
        print(f"fileconfig disabled: {item_id}")


def start_scheduler(scheduler_id: str) -> None:
    response = expect_ok(
        api_request("PUT", f"/api/admin/scheduler/{scheduler_id}/start"),
        f"start scheduler {scheduler_id}",
    )
    print(f"scheduler started: {scheduler_id} jobLogId={response.get('jobLogId')}")


def start_crawler() -> None:
    start_scheduler("default_crawler")


def refresh_labels() -> None:
    start_scheduler("reload_config")
    start_scheduler("label_updater")


def verify_summary() -> None:
    labels = api_request("GET", "/api/v1/labels")
    search = api_request("GET", "/api/v1/documents", params={"q": "*", "num": 0, "facet.field": "label", "facet.size": 50})
    print("public labels:", json.dumps(labels, ensure_ascii=False))
    print("label facets:", json.dumps(search.get("facet_field", []), ensure_ascii=False))


def main() -> None:
    print(f"Fess: {BASE_URL}")
    health = api_request("GET", "/api/v1/health")
    print("health:", health.get("data", {}).get("status"))
    labels = create_labeltypes()
    create_fileconfigs(labels)
    disable_old_var_www()
    start_crawler()
    refresh_labels()
    verify_summary()


if __name__ == "__main__":
    main()
