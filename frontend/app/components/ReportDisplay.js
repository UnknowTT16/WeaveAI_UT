// frontend/app/components/ReportDisplay.js
'use client';

import { useEffect, useState, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import debounce from 'lodash/debounce';

export default function ReportDisplay({ 
  profile, 
  onGenerationComplete,
  onError
}) {
  const [streamedContent, setStreamedContent] = useState({ thinking: '', report: '' });

  const debouncedSetStreamedContent = useMemo(
    () => debounce((content) => {
      setStreamedContent(content);
    }, 150),
    []
  );

  useEffect(() => {
    if (!profile) return;

    const abortController = new AbortController();

    const generateReport = async () => {
      setStreamedContent({ thinking: '正在连接AI服务...', report: '' });

      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/reports/market-insight`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(profile),
          signal: abortController.signal,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: "Server returned non-JSON error." }));
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.detail || response.statusText}`);
        }
        if (!response.body) return;
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = '';
        const thinkEndMarker = '<<<<THINKING_ENDS>>>>';
        const reportStartMarker = '<<<<REPORT_STARTS>>>>';
        
        // 【核心优化】: 增加一个标志位，用于首次渲染
        let isFirstChunk = true;

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          
          fullResponse += decoder.decode(value, { stream: true });

          const filteredResponse = fullResponse.replace(/<\|FunctionCallBegin\|>.*?<\|FunctionCallEnd\|>/gs, '');

          let currentThinking = '';
          let currentReport = '';

          if (filteredResponse.includes(reportStartMarker)) {
            const parts = filteredResponse.split(reportStartMarker, 2);
            currentThinking = parts[0].replace(thinkEndMarker, '');
            currentReport = parts[1];
          } else if (filteredResponse.includes(thinkEndMarker)) {
            currentThinking = filteredResponse.replace(thinkEndMarker, '');
          } else {
            currentThinking = filteredResponse;
          }
          
          const newContent = { thinking: currentThinking, report: currentReport };

          // 【核心优化】: 第一个数据块立即渲染，后续的才防抖
          if (isFirstChunk) {
            setStreamedContent(newContent);
            isFirstChunk = false;
          } else {
            debouncedSetStreamedContent(newContent);
          }
        }
        
        debouncedSetStreamedContent.flush();
        
        const finalFilteredResponse = fullResponse.replace(/<\|FunctionCallBegin\|>.*?<\|FunctionCallEnd\|>/gs, '');
        const finalParts = finalFilteredResponse.split(reportStartMarker, 2);
        
        if (finalParts.length > 1) {
          onGenerationComplete(finalParts[1].trim());
        } else {
            onError('AI未能生成格式正确的报告，请重试。');
        }

      } catch (e) {
        if (e.name === 'AbortError') {
          console.log('Fetch request was intentionally aborted.');
        } else {
          console.error(e);
          onError(`生成报告时发生网络或服务器错误: ${e.message}`);
        }
      }
    };

    generateReport();

    return () => {
      abortController.abort();
      debouncedSetStreamedContent.cancel();
    };
  }, [profile, onGenerationComplete, onError, debouncedSetStreamedContent]); 

  return (
    <div className="space-y-6">
       <details open className="bg-gray-700/50 p-4 rounded-lg">
          <summary className="text-lg font-semibold text-white mb-2 cursor-pointer">🧠 AI 思考过程</summary>
          <div className="prose prose-invert max-w-none text-gray-300 mt-4">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{streamedContent.thinking || ''}</ReactMarkdown>
          </div>
       </details>
       <div className="bg-gray-700/50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-2">📈 报告生成中...</h3>
          <div className="prose prose-invert max-w-none text-gray-300">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{streamedContent.report || ''}</ReactMarkdown>
          </div>
       </div>
    </div>
  );
}