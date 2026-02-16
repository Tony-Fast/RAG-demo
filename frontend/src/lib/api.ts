import axios, { AxiosInstance } from 'axios'

// 使用相对路径，让请求通过前端服务器的代理
// 这样可以避免CORS问题并确保更可靠的连接
const API_BASE_URL = '/api/v1'

// 单例模式，确保只创建一个API客户端实例
class ApiClient {
  private static instance: ApiClient
  private client: AxiosInstance
  private initialized: boolean = true
  
  private constructor() {
    // 创建axios实例
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 60000,
      headers: {},
      withCredentials: false,
      validateStatus: function(status) {
        return status >= 200 && status < 300; // 只接受200-299的状态码
      }
    })
    
    // 添加请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )
    
    // 添加响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        return response
      },
      (error) => {
        // 提供更详细的错误信息
        let errorMessage = '网络错误'
        
        if (error.code === 'ECONNABORTED') {
          errorMessage = '请求超时，请检查网络连接'
        } else if (error.code === 'ERR_NETWORK') {
          errorMessage = '网络错误，请检查后端服务是否运行在 http://localhost:8000'
        } else if (error.response) {
          // 服务器返回了错误状态码
          errorMessage = `服务器错误 (${error.response.status}): ${error.response.data?.detail || error.response.data?.error || '未知错误'}`
        } else if (error.request) {
          // 请求已发送但没有收到响应
          errorMessage = '未收到服务器响应，请检查后端服务是否运行'
        } else {
          // 其他错误
          errorMessage = error.message || '上传失败'
        }
        
        const enhancedError = new Error(errorMessage) as any
        enhancedError.originalError = error
        enhancedError.code = error.code
        
        return Promise.reject(enhancedError)
      }
    )
  }
  
  // 获取单例实例
  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient()
    }
    return ApiClient.instance
  }
  
  async uploadDocument(file: File): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    
    try {
      // 不手动设置Content-Type，让axios自动处理
      // 这样会包含正确的边界信息
      const response = await this.client.post('/documents/upload', formData)
      return response.data
    } catch (error: any) {
      console.error('Upload error:', error)
      throw error
    }
  }
  
  async getDocuments(): Promise<any[]> {
    try {
      const response = await this.client.get('/documents/list')
      return response.data.documents || []
    } catch (error) {
      console.error('Failed to load documents:', error)
      return []
    }
  }
  
  async deleteDocument(documentId: string): Promise<any> {
    return this.client.delete(`/documents/${documentId}`)
  }
  
  async query(question: string, documentId?: string, context?: any[]): Promise<any> {
    try {
      const response = await this.client.post('/chat/ask', {
        question,
        document_id: documentId,
        stream: false,
        return_paths: true,
        context: context
      })
      return response.data
    } catch (error: any) {
      console.error('Query error:', error)
      // 增强错误信息
      const errorMessage = error.message || '查询失败，请检查网络连接或后端服务'
      const enhancedError = new Error(errorMessage)
      throw enhancedError
    }
  }
  
  async getConfig(): Promise<any> {
    return this.client.get('/config')
  }
  
  async updateConfig(config: Record<string, any>): Promise<any> {
    return this.client.put('/config', config)
  }
  
  async healthCheck(): Promise<any> {
    return this.client.get('/health')
  }
  
  async getTokenUsage(): Promise<any> {
    try {
      const response = await this.client.get('/token/usage')
      return response.data
    } catch (error) {
      console.error('Failed to get token usage:', error)
      throw error
    }
  }
  
  async getTokenHistory(): Promise<any> {
    try {
      const response = await this.client.get('/token/history')
      return response.data
    } catch (error) {
      console.error('Failed to get token history:', error)
      throw error
    }
  }
  
  async resetTokenUsage(): Promise<any> {
    try {
      const response = await this.client.post('/token/reset')
      return response.data
    } catch (error) {
      console.error('Failed to reset token usage:', error)
      throw error
    }
  }
}

// 导出单例实例
const apiInstance = ApiClient.getInstance()
export const documentApi = apiInstance
export const chatApi = apiInstance
export const configApi = apiInstance
export default apiInstance
