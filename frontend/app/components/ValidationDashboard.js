// frontend/app/components/ValidationDashboard.js
'use client';

import { useState, useCallback, useEffect } from 'react';
import dynamic from 'next/dynamic';
import FileUpload from './FileUpload';
import DataTable from './DataTable';
import SentimentAnalysis from './SentimentAnalysis';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

export default function ValidationDashboard({ onValidationComplete }) {
  const [salesFile, setSalesFile] = useState(null);
  const [reviewsFile, setReviewsFile] = useState(null);
  const [analysisResults, setAnalysisResults] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('forecast');
  const [showAllProducts, setShowAllProducts] = useState(false);

  // 使用 useEffect 来监听分析结果的变化, 并通知父组件
  useEffect(() => {
    if (Object.keys(analysisResults).length > 0) {
      // 尝试从聚类分析结果中获取摘要
      const clusteringData = analysisResults['product-clustering'];
      if (clusteringData && clusteringData.hot_products && clusteringData.hot_products.length > 0) {
        const summary = `内部数据显示，热销商品主要集中在簇${clusteringData.cluster_summary[0].cluster}。主要热销SKU包括：${clusteringData.hot_products.slice(0, 3).map(p => p.SKU).join(', ')}。`;
        onValidationComplete(summary);
      } else {
        onValidationComplete('已完成至少一项数据验证。');
      }
    }
  }, [analysisResults, onValidationComplete]);

  const handleAnalysis = async (analysisType, file, endpoint) => {
    if (!file) {
      setError(`请先上传 ${analysisType === 'reviews' ? '评论' : '销售'} 数据文件。`);
      return;
    }

    setIsLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/data/${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '分析失败，请检查文件格式。');
      }

      const result = await response.json();
      setAnalysisResults(prev => ({ ...prev, [endpoint]: result }));
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleDownload = useCallback((hot_products) => {
    if (!hot_products || hot_products.length === 0) return;
    
    const headers = Object.keys(hot_products[0]);
    const csvContent = "data:text/csv;charset=utf-8," 
      + headers.join(",") + "\n"
      + hot_products.map(row => 
          headers.map(header => `"${row[header]}"`).join(",")
        ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "hot_products.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, []);

  const renderTabContent = () => {
    switch (activeTab) {
      case 'forecast':
        if (analysisResults.hasOwnProperty('forecast-sales')) {
            const figData = JSON.parse(analysisResults['forecast-sales']);
            return <Plot data={figData.data} layout={figData.layout} useResizeHandler={true} style={{ width: '100%', height: '100%' }} />;
        }
        return <button onClick={() => handleAnalysis('sales', salesFile, 'forecast-sales')} disabled={isLoading || !salesFile} className="btn-primary disabled:opacity-50">开始销售预测</button>;
      
      case 'clustering': {
        const clusteringData = analysisResults['product-clustering'];
        if (!clusteringData) {
          return <button onClick={() => handleAnalysis('sales', salesFile, 'product-clustering')} disabled={isLoading || !salesFile} className="btn-primary disabled:opacity-50">开始聚类分析</button>;
        }

        const { cluster_summary, hot_products } = clusteringData;
        const displayedProducts = showAllProducts ? hot_products : hot_products.slice(0, 20);

        return (
          <div className="space-y-8">
            <DataTable title="各商品簇特征均值" data={cluster_summary} />
            
            <div>
              <DataTable title={`热销商品列表 (${displayedProducts.length}/${hot_products.length} 条)`} data={displayedProducts} />
              <div className="mt-4 flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="show-all"
                    type="checkbox"
                    checked={showAllProducts}
                    onChange={(e) => setShowAllProducts(e.target.checked)}
                    className="h-4 w-4 rounded border-gray-600 bg-gray-700 text-indigo-600 focus:ring-indigo-500"
                  />
                  <label htmlFor="show-all" className="ml-2 block text-sm text-gray-300">
                    显示所有热销商品
                  </label>
                </div>
                <button onClick={() => handleDownload(hot_products)} className="btn-secondary">
                  下载列表 (CSV)
                </button>
              </div>
            </div>
          </div>
        );
      }
      
      case 'sentiment':
        if (analysisResults.hasOwnProperty('sentiment-analysis')) {
          return <SentimentAnalysis analysisResult={analysisResults['sentiment-analysis']} />;
        }
        return <button onClick={() => handleAnalysis('reviews', reviewsFile, 'sentiment-analysis')} disabled={isLoading || !reviewsFile} className="btn-primary disabled:opacity-50">开始情感分析</button>;

      default:  
        return null;
    }
  };

  return (
    <div className="space-y-8">
      {/* 文件上传区 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium text-white mb-2">1. 上传销售报告</h3>
          <FileUpload title="Amazon 销售报告 (.csv, .parquet)" onFileSelect={setSalesFile} isLoading={isLoading} />
          {salesFile && <p className="text-sm text-gray-400 mt-2">已选择: {salesFile.name}</p>}
        </div>
        <div>
          <h3 className="text-lg font-medium text-white mb-2">2. 上传评论数据 (可选)</h3>
          <FileUpload title="Amazon 评论数据 (.csv, .parquet)" onFileSelect={setReviewsFile} isLoading={isLoading} />
          {reviewsFile && <p className="text-sm text-gray-400 mt-2">已选择: {reviewsFile.name}</p>}
        </div>
      </div>

      {/* 分析结果区 */}
      <div className="bg-gray-900/50 rounded-lg p-6 min-h-[300px]">
        <h3 className="text-lg font-medium text-white mb-4">分析仪表盘</h3>
        
        {/* Tab 导航 */}
        <div className="border-b border-gray-700 mb-4">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            <button onClick={() => setActiveTab('forecast')} className={`${activeTab === 'forecast' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}>
              销售预测
            </button>
            <button onClick={() => setActiveTab('clustering')} className={`${activeTab === 'clustering' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}>
              热销品聚类
            </button>
            <button onClick={() => setActiveTab('sentiment')} className={`${activeTab === 'sentiment' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-500'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}>
              情感分析
            </button>
          </nav>
        </div>

        {/* Tab 内容 */}
        <div className="mt-4">
          {isLoading && <p className="text-indigo-400 animate-pulse">分析中，请稍候...</p>}
          {error && <p className="text-red-400">{error}</p>}
          {!isLoading && !error && renderTabContent()}
        </div>
      </div>
    </div>
  );
}