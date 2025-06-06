import axios, {AxiosError} from 'axios';
import {useNotification} from '../contexts/NotificationContext';

/**
 * Custom hook for handling API errors and displaying notifications
 * @returns Object with utility functions for error handling
 */
export const useErrorHandler = () => {
    const {addNotification} = useNotification();

    /**
     * Handles API errors and displays appropriate notifications
     * @param error - The error object
     * @param customMessage - Optional custom message to display instead of the default
     */
    const handleApiError = (error: unknown, customMessage?: string) => {
        console.error('API Error:', error);

        let message = customMessage || 'An unexpected error occurred. Please try again.';

        if (axios.isAxiosError(error)) {
            const axiosError = error as AxiosError;

            if (axiosError.response) {
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                const status = axiosError.response.status;
                const data = axiosError.response.data as any;

                if (status === 401 || status === 403) {
                    message = 'Authentication error. Please log in again.';
                } else if (status === 404) {
                    message = 'The requested resource was not found.';
                } else if (status === 500) {
                    message = 'Server error. Please try again later.';
                } else if (data?.message) {
                    // Use the error message from the server if available
                    message = data.message;
                }
            } else if (axiosError.request) {
                // The request was made but no response was received
                message = 'No response from server. Please check your connection.';
            }
        }

        addNotification({
            type: 'error',
            message,
            duration: 5000, // Auto-dismiss after 5 seconds
        });
    };

    /**
     * Wraps an async function with error handling
     * @param fn - The async function to wrap
     * @param errorMessage - Optional custom error message
     * @returns A new function that handles errors
     */
    const withErrorHandling = <T extends (...args: any[]) => Promise<any>>(
        fn: T,
        errorMessage?: string
    ): ((...args: Parameters<T>) => Promise<Awaited<ReturnType<T>> | undefined>) => {
        return async (...args: Parameters<T>) => {
            try {
                return await fn(...args);
            } catch (error) {
                handleApiError(error, errorMessage);
                return undefined;
            }
        };
    };

    return {
        handleApiError,
        withErrorHandling,
    };
};

// @ts-ignore
/**
 * Creates a wrapped version of an API function with error handling
 * @param apiFn - The API function to wrap
 * @param errorMessage - Optional custom error message
 * @returns A new function that handles errors
 */
export const createSafeApiCall = <T extends (...args: any[]) => Promise<any>>(
    apiFn: T,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    errorMessage?: string
) => {
    return async (...args: Parameters<T>): Promise<Awaited<ReturnType<T>> | undefined> => {
        try {
            return await apiFn(...args);
        } catch (error) {
            console.error('API Error:', error);
            // Note: This function doesn't show notifications because it's not inside a component
            // Use useErrorHandler().withErrorHandling inside components instead
            return Promise.resolve(undefined);
        }
    };
};
