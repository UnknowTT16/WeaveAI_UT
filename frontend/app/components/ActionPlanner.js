// frontend/app/components/ActionPlanner.js
'use client';

import { useState, useMemo } from 'react'; // 1. 导入 useMemo
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import debounce from 'lodash/debounce'; // 2. 导入 debounce

export default function ActionPlanner({ marketReport, validationSummary }) {
  const [isLoading, setIsLoading] = useState(false);
  const [aiReport, setAiReport] = useState({ thinking: '', report: '' });
  const [error, setError] = useState('');

  // 3. 创建防抖版的 state 更新函数
  const debouncedSetAiReport = useMemo(
    () => debounce((content) => {
      setAiReport(content);
    }, 150),
    []
  );

  const handleGeneratePlan = async () => {
    setIsLoading(true);
    setError('');
    setAiReport({ thinking: '正在整合信息并调用AI...', report: '' });
    
    try {
     const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/reports/action-plan`,  {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          market_report: marketReport,
          validation_summary: validationSummary,
        }),
      });
      
      if (!response.ok) throw new Error("AI行动计划服务请求失败。");
      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';
      const thinkEndMarker = '<<<<THINKING_ENDS>>>>';
      const reportStartMarker = '<<<<REPORT_STARTS>>>>';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        fullResponse += decoder.decode(value, { stream: true });
        
        let currentThinking = '';
        let currentReport = '';

        if (fullResponse.includes(reportStartMarker)) {
          const parts = fullResponse.split(reportStartMarker, 2);
          currentThinking = parts[0].replace(thinkEndMarker, '');
          currentReport = parts[1];
        } else if (fullResponse.includes(thinkEndMarker)) {
            currentThinking = fullResponse.replace(thinkEndMarker, '');
        } else {
            currentThinking = fullResponse;
        }
        
        // 4. 调用防抖函数，而不是直接 setAiReport
        debouncedSetAiReport({ thinking: currentThinking, report: currentReport });
      }

      // 5. 确保最后一次更新被执行
      debouncedSetAiReport.flush();

    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <h3 className="text-lg font-medium text-white">决策依据预览</h3>
        <details className="bg-gray-900/50 p-3 rounded-lg text-sm">
          <summary className="cursor-pointer font-semibold text-gray-300 hover:text-white">市场洞察报告</summary>
          <div className="mt-2 prose prose-invert max-w-none prose-sm text-gray-400">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{marketReport}</ReactMarkdown>
          </div>
        </details>
        <details className="bg-gray-900/50 p-3 rounded-lg text-sm">
          <summary className="cursor-pointer font-semibold text-gray-300 hover:text-white">内部数据验证摘要</summary>
          <div className="mt-2 prose prose-invert max-w-none prose-sm text-gray-400">
            <p>{validationSummary}</p>
          </div>
        </details>
      </div>
      
      <button onClick={handleGeneratePlan} disabled={isLoading} className="btn-primary w-full disabled:opacity-50">
        {isLoading ? "AI 正在规划..." : "💡 生成我的行动计划"}
      </button>

      {error && <p className="text-red-400 mt-4">{error}</p>}
      
      {/* 优化UI，只在开始加载后才显示思考过程 */}
      {(isLoading || aiReport.thinking || aiReport.report) && (
        <div className="mt-6 space-y-4">
          <details open className="bg-gray-900/50 p-4 rounded-lg">
            <summary className="text-md font-semibold text-white cursor-pointer">查看AI思考过程</summary>
            <div className="mt-2 prose prose-invert max-w-none text-gray-300">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{aiReport.thinking}</ReactMarkdown>
            </div>
          </details>
          {aiReport.report && (
            <div className="prose prose-invert max-w-none bg-gray-900/50 p-6 rounded-lg">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{aiReport.report}</ReactMarkdown>
            </div>
          )}
        </div>
      )}
    </div>
  );
}