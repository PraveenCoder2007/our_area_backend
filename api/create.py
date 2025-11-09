from http.server import BaseHTTPRequestHandler
import json
import os
import libsql_client
import uuid
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Get parameters
            text = query_params.get('text', ['Default post from GET method'])[0]
            category = query_params.get('category', ['event'])[0]
            area_id = query_params.get('area_id', ['area1'])[0]
            
            # Connect to Turso
            db = libsql_client.create_client(
                url=os.getenv("TURSO_DB_URL"),
                auth_token=os.getenv("TURSO_DB_TOKEN")
            )
            
            # Create post
            post_id = str(uuid.uuid4())
            user_id = "user1"  # Using existing user
            
            db.execute(
                "INSERT INTO posts (id, user_id, area_id, text, category) VALUES (?, ?, ?, ?, ?)",
                [post_id, user_id, area_id, text, category]
            )
            
            response = {
                "status": "success",
                "message": "Post created successfully via GET method",
                "data": {
                    "post_id": post_id,
                    "text": text,
                    "category": category,
                    "area_id": area_id,
                    "user_id": user_id
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                "status": "error",
                "message": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())