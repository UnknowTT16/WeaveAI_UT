// frontend/app/components/StepsIndicator.js
'use client';

export default function StepsIndicator({ activeStep, setActiveStep, stepsStatus }) {
  const steps = [
    { id: 'insight', name: '机会洞察' },
    { id: 'validation', name: '自我验证' },
    { id: 'action', name: '行动计划' },
  ];

  const actionStepTooltip = stepsStatus.action === 'upcoming' 
    ? "请先完成“机会洞察”并进行至少一次“自我验证”分析" 
    : "生成行动计划";

  return (
    <nav aria-label="Progress">
      <ol role="list" className="flex justify-between items-start">
        {steps.map((step, stepIdx) => {
          const isCurrent = step.id === activeStep;
          const isClickable = stepsStatus[step.id] !== 'upcoming';

          return (
            <li key={step.name} className="relative flex-1 flex justify-center">
              
              {/* 【核心修复】: 只在中间的元素上画线 */}
              {stepIdx > 0 && stepIdx < steps.length - 1 && (
                <>
                  {/* Line to the left */}
                  <div className="absolute w-1/2 h-0.5 bg-gray-700 top-4 right-1/2 z-0" aria-hidden="true" />
                  {/* Line to the right */}
                  <div className="absolute w-1/2 h-0.5 bg-gray-700 top-4 left-1/2 z-0" aria-hidden="true" />
                </>
              )}
              {/* Special case for the first item's right line */}
              {stepIdx === 0 && (
                <div className="absolute w-1/2 h-0.5 bg-gray-700 top-4 left-1/2 z-0" aria-hidden="true" />
              )}
              {/* Special case for the last item's left line */}
              {stepIdx === steps.length - 1 && (
                <div className="absolute w-1/2 h-0.5 bg-gray-700 top-4 right-1/2 z-0" aria-hidden="true" />
              )}

              <div className="relative flex flex-col items-center">
                <button
                  onClick={() => isClickable && setActiveStep(step.id)}
                  disabled={!isClickable}
                  className={`relative z-10 group flex h-8 w-8 items-center justify-center rounded-full transition-colors duration-200 ${
                    isCurrent ? 'border-2 border-indigo-600 bg-gray-800' : 
                    'border-2 border-gray-600 bg-gray-800 hover:border-gray-400'
                  } disabled:cursor-not-allowed disabled:hover:border-gray-600`}
                  aria-current={isCurrent ? 'step' : undefined}
                  title={step.id === 'action' ? actionStepTooltip : ''}
                >
                  <span className={`h-2.5 w-2.5 rounded-full transition-colors duration-200 ${
                      isCurrent ? 'bg-indigo-600' : 'bg-gray-600'
                  } ${isClickable && !isCurrent ? 'group-hover:bg-gray-400' : ''}`} aria-hidden="true" />
                </button>
                
                <span className={`mt-2 text-xs text-center ${isCurrent ? 'text-white font-semibold' : 'text-gray-400'}`}>{step.name}</span>
              </div>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}