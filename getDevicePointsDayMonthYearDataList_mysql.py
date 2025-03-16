import requests
import json
import mysql.connector
from token_manager import get_token  # Import the function to get a valid token

# Load credentials from JSON config file
with open("config.json", "r") as file:
    config = json.load(file)

with open("devicelist_ids.json", "r") as file:
    ps_key_list = json.load(file)  # Load device list

# MySQL Configuration
DB_CONFIG = {
    "host": "34.72.218.246",
    "user": "admin",
    "password": "emitsolar2023",
    "database": "sungrow_db",
}

# API Endpoint
url = "https://gateway.isolarcloud.com.hk/openapi/getDevicePointsDayMonthYearDataList"

# MySQL Query
query = """
    INSERT INTO daily_inverter_data (ps_key, yield_today, yield_today_date, total_yield, total_yield_date, 
                                     total_dc_power, total_dc_power_date, total_active_power, total_active_power_date) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

def get_headers():
    """Returns the API request headers with a fresh token."""
    return {
        "Content-Type": "application/json;charset=UTF-8",
        "sys_code": "901",
        "x-access-key": config["x_access_key"],
        "token": get_token(),  # Get a valid token
    }

def connect_to_db():
    """Establishes and returns a MySQL connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✅ Connected to MySQL database successfully.")
        return connection
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")
        return None

def chunk_list(lst, chunk_size=50):
    """Splits a list into smaller chunks of given size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def fetch_and_store_data(chunk):
    """Fetch data from API and store results in the database."""
    payload = {
        "appkey": config["appkey"],
        "data_point": "p1,p2,p24,p14",
        "data_type": "2",
        "end_time": "20240431",
        "order": "asc",
        "ps_key_list": chunk,  # Process 50 items per batch
        "query_type": "1",
        "start_time": "20240401"
    }

    try:
        response = requests.post(url, json=payload, headers=get_headers(), timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("🔵 Raw API Response:")
            print(json.dumps(data, indent=2))  # ✅ Print entire response

            if data.get("result_code") == "1":
                if not data.get("result_data"):  # 🔴 Empty response, but continue
                    print("⚠️ No valid data extracted. Moving to next batch...")
                    return  # Skip insertion but continue the loop

                extracted_data = []
                for ps_key, station_data in data["result_data"].items():
                    print(f"📌 Processing PS_KEY: {ps_key}")  # ✅ Print each station key

                    for record in station_data.get("p1", []):  # Process multiple timestamps
                        extracted_data.append((
                            ps_key,
                            record.get("2", "N/A"),  # Yield Today
                            record.get("time_stamp", "N/A"),
                            next((x["2"] for x in station_data.get("p2", []) if x["time_stamp"] == record["time_stamp"]), "N/A"),
                            record.get("time_stamp", "N/A"),
                            next((x["2"] for x in station_data.get("p14", []) if x["time_stamp"] == record["time_stamp"]), "N/A"),
                            record.get("time_stamp", "N/A"),
                            next((x["2"] for x in station_data.get("p24", []) if x["time_stamp"] == record["time_stamp"]), "N/A"),
                            record.get("time_stamp", "N/A")
                        ))

                if extracted_data:
                    insert_into_database(extracted_data)
                else:
                    print("⚠️ No valid data extracted.")

            else:
                print(f"⚠️ API Error: {data.get('error_msg', 'Unknown error')}")

        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Error while fetching data: {e}")

def insert_into_database(data):
    """Insert extracted data into MySQL and confirm success or failure."""
    connection = connect_to_db()
    if connection is None:
        print("❌ Skipping database insert due to connection failure.")
        return

    try:
        cursor = connection.cursor()

        if not data:
            print("⚠️ No data to insert.")
            return

        print("📌 Data Ready for Insert:", data)  # ✅ Print data before inserting

        cursor.executemany(query, data)

        connection.commit()
        print(f"✅ Successfully inserted {len(data)} records into the database.")

    except Exception as e:
        print(f"❌ Database insertion failed: {e}")

    finally:
        cursor.close()
        connection.close()

# Loop through all chunks and send API requests
for chunk in chunk_list(ps_key_list, 50):
    fetch_and_store_data(chunk)  # Execute function for each chunk
