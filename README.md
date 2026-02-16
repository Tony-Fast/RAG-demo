# RAG Knowledge Base - 面试演示项目

一个完整的RAG（检索增强生成）知识库网站，用于展示智能问答与信息检索技术。

## 🎯 技术架构

### 前端技术栈
- **React 18** + **TypeScript** - 现代前端框架
- **Tailwind CSS** - 原子化CSS框架
- **Shadcn/UI** - 现代化UI组件库
- **Vite** - 极速构建工具
- **Axios** - HTTP客户端

### 后端技术栈
- **FastAPI** - 高性能Python Web框架
- **FAISS** - Facebook AI相似性搜索库
- **DeepSeek API** - LLM推理服务
- **Sentence-Transformers** - 文本向量化模型

## 📁 项目结构

```
rag-knowledge-base/
├── frontend/                 # React前端项目
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── services/         # API服务
│   │   ├── hooks/            # React Hooks
│   │   ├── types/            # TypeScript类型定义
│   │   ├── stores/           # 状态管理
│   │   ├── utils/            # 工具函数
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── ...
│
├── backend/                  # FastAPI后端项目
│   ├── app/
│   │   ├── api/              # API路由
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务逻辑层
│   │   ├── core/             # 核心配置
│   │   └── main.py           # FastAPI应用入口
│   ├── data/                 # 数据存储目录
│   └── requirements.txt
│
└── README.md
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd rag-knowledge-base
```

### 2. 后端设置
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 DeepSeek API 密钥

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端设置
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用
- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 📖 功能特性

### 核心功能
- 📄 **文档上传** - 支持PDF、Excel、Word、TXT格式
- 🧠 **智能问答** - 基于RAG的问答系统
- 🔍 **向量检索** - FAISS相似性搜索
- 💬 **实时对话** - 流式响应展示
- ⚙️ **配置调整** - 实时调整检索参数

### 高级功能
- 📊 **检索来源** - 显示答案引用来源
- 📁 **知识库管理** - 文档增删改查
- 📝 **对话历史** - 保存历史记录
- 🎨 **主题切换** - 深色/浅色模式

## 🔧 配置说明

### 环境变量 (.env)
```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com

# FAISS 向量存储路径
VECTOR_STORE_PATH=./data/vector_store

# 文档存储路径
DOCUMENTS_PATH=./data/documents

# 嵌入模型
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
CORS_ORIGINS=http://localhost:5173
```

## 📚 API 接口

### 文档管理
- `POST /api/v1/documents/upload` - 上传文档
- `GET /api/v1/documents/list` - 获取文档列表
- `DELETE /api/v1/documents/{id}` - 删除文档

### 问答交互
- `POST /api/v1/chat/ask` - 发送问答请求
- `GET /api/v1/chat/stream` - 流式响应

### 向量存储
- `POST /api/v1/vector/index` - 重建索引
- `GET /api/v1/vector/search` - 测试检索

### 配置管理
- `GET /api/v1/config` - 获取当前配置
- `PUT /api/v1/config` - 更新配置

## 🎨 演示流程

### 1. 上传文档
- 拖拽或选择文档
- 系统自动解析和向量化
- 显示处理进度

### 2. 提问问答
- 输入技术面试问题
- 系统检索相关文档
- 生成带引用的答案

### 3. 调整配置
- 调整检索数量(Top-K)
- 修改相似度阈值
- 观察效果变化

## 🛠️ 技术亮点

1. **完整RAG流程** - 展示文档到问答的完整技术栈
2. **多格式支持** - PDF、Excel、Word、TXT
3. **DeepSeek集成** - 展示国产LLM能力
4. **FAISS本地部署** - 展示向量数据库理解
5. **实时配置** - 演示系统的灵活性

## 📝 面试演示建议

### 开场介绍 (30秒)
- 项目背景和技术选型
- DeepSeek + FAISS 架构优势

### 功能演示 (5分钟)
- 上传技术面试文档
- 演示智能问答功能
- 展示检索来源
- 调整配置参数

### 技术深度 (2分钟)
- 向量检索原理
- 提示词设计思路
- 优化策略讨论

## 📦 依赖说明

### 后端依赖
- fastapi==0.109.0
- uvicorn==0.27.0
- faiss-cpu==1.8.0
- sentence-transformers==2.2.2
- openpyxl==3.1.2
- pypdf2==3.0.1
- python-docx==1.1.0
- aiofiles==23.2.1
- python-multipart==0.0.6

### 前端依赖
- react==18.2.0
- typescript==5.3.3
- tailwindcss==3.4.1
- axios==1.6.5
- shadcn-ui (组件库)

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👨‍💻 作者

[Your Name]

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - LLM服务提供商
- [FAISS](https://github.com/facebookresearch/FAISS) - 向量数据库
- [Sentence-Transformers](https://www.sbert.net/) - 文本嵌入模型
