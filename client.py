
import requests
import time

def fetch_price():
    try:
        response = requests.get("http://localhost:8000")  # Server URL
        if response.status_code == 200:
            print(f"Current Price: {response.text}")
        else:
            print(f"Failed to fetch price. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    while True:
        fetch_price()
        time.sleep(10)  # Fetch price every 10 seconds
