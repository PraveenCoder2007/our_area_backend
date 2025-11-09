import asyncio
import aiohttp
import json

async def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test root endpoint
        print("Testing root endpoint...")
        async with session.get(f"{base_url}/") as resp:
            data = await resp.json()
            print(f"Root: {data}")
        
        # Test login with sample user
        print("\nTesting login...")
        login_data = {
            "username": "johndoe",
            "password": "password123"
        }
        async with session.post(f"{base_url}/auth/login", json=login_data) as resp:
            if resp.status == 200:
                token_data = await resp.json()
                token = token_data["access_token"]
                print(f"Login successful: {token[:20]}...")
                
                # Test authenticated endpoint
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(f"{base_url}/users/me", headers=headers) as resp:
                    if resp.status == 200:
                        user_data = await resp.json()
                        print(f"User data: {user_data}")
                    else:
                        print(f"Failed to get user data: {resp.status}")
            else:
                print(f"Login failed: {resp.status}")
        
        # Test areas endpoint
        print("\nTesting areas endpoint...")
        async with session.get(f"{base_url}/areas/near?lat=40.7128&lng=-74.0060") as resp:
            if resp.status == 200:
                areas = await resp.json()
                print(f"Found {len(areas)} areas")
            else:
                print(f"Failed to get areas: {resp.status}")

if __name__ == "__main__":
    print("Make sure the server is running with: python run.py")
    print("Then run this test in another terminal")
    # asyncio.run(test_api())