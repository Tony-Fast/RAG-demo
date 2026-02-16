import React from 'react';
import { Copy } from 'lucide-react';
import { ChatMessage } from '../lib/types';

interface MessageBubbleProps {
  message: ChatMessage;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  console.log('=== MessageBubble 组件 ===');
  console.log('接收到的消息:', message);
  
  const isUser = message.role === 'user';
  console.log('是否为用户消息:', isUser);


  // 格式化时间戳
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // 处理消息内容，移除不需要的标点符号
  const processMessageContent = (content: string): string => {
    // 移除 Markdown 格式的 * 号（斜体和粗体标记）
    let processedContent = content
      // 移除粗体标记：**text** -> text
      .replace(/\*\*(.*?)\*\*/g, '$1')
      // 移除斜体标记：*text* -> text
      .replace(/\*(.*?)\*/g, '$1')
      // 移除其他可能的 Markdown 标记
      .replace(/\[(.*?)\]\((.*?)\)/g, '$1') // 移除链接标记
      .replace(/`(.*?)`/g, '$1') // 移除代码标记
      .replace(/~(.*?)~/g, '$1') // 移除删除线标记
      .replace(/__(.*?)__/g, '$1') // 移除下划线粗体标记
      .replace(/_(.*?)_/g, '$1'); // 移除下划线斜体标记
    
    return processedContent;
  };

  // 复制消息内容
  const handleCopyMessage = () => {
    navigator.clipboard.writeText(message.content)
      .then(() => console.log('Message copied to clipboard'))
      .catch(err => {
        console.error('Copy failed:', err);
      });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} items-end mb-4`}>
      <div className={`max-w-[80%] ${isUser ? 'bg-blue-600 text-white' : 'bg-white border border-gray-100'} rounded-2xl p-4 relative`}>
        {!isUser && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex-shrink-0 flex items-center justify-center overflow-hidden">
              <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=white%20M%20letter%20with%20green%20leaf%20logo%20on%20dark%20blue%20background&image_size=square" alt="Logo" className="w-full h-full object-cover" />
            </div>
            <div className="flex-1">
              <p className="whitespace-pre-wrap break-words">{processMessageContent(message.content)}</p>
            </div>
          </div>
        )}
        {isUser && (
          <div className="flex-1">
            <p className="whitespace-pre-wrap break-words">{processMessageContent(message.content)}</p>
          </div>
        )}
        {/* 时间戳 */}
        <div className={`text-xs mt-2 ${isUser ? 'text-blue-200 text-right' : 'text-gray-400 text-left'}`}>
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;