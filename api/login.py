from http.server import BaseHTTPRequestHandler
import json
import os
import libsql_client
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            credentials = json.loads(post_data.decode('utf-8'))
            
            # Connect to Turso
            db = libsql_client.create_client(
                url=os.getenv("TURSO_DATABASE_URL"),
                auth_token=os.getenv("TURSO_AUTH_TOKEN")
            )
            
            result = db.execute(
                "SELECT * FROM users WHERE username = ?",
                [credentials["username"]]
            )
            
            if not result.rows or not pwd_context.verify(credentials["password"], result.rows[0][7]):
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid credentials"}).encode())
                return
            
            token = jwt.encode(
                {"sub": result.rows[0][0], "exp": datetime.utcnow() + timedelta(minutes=30)},
                os.getenv("SECRET_KEY", "fallback-secret"),
                algorithm="HS256"
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {"access_token": token, "token_type": "bearer"}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()