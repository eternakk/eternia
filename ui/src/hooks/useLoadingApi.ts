import { useCallback } from 'react';
import { useLoading } from '../contexts/LoadingContext';
import { useErrorHandler } from '../utils/errorHandling';

/**
 * A hook that combines loading state management with API calls
 * @returns Object with utility functions for API calls with loading state management
 */
export const useLoadingApi = () => {
  const { startLoading, stopLoading } = useLoading();
  const { handleApiError } = useErrorHandler();

  /**
   * Wraps an async function with loading state management and error handling
   * @param fn - The async function to wrap
   * @param operationKey - A unique key to identify this operation in the loading state
   * @param errorMessage - Optional custom error message
   * @returns A new function that manages loading state and handles errors
   */
  const withLoading = useCallback(
    <A extends unknown[], R>(
      fn: (...args: A) => Promise<R>,
      operationKey: string,
      errorMessage?: string
    ): ((...args: A) => Promise<R | undefined>) => {
      return async (...args: A) => {
        const loadingId = startLoading(operationKey);
        try {
          const result = await fn(...args);
          return result;
        } catch (error) {
          handleApiError(error, errorMessage);
          return undefined;
        } finally {
          stopLoading(loadingId);
        }
      };
    },
    [startLoading, stopLoading, handleApiError]
  );

  return {
    withLoading,
  };
};