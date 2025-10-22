// frontend/app/components/SentimentAnalysis.js
'use client';

import { useState, useMemo, useCallback } from 'react';
import Slider from 'rc-slider';
import DataTable from './DataTable';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function SentimentAnalysis({ analysisResult }) {
  const { reviews, average_sentiment } = analysisResult;
  
  // 1. 【核心优化】: 默认星级范围设置为 [4, 5]
  const [ratingRange, setRatingRange] = useState([4, 5]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [aiReport, setAiReport] = useState({ thinking: '', report: '' });
  const [error, setError] = useState('');
  
  // 2. 【核心优化】: 新增 state 来控制是否显示全部评论
  const [showAllReviews, setShowAllReviews] = useState(false);

  // 首先根据滑块范围筛选出所有符合条件的评论
  const filteredReviews = useMemo(() => {
    return reviews.filter(r => r.rating >= ratingRange[0] && r.rating <= ratingRange[1]);
  }, [reviews, ratingRange]);
  
  // 接着根据 showAllReviews 的状态，决定最终要渲染的评论
  const displayedReviews = useMemo(() => {
    return showAllReviews ? filteredReviews : filteredReviews.slice(0, 20);
  }, [filteredReviews, showAllReviews]);

  // 平均分计算应该基于所有筛选出的评论，而不是只基于显示的
  const avgFilteredSentiment = useMemo(() => {
    if (filteredReviews.length === 0) return 0;
    const totalSentiment = filteredReviews.reduce((acc, r) => acc + r.sentiment, 0);
    return totalSentiment / filteredReviews.length;
  }, [filteredReviews]);
  
  // AI分析也应该基于所有筛选出的评论
  const handleAiAnalysis = useCallback(async () => {
    if (filteredReviews.length === 0) {
      setError("当前筛选范围内没有评论可供AI分析，请调整滑块。");
      return;
    }
    
    setIsGenerating(true);
    setError('');
    setAiReport({ thinking: '正在抽样并调用AI...', report: '' });

    const sortedReviews = [...filteredReviews].sort((a, b) => a.sentiment - b.sentiment);
    const negativeSamples = sortedReviews.slice(0, 15);
    const positiveSamples = sortedReviews.slice(-15).reverse();

    const positiveText = positiveSamples.map(r => `- ${r.review_text}`).join("\n");
    const negativeText = negativeSamples.map(r => `- ${r.review_text}`).join("\n");
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/reports/review-summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                positive_reviews: positiveText,
                negative_reviews: negativeText,
            }),
        });

        if (!response.ok) throw new Error("AI分析服务请求失败。");
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
            setAiReport({ thinking: currentThinking, report: currentReport });
        }
        
    } catch (e) {
        setError(e.message);
    } finally {
        setIsGenerating(false);
    }
  }, [filteredReviews]);

  return (
    <div className="space-y-8">
      <div>
        <h4 className="font-semibold text-white mb-2">按星级筛选评论</h4>
        <div className="p-4 bg-gray-800 rounded-lg">
          <Slider
            range
            min={1}
            max={5}
            step={1}
            value={ratingRange}
            onChange={setRatingRange}
            marks={{ 1: '1☆', 2: '2☆', 3: '3☆', 4: '4☆', 5: '5☆' }}
            trackStyle={[{ backgroundColor: '#4f46e5' }]}
            handleStyle={[{ borderColor: '#4f46e5' }, { borderColor: '#4f46e5' }]}
            railStyle={{ backgroundColor: '#4b5563' }}
          />
        </div>
      </div>
      
      <div>
        {/* 3. 【核心优化】: 更新提示文本 */}
        <p className="text-sm text-gray-400 mb-4">
          在 **{filteredReviews.length}** 条评分为 **{ratingRange[0]}** 到 **{ratingRange[1]}** 星的评论中，当前显示 **{displayedReviews.length}** 条。
        </p>
        
        <DataTable title="评论详情" data={displayedReviews} />

        {/* 4. 【核心优化】: 只有当筛选出的评论超过20条时，才显示“查看全部”选项 */}
        {filteredReviews.length > 20 && (
          <div className="mt-4 flex items-center">
            <input
              id="show-all-reviews"
              type="checkbox"
              checked={showAllReviews}
              onChange={(e) => setShowAllReviews(e.target.checked)}
              className="h-4 w-4 rounded border-gray-600 bg-gray-700 text-indigo-600 focus:ring-indigo-500"
            />
            <label htmlFor="show-all-reviews" className="ml-2 block text-sm text-gray-300">
              显示全部 {filteredReviews.length} 条评论
            </label>
          </div>
        )}
      </div>

      <div>
        <h4 className="font-semibold text-white mb-2">情感分数统计</h4>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800 p-4 rounded-lg text-center">
            <p className="text-sm text-gray-400">所选评论 ({ratingRange[0]}-{ratingRange[1]} 星) 的平均情感分</p>
            <p className="text-3xl font-bold text-white mt-1">{avgFilteredSentiment.toFixed(2)}</p>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg text-center">
            <p className="text-sm text-gray-400">所有评论的平均情感分</p>
            <p className="text-3xl font-bold text-white mt-1">{average_sentiment.toFixed(2)}</p>
          </div>
        </div>
      </div>
      
      <div className="border-t border-gray-700 pt-8">
        <h3 className="text-xl font-semibold text-white mb-4">🤖 AI 评论深度分析报告</h3>
        <button onClick={handleAiAnalysis} disabled={isGenerating} className="btn-primary w-full disabled:opacity-50">
          {isGenerating ? "AI 正在分析..." : "生成 AI 分析报告"}
        </button>
        {error && <p className="text-red-400 mt-4">{error}</p>}
        
        {isGenerating && (
            <div className="space-y-4 mt-6">
                <details open className="bg-gray-900/50 p-4 rounded-lg">
                    <summary className="text-md font-semibold text-white cursor-pointer">查看AI思考过程</summary>
                    <div className="prose prose-invert max-w-none text-gray-300 mt-4">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{aiReport.thinking}</ReactMarkdown>
                    </div>
                </details>
            </div>
        )}
        
        {aiReport.report && (
          <div className="mt-6 prose prose-invert max-w-none bg-gray-900/50 p-6 rounded-lg">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{aiReport.report}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}