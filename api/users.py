from http.server import BaseHTTPRequestHandler
import json
import os
import libsql_client
from jose import jwt

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
            db = libsql_client.create_client(
                url=os.getenv("TURSO_DATABASE_URL"),
                auth_token=os.getenv("TURSO_AUTH_TOKEN")
            )
            
            result = db.execute("SELECT * FROM users WHERE id = ?", [user["id"]])
            if not result.rows:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "User not found"}).encode())
                return
            
            user_data = result.rows[0]
            response = {
                "id": user_data[0],
                "display_name": user_data[1],
                "username": user_data[2],
                "phone": user_data[3],
                "email": user_data[4]
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_PUT(self):
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
            user_update = json.loads(post_data.decode('utf-8'))
            
            db = libsql_client.create_client(
                url=os.getenv("TURSO_DATABASE_URL"),
                auth_token=os.getenv("TURSO_AUTH_TOKEN")
            )
            
            fields = []
            values = []
            for key, value in user_update.items():
                if key in ["display_name", "phone", "email", "bio"]:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if fields:
                values.append(user["id"])
                db.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": "Profile updated"}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()