import React from 'react';
import { useNotification, NotificationType } from '../contexts/NotificationContext';

// Define the color and icon for each notification type
const notificationStyles: Record<NotificationType, { bgColor: string; textColor: string; icon: string }> = {
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
const formatMessage = (message: string): React.ReactNode => {
  // Check if the message is a JSON string
  try {
    // Look for patterns that suggest this might be JSON
    if (
      (message.startsWith('{') && message.endsWith('}')) || 
      (message.startsWith('[') && message.endsWith(']'))
    ) {
      const jsonData = JSON.parse(message);
      return <JsonFormatter data={jsonData} />;
    }
  } catch {
    // Not valid JSON, continue with other formatting
  }

  // Check for error-like messages with stack traces
  if (message.includes('Error:') && message.includes('\n    at ')) {
    // Extract just the error message without the stack trace
    const errorMessage = message.split('\n')[0];
    return (
      <div>
        <div>{errorMessage}</div>
        <details className="mt-1 text-xs">
          <summary className="cursor-pointer hover:underline">View details</summary>
          <pre className="mt-1 whitespace-pre-wrap text-xs overflow-auto max-h-32">
            {message}
          </pre>
        </details>
      </div>
    );
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
const formatMessageWithLinks = (message: string): React.ReactNode => {
  // Simple regex to find URLs
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const parts = message.split(urlRegex);

  return (
    <>
      {parts.map((part, i) => {
        if (part.match(urlRegex)) {
          return (
            <a 
              key={i} 
              href={part} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              {part}
            </a>
          );
        }
        return part;
      })}
    </>
  );
};

/**
 * Component to format JSON data in a user-friendly way
 */
const JsonFormatter = ({ data }: { data: unknown }): React.ReactElement => {
  // For simple error objects with a message property
  if (data && typeof data === 'object') {
    const obj = data as Record<string, unknown>;
    if ('message' in obj) {
      return <span>{String(obj.message)}</span>;
    }
    // For API error responses
    if ('error' in obj) {
      const errVal = obj.error;
      return <span>{typeof errVal === 'string' ? errVal : JSON.stringify(errVal)}</span>;
    }
  }

  // For arrays, show a summary
  if (Array.isArray(data)) {
    return (
      <div>
        <span>Received {data.length} items</span>
        <details className="mt-1 text-xs">
          <summary className="cursor-pointer hover:underline">View data</summary>
          <pre className="mt-1 whitespace-pre-wrap text-xs overflow-auto max-h-32">
            {JSON.stringify(data, null, 2)}
          </pre>
        </details>
      </div>
    );
  }

  // For other objects, show a formatted version
  if (data && typeof data === 'object') {
    const entries = Object.entries(data as Record<string, unknown>);
    if (entries.length <= 3) {
      // For simple objects, show inline
      return (
        <span>
          {entries.map(([key, value]) => (
            <span key={key}>
              <strong>{key}:</strong> {typeof value === 'object' ? '[Object]' : String(value)}{' '}
            </span>
          ))}
        </span>
      );
    } else {
      // For complex objects, use details/summary
      return (
        <div>
          <span>Received data with {entries.length} properties</span>
          <details className="mt-1 text-xs">
            <summary className="cursor-pointer hover:underline">View data</summary>
            <pre className="mt-1 whitespace-pre-wrap text-xs overflow-auto max-h-32">
              {JSON.stringify(data, null, 2)}
            </pre>
          </details>
        </div>
      );
    }
  }

  // Fallback for anything else
  return <span>{String(data)}</span>;
};

const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useNotification();

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      {notifications.map((notification) => {
        const { bgColor, textColor, icon } = notificationStyles[notification.type];

        return (
          <div
            key={notification.id}
            className={`${bgColor} ${textColor} p-4 rounded-md shadow-md flex items-start animate-fade-in`}
            role="alert"
            aria-live="assertive"
          >
            <div className="mr-2" aria-hidden="true">{icon}</div>
            <div className="flex-1">{formatMessage(notification.message)}</div>
            <button
              onClick={() => removeNotification(notification.id)}
              className="ml-2 text-gray-500 hover:text-gray-700"
              aria-label="Close notification"
            >
              ×
            </button>
          </div>
        );
      })}
    </div>
  );
};

export default NotificationContainer;

// Add this to your global CSS or create a new CSS file
// .animate-fade-in {
//   animation: fadeIn 0.3s ease-in-out;
// }
// 
// @keyframes fadeIn {
//   from {
//     opacity: 0;
//     transform: translateY(-10px);
//   }
//   to {
//     opacity: 1;
//     transform: translateY(0);
//   }
// }
