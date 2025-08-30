import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useNotification } from '../contexts/NotificationContext';
// Define the color and icon for each notification type
const notificationStyles = {
    info: {
        bgColor: 'bg-blue-100',
        textColor: 'text-blue-800',
        icon: 'ℹ️',
    },
    success: {
        bgColor: 'bg-green-100',
        textColor: 'text-green-800',
        icon: '✅',
    },
    warning: {
        bgColor: 'bg-yellow-100',
        textColor: 'text-yellow-800',
        icon: '⚠️',
    },
    error: {
        bgColor: 'bg-red-100',
        textColor: 'text-red-800',
        icon: '❌',
    },
};
/**
 * Format notification messages to ensure they're user-friendly
 * This function handles:
 * 1. JSON strings (converts to formatted text)
 * 2. Error objects (extracts message)
 * 3. Regular strings (returns as is)
 */
const formatMessage = (message) => {
    // Check if the message is a JSON string
    try {
        // Look for patterns that suggest this might be JSON
        if ((message.startsWith('{') && message.endsWith('}')) ||
            (message.startsWith('[') && message.endsWith(']'))) {
            const jsonData = JSON.parse(message);
            return _jsx(JsonFormatter, { data: jsonData });
        }
    }
    catch {
        // Not valid JSON, continue with other formatting
    }
    // Check for error-like messages with stack traces
    if (message.includes('Error:') && message.includes('\n    at ')) {
        // Extract just the error message without the stack trace
        const errorMessage = message.split('\n')[0];
        return (_jsxs("div", { children: [_jsx("div", { children: errorMessage }), _jsxs("details", { className: "mt-1 text-xs", children: [_jsx("summary", { className: "cursor-pointer hover:underline", children: "View details" }), _jsx("pre", { className: "mt-1 whitespace-pre-wrap text-xs overflow-auto max-h-32", children: message })] })] }));
    }
    // Handle URLs by making them clickable
    if (message.includes('http://') || message.includes('https://')) {
        return formatMessageWithLinks(message);
    }
    // Return regular message
    return message;
};
/**
 * Make URLs in messages clickable
 */
const formatMessageWithLinks = (message) => {
    // Simple regex to find URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const parts = message.split(urlRegex);
    return (_jsx(_Fragment, { children: parts.map((part, i) => {
            if (part.match(urlRegex)) {
                return (_jsx("a", { href: part, target: "_blank", rel: "noopener noreferrer", className: "text-blue-600 hover:underline", children: part }, i));
            }
            return part;
        }) }));
};
/**
 * Component to format JSON data in a user-friendly way
 */
const JsonFormatter = ({ data }) => {
    // For simple error objects with a message property
    if (data && typeof data === 'object') {
        const obj = data;
        if ('message' in obj) {
            return _jsx("span", { children: String(obj.message) });
        }
        // For API error responses
        if ('error' in obj) {
            const errVal = obj.error;
            return _jsx("span", { children: typeof errVal === 'string' ? errVal : JSON.stringify(errVal) });
        }
    }
    // For arrays, show a summary
    if (Array.isArray(data)) {
        return (_jsxs("div", { children: [_jsxs("span", { children: ["Received ", data.length, " items"] }), _jsxs("details", { className: "mt-1 text-xs", children: [_jsx("summary", { className: "cursor-pointer hover:underline", children: "View data" }), _jsx("pre", { className: "mt-1 whitespace-pre-wrap text-xs overflow-auto max-h-32", children: JSON.stringify(data, null, 2) })] })] }));
    }
    // For other objects, show a formatted version
    if (data && typeof data === 'object') {
        const entries = Object.entries(data);
        if (entries.length <= 3) {
            // For simple objects, show inline
            return (_jsx("span", { children: entries.map(([key, value]) => (_jsxs("span", { children: [_jsxs("strong", { children: [key, ":"] }), " ", typeof value === 'object' ? '[Object]' : String(value), ' '] }, key))) }));
        }
        else {
            // For complex objects, use details/summary
            return (_jsxs("div", { children: [_jsxs("span", { children: ["Received data with ", entries.length, " properties"] }), _jsxs("details", { className: "mt-1 text-xs", children: [_jsx("summary", { className: "cursor-pointer hover:underline", children: "View data" }), _jsx("pre", { className: "mt-1 whitespace-pre-wrap text-xs overflow-auto max-h-32", children: JSON.stringify(data, null, 2) })] })] }));
        }
    }
    // Fallback for anything else
    return _jsx("span", { children: String(data) });
};
const NotificationContainer = () => {
    const { notifications, removeNotification } = useNotification();
    if (notifications.length === 0) {
        return null;
    }
    return (_jsx("div", { className: "fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md", children: notifications.map((notification) => {
            const { bgColor, textColor, icon } = notificationStyles[notification.type];
            return (_jsxs("div", { className: `${bgColor} ${textColor} p-4 rounded-md shadow-md flex items-start animate-fade-in`, role: "alert", "aria-live": "assertive", children: [_jsx("div", { className: "mr-2", "aria-hidden": "true", children: icon }), _jsx("div", { className: "flex-1", children: formatMessage(notification.message) }), _jsx("button", { onClick: () => removeNotification(notification.id), className: "ml-2 text-gray-500 hover:text-gray-700", "aria-label": "Close notification", children: "\u00D7" })] }, notification.id));
        }) }));
};
export default NotificationContainer;
