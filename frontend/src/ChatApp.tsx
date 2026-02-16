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
  const [tokenUsage, setTokenUsage] = useState(0);
  const [tokenLimit, setTokenLimit] = useState(2000000);

  useEffect(() => {
    console.log('=== ChatApp 组件挂载 ===');
    loadSessions();
    loadDocuments();
    // 加载token使用情况
    loadTokenUsage();
  }, []);

  const loadTokenUsage = async () => {
    try {
      const usageInfo = await chatApi.getTokenUsage();
      setTokenUsage(usageInfo.current_usage);
      setTokenLimit(usageInfo.daily_limit);
    } catch (error) {
      console.error('Failed to load token usage:', error);
      // 出错时使用默认值
      setTokenUsage(0);
      setTokenLimit(2000000);
    }
  };

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
        // 如果加载失败，创建一个新会话
        createNewSession();
      }
    } else {
      // 如果没有保存的会话，创建一个新会话
      createNewSession();
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
    if (!message.trim()) return;
    
    // 如果没有当前会话，自动创建一个新会话
    if (!currentSession) {
      console.log('=== 没有当前会话，自动创建新会话 ===');
      createNewSession();
      // 等待会话创建完成后再继续
      await new Promise(resolve => setTimeout(resolve, 100));
      // 如果仍然没有会话，返回
      if (!currentSession) return;
    }
    
    console.log('=== 发送消息 ===');
    console.log('消息内容:', message);
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

    // 立即更新状态，确保用户消息能够立即显示
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
      // 设置请求超时
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => reject(new Error('请求超时，请检查网络连接')), 30000);
      });

      // 提取完整对话上下文，确保AI回答考虑整个对话历史
      const context = updatedMessages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // 调用后端大模型API，传递上下文和文档ID，使用Promise.race实现超时处理
      const data = await Promise.race([
        chatApi.query(message, documentId, context),
        timeoutPromise
      ]);
      
      // 验证返回数据的完整性
      if (!data || typeof data !== 'object') {
        throw new Error('收到无效的响应数据');
      }
      
      if (!data.answer) {
        throw new Error('未收到回答内容');
      }
      
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
        onCreateSession={createNewSession}
      />
      

    </div>
  );
}

export default ChatApp;