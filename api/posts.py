from http.server import BaseHTTPRequestHandler
import json
import os
import libsql_client
from jose import jwt
import uuid
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def get_user_from_token(self):
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, os.getenv("SECRET_KEY", "fallback-secret"), algorithms=["HS256"])
            return {"id": payload.get("sub")}
        except:
            return None
    
    def do_GET(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        
        user = self.get_user_from_token()
        if not user:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return
        
        try:
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            area_id = query_params.get('area_id', ['area1'])[0]
            page = int(query_params.get('page', ['1'])[0])
            limit = int(query_params.get('limit', ['20'])[0])
            offset = (page - 1) * limit
            
            db = libsql_client.create_client(
                url=os.getenv("TURSO_DATABASE_URL"),
                auth_token=os.getenv("TURSO_AUTH_TOKEN")
            )
            
            result = db.execute(
                "SELECT p.*, u.display_name, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.area_id = ? AND p.is_deleted = 0 ORDER BY p.created_at DESC LIMIT ? OFFSET ?",
                [area_id, limit, offset]
            )
            
            posts = [{
                "id": row[0],
                "user_id": row[1],
                "area_id": row[2],
                "text": row[4],
                "category": row[5],
                "created_at": row[8],
                "user": {"display_name": row[11], "username": row[12]}
            } for row in result.rows]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(posts).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_POST(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        
        user = self.get_user_from_token()
        if not user:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_info = json.loads(post_data.decode('utf-8'))
            
            db = libsql_client.create_client(
                url=os.getenv("TURSO_DATABASE_URL"),
                auth_token=os.getenv("TURSO_AUTH_TOKEN")
            )
            
            post_id = str(uuid.uuid4())
            
            db.execute(
                "INSERT INTO posts (id, user_id, area_id, text, category) VALUES (?, ?, ?, ?, ?)",
                [post_id, user["id"], post_info["area_id"], post_info["text"], post_info["category"]]
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Post created", "data": {"post_id": post_id}}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()