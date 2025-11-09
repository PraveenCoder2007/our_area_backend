from http.server import BaseHTTPRequestHandler
import json
import os
import libsql_client
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            action = query_params.get('action', [''])[0]
            
            if action == 'login':
                username = query_params.get('username', [''])[0]
                password = query_params.get('password', [''])[0]
                
                if not username or not password:
                    response = {"error": "Username and password required"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                db = libsql_client.create_client(
                    url=os.getenv("TURSO_DB_URL"),
                    auth_token=os.getenv("TURSO_DB_TOKEN")
                )
                
                result = db.execute(
                    "SELECT * FROM users WHERE username = ?",
                    [username]
                )
                
                if not result.rows or not pwd_context.verify(password, result.rows[0][7]):
                    response = {"error": "Invalid credentials"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                token = jwt.encode(
                    {"sub": result.rows[0][0], "exp": datetime.utcnow() + timedelta(minutes=30)},
                    os.getenv("SECRET_KEY", "fallback-secret"),
                    algorithm="HS256"
                )
                
                response = {"access_token": token, "token_type": "bearer"}
                self.wfile.write(json.dumps(response).encode())
                
            elif action == 'areas':
                db = libsql_client.create_client(
                    url=os.getenv("TURSO_DB_URL"),
                    auth_token=os.getenv("TURSO_DB_TOKEN")
                )
                
                result = db.execute("SELECT * FROM areas")
                
                areas = [{
                    "id": row[0],
                    "name": row[1],
                    "center_lat": row[2],
                    "center_lng": row[3],
                    "radius_m": row[4]
                } for row in result.rows]
                
                self.wfile.write(json.dumps(areas).encode())
                
            else:
                response = {
                    "message": "Our Area API - Vercel Workaround",
                    "available_actions": [
                        "login: ?action=login&username=johndoe&password=password123",
                        "areas: ?action=areas"
                    ]
                }
                self.wfile.write(json.dumps(response).encode())
                
        except Exception as e:
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())