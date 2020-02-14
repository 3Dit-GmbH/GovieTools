from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir
import sys


class RequestHandler(BaseHTTPRequestHandler):

    file_path = sys.argv[1]

    def _send_cors_headers(self):
        """ Sets headers required for CORS """
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers",
                         "x-api-key,Content-Type")

    def do_GET(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

        with open(self.file_path, 'rb') as file: 
            self.wfile.write(file.read()) 
        
        response = {}
        response["status"] = "OK"

httpd = HTTPServer(("127.0.0.1", 8000), RequestHandler)
print("Hosting server http://127.0.0.1:8000")
httpd.serve_forever()
