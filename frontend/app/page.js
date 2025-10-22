// frontend/app/page.js
'use client';

import { useState, useMemo } from 'react';
import ProfileForm from './components/ProfileForm';
import ReportDisplay from './components/ReportDisplay';
import ProfileSidebar from './components/ProfileSidebar';
import ValidationDashboard from './components/ValidationDashboard';
import ActionPlanner from './components/ActionPlanner';
import CommandModal from './components/CommandModal';
import StepsIndicator from './components/StepsIndicator';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { visit } from 'unist-util-visit';

function remarkAddTargetBlank() {
  return (tree) => {
    visit(tree, 'link', (node) => {
      node.data = node.data || {};
      node.data.hProperties = { target: '_blank', rel: 'noopener noreferrer' };
    });
  };
}

export default function Home() {
  const [userProfile, setUserProfile] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportContent, setReportContent] = useState(''); 
  const [error, setError] = useState('');
  const [validationSummary, setValidationSummary] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeStep, setActiveStep] = useState('insight');

  const handleProfileSubmit = (profile) => {
    setIsModalOpen(false);
    setReportContent('');
    setError('');
    setValidationSummary('');
    setUserProfile(profile);
    setIsGenerating(true);
    setActiveStep('insight');
  };

  const handleGenerationComplete = (finalReport) => {
    setReportContent(finalReport);
    setIsGenerating(false);
  };

  const handleGenerationError = (errorMessage) => {
    setError(errorMessage);
    setIsGenerating(false);
  };

  const handleValidationComplete = (summary) => {
    setValidationSummary(summary);
  };

  const handleReset = () => {
    setUserProfile(null);
    setIsGenerating(false);
    setReportContent('');
    setError('');
    setValidationSummary('');
    setActiveStep('insight');
  };

  const stepsStatus = useMemo(() => {
    let status = { 
      insight: 'current', 
      validation: 'current', 
      action: 'upcoming' 
    };
    
    if (reportContent && validationSummary) {
      status.action = 'current';
    }
    
    return status;
  }, [reportContent, validationSummary]);

  return (
    <main className="min-h-screen bg-gray-900 text-gray-300 flex flex-col">
      
      {userProfile ? (
        <>
          {/* === 仪表盘视图 Header === */}
          <header className="text-center py-6 border-b border-gray-800 flex-shrink-0">
            <h1 className="text-3xl font-bold text-white">📈 WeaveAI 智能分析助手</h1>
            <p className="text-gray-400 mt-2 text-sm">告别感觉，让数据与AI为您引航</p>
          </header>
          
          <div className="flex-grow flex overflow-hidden">
            {/* === 左侧侧边栏 === */}
            <aside className="w-72 flex-shrink-0 p-6 border-r border-gray-800 overflow-y-auto">
              <ProfileSidebar profile={userProfile} onReset={handleReset} />
            </aside>

            {/* === 右侧主内容区 === */}
            <div className="flex-grow p-6 md:p-8 overflow-y-auto">
              <div className="mb-10">
                <StepsIndicator activeStep={activeStep} setActiveStep={setActiveStep} stepsStatus={stepsStatus} />
              </div>

              <div className="space-y-8">
                {activeStep === 'insight' && (
                  <div className="bg-gray-800 rounded-lg shadow-lg p-6">
                    <h2 className="text-2xl font-semibold text-white mb-4">第一步：机会洞察 (Insight)</h2>
                    {isGenerating ? (
                      <ReportDisplay
                        profile={userProfile}
                        onGenerationComplete={handleGenerationComplete}
                        onError={handleGenerationError}
                      />
                    ) : reportContent ? (
                      <div className="prose prose-invert max-w-none bg-gray-900/50 p-6 rounded-lg">
                        <ReactMarkdown remarkPlugins={[remarkGfm, remarkAddTargetBlank]}>{reportContent}</ReactMarkdown>
                      </div>
                    ) : (
                      <div className="text-center py-10">
                        <p className="text-gray-400">档案已创建，请在左侧点击“开始新的分析”以生成报告，或切换到其他步骤。</p>
                      </div>
                    )}
                    {error && !isGenerating && ( <div className="mt-4 text-red-400 bg-red-900/50 p-4 rounded-md"><p>{error}</p></div> )}
                  </div>
                )}

                {activeStep === 'validation' && (
                  <div className="bg-gray-800 rounded-lg shadow-lg p-6">
                    <h2 className="text-2xl font-semibold text-white mb-4">第二步：自我验证 (Validation)</h2>
                    <ValidationDashboard onValidationComplete={handleValidationComplete} />
                  </div>
                )}

                {activeStep === 'action' && (
                   <>
                    {stepsStatus.action === 'upcoming' ? (
                        <div className="text-center p-12 bg-gray-800 rounded-lg">
                            <h2 className="text-2xl font-semibold text-white mb-4">第三步：行动计划 (Action Plan)</h2>
                            <p className="text-gray-400">请先完成“机会洞察”并进行至少一次“自我验证”分析，以解锁行动计划。</p>
                        </div>
                    ) : (
                        <div className="bg-gray-800 rounded-lg shadow-lg p-6">
                            <h2 className="text-2xl font-semibold text-white mb-4">第三步：行动计划 (Action Plan)</h2>
                            <ActionPlanner marketReport={reportContent} validationSummary={validationSummary} />
                        </div>
                    )}
                   </>
                )}
              </div>
            </div>
          </div>
        </>
      ) : (
        // --- 初始欢迎视图 ---
        <div className="flex-grow flex items-center justify-center p-4">
          <div className="text-center max-w-2xl w-full">
            <div className="mb-8">
              <h1 className="text-4xl md:text-5xl font-bold text-white">
                📈 WeaveAI 智能分析助手
              </h1>
              <p className="text-gray-400 mt-4 text-lg">
                告别感觉，让数据与AI为您引航
              </p>
            </div>
            
            <div className="bg-gray-800/50 rounded-xl p-8 shadow-2xl border border-gray-700">
              <h2 className="text-3xl font-bold text-white mb-4">开始您的跨境选品之旅</h2>
              <p className="text-gray-400 mb-8">
                提供您的商业画像，我们的AI战略顾问将为您生成一份高度定制化的市场分析报告，助您发现下一个爆款。
              </p>
              <button 
                onClick={() => setIsModalOpen(true)}
                className="px-8 py-4 text-lg font-bold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-transform transform hover:scale-105 shadow-lg shadow-indigo-600/30"
              >
                🚀 开始新的分析
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- 命令面板模态框 --- */}
      <CommandModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <ProfileForm onFormSubmit={handleProfileSubmit} isLoading={isGenerating} />
      </CommandModal>
    </main>
  );
}