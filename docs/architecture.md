# RAG 知识库系统 - 架构设计文档

本文档详细描述 RAG 知识库系统的技术架构设计，包括组件划分、数据流程和关键技术实现。

## 1. 系统概述

RAG（Retrieval-Augmented Generation）知识库系统是一个基于检索增强生成技术的智能问答平台。系统核心目标是展示如何将外部知识库与大语言模型结合，实现准确、可溯源的问答功能。

### 1.1 系统目标

- **核心功能**：支持多格式文档上传、智能问答、检索结果可视化
- **性能要求**：响应时间小于 5 秒，支持并发请求
- **可用性**：友好的用户界面，清晰的交互流程
- **可扩展性**：模块化设计，便于功能扩展和维护

### 1.2 技术选型理由

| 组件 | 选择 | 理由 |
|------|------|------|
| 前端框架 | React 18 + TypeScript | 组件化开发、类型安全、生态丰富 |
| 后端框架 | FastAPI | 高性能、异步支持、自动文档 |
| 向量数据库 | FAISS | 高效检索、本地部署、开源免费 |
| 大语言模型 | DeepSeek | 性价比高、中文能力强 |
| 文本嵌入 | Sentence-Transformers | 多语言支持、预训练模型 |
| CSS 框架 | Tailwind CSS | 原子化设计、灵活定制 |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  React 前端应用                       │   │
│  │  ┌───────────┐ ┌───────────┐ ┌─────────────────┐  │   │
│  │  │  问答界面   │ │ 文档管理  │ │    配置面板      │  │   │
│  │  └───────────┘ └───────────┘ └─────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI 后端服务                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    API 网关                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │   │
│  │  │ 问答接口  │ │文档接口  │ │配置接口  │ │健康检查  │  │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │   │
│  └───────┼───────────┼───────────┼───────────┼───────┘   │
│          │           │           │           │             │
│          ▼           ▼           ▼           ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   业务服务层                          │   │
│  │  ┌────────────┐ ┌────────────┐ ┌─────────────────┐  │   │
│  │  │ 文档处理    │ │ 向量存储   │ │   RAG 问答服务   │  │   │
│  │  │  服务      │ │  服务      │ │                │  │   │
│  │  └────┬───────┘ └────┬───────┘ └───────┬─────────┘  │   │
│  └───────┼─────────────┼─────────────────┼─────────────┘   │
│          │             │                 │                  │
│          ▼             ▼                 ▼                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   基础设施层                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌───────────────┐  │   │
│  │  │  FAISS      │ │  DeepSeek   │ │  文件系统      │  │   │
│  │  │  向量库     │ │   API      │ │  (文档存储)    │  │   │
│  │  └─────────────┘ └─────────────┘ └───────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 前端架构

前端采用 React 框架，配合 Tailwind CSS 和 Shadcn/UI 组件库构建现代化界面。

#### 组件结构

```
frontend/src/
├── components/
│   ├── ui/                    # 基础 UI 组件
│   │   ├── button.tsx         # 按钮
│   │   ├── card.tsx          # 卡片
│   │   ├── input.tsx          # 输入框
│   │   ├── tabs.tsx          # 标签页
│   │   ├── scroll-area.tsx   # 滚动区域
│   │   └── progress.tsx      # 进度条
│   │
│   ├── ChatArea.tsx           # 核心问答组件
│   ├── DocumentUpload.tsx     # 文档上传组件
│   ├── KnowledgePanel.tsx     # 知识库管理面板
│   └── ConfigPanel.tsx        # 配置调整面板
│
├── lib/
│   ├── api.ts                # Axios API 客户端
│   ├── types.ts              # TypeScript 类型定义
│   └── utils.ts              # 工具函数
│
├── App.tsx                   # 主应用组件
└── main.tsx                  # 入口文件
```

#### 状态管理

前端状态管理采用 React Hooks 和 Context 模式：

- **局部状态**：组件内部的 UI 状态（如表单输入）
- **全局状态**：跨组件共享的状态（如用户配置）
- **服务端状态**：通过 React Query 或直接使用 Effect 管理

### 2.3 后端架构

后端采用 FastAPI 框架，提供 RESTful API 服务。

#### 模块划分

```
backend/app/
├── main.py                   # FastAPI 应用入口
├── core/
│   └── config.py            # 配置管理
├── api/v1/
│   ├── router.py            # 路由聚合
│   └── endpoints/
│       ├── chat.py          # 问答接口
│       ├── document.py       # 文档管理接口
│       ├── config.py        # 配置接口
│       └── health.py        # 健康检查接口
├── models/
│   ├── schemas.py           # Pydantic 数据模型
│   └── entities.py          # 业务实体类
└── services/
    ├── document_processor.py # 文档处理服务
    ├── embedding_service.py  # 文本向量化服务
    ├── vector_store.py       # 向量存储服务
    ├── llm_service.py        # 大语言模型服务
    └── rag_service.py        # RAG 核心服务
```

---

## 3. 数据流设计

### 3.1 文档上传流程

```
用户选择文件
    │
    ▼
前端：文件验证（格式、大小）
    │
    ▼
POST /api/v1/documents/upload
    │
    ▼
后端：接收文件并保存
    │
    ▼
文档处理服务：
  1. 根据格式调用对应的解析器
  2. 提取纯文本内容
  3. 文本分块（Chunking）
  4. 生成元数据
    │
    ▼
嵌入服务：文本向量化
    │
    ▼
向量存储：FAISS 索引
    │
    ▼
返回处理结果
```

**详细步骤：**

1. **文件接收**：FastAPI 使用 `UploadFile` 接收 multipart/form-data 格式的文件
2. **格式验证**：检查文件扩展名是否在支持列表中（.pdf、.docx、.xlsx、.txt、.csv）
3. **文件保存**：将文件保存到 `data/documents` 目录
4. **文本提取**：
   - PDF：使用 PyPDF2 提取页面文本
   - Word：使用 python-docx 提取段落
   - Excel：使用 OpenPyXL 读取单元格
   - TXT：使用 charset-normalizer 检测编码
5. **文本分块**：按配置的 chunk_size（默认 1000 字符）切分，支持重叠
6. **向量化**：使用 Sentence-Transformers 模型生成向量
7. **索引存储**：FAISS IndexIDMap 存储向量和 ID

### 3.2 问答流程

```
用户输入问题
    │
    ▼
前端：输入验证
    │
    ▼
POST /api/v1/chat/ask
    │
    ▼
问题向量化
    │
    ▼
FAISS 相似性搜索（Top-K）
    │
    ▼
结果过滤（相似度阈值）
    │
    ▼
构建 RAG 提示词
    │
    ▼
DeepSeek API 生成回答
    │
    ▼
格式化返回结果
    │
    ▼
前端展示
```

**详细步骤：**

1. **问题接收**：接收用户问题文本，验证非空
2. **向量化**：使用 Sentence-Transformers 将问题转换为向量
3. **向量检索**：
   - 在 FAISS 索引中搜索最相似的向量
   - 返回 Top-K（默认 5）个结果
   - 计算余弦相似度分数
4. **结果过滤**：过滤低于相似度阈值的结果
5. **提示词构建**：
   ```
   系统提示：你是一个专业的AI助手...
   
   上下文信息：
   [来源 1] 文档片段1...
   [来源 2] 文档片段2...
   
   用户问题：xxx
   
   请根据上下文回答...
   ```
6. **模型调用**：调用 DeepSeek API 发送完整提示词
7. **结果返回**：包含回答内容、来源信息、响应时间等

---

## 4. 核心技术实现

### 4.1 向量存储（FAISS）

FAISS（Facebook AI Similarity Search）是一个高效的向量相似性搜索库。

#### 索引选择

系统使用 `IndexIDMap` + `IndexFlatIP` 的组合：

- **IndexFlatIP**：内积索引，配合归一化向量实现余弦相似度
- **IndexIDMap**：支持自定义 ID 映射，便于元数据关联

#### 代码示例

```python
# 创建索引
index = faiss.IndexIDMap(faiss.IndexFlatIP(dimension))

# 归一化向量
faiss.normalize_L2(embeddings)

# 添加到索引
index.add_with_ids(embeddings.astype('float32'), ids)

# 检索
scores, indices = index.search(query_vector.reshape(1, -1), top_k)
```

### 4.2 文本向量化

使用 Sentence-Transformers 库的预训练模型：

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 生成嵌入
embeddings = model.encode(texts, normalize_embeddings=True)
```

**模型选择理由：**
- `paraphrase-multilingual-MiniLM-L12-v2`：12 层 Transformer，384 维向量
- 支持多语言（包含中文）
- 性能与效果平衡好

### 4.3 文档处理

#### PDF 解析

```python
from PyPDF2 import PdfReader

reader = PdfReader(file_path)
text_parts = []

for page_num, page in enumerate(reader.pages):
    page_text = page.extract_text()
    if page_text:
        text_parts.append(f"[Page {page_num + 1}]\n{page_text}")

text = "\n\n".join(text_parts)
```

#### 文本分块

```python
def create_chunks(self, document_id: str, text: str) -> List[DocumentChunk]:
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + self.chunk_size
        
        # 尝试在句子边界处分割
        if end < len(text):
            end = self._find_sentence_boundary(text, end)
        
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(DocumentChunk.create(document_id, len(chunks), chunk_text))
        
        # 重叠窗口
        start = end - self.chunk_overlap
    
    return chunks
```

### 4.4 API 设计

#### 问答接口

```python
@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    发送问答请求
    
    - question: 用户问题
    - top_k: 检索数量
    - stream: 是否流式响应
    """
    result = rag_service.ask(
        question=request.question,
        top_k=request.top_k
    )
    
    return AnswerResponse(
        question=result["question"],
        answer=result["answer"],
        sources=result["sources"],
        model=result["model"],
        response_time=result["response_time"]
    )
```

#### 响应格式

```json
{
  "question": "什么是RAG？",
  "answer": "RAG（Retrieval-Augmented Generation）是一种...",
  "sources": [
    {
      "id": "chunk_xxx",
      "filename": "技术介绍.pdf",
      "chunk_index": 0,
      "similarity_score": 0.95,
      "content": "RAG技术是..."
    }
  ],
  "model": "deepseek-chat",
  "response_time": 2.5
}
```

---

## 5. 配置管理

### 5.1 环境变量

```env
# DeepSeek API
DEEPSEEK_API_KEY=your_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# 向量存储
VECTOR_STORE_PATH=./data/vector_store
DOCUMENTS_PATH=./data/documents

# 嵌入模型
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# RAG 参数
DEFAULT_TOP_K=5
MAX_TOKENS=1000
TEMPERATURE=0.7

# 文档处理
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 5.2 动态配置

系统支持运行时配置更新：

```python
@router.put("/config")
async def update_configuration(request: ConfigUpdateRequest):
    """
    更新 RAG 配置
    
    可调参数：
    - top_k: 检索数量
    - temperature: 生成温度
    - max_tokens: 最大 token 数
    - chunk_size: 分块大小
    - similarity_threshold: 相似度阈值
    """
    rag_service.update_config({
        'top_k': request.top_k,
        'temperature': request.temperature,
        # ...
    })
```

---

## 6. 错误处理

### 6.1 错误分类

| 错误类型 | 处理方式 | HTTP 状态码 |
|---------|---------|------------|
| 参数验证失败 | 返回详细错误信息 | 400 |
| 文件格式不支持 | 列出支持格式 | 400 |
| 文件过大 | 返回大小限制 | 400 |
| API 调用失败 | 重试 + 错误提示 | 500 |
| 索引为空 | 提示上传文档 | 400 |

### 6.2 错误响应格式

```json
{
  "error": "Invalid file format",
  "detail": "Supported formats: .pdf, .docx, .xlsx, .txt",
  "status_code": 400
}
```

---

## 7. 性能优化

### 7.1 后端优化

- **异步处理**：FastAPI 原生支持异步
- **向量化批处理**：批量处理文本嵌入
- **索引持久化**：避免重复加载
- **缓存机制**：可添加 Redis 缓存

### 7.2 前端优化

- **代码分割**：按路由懒加载
- **请求取消**：AbortController 取消重复请求
- **加载状态**：良好的用户反馈
- **响应式设计**：适配不同屏幕

---

## 8. 安全性

### 8.1 当前版本安全措施

- **输入验证**：Pydantic 模型验证
- **文件大小限制**：防止资源耗尽
- **CORS 配置**：限制跨域请求
- **API 密钥管理**：通过环境变量注入

### 8.2 生产环境建议

- 添加用户认证（JWT）
- 实现权限控制
- 添加请求速率限制
- 启用 HTTPS
- 敏感数据加密

---

## 9. 扩展性

### 9.1 功能扩展方向

1. **多用户支持**：用户隔离、权限管理
2. **对话历史**：持久化存储对话记录
3. **多种文档格式**：Markdown、HTML、图片 OCR
4. **高级检索**：混合检索、重排序
5. **监控告警**：性能监控、异常告警

### 9.2 组件替换

系统设计为可替换组件：

- **向量数据库**：可切换到 Pinecone、Weaviate
- **大语言模型**：可切换到 GPT、Claude
- **嵌入模型**：可选择其他预训练模型
- **前端框架**：可迁移到 Vue、Angular

---

## 10. 部署架构

### 10.1 开发环境

```
前端：Vite 开发服务器 (localhost:5173)
     ↓ 代理
后端：Uvicorn (localhost:8000)
     ↓ 本地
存储：FAISS 本地文件 + 文件系统
```

### 10.2 生产环境建议

```
┌─────────────────────────────────────────────────┐
│                   Nginx / CDN                  │
│            (负载均衡、静态资源)                  │
└─────────────────────┬───────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌─────────────────┐     ┌─────────────────┐
│  前端服务器      │     │  后端服务器      │
│  (Vercel/AWS)   │     │  (Docker)       │
└─────────────────┘     └────────┬────────┘
                                 │
        ┌────────────────────────┴────────────────────────┐
        ▼                          ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  FAISS 集群     │     │  DeepSeek API   │     │  对象存储        │
│  (可选)         │     │  (云服务)        │     │  (S3/MinIO)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 总结

本文档详细描述了 RAG 知识库系统的完整架构设计，涵盖了：

1. **整体架构**：前后端分离的 Web 应用架构
2. **模块划分**：清晰的职责分离和组件划分
3. **数据流程**：文档上传和问答处理的完整流程
4. **技术实现**：核心算法的代码示例和原理说明
5. **配置管理**：灵活的配置机制
6. **扩展性**：组件可替换、功能可扩展

该架构设计展示了：
- 现代 Web 应用的最佳实践
- AI 应用的核心技术点
- 良好的工程实践（测试、文档、错误处理）
- 系统思考和架构设计能力
