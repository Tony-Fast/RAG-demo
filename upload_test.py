import requests
import os

# 上传文档的API端点
url = 'http://localhost:8000/api/v1/documents/upload'

# 测试文档的路径
test_file_path = 'e:\\TRAE测试调试RAG\\RAG\\测试文档.txt'

# 检查文件是否存在
if not os.path.exists(test_file_path):
    print(f"文件不存在: {test_file_path}")
    exit(1)

# 读取文件内容
with open(test_file_path, 'rb') as f:
    files = {
        'file': ('测试文档.txt', f, 'text/plain')
    }

    # 发送POST请求上传文档
    print("开始上传测试文档...")
    response = requests.post(url, files=files)

    # 打印响应结果
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")

    if response.status_code == 200:
        print("文档上传成功！")
    else:
        print("文档上传失败！")
