import axios
import os

# 使用axios模拟前端的文件上传流程
def test_axios_upload():
    api_base_url = 'http://localhost:8000/api/v1'
    
    # 创建axios实例，与前端配置相同
    client = axios.create({
        baseURL: api_base_url,
        timeout: 60000,
        headers: {
            'Content-Type': 'application/json',
        },
    })
    
    # 创建一个测试文件
    test_file_path = "test_axios_upload.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("# 测试文档\n\n")
        f.write("这是一个使用axios库测试的文档，用于验证前端文件上传修复是否有效。\n\n")
        f.write("## 测试内容\n")
        f.write("1. 使用axios上传文件\n")
        f.write("2. 不手动设置Content-Type\n")
        f.write("3. 验证上传是否成功\n")
    
    try:
        # 准备FormData
        from requests_toolbelt.multipart.encoder import MultipartEncoder
        
        # 模拟FormData的创建和发送
        m = MultipartEncoder(
            fields={'file': (test_file_path, open(test_file_path, 'rb'), 'text/plain')}
        )
        
        print("正在使用axios模拟前端文件上传...")
        print(f"API URL: {api_base_url}/documents/upload")
        print(f"测试文件: {test_file_path}")
        
        # 发送请求，让axios自动处理Content-Type
        response = client.post(
            '/documents/upload',
            data=m,
            headers={'Content-Type': m.content_type}
        )
        
        print(f"\n响应状态码: {response.status}")
        print(f"响应内容: {response.data}")
        
        if response.status == 200:
            print("\n✅ Axios上传测试成功！")
            print(f"📄 文档ID: {response.data.get('document_id')}")
            print(f"📁 文件名: {response.data.get('filename')}")
            print(f"📊 文件大小: {response.data.get('file_size')} 字节")
            print(f"⏱️ 处理时间: {response.data.get('processing_time')} 秒")
        else:
            print("\n❌ Axios上传测试失败！")
            
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试文件
        try:
            if os.path.exists(test_file_path):
                import time
                time.sleep(0.5)
                os.remove(test_file_path)
                print(f"\n清理测试文件: {test_file_path}")
        except Exception as e:
            print(f"清理文件时出错: {e}")

if __name__ == "__main__":
    test_axios_upload()
