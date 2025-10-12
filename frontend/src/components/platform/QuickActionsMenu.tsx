import React from 'react';

interface QuickActionsMenuProps {
  className?: string;
}

const QuickActionsMenu: React.FC<QuickActionsMenuProps> = ({ className = '' }) => {
  return (
    <div className={`quick-actions-menu ${className}`}>
      <div className="flex space-x-4">
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
          New Deal
        </button>
        <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
          Upload Document
        </button>
        <button className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors">
          Create Report
        </button>
      </div>
    </div>
  );
};

export default QuickActionsMenu;
