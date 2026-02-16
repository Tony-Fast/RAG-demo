/**
 * Settings Panel Component
 * Collapsible panel for all non-core settings and configurations
 */

import React, { useState, useEffect } from 'react';
import { X, Save, RotateCcw, Settings, Database, Sparkles, FileText, Info } from 'lucide-react';
import { chatApi } from '../lib/api';

interface SettingsPanelProps {
  onClose: () => void;
}

interface SystemConfig {
  embedding_model: string;
  chunk_size: number;
  chunk_overlap: number;
  similarity_threshold: number;
  top_k: number;
  temperature: number;
  max_tokens: number;
  system_prompt: string;
}

const SettingsPanel: React.FC<SettingsPanelProps> = ({ onClose }) => {
  const [config, setConfig] = useState<SystemConfig>({
    embedding_model: 'all-MiniLM-L6-v2',
    chunk_size: 500,
    chunk_overlap: 50,
    similarity_threshold: 0.5,
    top_k: 5,
    temperature: 0.7,
    max_tokens: 1000,
    system_prompt: '你是一个专业的问答助手，请基于提供的文档内容回答用户的问题。'
  });
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'retrieval' | 'generation' | 'system'>('retrieval');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await chatApi.getConfig();
      setConfig(prev => ({ ...prev, ...response }));
    } catch (error: any) {
      console.error('Failed to load config:', error);
      alert('加载配置失败: ' + (error.message || '请检查后端服务'));
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await chatApi.updateConfig(config);
      alert('设置已保存');
    } catch (error: any) {
      console.error('Failed to save config:', error);
      alert('保存配置失败: ' + (error.message || '请检查后端服务'));
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm('确定要恢复默认设置吗？')) {
      setConfig({
        embedding_model: 'all-MiniLM-L6-v2',
        chunk_size: 500,
        chunk_overlap: 50,
        similarity_threshold: 0.5,
        top_k: 5,
        temperature: 0.7,
        max_tokens: 1000,
        system_prompt: '你是一个专业的问答助手，请基于提供的文档内容回答用户的问题。'
      });
    }
  };

  const tabs = [
    { id: 'retrieval', label: '检索设置', icon: Database },
    { id: 'generation', label: '生成设置', icon: Sparkles },
    { id: 'system', label: '系统信息', icon: Info }
  ] as const;

  return (
    <div className="bg-white border-b shadow-lg">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div className="flex items-center space-x-3">
            <Settings className="w-5 h-5 text-gray-400" />
            <h2 className="text-lg font-semibold text-gray-800">系统设置</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex items-center space-x-1 px-6 py-2 border-b border-gray-100 bg-gray-50">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm transition
                  ${activeTab === tab.id 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }
                `}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'retrieval' && (
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    嵌入模型
                  </label>
                  <select
                    value={config.embedding_model}
                    onChange={(e) => setConfig({ ...config, embedding_model: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2 (轻量, 英文)</option>
                    <option value="paraphrase-multilingual-MiniLM-L12-v2">
                      paraphrase-multilingual-MiniLM-L12-v2 (多语言)
                    </option>
                  </select>
                  <p className="mt-1 text-xs text-gray-400">
                    用于将文本转换为向量
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    段落大小: {config.chunk_size}
                  </label>
                  <input
                    type="range"
                    min="100"
                    max="2000"
                    step="100"
                    value={config.chunk_size}
                    onChange={(e) => setConfig({ ...config, chunk_size: parseInt(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>100</span>
                    <span>2000</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    段落重叠: {config.chunk_overlap}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="500"
                    step="10"
                    value={config.chunk_overlap}
                    onChange={(e) => setConfig({ ...config, chunk_overlap: parseInt(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>0</span>
                    <span>500</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    相似度阈值: {config.similarity_threshold}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.05"
                    value={config.similarity_threshold}
                    onChange={(e) => setConfig({ ...config, similarity_threshold: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                  <p className="mt-1 text-xs text-gray-400">
                    低于此相似度的结果将被过滤
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    返回结果数量: {config.top_k}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="20"
                    step="1"
                    value={config.top_k}
                    onChange={(e) => setConfig({ ...config, top_k: parseInt(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>1</span>
                    <span>20</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'generation' && (
            <div className="max-w-3xl space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  AI 温度: {config.temperature}
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="2.0"
                  step="0.1"
                  value={config.temperature}
                  onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                  className="w-full max-w-md"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1 max-w-md">
                  <span>精确 (0.1)</span>
                  <span>创意 (2.0)</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  最大输出长度: {config.max_tokens}
                </label>
                <input
                  type="range"
                  min="100"
                  max="4000"
                  step="100"
                  value={config.max_tokens}
                  onChange={(e) => setConfig({ ...config, max_tokens: parseInt(e.target.value) })}
                  className="w-full max-w-md"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1 max-w-md">
                  <span>100</span>
                  <span>4000</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  系统提示词
                </label>
                <textarea
                  value={config.system_prompt}
                  onChange={(e) => setConfig({ ...config, system_prompt: e.target.value })}
                  rows={4}
                  className="w-full max-w-2xl px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-xs text-gray-400">
                  定义 AI 助手的角色和行为
                </p>
              </div>
            </div>
          )}

          {activeTab === 'system' && (
            <div className="space-y-4">
              <div className="bg-blue-50 rounded-xl p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <FileText className="w-6 h-6 text-blue-600" />
                  <div>
                    <h3 className="font-semibold text-blue-800">RAG Knowledge Base</h3>
                    <p className="text-sm text-blue-600">版本 1.0.0</p>
                  </div>
                </div>
                <p className="text-sm text-blue-700">
                  基于检索增强生成（RAG）技术的知识库问答系统。
                  支持多种文档格式，提供智能问答功能。
                </p>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="text-2xl font-bold text-gray-800">
                    {config.embedding_model}
                  </div>
                  <div className="text-sm text-gray-500">嵌入模型</div>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="text-2xl font-bold text-gray-800">
                    {config.chunk_size}
                  </div>
                  <div className="text-sm text-gray-500">默认段落大小</div>
                </div>
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="text-2xl font-bold text-gray-800">
                    {config.top_k}
                  </div>
                  <div className="text-sm text-gray-500">检索数量</div>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 mt-8 pt-6 border-t border-gray-100">
            <button
              onClick={handleReset}
              className="flex items-center space-x-2 px-4 py-2 text-gray-500 hover:text-gray-700 
                hover:bg-gray-100 rounded-lg transition"
            >
              <RotateCcw className="w-4 h-4" />
              <span>恢复默认</span>
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg 
                hover:bg-blue-700 transition disabled:opacity-50"
            >
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>保存中...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>保存设置</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;
