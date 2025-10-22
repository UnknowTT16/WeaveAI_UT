// frontend/app/components/ProfileForm.js
'use client';

import { useState } from 'react';

// 接收一个新的 prop: onFormSubmit, 并继续接收 isLoading
export default function ProfileForm({ onFormSubmit, isLoading }) {
  // 使用 useState 来“控制”每一个输入框的状态
  const [profileData, setProfileData] = useState({
    target_market: '德国',
    supply_chain: '消费电子, 户外用品',
    seller_type: '品牌方',
    min_price: 30,
    max_price: 90,
  });

  // 创建一个统一的 change 事件处理函数
  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    // 提交时，直接使用我们自己管理的 state
    const profileToSubmit = {
        ...profileData,
        min_price: parseInt(profileData.min_price) || 0,
        max_price: parseInt(profileData.max_price) || 0,
    };
    onFormSubmit(profileToSubmit); // 调用新的 prop
  };

  return (
    <div>
      <h3 className="text-xl font-semibold text-white mb-6">✨ 创建您的战略档案</h3>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="target_market" className="block text-sm font-medium text-gray-300">目标市场</label>
          <input type="text" name="target_market" id="target_market" value={profileData.target_market} onChange={handleChange} required className="mt-1 block w-full bg-gray-700 border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-white p-2"/>
        </div>
        <div>
          <label htmlFor="supply_chain" className="block text-sm font-medium text-gray-300">核心品类 (逗号分隔)</label>
          <input type="text" name="supply_chain" id="supply_chain" value={profileData.supply_chain} onChange={handleChange} required className="mt-1 block w-full bg-gray-700 border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-white p-2"/>
        </div>
        <div>
          <label htmlFor="seller_type" className="block text-sm font-medium text-gray-300">卖家类型</label>
          <select name="seller_type" id="seller_type" value={profileData.seller_type} onChange={handleChange} className="mt-1 block w-full bg-gray-700 border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-white p-2">
            <option>品牌方</option>
            <option>工厂转型</option>
            <option>贸易商</option>
            <option>个人卖家</option>
          </select>
        </div>
        <div className="flex space-x-4">
          <div className="w-1/2">
            <label htmlFor="min_price" className="block text-sm font-medium text-gray-300">最低售价 ($)</label>
            <input type="number" name="min_price" id="min_price" value={profileData.min_price} onChange={handleChange} required className="mt-1 block w-full bg-gray-700 border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-white p-2"/>
          </div>
          <div className="w-1/2">
            <label htmlFor="max_price" className="block text-sm font-medium text-gray-300">最高售价 ($)</label>
            <input type="number" name="max_price" id="max_price" value={profileData.max_price} onChange={handleChange} required className="mt-1 block w-full bg-gray-700 border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-white p-2"/>
          </div>
        </div>
        <button type="submit" disabled={isLoading} className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-500 disabled:cursor-not-allowed">
          {isLoading ? '生成中...' : '🤖 生成分析报告'}
        </button>
      </form>
    </div>
  );
}