import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import { ChatMessage, ChatSession, Document } from './lib/types';
import { chatApi, documentApi } from './lib/api';

function ChatApp() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentDoc, setCurrentDoc] = useState<Document | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [showPasswordInput, setShowPasswordInput] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  // 从localStorage加载认证状态
  useEffect(() => {
    // 暂时不自动加载认证状态，确保每次刷新都需要重新验证
    // 这样可以测试密码输入功能是否正常
    setIsAuthenticated(false);
    localStorage.removeItem('chatAuth');
  }, []);

  const authenticate = (pwd: string) => {
    // 这里使用简单的密码验证，实际项目中应该使用更安全的方式
    // 密码可以从环境变量或配置文件中读取
    const correctPassword = 'demo123'; // 示例密码，实际应该从安全的地方获取
    
    if (pwd === correctPassword) {
      setIsAuthenticated(true);
      setPasswordError('');
      setShowPasswordInput(false);
      // 保存认证状态到localStorage
      localStorage.setItem('chatAuth', JSON.stringify({ authenticated: true }));
      return true;
    } else {
      setPasswordError('密码错误，请重试');
      return false;
    }
  };

  useEffect(() => {
    console.log('=== ChatApp 组件挂载 ===');
    loadSessions();
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await documentApi.getDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !currentDoc) {
        setCurrentDoc(docs[0]);
      }
    } catch (err: any) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleDocSelect = (doc: Document) => {
    setCurrentDoc(doc);
  };

  const handleDocDelete = async (docId: string) => {
    try {
      await documentApi.deleteDocument(docId);
      await loadDocuments();
      if (currentDoc?.id === docId) {
        setCurrentDoc(documents.find(d => d.id !== docId) || null);
      }
    } catch (err: any) {
      console.error('Delete failed:', err);
    }
  };

  useEffect(() => {
    console.log('=== 消息状态更新 ===');
    console.log('当前消息列表长度:', messages.length);
    console.log('当前消息列表:', messages);
  }, [messages]);

  const loadSessions = () => {
    const savedSessions = localStorage.getItem('chatSessions');
    if (savedSessions) {
      try {
        const parsedSessions = JSON.parse(savedSessions);
        setSessions(parsedSessions);
        if (parsedSessions.length > 0 && !currentSession) {
          setCurrentSession(parsedSessions[0].id);
          loadSessionMessages(parsedSessions[0].id);
        }
      } catch (error) {
        console.error('Failed to load sessions:', error);
      }
    }
  };

  const loadSessionMessages = (sessionId: string) => {
    const savedMessages = localStorage.getItem(`chatMessages_${sessionId}`);
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        setMessages(parsedMessages);
      } catch (error) {
        console.error('Failed to load messages:', error);
      }
    } else {
      setMessages([]);
    }
  };

  const saveSessionMessages = (sessionId: string, sessionMessages: ChatMessage[]) => {
    localStorage.setItem(`chatMessages_${sessionId}`, JSON.stringify(sessionMessages));
  };

  const createNewSession = () => {
    const newSession: ChatSession = {
      id: `session_${Date.now()}`,
      title: '新对话',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    const updatedSessions = [newSession, ...sessions];
    setSessions(updatedSessions);
    setCurrentSession(newSession.id);
    setMessages([]);
    localStorage.setItem('chatSessions', JSON.stringify(updatedSessions));
    localStorage.setItem(`chatMessages_${newSession.id}`, JSON.stringify([]));
  };

  const handleSendMessage = async (message: string, documentId?: string) => {
    if (!message.trim() || !currentSession) return;

    // 检查认证状态
    if (!isAuthenticated) {
      setShowPasswordInput(true);
      return;
    }

    console.log('=== 开始发送消息 ===');
    console.log('原始消息:', message);
    console.log('当前会话:', currentSession);
    console.log('当前消息列表长度:', messages.length);
    console.log('当前选择的文档ID:', documentId);

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      sessionId: currentSession
    };

    console.log('创建的用户消息:', userMessage);

    const updatedMessages = [...messages, userMessage];
    console.log('更新后的消息列表长度:', updatedMessages.length);
    console.log('更新后的消息列表:', updatedMessages);

    // 立即更新状态
    setMessages(prevMessages => {
      console.log('Prev messages:', prevMessages);
      const newMessages = [...prevMessages, userMessage];
      console.log('New messages:', newMessages);
      return newMessages;
    });
    console.log('状态更新后');
    
    // 保存到localStorage
    setTimeout(() => {
      saveSessionMessages(currentSession, updatedMessages);
      console.log('消息已保存到localStorage');
    }, 0);


    setIsLoading(true);

    try {
      // 提取完整对话上下文，确保AI回答考虑整个对话历史
      const context = updatedMessages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // 调用后端大模型API，传递上下文和文档ID
      const data = await chatApi.query(message, documentId, context);
      
      const aiMessage: ChatMessage = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: data.answer || '我收到了你的消息，但无法生成回复。',
        timestamp: new Date().toISOString(),
        sessionId: currentSession
      };

      const finalMessages = [...updatedMessages, aiMessage];
      setMessages(finalMessages);
      saveSessionMessages(currentSession, finalMessages);

      // 更新会话标题
      const updatedSessions = sessions.map(session => 
        session.id === currentSession 
          ? { ...session, title: message.substring(0, 30), updatedAt: new Date().toISOString() }
          : session
      );
      setSessions(updatedSessions);
      localStorage.setItem('chatSessions', JSON.stringify(updatedSessions));

    } catch (error: any) {
      console.error('Chat API error:', error);
      
      // 错误处理：显示错误消息
      const errorMessage: ChatMessage = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: `抱歉，我无法处理你的请求：${error.message || '请检查后端服务是否运行'}`,
        timestamp: new Date().toISOString(),
        sessionId: currentSession
      };

      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);
      saveSessionMessages(currentSession, finalMessages);

    } finally {
      setIsLoading(false);
    }
  };

  const handleSessionSelect = (sessionId: string) => {
    setCurrentSession(sessionId);
    loadSessionMessages(sessionId);
  };

  const handleSessionDelete = (sessionId: string) => {
    const updatedSessions = sessions.filter(session => session.id !== sessionId);
    setSessions(updatedSessions);
    localStorage.setItem('chatSessions', JSON.stringify(updatedSessions));
    localStorage.removeItem(`chatMessages_${sessionId}`);

    if (currentSession === sessionId) {
      if (updatedSessions.length > 0) {
        setCurrentSession(updatedSessions[0].id);
        loadSessionMessages(updatedSessions[0].id);
      } else {
        setCurrentSession(null);
        setMessages([]);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar
        sessions={sessions}
        currentSession={currentSession}
        onSessionSelect={handleSessionSelect}
        onSessionDelete={handleSessionDelete}
        onCreateSession={createNewSession}
      />
      <ChatArea
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        currentSession={currentSession}
        currentDoc={currentDoc}
        onDocSelect={handleDocSelect}
        onDocDelete={handleDocDelete}
        documents={documents}
      />
      
      {/* 密码输入模态框 */}
      {showPasswordInput && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h3 className="text-2xl font-bold mb-4 text-gray-800">请输入密码</h3>
            <p className="text-gray-600 mb-6">需要密码才能使用网站输出功能</p>
            
            {passwordError && (
              <div className="bg-red-100 text-red-700 p-3 rounded-md mb-4">
                {passwordError}
              </div>
            )}
            
            <div className="mb-4">
              <input
                type="password"
                placeholder="请输入密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => {
                  setShowPasswordInput(false);
                  setPassword('');
                  setPasswordError('');
                }}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition"
              >
                取消
              </button>
              <button
                onClick={() => authenticate(password)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
              >
                确认
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatApp;