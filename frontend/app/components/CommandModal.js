// frontend/app/components/CommandModal.js
'use client';

import { useState, useEffect } from 'react';

export default function CommandModal({ isOpen, onClose, children }) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    // 当 isOpen 变为 true 时，我们先挂载组件，然后延迟一小段时间再添加 show 类，以触发进入动画
    if (isOpen) {
      const timer = setTimeout(() => setShow(true), 10); // 10ms delay
      return () => clearTimeout(timer);
    } 
    // 当 isOpen 变为 false 时，我们先移除 show 类以触发出动画，延迟关闭组件
    else {
      setShow(false);
    }
  }, [isOpen]);

  if (!isOpen) return null; // 如果 isOpen 为 false，我们什么都不渲染

  return (
    <div className="relative z-50" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      {/* Background backdrop, with fade transition */}
      <div 
        className={`fixed inset-0 bg-gray-900 bg-opacity-75 transition-opacity duration-300 ease-out ${show ? 'opacity-100' : 'opacity-0'}`}
      ></div>

      <div className="fixed inset-0 z-50 w-screen overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4 text-center">
          {/* Modal panel, with scale and fade transition */}
          <div 
            className={`relative transform overflow-hidden rounded-lg bg-gray-800 text-left shadow-xl transition-all duration-300 ease-out sm:my-8 sm:w-full sm:max-w-2xl ${show ? 'opacity-100 translate-y-0 sm:scale-100' : 'opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95'}`}
          >
            <div className="p-6">
              {children}
            </div>
            <div className="bg-gray-700/50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
              <button
                type="button"
                className="btn-secondary mt-3 sm:mt-0 w-full sm:w-auto"
                onClick={onClose}
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}