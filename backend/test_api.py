import requests
import json

# Test chat API with password authentication
def test_chat_api():
    url = "http://localhost:8000/api/v1/chat/ask"
    headers = {
        "Content-Type": "application/json",
        "X-App-Password": "demo123"
    }
    data = {
        "question": "Hello world",
        "document_id": None
    }
    
    print("Testing chat API...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Chat API test passed!")
        else:
            print("❌ Chat API test failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Test health check endpoint
def test_health_check():
    url = "http://localhost:8000/health"
    
    print("\nTesting health check...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Health check test passed!")
        else:
            print("❌ Health check test failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=== API Test Suite ===")
    test_health_check()
    test_chat_api()
    print("=== Test Complete ===")
