import requests
import json
from token_manager import get_token  # Import the function to get a valid token
import os

# Load credentials from JSON config file
with open("config.json", "r") as file:   #FOR DAILYYYYYY
    config = json.load(file)

# API Endpoint
url = "https://gateway.isolarcloud.com.hk/openapi/getDeviceListByUser"

# Function to get a valid token (retries if the token is invalid)
def get_valid_token():
    token = get_token()  # Get a valid token from the token manager
    while not token:  # If the token is invalid, keep retrying
        print("Token is invalid or expired, requesting a new token...")
        token = get_token()  # Try to get a new token
    return token

# Request Headers
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "sys_code": "901",
    "x-access-key": config["x_access_key"],
    "token": get_valid_token(),  # Get a valid token
}

# API Request Payload
payload = {
    "appkey": config["appkey"],
    "curPage": 1,
    "size": 1000,
    "device_type_list": [1],  # Adjust if needed # Equipment Type List (such as: 11: Plant; 1: Inverter; 3: Grid Connection Point; 17: Unit; defaults to all when empty). Refer to Appendix: Device Type Definitions for details
}

# Send API Request
response = requests.post(url, json=payload, headers=headers)

# Process Response
if response.status_code == 200:
    data = response.json()
    print("PRINTINGGGG")
    
    if data.get("result_code") == "1":  # Check if request was successful
        stations = data["result_data"]["pageList"]
        
        extracted_data = []
        
        for station in stations:
            extracted_data.append({
                "type_name": station.get("type_name", "N/A"),
                "ps_key": station.get("ps_key", "N/A"),
                "device_sn": station.get("device_sn", "N/A"),
                "uuid": station.get("uuid", "N/A"),
                "grid_connection_date": station.get("grid_connection_date", "N/A"),
                "device_name": station.get("device_name", "N/A"),
                "rel_state": station.get("rel_state", "N/A"),
                "device_code": station.get("device_code", "N/A"),
                "ps_id": station.get("ps_id", "N/A"),
                "device_model_id": station.get("device_model_id", "N/A"),
                "communication_dev_sn": station.get("communication_dev_sn", "N/A"),
                "device_model_code": station.get("device_model_code", "N/A")
            })
        
        # Print extracted station data
        print(json.dumps(extracted_data, indent=4))

        # Extract ps_key for saving to file
        ps_keys = [station["ps_key"] for station in extracted_data if station["ps_key"] != "N/A"]

        # Define the folder path where you want to save the file


        # Save the ps_keys to the specified folder
        with open("sungrow_daily/devicelist_ids.json", "w", encoding="utf-8") as f:
            json.dump(ps_keys, f, indent=4)

    else:
        print("API Response Error:", data.get("result_msg"))

else:
    print("Failed to fetch power station data:", response.text)
