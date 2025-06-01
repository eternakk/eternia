import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define the shape of a loading operation
export interface LoadingOperation {
  id: string;
  operationKey: string;
  message?: string;
}

interface LoadingContextType {
  loadingOperations: LoadingOperation[];
  startLoading: (operationKey: string, message?: string) => string;
  stopLoading: (id: string) => void;
  isLoading: (operationKey?: string) => boolean;
}

const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

export const useLoading = () => {
  const context = useContext(LoadingContext);
  if (context === undefined) {
    throw new Error('useLoading must be used within a LoadingProvider');
  }
  return context;
};

interface LoadingProviderProps {
  children: ReactNode;
}

export const LoadingProvider: React.FC<LoadingProviderProps> = ({ children }) => {
  const [loadingOperations, setLoadingOperations] = useState<LoadingOperation[]>([]);

  const startLoading = (operationKey: string, message?: string): string => {
    const id = Math.random().toString(36).substring(2, 9);
    const newOperation: LoadingOperation = { id, operationKey, message };
    
    setLoadingOperations((prev) => [...prev, newOperation]);
    return id;
  };

  const stopLoading = (id: string) => {
    setLoadingOperations((prev) => prev.filter((operation) => operation.id !== id));
  };

  const isLoading = (operationKey?: string): boolean => {
    if (operationKey) {
      return loadingOperations.some((operation) => operation.operationKey === operationKey);
    }
    return loadingOperations.length > 0;
  };

  return (
    <LoadingContext.Provider value={{ loadingOperations, startLoading, stopLoading, isLoading }}>
      {children}
    </LoadingContext.Provider>
  );
};