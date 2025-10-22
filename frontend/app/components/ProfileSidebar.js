// frontend/app/components/ProfileSidebar.js
'use client';

export default function ProfileSidebar({ profile, onReset }) {
  if (!profile) return null; // 如果没有profile，则不渲染任何东西

  return (
    <div className="bg-gray-800 rounded-lg shadow-lg p-6 sticky top-8">
      <h3 className="text-xl font-semibold text-white mb-4 border-b border-gray-600 pb-2">
        📝 您的战略档案
      </h3>
      <dl className="space-y-4 text-sm">
        <div>
          <dt className="font-medium text-gray-400">目标市场</dt>
          <dd className="mt-1 text-white font-semibold">{profile.target_market}</dd>
        </div>
        <div>
          <dt className="font-medium text-gray-400">核心品类</dt>
          <dd className="mt-1 text-white font-semibold">{profile.supply_chain}</dd>
        </div>
        <div>
          <dt className="font-medium text-gray-400">卖家类型</dt>
          <dd className="mt-1 text-white font-semibold">{profile.seller_type}</dd>
        </div>
        <div>
          <dt className="font-medium text-gray-400">定价区间</dt>
          <dd className="mt-1 text-white font-semibold">${profile.min_price} - ${profile.max_price}</dd>
        </div>
      </dl>
      <button 
        onClick={onReset} 
        className="mt-8 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        🔄 开始新的分析
      </button>
    </div>
  );
}