import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

const QueryInput: React.FC<QueryInputProps> = ({ onSubmit, isLoading, disabled }) => {
  const [query, setQuery] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [query]);

  const handleSubmit = () => {
    if (query.trim() && !isLoading && !disabled) {
      onSubmit(query.trim());
      setQuery('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="max-w-4xl mx-auto relative">
      <div className={`bg-white border-2 rounded-2xl overflow-hidden transition-all duration-200
        ${isFocused ? 'border-blue-500 shadow-lg' : 'border-gray-200 hover:border-gray-300'}
      `}>
        <textarea
          ref={textareaRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={disabled ? "请先选择一个文档" : "输入问题，查询知识库内容..."}
          disabled={disabled || isLoading}
          className="w-full px-6 py-4 text-gray-700 placeholder-gray-400 resize-none outline-none bg-transparent min-h-[60px] max-h-[200px]"
          rows={1}
        />

        <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-t border-gray-100">
          <div className="flex items-center space-x-2 text-xs text-gray-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>按 Enter 发送，Shift+Enter 换行</span>
          </div>

          <button
            onClick={handleSubmit}
            disabled={!query.trim() || isLoading || disabled}
            className={`flex items-center space-x-2 px-5 py-2 rounded-xl font-medium transition-all duration-200
              ${!query.trim() || isLoading || disabled
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-500/30'
              }
            `}
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                <span>思考中...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>发送</span>
              </>
            )}
          </button>
        </div>
      </div>

      {!disabled && query.trim() && (
        <div className="absolute -bottom-8 left-4 text-xs text-gray-400">
          AI 将基于当前文档生成回答
        </div>
      )}
    </div>
  );
};

export default QueryInput;
