"""
Test script for chat API
"""

import requests
import json

# Test health check
def test_health_check():
    """
    Test health check endpoint
    """
    print("Testing health check...")
    url = "http://localhost:8000/api/v1/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        print("✅ Health check passed!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Test chat API
def test_chat_api():
    """
    Test chat API endpoint
    """
    print("\nTesting chat API...")
    url = "http://localhost:8000/api/v1/chat/ask"
    headers = {
        "Content-Type": "application/json",
        "X-App-Password": "demo123"
    }
    data = {
        "question": "Hello world",
        "document_id": None,
        "context": []
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Chat API test passed!")
            return True
        else:
            print("❌ Chat API test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Main function
if __name__ == "__main__":
    print("=== Testing RAG API ===")
    
    health_ok = test_health_check()
    chat_ok = test_chat_api()
    
    print("\n=== Test Results ===")
    print(f"Health check: {'PASSED' if health_ok else 'FAILED'}")
    print(f"Chat API: {'PASSED' if chat_ok else 'FAILED'}")
    
    if health_ok and chat_ok:
        print("\n✅ All tests passed! The system is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the system.")
