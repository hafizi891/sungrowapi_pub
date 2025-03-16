import requests
import json
from token_manager import get_token  # Import the function to get a valid token

# Load credentials from JSON config file
with open("config.json", "r") as file:
    config = json.load(file)

# API Endpoint
url = "https://gateway.isolarcloud.com.hk//openapi/getDeviceList"

# Request Headers
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "sys_code": "901",
    "x-access-key": config["x_access_key"],
    "token": get_token(),  # Get a valid token
}

# API Request Payload
payload = {
    "appkey": config["appkey"],
    "curPage": 1,
    "size": 1000,
    "ps_id":1531638,  # Adjust if needed
}

# Send API Request
response = requests.post(url, json=payload, headers=headers)

# Process Response
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data,indent=2))
    
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
            })
        
        # Print extracted station data
        print(json.dumps(extracted_data, indent=4))

    else:
        print("API Response Error:", data.get("result_msg"))

else:
    print("Failed to fetch power station data:", response.text)
