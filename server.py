import requests
from bs4 import BeautifulSoup
import schedule
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Cache to store the price
price_cache = "Price not available yet."

def scrape():
    global price_cache
    address = "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"  # Replace with the actual URL
    response = requests.get(address)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find('div', class_="Nx9bqj CxhGGd")  # Replace with the actual class or identifier
        if price_element:
            price_cache = price_element.get_text(strip=True)[1:]
            print(f"Price fetched: {price_cache}")
        else:
            print("Price element not found.")
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")

# Schedule the scrape function to run every 0.1 minutes (6 seconds)
schedule.every(0.1).minutes.do(scrape)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(price_cache, "utf-8"))

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("HTTP server running on port 8000...")
    httpd.serve_forever()

def run_scheduled_jobs():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Perform an initial scrape to ensure the cache is populated
    scrape()

    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # Ensure the thread exits when the main program does
    server_thread.start()

    # Run the scheduled scraping jobs
    run_scheduled_jobs()
