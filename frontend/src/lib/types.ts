export interface Document {
  id: string
  filename: string
  title?: string
  file_format: string
  file_size: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at?: string
  chunk_count: number
  chunks_count?: number
  content_preview?: string
  word_count?: number
  page_count?: number
  metadata?: Record<string, any>
}

export interface DocumentList {
  documents: Document[]
  total_count: number
  total_size: number
}

export interface UploadResponse {
  message: string
  document_id: string
  filename: string
  file_size: number
  processing_time: number
}

export interface SourceDocument {
  id: string
  document_id: string
  filename: string
  chunk_index: number
  similarity_score: number
  content: string
  page_number?: number
  start_position?: number
  end_position?: number
}

export interface AnswerResponse {
  question: string
  answer: string
  sources: SourceDocument[]
  model: string
  response_time: number
  tokens_used?: number
}

export interface SearchResult {
  content: string
  document_id: string
  document_name: string
  chunk_index: number
  similarity_score: number
  metadata?: Record<string, any>
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total_results: number
  search_time: number
}

export interface RAGConfig {
  rag_config: {
    top_k: number
    temperature: number
    max_tokens: number
    similarity_threshold: number
  }
  embedding_config: {
    model: string
    dimension: number
  }
  llm_config: {
    model: string
    provider: string
  }
  document_config: {
    chunk_size: number
    chunk_overlap: number
    supported_formats: string[]
  }
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: SourceDocument[]
  timestamp: string
  sessionId: string
  isLoading?: boolean
}

export interface ChatSession {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messageCount?: number
}

export interface SystemStats {
  vector_store: {
    total_vectors: number
    dimension: number
    index_type: string
    metadata_count: number
    documents_count: number
  }
  embedding_model: {
    model_name: string
    dimension: number
    max_sequence_length: number
    model_type: string
  }
  llm: {
    model: string
    api_base: string
    provider: string
  }
  config: Record<string, any>
  timestamp: string
}

export interface HealthCheck {
  status: 'healthy' | 'degraded' | 'unhealthy'
  components: {
    vector_store: { status: string; total_vectors?: number; documents?: number; error?: string }
    embedding: { status: string; model?: string; dimension?: number; error?: string }
    llm: { status: string; model?: string; api_accessible?: boolean; error?: string }
    app: { status: string; version?: string }
  }
  timestamp: string
}

export interface QueryResult {
  id: string
  question: string
  answer: string
  chunks: QueryChunk[]
  model: string
  response_time: number
  tokens_used?: number
}

export interface QueryChunk {
  id: string
  document_id: string
  document_title: string
  content: string
  score: number
  page_number?: number
  chunk_index: number
}
