import os
import time
import base64
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("client_id")
CLIENT_SECRET = os.getenv("client_secret")


latest_times = {
    "planned_time": None,
    "estimated_time": None,
    "minutes_left": None
}

# Helpers

def _basic_auth_header():
    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(auth.encode()).decode()
    return {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded}"
    }

def _bearer_header(token):
    return {"Authorization": f"Bearer {token}"}

# API Calls

def get_access_token():
    URL = "https://ext-api.vasttrafik.se/token"
    try:
        res = requests.post(URL, headers=_basic_auth_header(),
                            data={"grant_type": "client_credentials"})
        res.raise_for_status()
        return res.json().get("access_token")
    except requests.RequestException as e:
        print(f"[TOKEN ERROR] {e}")
        return None

def get_stop_area_gid(name, token):
    URL = "https://ext-api.vasttrafik.se/pr/v4/locations/by-text"
    try:
        res = requests.get(URL, headers=_bearer_header(token),
                           params={"q": name, "limit": 1})
        res.raise_for_status()
        results = res.json().get("results", [])
        return results[0]["gid"] if results else None
    except requests.RequestException as e:
        print(f"[LOCATION ERROR] {e}")
        return None

def fetch_departures(gid, token):
    URL = f"https://ext-api.vasttrafik.se/pr/v4/stop-areas/{gid}/departures"
    try:
        res = requests.get(URL, headers=_bearer_header(token),
                           params={"limit": 1, "platforms": "A"})
        res.raise_for_status()
        return res.json()
    except requests.RequestException:
        return None


# Background fetcher loop
def fetcher():
    print("[FETCHER] Starting background thread…")

    token = get_access_token()
    if not token:
        print("[FETCHER] No access token. Stopping.")
        return

    gid = get_stop_area_gid("Spaldingsgatan", token)
    if not gid:
        print("[FETCHER] Could not resolve stop area.")
        return

    token_expired = False

    while True:
        try:
            if token_expired:
                token = get_access_token()
                if not token:
                    print("[FETCHER] Token still invalid. Retry in 5s.")
                    time.sleep(5)
                    continue
                token_expired = False

            data = fetch_departures(gid, token)

            if data is None:
                print("[FETCHER] Invalid departure data → refresh token")
                token_expired = True
                time.sleep(1)
                continue

            results = data.get("results", [])
            if results:
                dep = results[0]
                planned = dep.get("plannedTime")
                estimated = dep.get("estimatedTime", planned)

                # Convert to datetime objects
                now = datetime.now(ZoneInfo("Europe/Stockholm"))
                planned_dt = datetime.fromisoformat(planned.replace("Z", "+00:00"))
                estimated_dt = datetime.fromisoformat(estimated.replace("Z", "+00:00"))

                # Calculate minutes left
                minutes_left = int((estimated_dt - now).total_seconds() / 60)
                if minutes_left < 0:
                    minutes_left = 0

                # Store in global state
                latest_times["planned_time"] = planned
                latest_times["estimated_time"] = estimated
                latest_times["minutes_left"] = minutes_left

                # Pretty print
                print(f"[FETCHER] {minutes_left} minuter till avgång")
            else:
                print("[FETCHER] No departure info.")

        except Exception as e:
            print(f"[FETCHER ERROR] {e}")
            token_expired = True

        time.sleep(60)
