import requests
import os

# 模拟前端的文件上传流程
def test_frontend_upload():
    url = "http://localhost:8000/api/v1/documents/upload"
    
    # 创建一个测试文件
    test_file_path = "test_frontend_upload.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("这是一个测试文件，用于模拟前端的文件上传流程。\n")
        f.write("如果能成功上传，说明API工作正常。\n")
    
    try:
        # 准备FormData，模拟前端的上传方式
        form_data = {}
        files = {
            'file': (test_file_path, open(test_file_path, 'rb'), 'text/plain')
        }
        
        print("正在模拟前端文件上传...")
        print(f"API URL: {url}")
        print(f"测试文件: {test_file_path}")
        
        # 发送请求，不设置Content-Type，让requests自动处理
        response = requests.post(url, files=files)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ 前端模拟上传测试成功！")
            print(f"📄 文档ID: {response.json().get('document_id')}")
            print(f"📁 文件名: {response.json().get('filename')}")
            print(f"📊 文件大小: {response.json().get('file_size')} 字节")
            print(f"⏱️ 处理时间: {response.json().get('processing_time')} 秒")
        else:
            print("\n❌ 前端模拟上传测试失败！")
            
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_file_path):
                # 确保文件关闭
                import time
                time.sleep(0.5)
                os.remove(test_file_path)
                print(f"\n清理测试文件: {test_file_path}")
        except Exception as e:
            print(f"清理文件时出错: {e}")

if __name__ == "__main__":
    test_frontend_upload()
