import requests
import os

# 测试文件上传API
def test_upload():
    url = "http://localhost:8000/api/v1/documents/upload"
    
    # 创建一个测试文件
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("这是一个测试文件，用于测试文件上传功能。\n")
        f.write("如果能成功上传，说明后端API工作正常。\n")
    
    try:
        # 准备文件数据
        files = {
            'file': (test_file_path, open(test_file_path, 'rb'), 'text/plain')
        }
        
        print("正在测试文件上传...")
        response = requests.post(url, files=files)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            print("✅ 文件上传测试成功！")
        else:
            print("❌ 文件上传测试失败！")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_upload()
