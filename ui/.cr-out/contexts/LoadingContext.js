import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useContext, useState } from 'react';
const LoadingContext = createContext(undefined);
export const useLoading = () => {
    const context = useContext(LoadingContext);
    if (context === undefined) {
        throw new Error('useLoading must be used within a LoadingProvider');
    }
    return context;
};
export const LoadingProvider = ({ children }) => {
    const [loadingOperations, setLoadingOperations] = useState([]);
    const startLoading = (operationKey, message) => {
        const id = Math.random().toString(36).substring(2, 9);
        const newOperation = { id, operationKey, message };
        setLoadingOperations((prev) => [...prev, newOperation]);
        return id;
    };
    const stopLoading = (id) => {
        setLoadingOperations((prev) => prev.filter((operation) => operation.id !== id));
    };
    const isLoading = (operationKey) => {
        if (operationKey) {
            return loadingOperations.some((operation) => operation.operationKey === operationKey);
        }
        return loadingOperations.length > 0;
    };
    return (_jsx(LoadingContext.Provider, { value: { loadingOperations, startLoading, stopLoading, isLoading }, children: children }));
};
