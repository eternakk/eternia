import axios from 'axios';
import { useNotification } from '../contexts/NotificationContext';
/**
 * Custom hook for handling API errors and displaying notifications
 * @returns Object with utility functions for error handling
 */
export const useErrorHandler = () => {
    const { addNotification } = useNotification();
    /**
     * Handles API errors and displays appropriate notifications
     * @param error - The error object
     * @param customMessage - Optional custom message to display instead of the default
     */
    const handleApiError = (error, customMessage) => {
        console.error('API Error:', error);
        let message = customMessage || 'An unexpected error occurred. Please try again.';
        if (axios.isAxiosError(error)) {
            const axiosError = error;
            if (axiosError.response) {
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                const status = axiosError.response.status;
                const data = axiosError.response.data;
                if (status === 401 || status === 403) {
                    message = 'Authentication error. Please log in again.';
                }
                else if (status === 404) {
                    message = 'The requested resource was not found.';
                }
                else if (status === 500) {
                    message = 'Server error. Please try again later.';
                }
                else if (data && typeof data === 'object' && 'message' in data) {
                    // Use the error message from the server if available
                    const d = data;
                    message = typeof d.message === 'string' ? d.message : String(d.message);
                }
            }
            else if (axiosError.request) {
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
    const withErrorHandling = (fn, errorMessage) => {
        return async (...args) => {
            try {
                return await fn(...args);
            }
            catch (error) {
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
/**
 * Creates a wrapped version of an API function with error handling
 * @param apiFn - The API function to wrap
 * @param errorMessage - Optional custom error message
 * @returns A new function that handles errors
 */
export const createSafeApiCall = (apiFn, 
// eslint-disable-next-line @typescript-eslint/no-unused-vars
_errorMessage) => {
    return async (...args) => {
        try {
            return await apiFn(...args);
        }
        catch (error) {
            console.error('API Error:', error);
            // Note: This function doesn't show notifications because it's not inside a component
            // Use useErrorHandler().withErrorHandling inside components instead
            return undefined;
        }
    };
};
