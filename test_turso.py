import os
import requests

def test_turso_connection():
    turso_url = "libsql://ourarea-praveencoder2007.aws-ap-south-1.turso.io"
    turso_token = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NjMwOTYyMzYsImlkIjoiNWM1ZjM1NTAtZjgyYi00YWNhLWFmOTgtMzY5N2VkZjQ5YjRmIiwicmlkIjoiNDI0ZWJiZDgtMmVmMS00NWU3LWJjNzMtZmRiNzE4NWJkZDllIn0.UF8VihY1tRgDrtMl7VLc7EjsHeuvITe2AVmo1_KtQaHRnjHSxRLXmuLRRpTU4dFd0m0fu-cu7uor-GcG0AoKDA"
    
    # Convert to HTTP API URL
    api_url = turso_url.replace("libsql://", "https://").replace(".turso.io", ".turso.io/v2/pipeline")
    
    headers = {
        "Authorization": f"Bearer {turso_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "requests": [{
            "type": "execute",
            "stmt": {
                "sql": "SELECT * FROM users LIMIT 5",
                "args": []
            }
        }]
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        print("Status:", response.status_code)
        print("Response:", response.json())
        return response.json()
    except Exception as e:
        print("Error:", str(e))
        return None

if __name__ == "__main__":
    test_turso_connection()