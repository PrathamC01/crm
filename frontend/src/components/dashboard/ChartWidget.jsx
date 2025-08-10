import React from 'react';

const ChartWidget = ({ title, type, data, height = 'h-64', color = 'blue' }) => {
  const ChartPlaceholder = ({ title, chartType }) => (
    <div className={`bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg ${height} flex items-center justify-center`}>
      <div className="text-center">
        <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {chartType === 'bar' && (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          )}
          {chartType === 'line' && (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          )}
          {chartType === 'pie' && (
            <>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
            </>
          )}
          {(!chartType || chartType === 'default') && (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          )}
        </svg>
        <p className={`text-${color}-500 font-medium`}>{title}</p>
        <p className="text-sm text-gray-400">Chart implementation coming soon</p>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ChartPlaceholder title={title} chartType={type} />
      
      {/* Data table for now */}
      {data && data.length > 0 && (
        <div className="mt-4">
          <div className="text-sm text-gray-500 mb-2">Sample Data:</div>
          <div className="text-xs text-gray-400 space-y-1">
            {data.slice(0, 3).map((item, index) => (
              <div key={index}>
                {typeof item === 'object' 
                  ? Object.entries(item).map(([key, value]) => `${key}: ${value}`).join(', ')
                  : item
                }
              </div>
            ))}
            {data.length > 3 && <div>... and {data.length - 3} more items</div>}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChartWidget;