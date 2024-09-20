from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from pyngrok import ngrok
import time
import requests


class HelloHandler(BaseHTTPRequestHandler):
    last_ip_time = 0
    delay_seconds = 1

    def do_GET(self):
        current_time = time.time()
        if current_time - HelloHandler.last_ip_time < HelloHandler.delay_seconds:
            self.send_response(429)
            self.end_headers()
            return

        forwarded_for = self.headers.get('X-Forwarded-For')
        if forwarded_for:
            visitor_ip = forwarded_for.split(',')[0].strip()
        else:
            visitor_ip = self.client_address[0]

        print(f"New IP found: {visitor_ip}")
        HelloHandler.last_ip_time = current_time
        ip_info = self.get_ip_info(visitor_ip)
        print()

        body = bytes("Hello, nice IP", "utf-8")
        self.protocol_version = "HTTP/1.1"
        self.send_response(200)  //  simple html messagge, comment these 4 lines if u want to redirect a user
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

        # Redirect response, uncomment these 3 lines if u wanna redirect a user
        # self.send_response(302)
        # self.send_header("Location", "https://c.tenor.com/boiPHdyVTJ8AAAAd/tenor.gif")  funny meme
        # self.end_headers()

    def get_ip_info(self, ip):
        url = f"https://ipinfo.io/{ip}/json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            print("IP Info:")
            for key, value in {
                "Hostname": data.get("hostname", "N/A"),
                "City": data.get("city", "N/A"),
                "Region": data.get("region", "N/A"),
                "Country": data.get("country", "N/A"),
                "Location": data.get("loc", "N/A"),
                "Organization": data.get("org", "N/A")
            }.items():
                print(f"{key}: {value}")
        except requests.RequestException:
            print("Error retrieving IP info")

    def log_message(self, format, *args):
        return


logging.getLogger().setLevel(logging.CRITICAL)

server = HTTPServer(("localhost", 0), HelloHandler)
port = server.server_address[1]
public_url = ngrok.connect(port)
print(f" {public_url} ")

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("Shutting down server...")

ngrok.disconnect(public_url)
