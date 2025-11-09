from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Test environment variables
        response = {
            "message": "Test endpoint working",
            "turso_url_exists": bool(os.getenv("TURSO_DATABASE_URL")),
            "turso_token_exists": bool(os.getenv("TURSO_AUTH_TOKEN")),
            "secret_key_exists": bool(os.getenv("SECRET_KEY"))
        }
        
        self.wfile.write(json.dumps(response).encode())