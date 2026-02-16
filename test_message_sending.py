import requests
import json

# 测试聊天 API
def test_chat_api():
    url = "http://localhost:8000/api/v1/chat/ask"
    headers = {"Content-Type": "application/json"}
    data = {
        "question": "你好，能告诉我什么是 RAG 技术吗？",
        "top_k": 5,
        "stream": False,
        "context": []
    }
    
    try:
        print("测试消息发送功能...")
        print(f"请求 URL: {url}")
        print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        json_data = response.json()
        print("\n响应数据:")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
        print(f"\n问题: {json_data.get('question')}")
        print(f"回答: {json_data.get('answer')}")
        print(f"来源数量: {len(json_data.get('sources', []))}")
        
        print("\n✅ 消息发送功能测试成功！")
        return True
    except Exception as e:
        print(f"\n❌ 消息发送功能测试失败: {e}")
        return False

if __name__ == "__main__":
    test_chat_api()
