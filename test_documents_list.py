import requests

# 测试文档列表接口
url = 'http://localhost:8000/api/v1/documents/list'

# 发送GET请求
print("开始测试文档列表接口...")
response = requests.get(url)

# 打印响应结果
print(f"响应状态码: {response.status_code}")
print(f"响应内容: {response.text}")

if response.status_code == 200:
    print("\n测试成功！后端返回了文档列表。")
    
    # 解析响应内容
    data = response.json()
    documents = data.get('documents', [])
    
    print(f"\n文档总数: {len(documents)}")
    
    # 打印每个文档的信息
    for i, doc in enumerate(documents, 1):
        print(f"\n文档 {i}:")
        print(f"  ID: {doc.get('id')}")
        print(f"  文件名: {doc.get('filename')}")
        print(f"  文件格式: {doc.get('file_format')}")
        print(f"  文件大小: {doc.get('file_size')} bytes")
        print(f"  状态: {doc.get('status')}")
        print(f"  创建时间: {doc.get('created_at')}")
        print(f"  段落数: {doc.get('chunk_count')}")
else:
    print("\n测试失败！后端返回了错误状态码。")
