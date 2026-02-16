import requests
import json

# 测试聊天 API
def test_chat_api():
    url = "http://localhost:8000/api/v1/chat/ask"
    headers = {"Content-Type": "application/json"}
    data = {
        "question": "测试消息",
        "top_k": 5,
        "stream": False,
        "context": []
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # 尝试以不同的编码解析
        try:
            json_data = response.json()
            print("\nResponse data:")
            print(json.dumps(json_data, ensure_ascii=False, indent=2))
            print(f"\nQuestion: {json_data.get('question')}")
            print(f"Answer: {json_data.get('answer')}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response content (raw): {response.content}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing chat API...")
    test_chat_api()
