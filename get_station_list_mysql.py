import requests
import json
import mysql.connector
from mysql.connector import Error
from token_manager import get_token  # Import function to get token

# Load credentials from JSON config file
with open("config.json", "r") as file:
    config = json.load(file)

# MySQL Database Configuration
DB_CONFIG = {
    "host": "34.72.218.246",
    "user": "admin",
    "password": "emitsolar2023",
    "database": "sungrow_db"
}

# API Endpoint
url = "https://gateway.isolarcloud.com.hk/openapi/getPowerStationList"

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
    "size": 1000  # Adjust as needed
}

# Send API Request
response = requests.post(url, json=payload, headers=headers)

# Process Response
if response.status_code == 200:
    data = response.json()
    
    if data.get("result_code") == "1":  # Check if request was successful
        stations = data["result_data"]["pageList"]
        extracted_data = []

        for station in stations:
            extracted_data.append((
                station.get("ps_name", "N/A"),
                station.get("install_date", None),
                float(station.get("total_capcity", {}).get("value", 0.0)),
                station.get("ps_location", "N/A"),
                station.get("ps_id","N/A")
            ))

        # Insert data into MySQL
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            cursor = connection.cursor()

            insert_query = """
                INSERT INTO list_station (ps_name, install_date, total_capcity, ps_location,ps_id)
                VALUES (%s, %s, %s, %s,%s)
            """

            cursor.executemany(insert_query, extracted_data)
            connection.commit()

            print(f"{cursor.rowcount} records inserted successfully.")

        except Error as e:
            print("Error connecting to MySQL:", e)

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    else:
        print("API Response Error:", data.get("result_msg"))

else:
    print("Failed to fetch power station data:", response.text)
