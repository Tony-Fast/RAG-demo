import requests

# 测试前端到后端的网络连接
def test_network_connection():
    # 模拟前端使用的API URL
    api_base_url = 'http://localhost:8000/api/v1'
    
    test_endpoints = [
        '/health',
        '/documents/list',
        '/chat/ask'
    ]
    
    print("测试前端到后端的网络连接...")
    print(f"API Base URL: {api_base_url}")
    print("=" * 60)
    
    for endpoint in test_endpoints:
        url = api_base_url + endpoint
        print(f"\n测试端点: {endpoint}")
        print(f"完整URL: {url}")
        
        try:
            if endpoint == '/chat/ask':
                # 对于POST请求
                response = requests.post(url, json={'question': '测试连接', 'stream': False})
            else:
                # 对于GET请求
                response = requests.get(url, timeout=10)
            
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json() if response.status_code == 200 else 'Error'}")
            print("✅ 连接成功!")
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
    
    print("\n" + "=" * 60)
    print("网络连接测试完成")

if __name__ == "__main__":
    test_network_connection()
