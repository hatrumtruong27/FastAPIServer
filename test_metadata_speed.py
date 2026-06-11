"""
Benchmark the /api/drive-sync/metadata-update/check-all endpoint via HTTP.

Usage:
    python test_metadata_speed.py

Requires:
    - FastAPIServer running at http://localhost:8001
    - A valid user account in the database
    - Drive Sync configured (folder_id, credentials, main BE token)
"""

import json
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"
EMAIL = "admin@gmail.com"
PASSWORD = "+E8ep0m7(h5ut#Q$"


def api_request(method: str, path: str, token: str | None = None,
                 body: dict | None = None, timeout: float = 600.0) -> tuple[dict, int]:
    """Make an authenticated HTTP request. Returns (json_data, status_code)."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = json.dumps(body).encode("utf-8") if body else None
    if body:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8")
            return (json.loads(text) if text else {}, resp.status)
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8")
        try:
            return (json.loads(body_text), e.code)
        except Exception:
            return ({"raw": body_text[:500]}, e.code)
    except urllib.error.URLError as e:
        return ({"error": str(e.reason)}, 0)


def main():
    print("=" * 60)
    print("Metadata Update HTTP Benchmark")
    print("=" * 60)

    # Step 1: Login
    print("\n[1] Logging in...")
    login_body = {"email": EMAIL, "password": PASSWORD}
    login_data, status = api_request("POST", "/api/auth/login", body=login_body, timeout=30)
    if status != 200:
        print(f"    LOGIN FAILED (status={status}): {login_data}")
        print("    Update EMAIL/PASSWORD in this script with your actual credentials.")
        sys.exit(1)

    token = login_data.get("access_token", "")
    user = login_data.get("user", {})
    print(f"    Logged in as: {user.get('email')} ({user.get('role')})")

    # Step 2: Check config
    print("\n[2] Checking Drive Sync config...")
    config_data, status = api_request("GET", "/api/drive-sync/config", token=token, timeout=15)
    if status != 200:
        print(f"    Config fetch failed (status={status}): {config_data}")
        sys.exit(1)

    folder_id = config_data.get("folderId") or config_data.get("folder_id")
    sa_json = config_data.get("serviceAccountJsonPath")
    main_be = config_data.get("mainBeApiBaseUrl") or config_data.get("main_be_api_base_url")
    print(f"    folder_id: {folder_id}")
    print(f"    sa_json:   {sa_json}")
    print(f"    main_be:   {main_be}")

    if not folder_id:
        print("    WARNING: Drive folder ID is not set. Config may not be complete.")
        print("    You may need to configure Drive Sync first via the UI.")

    # Step 3: Time the /check-all endpoint
    print("\n[3] Calling /api/drive-sync/metadata-update/check-all ...")
    print(f"    (timeout={600}s, this may take a while...)")

    overall_start = time.perf_counter()
    result, status = api_request("GET", "/api/drive-sync/metadata-update/check-all",
                                  token=token, timeout=600)
    overall_elapsed = time.perf_counter() - overall_start

    print(f"\n    HTTP status: {status}")
    print(f"    Total time: {overall_elapsed:.2f}s")

    if status == 200:
        can_update = result.get("can_update", [])
        all_match = result.get("all_match", [])
        no_match = result.get("no_server_match", [])
        print(f"\n    Results:")
        print(f"      can_update:      {len(can_update)}")
        print(f"      all_match:       {len(all_match)}")
        print(f"      no_server_match: {len(no_match)}")

        if can_update:
            print(f"\n    First 5 'can_update' entries:")
            for entry in can_update[:5]:
                diffs = [d.get("field", "?") for d in entry.get("differences", [])]
                print(f"      - {entry.get('story_title', '?')} ({entry.get('folder_name', '?')}): {diffs}")

        # Save result
        output_path = "metadata_check_result.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n    Full result saved to: {output_path}")
    else:
        print(f"    FAILED: {result}")

        # Try to extract error message
        if isinstance(result, dict):
            detail = result.get("detail") or result.get("message") or str(result)
            print(f"    Error: {detail[:500]}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"Done. Total elapsed: {overall_elapsed:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
