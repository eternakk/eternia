import React from 'react';
import { useLoading } from '../contexts/LoadingContext';

interface LoadingIndicatorProps {
  operationKey?: string;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

/**
 * A component that shows a loading indicator when the specified operation is loading
 * If no operationKey is provided, it will show the loading indicator when any operation is loading
 */
export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  operationKey,
  fallback,
  children,
}) => {
  const { isLoading, loadingOperations } = useLoading();
  const loading = isLoading(operationKey);

  // Get the message from the first matching operation
  const message = operationKey
    ? loadingOperations.find((op) => op.operationKey === operationKey)?.message
    : loadingOperations[0]?.message;

  if (loading) {
    return (
      <div className="relative">
        {fallback || (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 z-10">
            <div className="bg-white p-4 rounded-lg shadow-lg flex flex-col items-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2"></div>
              {message && <div className="text-sm text-gray-600">{message}</div>}
            </div>
          </div>
        )}
        <div className="opacity-50 pointer-events-none">{children}</div>
      </div>
    );
  }

  return <>{children}</>;
};

/**
 * A standalone loading spinner component
 */
export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg'; message?: string }> = ({
  size = 'md',
  message,
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className={`animate-spin rounded-full ${sizeClasses[size]} border-b-2 border-blue-500 mb-2`}></div>
      {message && <div className="text-sm text-gray-600">{message}</div>}
    </div>
  );
};