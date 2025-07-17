import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  fullScreen?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  text,
  fullScreen = false 
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const containerClasses = fullScreen 
    ? 'min-h-screen flex items-center justify-center' 
    : 'flex items-center justify-center p-4';

  return (
    <div className={containerClasses}>
      <div className="text-center">
        <div 
          className={`animate-spin rounded-full border-2 border-gray-200 border-t-primary-600 ${sizeClasses[size]} mx-auto`}
        />
        {text && (
          <p className="mt-2 text-gray-600 dark:text-gray-400 text-sm">
            {text}
          </p>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;