import json
import os
import libsql_client
import uuid
from datetime import datetime

def handler(event, context):
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }
    
    # Handle OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Connect to Turso
        db = libsql_client.create_client(
            url=os.getenv("TURSO_DB_URL"),
            auth_token=os.getenv("TURSO_DB_TOKEN")
        )
        
        # Create post data
        post_id = str(uuid.uuid4())
        user_id = "user1"  # Using existing user from seed data
        area_id = body.get('area_id', 'area1')
        text = body.get('text', 'Default post text')
        category = body.get('category', 'event')
        
        # Insert into database
        db.execute(
            "INSERT INTO posts (id, user_id, area_id, text, category) VALUES (?, ?, ?, ?, ?)",
            [post_id, user_id, area_id, text, category]
        )
        
        # Return success response
        response = {
            "status": "success",
            "message": "Post created successfully",
            "data": {
                "post_id": post_id,
                "text": text,
                "category": category,
                "area_id": area_id
            }
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        error_response = {
            "status": "error",
            "message": str(e)
        }
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps(error_response)
        }