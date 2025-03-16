import requests
import json
from token_manager import get_token  # Import the function to get a valid token

# Load credentials from JSON config file
with open("config.json", "r") as file:
    config = json.load(file)

with open("devicelist_ids.json", "r") as file:
    ps_key_list = json.load(file)  # Load device list

# API Endpoint
url = "https://gateway.isolarcloud.com.hk/openapi/getDevicePointsDayMonthYearDataList"

# Request Headers
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "sys_code": "901",
    "x-access-key": config["x_access_key"],
    "token": get_token(),  # Get a valid token
}

# Function to split list into chunks of 50
def chunk_list(lst, chunk_size=50):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]  # Returns chunks of `chunk_size`

# Loop through all chunks and send API requests
for chunk in chunk_list(ps_key_list, 50):
    payload = {
        "appkey": config["appkey"],
        "data_point": "p1,p2,p24,p14",
        "data_type": "2",
        "end_time": "20250313",
        "order": "0",
        "ps_key_list": chunk,  # Send only 50 items at a time
        "query_type": "1",
        "start_time": "20250301"
    }

    # ✅ Move API request inside the loop
    response = requests.post(url, json=payload, headers=headers)

    # Process Response
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))  # ✅ Print response for each batch

        if data.get("result_code") == "1":  # Check if request was successful
            result_data = data.get("result_data", {})  # Extract result_data properly

            extracted_data = []
            for ps_key, station_data in result_data.items():
                extracted_data.append({
                    "ps_key": ps_key,
                    "Yield_Today": station_data.get("p1", [{}])[0].get("time_stamp", "N/A"),
                    "Total_Yield": station_data.get("p2", [{}])[0].get("2", "N/A"),
                    "Total_Dc_Power": station_data.get("p14", [{}])[0].get("2", "N/A"),
                    "Total_Active_Power": station_data.get("p24", [{}])[0].get("2", "N/A"),
                })

            print(json.dumps(extracted_data, indent=4))  # ✅ Print extracted data per batch

        else:
            print("API Response Error:", data.get("result_msg"))
    else:
        print("Failed to fetch power station data:", response.text)
