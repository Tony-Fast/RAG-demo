import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Image, X, CheckCircle } from 'lucide-react';

interface FileUploaderProps {
  accept: string;
  onUpload: (files: File[]) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ accept, onUpload }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prevFiles => [...prevFiles, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: accept as any,
    multiple: true
  });

  const handleRemoveFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleUpload = () => {
    if (files.length === 0) return;

    setUploading(true);
    setProgress(0);

    // 模拟上传进度
    const interval = setInterval(() => {
      setProgress(prev => {
        const next = prev + 10;
        if (next >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setUploading(false);
            onUpload(files);
            setFiles([]);
          }, 500);
        }
        return next;
      });
    }, 200);
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="w-5 h-5" />;
    }
    return <FileText className="w-5 h-5" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div>
      {/* 拖拽上传区域 */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center">
          <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <Upload className="w-6 h-6 text-gray-400" />
          </div>
          <p className="text-gray-600 mb-2">拖拽文件到此处，或</p>
          <button
            type="button"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            选择文件
          </button>
          <p className="text-xs text-gray-500 mt-2">{accept}</p>
        </div>
      </div>

      {/* 已选择的文件 */}
      {files.length > 0 && (
        <div className="mt-4">
          <h4 className="font-medium text-gray-700 mb-2">已选择的文件</h4>
          <div className="space-y-2 mb-4">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center">
                    {getFileIcon(file)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h5 className="font-medium text-gray-800 truncate">{file.name}</h5>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleRemoveFile(index)}
                  className="p-1.5 text-gray-500 hover:text-red-600 transition"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>

          {/* 上传进度 */}
          {uploading && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-600">上传中...</span>
                <span className="text-sm text-gray-600">{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={uploading}
            className={`w-full py-2 rounded-lg transition ${uploading ? 'bg-gray-400 text-white cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700'}`}
          >
            {uploading ? '上传中...' : '开始上传'}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUploader;