"""
Debug test: call the /check-all endpoint directly via FastAPIServer proxy.
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
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode("utf-8") if body else None
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
            return ({"raw": body_text[:1000]}, e.code)
    except urllib.error.URLError as e:
        return ({"error": str(e.reason)}, 0)


def main():
    # Login
    login_data, status = api_request("POST", "/api/auth/login",
                                     body={"email": EMAIL, "password": PASSWORD}, timeout=15)
    if status != 200:
        print(f"Login failed: {login_data}")
        sys.exit(1)
    token = login_data["access_token"]

    # Check if the proxy works
    print("Testing direct BedReadDriveSync endpoint...")
    url = "http://localhost:8003/api/drive-sync/metadata-update/check-all"
    req = urllib.request.Request(url, headers={}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Direct call: status={resp.status}")
    except urllib.error.HTTPError as e:
        print(f"Direct call HTTP error: {e.code}")
        print(e.read().decode()[:500])
    except urllib.error.URLError as e:
        print(f"Direct call network error: {e.reason}")

    # Now test through proxy
    print("\nTesting through FastAPIServer proxy...")
    result, status = api_request("GET",
                                  "/api/drive-sync/metadata-update/check-all",
                                  token=token, timeout=30)
    print(f"Status: {status}")
    if status != 200:
        print(f"Response: {result}")
    else:
        print("Success!")


if __name__ == "__main__":
    main()
