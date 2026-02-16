import React from 'react';
import { FileText } from 'lucide-react';
import { Document } from '../lib/types';

interface DocumentViewerProps {
  document: Document | null;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ document }) => {
  if (!document) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400">
        <FileText className="w-16 h-16 mb-4" />
        <p className="text-lg">选择一个文档开始查看</p>
        <p className="text-sm mt-2">上传文档后即可在此查看内容</p>
      </div>
    );
  }

  const isProcessed = document.status === 'completed';
  const format = document.file_format?.toUpperCase() || 'DOC';

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6 pb-4 border-b">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">
          {document.title || document.filename}
        </h2>
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <span>
            {new Date(document.created_at).toLocaleDateString('zh-CN')}
          </span>
          <span>{format}</span>
          <span>
            {document.chunk_count} 个段落
          </span>
          <span>
            {isProcessed ? '✓ 已处理' : '⏳ 处理中'}
          </span>
        </div>
      </div>

      <div className="prose prose-gray max-w-none">
        <div className="bg-gray-50 rounded-xl p-6 text-gray-600">
          <p className="text-center text-gray-400">
            文档内容预览区域
          </p>
          <p className="text-center text-sm text-gray-400 mt-2">
            文件已成功上传并处理，共 {document.chunk_count} 个段落
          </p>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {document.chunk_count}
          </div>
          <div className="text-sm text-blue-500">段落数量</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {(document.file_size / 1024).toFixed(1)} KB
          </div>
          <div className="text-sm text-green-500">文件大小</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {format}
          </div>
          <div className="text-sm text-purple-500">文件格式</div>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
