from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "Our Area API is running on Vercel",
            "status": "ok",
            "endpoints": [
                "GET /api/health",
                "POST /api/signup",
                "POST /api/login",
                "GET /api/users (auth required)",
                "PUT /api/users (auth required)",
                "GET /api/areas",
                "GET /api/posts (auth required)",
                "POST /api/posts (auth required)"
            ]
        }
        
        self.wfile.write(json.dumps(response).encode())