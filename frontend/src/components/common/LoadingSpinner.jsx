import React from 'react';

const LoadingSpinner = ({ size = 'medium', color = 'blue' }) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  };

  const colorClasses = {
    blue: 'border-blue-600',
    green: 'border-green-600',
    red: 'border-red-600',
    gray: 'border-gray-600'
  };

  return (
    <div className="flex justify-center items-center py-8">
      <div className={`
        ${sizeClasses[size]} 
        border-4 
        ${colorClasses[color]} 
        border-t-transparent 
        rounded-full 
        animate-spin
      `}></div>
    </div>
  );
};

export default LoadingSpinner;