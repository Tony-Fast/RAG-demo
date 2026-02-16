# Docker 部署配置

本项目支持使用 Docker 进行容器化部署。

## 快速开始

### 1. 构建并启动服务

```bash
docker-compose up -d
```

### 2. 查看日志

```bash
docker-compose logs -f
```

### 3. 停止服务

```bash
docker-compose down
```

## 服务说明

### 后端服务

- **端口**: 8000
- **健康检查**: http://localhost:8000/health

### 前端服务（生产构建）

- **端口**: 80 (通过 Nginx 托管)

## 环境变量

创建 `.env` 文件并配置以下变量：

```env
# DeepSeek API
DEEPSEEK_API_KEY=your_api_key

# 存储路径
VECTOR_STORE_PATH=/app/data/vector_store
DOCUMENTS_PATH=/app/data/documents
```

## 开发模式

如需进入开发模式：

```bash
# 后端
docker-compose exec backend bash

# 前端
docker-compose exec frontend sh
```

## 数据持久化

以下目录会被挂载到宿主机：

- `./data/documents` - 上传的文档
- `./data/vector_store` - FAISS 索引

## 生产部署建议

1. 修改 `nginx.conf` 配置 SSL 证书
2. 使用环境变量管理敏感信息
3. 配置日志收集系统
4. 设置监控告警
