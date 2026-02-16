import requests
import time

# 测试前端到后端的网络连接
def test_frontend_connection():
    # 模拟前端使用的API基础URL
    api_base_url = 'http://localhost:8000/api/v1'
    
    # 测试的API端点
    endpoints = [
        {
            'name': '健康检查',
            'url': '/health',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': '文档列表',
            'url': '/documents/list',
            'method': 'GET',
            'expected_status': 200
        },
        {
            'name': '文档上传',
            'url': '/documents/upload',
            'method': 'POST',
            'expected_status': 200,
            'is_file_upload': True
        },
        {
            'name': '对话功能',
            'url': '/chat/ask',
            'method': 'POST',
            'expected_status': 200,
            'data': {
                'question': '测试网络连接',
                'stream': False,
                'return_paths': True
            }
        }
    ]
    
    print("=" * 80)
    print("📡 前端到后端网络连接测试")
    print("=" * 80)
    print(f"API基础URL: {api_base_url}")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_tests_passed = True
    
    for endpoint in endpoints:
        print(f"\n测试: {endpoint['name']}")
        print(f"端点: {endpoint['url']}")
        print(f"方法: {endpoint['method']}")
        
        try:
            start_time = time.time()
            
            if endpoint.get('is_file_upload'):
                # 测试文件上传
                test_file_content = b"This is a test file for testing file upload functionality"
                files = {'file': ('test.txt', test_file_content, 'text/plain')}
                response = requests.post(
                    api_base_url + endpoint['url'],
                    files=files,
                    timeout=30
                )
            elif endpoint['method'] == 'POST':
                # 测试POST请求
                response = requests.post(
                    api_base_url + endpoint['url'],
                    json=endpoint.get('data', {}),
                    timeout=30
                )
            else:
                # 测试GET请求
                response = requests.get(
                    api_base_url + endpoint['url'],
                    timeout=30
                )
            
            end_time = time.time()
            response_time = round(end_time - start_time, 3)
            
            print(f"状态码: {response.status_code} (预期: {endpoint['expected_status']})")
            print(f"响应时间: {response_time} 秒")
            
            if response.status_code == endpoint['expected_status']:
                print("✅ 测试通过")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"响应类型: JSON")
                        print(f"响应长度: {len(str(data))} 字符")
                    except:
                        print(f"响应类型: 非JSON")
                        print(f"响应长度: {len(response.text)} 字符")
            else:
                print(f"❌ 测试失败，状态码不符")
                print(f"响应内容: {response.text[:200]}...")
                all_tests_passed = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 测试失败，网络错误: {e}")
            print(f"错误类型: {type(e).__name__}")
            all_tests_passed = False
        
        print("-" * 60)
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    if all_tests_passed:
        print("🎉 所有测试通过！前端到后端的网络连接正常")
    else:
        print("⚠️  部分测试失败，需要进一步检查")
    print("=" * 80)

if __name__ == "__main__":
    test_frontend_connection()
