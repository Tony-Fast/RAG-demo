import requests
import json

# 测试文档上传 API
def test_document_upload():
    url = "http://localhost:8000/api/v1/documents/upload"
    file_path = "test_document.txt"
    
    try:
        print("测试文档上传功能...")
        print(f"请求 URL: {url}")
        print(f"上传文件: {file_path}")
        
        # 构建 multipart/form-data 请求
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'text/plain')}
            response = requests.post(url, files=files, timeout=30)
        
        response.raise_for_status()
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        json_data = response.json()
        print("\n响应数据:")
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
        
        print("\n✅ 文档上传功能测试成功！")
        return True
    except Exception as e:
        print(f"\n❌ 文档上传功能测试失败: {e}")
        return False

if __name__ == "__main__":
    test_document_upload()
