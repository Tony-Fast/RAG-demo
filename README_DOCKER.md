# Docker部署指南

本指南提供了使用Docker容器化技术部署RAG知识库系统的详细步骤。

## 环境要求

- Docker 19.03+ 
- Docker Compose 1.25+
- 至少 2GB RAM
- 至少 10GB 磁盘空间

## 快速开始

### 1. 配置环境变量

复制环境变量模板文件并根据需要修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置您的 DeepSeek API 密钥：

```env
DEEPSEEK_API_KEY=your_actual_api_key_here
```

### 2. 构建和启动容器

使用 Docker Compose 构建和启动整个应用：

```bash
docker-compose up -d --build
```

### 3. 访问应用

容器启动后，您可以通过以下地址访问应用：

- **前端应用**：http://localhost
- **后端API**：http://localhost:8000
- **API文档**：http://localhost:8000/docs

### 4. 查看容器状态

```bash
docker-compose ps
```

### 5. 查看容器日志

```bash
# 查看后端日志
docker-compose logs backend

# 查看前端日志
docker-compose logs frontend
```

## 详细配置

### 后端配置

后端容器配置包括：

- 端口映射：8000:8000
- 数据持久化：使用Docker卷存储数据
- 环境变量：支持多种配置选项
- 健康检查：自动监控服务状态

### 前端配置

前端容器配置包括：

- 端口映射：80:80
- 依赖关系：在后端启动后启动
- 健康检查：自动监控服务状态

### 网络配置

应用使用自定义Docker网络 `rag-network`，确保前端和后端能够安全通信。

## 管理命令

### 停止容器

```bash
docker-compose down
```

### 重启容器

```bash
docker-compose restart
```

### 更新应用

当您修改代码后，需要重新构建和启动容器：

```bash
docker-compose up -d --build
```

### 清理数据

如果需要清理所有数据并重新开始：

```bash
docker-compose down -v
docker-compose up -d --build
```

## 故障排查

### 常见问题

1. **API密钥错误**：确保您在 `.env` 文件中正确配置了 DeepSeek API 密钥

2. **端口冲突**：如果80或8000端口已被占用，请修改 `docker-compose.yml` 文件中的端口映射

3. **容器启动失败**：使用 `docker-compose logs` 查看详细错误信息

4. **前端无法连接后端**：确保后端容器已成功启动且健康检查通过

### 健康检查

系统包含内置的健康检查机制，可自动监控服务状态：

- 后端：每30秒检查一次 `/health` 端点
- 前端：每30秒检查一次根路径

## 性能优化

### 资源限制

您可以在 `docker-compose.yml` 文件中添加资源限制，避免容器占用过多资源：

```yaml
backend:
  # 其他配置...
  deploy:
    resources:
      limits:
        cpus: "2"
        memory: "2G"

frontend:
  # 其他配置...
  deploy:
    resources:
      limits:
        cpus: "1"
        memory: "1G"
```

### 缓存优化

Docker会自动缓存构建步骤，提高后续构建速度。如需强制重新构建：

```bash
docker-compose build --no-cache
```

## 生产环境部署

### 安全建议

1. **使用HTTPS**：在生产环境中，建议配置SSL证书
2. **设置强密码**：如果添加认证，使用强密码
3. **限制访问**：配置防火墙，只允许必要的端口访问
4. **定期更新**：定期更新Docker镜像和依赖项

### 监控

在生产环境中，建议添加监控系统，如Prometheus和Grafana，监控容器状态和性能。

## 常见问题

### Q: 为什么容器启动后无法访问应用？
A: 请检查：
- 容器是否正常运行 (`docker-compose ps`)
- 端口是否正确映射 (`docker-compose logs`)
- 防火墙是否允许访问

### Q: 如何更新应用代码？
A: 修改代码后，运行 `docker-compose up -d --build` 重新构建和启动容器。

### Q: 数据存储在哪里？
A: 数据存储在Docker卷 `backend-data` 中，位于 `/var/lib/docker/volumes/rag-backend-data/`。

### Q: 如何备份数据？
A: 可以使用 `docker cp` 命令从容器中复制数据：

```bash
docker cp rag-backend:/app/data ./backup
```

## 联系支持

如果您在部署过程中遇到任何问题，请参考项目文档或联系技术支持。
