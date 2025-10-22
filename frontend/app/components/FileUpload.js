// frontend/app/components/FileUpload.js
'use client';

export default function FileUpload({ title, onFileSelect, isLoading }) {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center hover:border-indigo-500 transition-colors duration-300">
      <label htmlFor={title} className="cursor-pointer">
        <div className="text-gray-400">
          <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <p className="mt-2 text-sm">
            <span className="font-semibold text-indigo-400">点击上传</span> 或拖拽文件到此区域
          </p>
          <p className="text-xs text-gray-500">{title}</p>
        </div>
        <input id={title} name={title} type="file" className="sr-only" onChange={handleFileChange} disabled={isLoading} accept=".csv,.parquet" />
      </label>
    </div>
  );
} 