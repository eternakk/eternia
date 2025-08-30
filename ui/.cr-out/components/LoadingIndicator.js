import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useLoading } from '../contexts/LoadingContext';
/**
 * A component that shows a loading indicator when the specified operation is loading
 * If no operationKey is provided, it will show the loading indicator when any operation is loading
 */
export const LoadingIndicator = ({ operationKey, fallback, children, }) => {
    const { isLoading, loadingOperations } = useLoading();
    const loading = isLoading(operationKey);
    // Get the message from the first matching operation
    const message = operationKey
        ? loadingOperations.find((op) => op.operationKey === operationKey)?.message
        : loadingOperations[0]?.message;
    if (loading) {
        return (_jsxs("div", { className: "relative", children: [fallback || (_jsx("div", { className: "absolute inset-0 flex items-center justify-center bg-black bg-opacity-30 z-10", children: _jsxs("div", { className: "bg-white p-4 rounded-lg shadow-lg flex flex-col items-center", children: [_jsx("div", { className: "animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-2" }), message && _jsx("div", { className: "text-sm text-gray-600", children: message })] }) })), _jsx("div", { className: "opacity-50 pointer-events-none", children: children })] }));
    }
    return _jsx(_Fragment, { children: children });
};
/**
 * A standalone loading spinner component
 */
export const LoadingSpinner = ({ size = 'md', message, }) => {
    const sizeClasses = {
        sm: 'h-4 w-4',
        md: 'h-8 w-8',
        lg: 'h-12 w-12',
    };
    return (_jsxs("div", { className: "flex flex-col items-center justify-center", children: [_jsx("div", { className: `animate-spin rounded-full ${sizeClasses[size]} border-b-2 border-blue-500 mb-2` }), message && _jsx("div", { className: "text-sm text-gray-600", children: message })] }));
};
