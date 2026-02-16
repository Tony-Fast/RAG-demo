import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Copy, Check, FileText, Sparkles } from 'lucide-react';
import { QueryResult } from '../lib/types';

interface QueryResultsProps {
  results: QueryResult[];
  isLoading: boolean;
}

const QueryResults: React.FC<QueryResultsProps> = ({ results, isLoading }) => {
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const toggleChunk = (chunkId: string) => {
    const newExpanded = new Set(expandedChunks);
    if (newExpanded.has(chunkId)) {
      newExpanded.delete(chunkId);
    } else {
      newExpanded.add(chunkId);
    }
    setExpandedChunks(newExpanded);
  };

  const copyToClipboard = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center space-x-3 text-gray-500">
            <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-lg">正在思考...</span>
          </div>
          <p className="text-center text-sm text-gray-400 mt-3">
            基于文档内容生成回答中
          </p>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {results.map((result, index) => (
        <div key={result.id || index} className="mb-6">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 mb-4">
            <div className="flex items-center space-x-2 mb-3">
              <Sparkles className="w-5 h-5 text-blue-600" />
              <span className="font-medium text-blue-800">AI 回答</span>
            </div>
            <div className="prose prose-blue max-w-none">
              <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                {result.answer}
              </p>
            </div>
            
            <button
              onClick={() => copyToClipboard(result.answer, `answer-${index}`)}
              className="mt-4 flex items-center space-x-1.5 text-sm text-gray-400 hover:text-blue-600 transition"
            >
              {copiedId === `answer-${index}` ? (
                <>
                  <Check className="w-4 h-4" />
                  <span>已复制</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>复制回答</span>
                </>
              )}
            </button>
          </div>

          {/* 路径可视化 */}
          {result.search_paths && (
            <div className="mt-6">
              <div className="flex items-center space-x-2 text-sm font-medium text-gray-500 mb-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                <span>检索路径</span>
              </div>
              <div className="border rounded-xl p-4 bg-white">
                {result.search_paths.search_path && result.search_paths.search_path.map((path: any, pathIndex: number) => (
                  <div key={pathIndex} className="space-y-2">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="text-xs text-gray-500 mb-1">查询</div>
                      <div className="text-sm font-medium">{path.content}</div>
                    </div>
                    <div className="ml-6 space-y-2">
                      {path.children && path.children.map((child: any, childIndex: number) => (
                        <div key={childIndex} className="bg-blue-50 p-3 rounded-lg border border-blue-100">
                          <div className="flex justify-between items-center mb-1">
                            <div className="text-xs text-blue-600">{child.document}</div>
                            <div className="text-xs font-medium text-blue-800">相似度: {((child.score || 0) * 100).toFixed(1)}%</div>
                          </div>
                          <div className="text-sm text-gray-700">{child.content}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-3 mt-6">
            <div className="flex items-center space-x-2 text-sm font-medium text-gray-500">
              <FileText className="w-4 h-4" />
              <span>参考内容</span>
            </div>
            
            {result.chunks.map((chunk, chunkIndex) => {
              const chunkId = `${index}-${chunkIndex}`;
              const isExpanded = expandedChunks.has(chunkId);
              
              return (
                <div 
                  key={chunkId}
                  className="border rounded-xl overflow-hidden transition-all duration-200 hover:shadow-md"
                >
                  <button
                    onClick={() => toggleChunk(chunkId)}
                    className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded">
                        匹配度: {((chunk.score || 0) * 100).toFixed(1)}%
                      </span>
                      <span className="text-sm text-gray-600">
                        {chunk.document_title}
                      </span>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="p-4 bg-white border-t">
                      <p className="text-sm text-gray-600 leading-relaxed">
                        {chunk.content}
                      </p>
                      <button
                        onClick={() => copyToClipboard(chunk.content, chunkId)}
                        className="mt-3 flex items-center space-x-1.5 text-xs text-gray-400 hover:text-blue-600 transition"
                      >
                        {copiedId === chunkId ? (
                          <>
                            <Check className="w-3 h-3" />
                            <span>已复制</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>复制内容</span>
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

export default QueryResults;
