import React from 'react';
import { useLoading } from '../contexts/LoadingContext';
import { LoadingSpinner } from './LoadingIndicator';

/**
 * A global loading indicator that appears in the top-right corner of the screen
 * when any operation is loading.
 */
const GlobalLoadingIndicator: React.FC = () => {
    const { isLoading, loadingOperations } = useLoading();
    
    if (!isLoading()) return null;
    
    return (
        <div className="fixed top-4 right-4 z-50">
            <div className="bg-white p-2 rounded-lg shadow-lg flex items-center">
                <LoadingSpinner size="sm" />
                <span className="ml-2 text-sm text-gray-600">
                    {loadingOperations.length > 0 && loadingOperations[0].message 
                        ? loadingOperations[0].message 
                        : 'Loading...'}
                </span>
            </div>
        </div>
    );
};

export default GlobalLoadingIndicator;