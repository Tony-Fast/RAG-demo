import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Image as ImageIcon, FileText, Smile, X, Upload, AlertCircle, CheckCircle, ChevronDown, ChevronUp, Settings } from 'lucide-react';
import MessageBubble from './MessageBubble';
import FileUploader from './FileUploader';
import DocumentSwitcher from './DocumentSwitcher';
import DocumentViewer from './DocumentViewer';
import QueryResults from './QueryResults';
import SettingsPanel from './SettingsPanel';
import { ChatMessage, Document, QueryResult } from '../lib/types';
import { documentApi, chatApi } from '../lib/api';

interface ChatAreaProps {
  messages: ChatMessage[];
  onSendMessage: (message: string, documentId?: string) => void;
  isLoading: boolean;
  currentSession: string | null;
  currentDoc: Document | null;
  onDocSelect: (doc: Document) => void;
  onDocDelete: (docId: string) => void;
  documents: Document[];
}

const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  onSendMessage,
  isLoading,
  currentSession,
  currentDoc,
  onDocSelect,
  onDocDelete,
  documents
}) => {
  console.log('=== ChatArea 组件 ===');
  console.log('接收到的消息列表长度:', messages.length);
  console.log('接收到的消息列表:', messages);
  console.log('是否正在加载:', isLoading);
  console.log('当前会话:', currentSession);
  console.log('当前文档:', currentDoc);
  console.log('文档列表:', documents);

  const [inputValue, setInputValue] = useState('');
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [selectedModel, setSelectedModel] = useState('GPT 4.0');
  const [selectedFileType, setSelectedFileType] = useState<'image' | 'document'>('image');
  const [queryResults, setQueryResults] = useState<QueryResult[]>([]);
  const [isRagLoading, setIsRagLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showDocumentPanel, setShowDocumentPanel] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const models = ['GPT 4.0', 'GPT 3.5', 'DeepSeek', 'Claude'];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 自动清除通知
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const handleSend = () => {
    if (inputValue.trim()) {
      onSendMessage(inputValue, currentDoc?.id);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = async (files: File[]) => {
    if (!files || files.length === 0) return;
    
    setIsUploading(true);
    setError(null);
    try {
      for (const file of files) {
        await documentApi.uploadDocument(file);
      }
      setSuccess('文件上传成功！');
      // 父组件会自动更新文档列表
    } catch (err: any) {
      console.error('File upload failed:', err);
      setError(err.message || '文件上传失败，请重试');
    } finally {
      setIsUploading(false);
      setShowFileUpload(false);
    }
  };

  // RAG知识库功能
  const handleRagQuery = async (query: string) => {
    if (!query.trim()) return;

    setIsRagLoading(true);
    try {
      const data = await chatApi.query(query, currentDoc?.id);
      const transformedResult: QueryResult = {
        id: Date.now().toString(),
        question: data.question,
        answer: data.answer,
        chunks: (data.sources || []).map((s: any) => ({
          id: s.id || '',
          document_id: s.document_id || '',
          document_title: s.filename || '',
          content: s.content || '',
          score: s.similarity_score || 0,
          chunk_index: s.chunk_index || 0
        })),
        model: data.model || 'unknown',
        response_time: data.response_time || 0,
        tokens_used: data.tokens_used
      };
      setQueryResults([transformedResult]);
    } catch (err: any) {
      console.error('Query failed:', err);
      setError(err.message || '查询失败，请检查后端服务是否运行');
    } finally {
      setIsRagLoading(false);
    }
  };

  const handleDocumentUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      await documentApi.uploadDocument(file);
      setSuccess('文档上传成功！');
      // 父组件会自动更新文档列表
    } catch (err: any) {
      console.error('Upload failed:', err);
      setError(err.message || '文档上传失败，请重试');
    } finally {
      setIsUploading(false);
    }
  };

  // 清空对话历史
  const handleClearHistory = () => {
    if (window.confirm('确定要清空当前对话历史吗？此操作不可恢复。')) {
      setMessages([]);
      if (currentSession) {
        localStorage.setItem(`chatMessages_${currentSession}`, JSON.stringify([]));
      }
      setSuccess('对话历史已清空');
    }
  };

  // 复制消息内容
  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
      .then(() => setSuccess('内容已复制到剪贴板'))
      .catch(err => {
        console.error('复制失败:', err);
        setError('复制失败，请手动复制');
      });
  };

  return (
    <div className="flex-1 flex flex-col h-screen md:ml-64">
      {/* 顶部导航 */}
      <header className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-6">
          {/* 站点信息 */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold">
              陈
            </div>
            <div className="text-sm font-medium">
              <div className="flex items-center space-x-2">
                <span className="text-gray-800 font-semibold">陈柯帆</span>
                <span className="text-gray-500">｜</span>
                <span className="text-blue-600 font-medium">产品学习 Demo 站点</span>
              </div>
              <div className="flex items-center space-x-2 mt-1 text-xs text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>联系方式: 18908149320</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <select
              className="px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              {models.map(model => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
            
            {/* 文档管理按钮 */}
            <button
              onClick={() => setShowDocumentPanel(!showDocumentPanel)}
              className="flex items-center space-x-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg transition text-sm"
            >
              <span>文档管理</span>
              {showDocumentPanel ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {/* 文档上传按钮 */}
          <label className="cursor-pointer px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center space-x-1.5 text-sm">
            <Upload className="w-4 h-4" />
            <span>上传文档</span>
            <input 
              type="file" 
              className="hidden" 
              accept=".pdf,.docx,.doc,.txt,.xlsx,.xls"
              onChange={(e) => e.target.files?.[0] && handleDocumentUpload(e.target.files[0])}
            />
          </label>
          
          {/* 设置按钮 */}
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            <Settings className="w-5 h-5" />
          </button>
          
          {/* 清空对话历史按钮 */}
          <button
            onClick={handleClearHistory}
            className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition text-sm"
          >
            清空历史
          </button>
          
          {/* 新建对话按钮 */}
          <button
            className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
          >
            + 新建对话
          </button>
        </div>
      </header>



      {/* 通知区域 */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-6 py-3 flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border-b border-green-200 px-6 py-3 flex items-center space-x-3">
          <CheckCircle className="w-5 h-5 text-green-500" />
          <span className="text-green-700">{success}</span>
        </div>
      )}

      {/* 系统设置面板 */}
      {showSettings && (
        <SettingsPanel 
          onClose={() => setShowSettings(false)}
        />
      )}

      {/* 文档管理面板 */}
      {showDocumentPanel && (
        <div className="fixed top-14 left-0 right-0 z-10 bg-white border-b px-6 py-3">
          <DocumentSwitcher
            documents={documents}
            currentDoc={currentDoc}
            onSelect={onDocSelect}
            onDelete={onDocDelete}
          />
        </div>
      )}

      {/* 主内容区域 */}
      <div className="flex-1 overflow-y-auto bg-gray-50 p-6 pb-32" style={{ minHeight: '400px' }}>
        <div className="max-w-5xl mx-auto">
          {/* 文档查看器 */}
          {showDocumentPanel && currentDoc && (
            <div className="mb-6">
              <DocumentViewer document={currentDoc} />
            </div>
          )}

          {/* 对话区域 */}
          <div className="space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center py-16">
                <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mb-4 overflow-hidden">
                  <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=white%20M%20letter%20with%20green%20leaf%20logo%20on%20dark%20blue%20background&image_size=square" alt="Logo" className="w-full h-full object-cover" />
                </div>
                <h2 className="text-xl font-semibold text-gray-800 mb-2">你好！</h2>
                <p className="text-gray-500 mb-6">今天需要我帮你做点什么吗？</p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map(message => (
                  <MessageBubble key={message.id} message={message} />
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] bg-white rounded-2xl border border-gray-100 p-4">
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-gray-200 rounded-full flex-shrink-0 flex items-center justify-center">
                          <span className="text-gray-600 text-xs font-bold">AI</span>
                        </div>
                        <div className="flex-1">
                          <div className="flex space-x-2">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* RAG查询结果 */}
          {queryResults.length > 0 && (
            <div className="mt-8 border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">文档查询结果</h3>
              <QueryResults results={queryResults} isLoading={isRagLoading} />
            </div>
          )}
        </div>
      </div>

      {/* 输入区域 */}
      <footer className="bg-white border-t p-4">
        <div className="max-w-5xl mx-auto">
          {/* 文档选择组件 */}
          <div className="mb-4">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-sm font-medium text-gray-700">选择文档：</span>
              <DocumentSwitcher
                documents={documents}
                currentDoc={currentDoc}
                onSelect={onDocSelect}
                onDelete={onDocDelete}
              />
            </div>
          </div>
          
          {showFileUpload && (
            <div className="mb-4 p-4 border border-gray-200 rounded-lg bg-gray-50">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-gray-700">上传文件</h3>
                <button
                  onClick={() => setShowFileUpload(false)}
                  className="p-1 text-gray-500 hover:text-gray-700"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="flex space-x-3 mb-3">
                <button
                  className={`px-3 py-1.5 rounded-lg text-sm ${selectedFileType === 'image' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
                  onClick={() => setSelectedFileType('image')}
                >
                  <ImageIcon className="w-4 h-4 inline mr-1" />
                  图片
                </button>
                <button
                  className={`px-3 py-1.5 rounded-lg text-sm ${selectedFileType === 'document' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
                  onClick={() => setSelectedFileType('document')}
                >
                  <FileText className="w-4 h-4 inline mr-1" />
                  文档
                </button>
              </div>
              <FileUploader
                accept={selectedFileType === 'image' ? 'image/*' : '.pdf,.docx,.doc,.txt,.xlsx,.xls'}
                onUpload={handleFileUpload}
              />
            </div>
          )}
          <div className="flex items-end space-x-3">
            <div className="flex-1 border border-gray-200 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-transparent">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="请输入内容..."
                className="w-full p-3 resize-none min-h-[80px] max-h-[200px] focus:outline-none text-gray-800"
              />
              <div className="flex items-center justify-between px-3 py-2 bg-gray-50 border-t border-gray-200">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowFileUpload(true)}
                    className="p-1.5 text-gray-500 hover:text-blue-600 transition"
                  >
                    <Paperclip className="w-4 h-4" />
                  </button>
                  <button className="p-1.5 text-gray-500 hover:text-blue-600 transition">
                    <Smile className="w-4 h-4" />
                  </button>
                </div>
                <span className="text-xs text-gray-500">{inputValue.length}/2000</span>
              </div>
            </div>
            <div className="flex space-x-2">
              {/* 智能查询按钮 */}
              {currentDoc && (
                <button
                  onClick={() => handleRagQuery(inputValue)}
                  disabled={!inputValue.trim()}
                  className={`px-3 py-3 rounded-lg transition ${inputValue.trim() ? 'bg-green-600 text-white hover:bg-green-700' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
                >
                  <span className="text-sm font-medium">智能查询</span>
                </button>
              )}
              
              {/* 发送按钮 */}
              <button
                onClick={handleSend}
                disabled={!inputValue.trim()}
                className={`p-3 rounded-lg transition ${inputValue.trim() ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </footer>

      {/* 加载状态 */}
      {(isUploading || isRagLoading || isLoading) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 flex items-center space-x-4">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-gray-700">{isUploading ? '正在上传文档...' : isRagLoading ? '正在查询...' : '正在处理...'}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatArea;