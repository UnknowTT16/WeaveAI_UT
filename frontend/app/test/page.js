// frontend/app/test/page.js
'use client';

import { useState } from 'react';

export default function TestPage() {
  const [message, setMessage] = useState('Initial State');
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = () => {
    console.log('Button clicked!'); // 在浏览器控制台打印日志
    setIsLoading(true);
    setMessage('State is now LOADING!');

    // 模拟一个2秒的异步操作
    setTimeout(() => {
      setIsLoading(false);
      setMessage('State has been UPDATED after 2 seconds!');
    }, 2000);
  };

  return (
    <main className="container mx-auto p-8 text-white">
      <h1 className="text-3xl font-bold mb-4">React State Test Page</h1>
      
      <div className="mb-4">
        <p>Current Message:</p>
        <p className="text-2xl font-mono p-4 bg-gray-700 rounded-md">{message}</p>
      </div>

      <button 
        onClick={handleClick}
        disabled={isLoading}
        className="w-full px-4 py-2 font-bold text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-500"
      >
        {isLoading ? 'Loading...' : 'Click to Change State'}
      </button>
    </main>
  );
}