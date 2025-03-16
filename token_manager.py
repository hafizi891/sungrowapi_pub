import requests
import json
import os
import time
from datetime import datetime, timedelta

CONFIG_FILE = "config.json"
TOKEN_FILE = "token.json"

# Load credentials from JSON config file
try:
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
except Exception as e:
    print(f"[ERROR] Failed to load {CONFIG_FILE}: {e}")
    exit(1)

def get_token():
    """Retrieve the token from file or request a new one if expired."""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as file:
                token_data = json.load(file)
                expires_at = token_data.get("expires_at", 0)
                remaining_time = expires_at - time.time()

                # Check if the token is still valid
                if remaining_time > 0:
                    print(f"[INFO] Token is still valid.\nValid until: {datetime.fromtimestamp(expires_at)}\nTime left: {str(timedelta(seconds=int(remaining_time)))}")
                    return token_data["token"]
                else:
                    print("[WARNING] Token expired, requesting a new one...")
        except json.JSONDecodeError:
            print("[ERROR] Token file is corrupted. Requesting a new token...")

    # If token is missing or expired, request a new one
    return request_new_token()

def request_new_token():
    """Request a new token and save it with expiration time."""
    print("[INFO] Requesting a new token from API...")

    url = "https://gateway.isolarcloud.com.hk/openapi/login"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "sys_code": "901",
        "x-access-key": config["x_access_key"],
    }

    payload = {
        "appkey": config["appkey"],
        "lang": "_en_US",
        "user_account": config["user_account"],
        "user_password": config["user_password"],
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an exception for HTTP errors
    except requests.RequestException as e:
        print("[ERROR] Request failed:", e)
        return None

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse JSON response:", response.text)
        return None

    # Debugging: Print the full API response
    print("[DEBUG] API Response:", json.dumps(data, indent=4))

    # Validate response structure
    if data.get("result_code") == "1" and isinstance(data.get("result_data"), dict):
        token_data = data["result_data"]

        if "token" in token_data:
            token = token_data["token"]
            expires_in = 24 * 3600  # 24 hours in seconds
            expiration_time = time.time() + expires_in
            
            # Save token and expiration time to file
            with open(TOKEN_FILE, "w") as file:
                json.dump({
                    "token": token,
                    "expires_at": expiration_time,
                    "valid_until": datetime.fromtimestamp(expiration_time).strftime("%Y-%m-%d %H:%M:%S")
                }, file, indent=4)

            print(f"[SUCCESS] New token saved.\nValid until: {datetime.fromtimestamp(expiration_time)}")
            return token
        else:
            print("[ERROR] 'token' key not found in 'result_data':", token_data)
    else:
        print("[ERROR] Unexpected API response structure:", data)

    return None

# Run test
if __name__ == "__main__":
    print("[INFO] Running token manager test...")
    token = get_token()
    print(f"[INFO] Using Token: {token}")
