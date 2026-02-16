import React, { useState } from 'react';
import { MessageSquare, Plus, Search, Menu, X, Trash2 } from 'lucide-react';
import { ChatSession } from '../lib/types';

interface SidebarProps {
  sessions: ChatSession[];
  currentSession: string | null;
  onSessionSelect: (sessionId: string) => void;
  onSessionDelete: (sessionId: string) => void;
  onCreateSession: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  currentSession,
  onSessionSelect,
  onSessionDelete,
  onCreateSession
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      {/* Mobile sidebar */}
      <div className="md:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out"
           style={{ transform: isMobileOpen ? 'translateX(0)' : 'translateX(-100%)' }}>
        <div className="h-full flex flex-col">
          <div className="p-4 border-b flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center overflow-hidden">
                <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=white%20M%20letter%20with%20green%20leaf%20logo%20on%20dark%20blue%20background&image_size=square" alt="Logo" className="w-full h-full object-cover" />
              </div>
              <span className="font-semibold text-gray-800">RAG demo</span>
            </div>
            <button
              onClick={() => setIsMobileOpen(false)}
              className="p-1 text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="p-3">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="搜索对话..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-8 pr-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-3">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">历史对话</h3>
            <div className="space-y-1">
              {filteredSessions.map(session => (
                <div
                  key={session.id}
                  className={`p-3 rounded-lg cursor-pointer transition-all ${currentSession === session.id ? 'bg-blue-50 border-l-4 border-blue-500' : 'hover:bg-gray-50'}`}
                  onClick={() => {
                    onSessionSelect(session.id);
                    setIsMobileOpen(false);
                  }}
                >
                  <div className="flex items-start justify-between">
                    <h4 className="font-medium text-gray-800 truncate">{session.title}</h4>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSessionDelete(session.id);
                      }}
                      className="text-gray-400 hover:text-red-500"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <p className="text-sm text-gray-500 truncate mt-1">{session.title}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(session.updatedAt).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
          <div className="p-4 border-t">
            <button
              onClick={() => {
                onCreateSession();
                setIsMobileOpen(false);
              }}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Plus className="w-4 h-4" />
              <span>新建对话</span>
            </button>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden md:flex md:flex-col md:w-64 bg-white border-r h-screen fixed left-0 top-0 z-40">
        <div className="p-4 border-b flex items-center space-x-2">
          <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center overflow-hidden">
            <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=white%20M%20letter%20with%20green%20leaf%20logo%20on%20dark%20blue%20background&image_size=square" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <span className="font-semibold text-gray-800">RAG demo</span>
        </div>
        
        <div className="p-3">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索对话..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3">
          <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">历史对话</h3>
          <div className="space-y-1">
            {filteredSessions.map(session => (
              <div
                key={session.id}
                className={`p-3 rounded-lg cursor-pointer transition-all ${currentSession === session.id ? 'bg-blue-50 border-l-4 border-blue-500' : 'hover:bg-gray-50'}`}
                onClick={() => onSessionSelect(session.id)}
              >
                <div className="flex items-start justify-between">
                  <h4 className="font-medium text-gray-800 truncate">{session.title}</h4>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSessionDelete(session.id);
                    }}
                    className="text-gray-400 hover:text-red-500"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-sm text-gray-500 truncate mt-1">{session.title}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {new Date(session.updatedAt).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </div>
        
        <div className="p-4 border-t">
          <button
            onClick={onCreateSession}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Plus className="w-4 h-4" />
            <span>新建对话</span>
          </button>
        </div>
      </div>

      {/* Mobile menu button */}
      <div className="md:hidden fixed top-4 left-4 z-40">
        <button
          onClick={() => setIsMobileOpen(true)}
          className="p-2 bg-white rounded-lg shadow-md"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>
    </>
  );
};

export default Sidebar;