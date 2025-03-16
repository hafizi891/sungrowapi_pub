import requests
import json
from token_manager import get_token, get_manager_token  # Import functions to get tokens
import os

# Load credentials from JSON config file
with open("config.json", "r") as file:
    config = json.load(file)

# API Endpoint
url = "https://gateway.isolarcloud.com.hk/openapi/getPowerStationList"

# Function to get a valid token (retries if the token is invalid)
def get_valid_token():
    token, _ = get_token()  # Get a valid token from the token manager
    while not token:  # If the token is invalid, keep retrying
        print("Token is invalid or expired, requesting a new token...")
        token, _ = get_token()  # Try to get a new token
    return token

# Function to get a valid manager_token
def get_valid_manager_token():
    manager_token = get_manager_token()
    while not manager_token:
        print("Manager token is invalid or expired, requesting a new token...")
        manager_token = get_manager_token()
    return manager_token

# Request Headers
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "sys_code": "901",
    "x-access-key": config["x_access_key"],
    "token": get_valid_token(),  # Get a valid token
    "manager_token": get_valid_manager_token(),  # Get a valid manager token
}

# API Request Payload
payload = {
    "appkey": config["appkey"],
    "curPage": 1,
    "size": 1000  # Adjust if needed
}

# Send API Request
response = requests.post(url, json=payload, headers=headers)

# Process Response
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if data.get("result_code") == "1":  # Check if request was successful
        stations = data["result_data"]["pageList"]
        
        extracted_data = []
        
        for station in stations:
            extracted_data.append({
                "ps_name": station.get("ps_name", "N/A"),
                "install_date": station.get("install_date", "N/A"),
                "total_capcity": station.get("total_capcity", {}).get("value", "N/A"),
                "ps_location": station.get("ps_location", "N/A"),
                "ps_type": station.get("ps_type", "N/A"),
                "ps_id": station.get("ps_id", "N/A"),
            })
        
        # Print extracted station data
        print(json.dumps(extracted_data, indent=4))
        
        # Save each station data into a JSON file named by ps_id
        ps_ids = [station["ps_id"] for station in extracted_data if station["ps_id"] != "N/A"]

        with open("sungrow_daily/ps_ids.json", "w", encoding="utf-8") as f:
            json.dump(ps_ids, f, indent=4)

    else:
        print("API Response Error:", data.get("result_msg"))

else:
    print("Failed to fetch power station data:", response.text)
