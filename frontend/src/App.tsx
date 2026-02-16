import React, { useState, useEffect } from 'react';
import { MessageSquare, ChevronUp, ChevronDown, Upload, AlertCircle, CheckCircle } from 'lucide-react';
import DocumentViewer from './components/DocumentViewer';
import QueryInput from './components/QueryInput';
import QueryResults from './components/QueryResults';
import DocumentSwitcher from './components/DocumentSwitcher';
import SettingsPanel from './components/SettingsPanel';
import { Document, QueryResult } from './lib/types';
import { documentApi, chatApi } from './lib/api';

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [currentDoc, setCurrentDoc] = useState<Document | null>(null);
  const [queryResults, setQueryResults] = useState<QueryResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

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

  const loadDocuments = async () => {
    try {
      const docs = await documentApi.getDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !currentDoc) {
        setCurrentDoc(docs[0]);
      }
    } catch (err: any) {
      console.error('Failed to load documents:', err);
      setError('加载文档列表失败');
    }
  };

  const handleQuery = async (query: string) => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      // chatApi.query直接返回response.data，不需要再访问data属性
      const data = await chatApi.query(query, currentDoc?.id);
      console.log('API response:', data);
      // Transform backend response to frontend format
      const transformedResult = {
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
      console.log('Transformed result:', transformedResult);
      setQueryResults([transformedResult]);
    } catch (err: any) {
      console.error('Query failed:', err);
      setError(err.message || '查询失败，请检查后端服务是否运行');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      await documentApi.uploadDocument(file);
      setSuccess('文档上传成功！');
      await loadDocuments();
    } catch (err: any) {
      console.error('Upload failed:', err);
      setError(err.message || '文档上传失败，请重试');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    try {
      await documentApi.deleteDocument(docId);
      setSuccess('文档删除成功');
      await loadDocuments();
      if (currentDoc?.id === docId) {
        setCurrentDoc(documents.find(d => d.id !== docId) || null);
      }
    } catch (err: any) {
      console.error('Delete failed:', err);
      setError(err.message || '删除文档失败');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
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

      <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <MessageSquare className="w-6 h-6 text-blue-600" />
          <h1 className="text-lg font-semibold text-gray-800">RAG Knowledge Base</h1>
        </div>
        
        <div className="flex items-center space-x-3">
          <label className="cursor-pointer px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center space-x-1.5">
            <Upload className="w-4 h-4" />
            <span className="text-sm">上传文档</span>
            <input 
              type="file" 
              className="hidden" 
              accept=".pdf,.docx,.doc,.txt,.xlsx,.xls"
              onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
            />
          </label>
          
          <button 
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition"
          >
            {showSettings ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
        </div>
      </header>

      {showSettings && (
        <SettingsPanel 
          onClose={() => setShowSettings(false)}
        />
      )}

      <main className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="bg-white border-b px-6 py-2">
            <DocumentSwitcher
              documents={documents}
              currentDoc={currentDoc}
              onSelect={setCurrentDoc}
              onDelete={handleDeleteDocument}
            />
          </div>

          <div className="flex-1 overflow-auto p-6">
            <DocumentViewer document={currentDoc} />
          </div>

          {queryResults.length > 0 && (
            <div className="border-t bg-white">
              <QueryResults results={queryResults} isLoading={isLoading} />
            </div>
          )}
        </div>
      </main>

      <footer className="bg-white border-t p-4">
        <QueryInput 
          onSubmit={handleQuery}
          isLoading={isLoading}
          disabled={!currentDoc}
        />
      </footer>

      {isUploading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 flex items-center space-x-4">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-gray-700">正在上传文档...</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
