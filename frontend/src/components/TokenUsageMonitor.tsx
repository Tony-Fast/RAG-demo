import React, { useEffect, useState } from 'react';
import { chatApi } from '../lib/api';

interface TokenUsageMonitorProps {
  className?: string;
}

const TokenUsageMonitor: React.FC<TokenUsageMonitorProps> = ({ className = '' }) => {
  const [tokenUsage, setTokenUsage] = useState(0);
  const [tokenLimit, setTokenLimit] = useState(2000000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTokenUsage = async () => {
    setLoading(true);
    setError(null);
    try {
      const usageInfo = await chatApi.getTokenUsage();
      setTokenUsage(usageInfo.current_usage);
      setTokenLimit(usageInfo.daily_limit);
    } catch (err) {
      console.error('Failed to load token usage:', err);
      setError('获取token使用情况失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始加载
  useEffect(() => {
    loadTokenUsage();
    
    // 每30秒自动刷新一次
    const intervalId = setInterval(loadTokenUsage, 30000);
    
    return () => clearInterval(intervalId);
  }, []);

  // 格式化数字，添加千分位
  const formatNumber = (num: number): string => {
    return num.toLocaleString('zh-CN');
  };

  // 计算使用百分比
  const usagePercentage = (tokenUsage / tokenLimit) * 100;

  // 根据使用百分比确定颜色
  const getProgressColor = (percentage: number): string => {
    if (percentage < 30) return 'bg-green-500';
    if (percentage < 70) return 'bg-yellow-500';
    if (percentage < 90) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 shadow-sm ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-800">Token使用监控</h3>
        <button
          onClick={loadTokenUsage}
          disabled={loading}
          className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
        >
          {loading ? '刷新中...' : '刷新'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-2 rounded mb-3 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-3">
        {/* 进度条 */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">今日使用量</span>
            <span className="text-sm font-medium text-gray-800">
              {formatNumber(tokenUsage)} / {formatNumber(tokenLimit)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className={`h-2.5 rounded-full transition-all duration-300 ${getProgressColor(usagePercentage)}`}
              style={{ width: `${Math.min(usagePercentage, 100)}%` }}
            />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">剩余</span>
            <span className="text-xs font-medium text-gray-700">
              {formatNumber(tokenLimit - tokenUsage)} ({Math.round(100 - usagePercentage)}%)
            </span>
          </div>
        </div>

        {/* 使用情况详情 */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-500 mb-1">当前使用</p>
            <p className="text-xl font-bold text-gray-800">{formatNumber(tokenUsage)}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-xs text-gray-500 mb-1">每日上限</p>
            <p className="text-xl font-bold text-gray-800">{formatNumber(tokenLimit)}</p>
          </div>
        </div>

        {/* 状态提示 */}
        <div className={`p-2 rounded text-sm ${usagePercentage >= 90 ? 'bg-red-50 text-red-600' : usagePercentage >= 70 ? 'bg-orange-50 text-orange-600' : 'bg-green-50 text-green-600'}`}>
          {usagePercentage >= 90
            ? '⚠️ 接近每日上限，请合理使用'
            : usagePercentage >= 70
            ? '⚠️ 使用量较高，请注意控制'
            : '✅ 使用量正常'}
        </div>
      </div>
    </div>
  );
};

export default TokenUsageMonitor;