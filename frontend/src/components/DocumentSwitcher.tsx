import React, { useState, useEffect } from 'react';
import { ChevronDown, Trash2 } from 'lucide-react';
import { Document } from '../lib/types';

interface DocumentSwitcherProps {
  documents: Document[];
  currentDoc: Document | null;
  onSelect: (doc: Document) => void;
  onDelete: (docId: string) => void;
}

const DocumentSwitcher: React.FC<DocumentSwitcherProps> = ({ documents, currentDoc, onSelect, onDelete }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  // 调试：打印文档数据结构
  useEffect(() => {
    console.log('=== DocumentSwitcher 文档数据 ===');
    console.log('当前文档:', currentDoc);
    console.log('文档列表:', documents);
    if (documents.length > 0) {
      console.log('第一个文档详情:', {
        id: documents[0].id,
        filename: documents[0].filename,
        title: documents[0].title,
        hasTitle: !!documents[0].title
      });
    }
  }, [documents, currentDoc]);

  const handleDelete = (e: React.MouseEvent, docId: string) => {
    e.stopPropagation();
    if (window.confirm('确定要删除这个文档吗？')) {
      onDelete(docId);
    }
  };

  if (documents.length === 0) {
    return (
      <div className="text-sm text-gray-400">
        暂无文档，请上传文档
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
      >
        <span className="text-sm font-medium text-gray-700">
          {currentDoc?.title || currentDoc?.filename || '选择一个文档'}
        </span>
        <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white border rounded-lg shadow-lg z-10">
          <div className="max-h-60 overflow-auto">
            {documents.map((doc) => (
              <div
                key={doc.id}
                onClick={() => {
                  onSelect(doc);
                  setIsOpen(false);
                }}
                className={`px-4 py-2 cursor-pointer hover:bg-gray-100 flex items-center justify-between
                  ${currentDoc?.id === doc.id ? 'bg-blue-50' : ''}
                `}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-700 truncate">
                    {doc.title || doc.filename}
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(doc.created_at).toLocaleDateString()} · {doc.chunk_count} 段落
                  </p>
                </div>
                <button
                  onClick={(e) => handleDelete(e, doc.id)}
                  className="ml-2 p-1 text-gray-400 hover:text-red-500 transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentSwitcher;
