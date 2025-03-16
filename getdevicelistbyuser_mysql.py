import requests
import json
from token_manager import get_token  # Import the function to get a valid token
import mysql.connector
from mysql.connector import Error

# MySQL connection setup (Update with your database credentials)
DB_CONFIG = {
    "host": "34.72.218.246",
    "user": "admin",
    "password": "emitsolar2023",
    "database": "sungrow_db"
}

try:
    # Establish MySQL connection
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Load credentials from JSON config file
    with open("config.json", "r") as file:
        config = json.load(file)

    # API Endpoint
    url = "https://gateway.isolarcloud.com.hk/openapi/getDeviceListByUser"

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
        "device_type_list": [1]  # Adjust if needed
    }
    
    # Send API Request
    response = requests.post(url, json=payload, headers=headers)

    # Process Response
    if response.status_code == 200:
        data = response.json()
        #print(json.dumps(data, indent=4))

        if data.get("result_code") == "1":  # Check if request was successful
            stations = data["result_data"]["pageList"]
            extracted_data = []

            for station in stations:
                extracted_data.append((
                    station.get("type_name", "N/A"),
                    station.get("ps_key", "N/A"),
                    station.get("device_sn", "N/A"),
                    station.get("uuid", "N/A"),
                    station.get("grid_connection_date", "N/A"),
                    station.get("device_name", "N/A"),
                    station.get("rel_state", "N/A"),
                    station.get("device_code", "N/A"),
                    station.get("ps_id", "N/A"),
                    station.get("device_model_id", "N/A"),
                    station.get("communication_dev_sn", "N/A"),
                    station.get("device_model_code", "N/A")
                ))

            # Insert data into MySQL
            insert_query = """
                INSERT INTO list_inverter (
                    type_name, ps_key, device_sn, uuid, grid_connection_date, 
                    device_name, rel_state, device_code, ps_id, 
                    device_model_id, communication_dev_sn, device_model_code
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.executemany(insert_query, extracted_data)
            conn.commit()

            print(f"{cursor.rowcount} records inserted successfully.")

        else:
            print("API Response Error:", data.get("result_msg"))

    else:
        print("Failed to fetch power station data:", response.text)

except Error as e:
    print("Error connecting to MySQL:", e)

finally:
    # Close database connection
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
