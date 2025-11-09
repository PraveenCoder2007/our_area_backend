from http.server import BaseHTTPRequestHandler
import json
import os
import libsql_client
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        
        try:
            db = libsql_client.create_client(
                url=os.getenv("TURSO_DATABASE_URL"),
                auth_token=os.getenv("TURSO_AUTH_TOKEN")
            )
            
            result = db.execute("SELECT * FROM areas")
            
            areas = [{
                "id": row[0],
                "name": row[1],
                "center_lat": row[2],
                "center_lng": row[3],
                "radius_m": row[4]
            } for row in result.rows]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(areas).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())