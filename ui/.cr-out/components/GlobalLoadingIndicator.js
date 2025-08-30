import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useLoading } from '../contexts/LoadingContext';
import { LoadingSpinner } from './LoadingIndicator';
/**
 * A global loading indicator that appears in the top-right corner of the screen
 * when any operation is loading.
 */
const GlobalLoadingIndicator = () => {
    const { isLoading, loadingOperations } = useLoading();
    if (!isLoading())
        return null;
    return (_jsx("div", { className: "fixed top-4 right-4 z-50", children: _jsxs("div", { className: "bg-white p-2 rounded-lg shadow-lg flex items-center", children: [_jsx(LoadingSpinner, { size: "sm" }), _jsx("span", { className: "ml-2 text-sm text-gray-600", children: loadingOperations.length > 0 && loadingOperations[0].message
                        ? loadingOperations[0].message
                        : 'Loading...' })] }) }));
};
export default GlobalLoadingIndicator;
