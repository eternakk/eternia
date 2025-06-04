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
          >
            <div className="mr-2">{icon}</div>
            <div className="flex-1">{notification.message}</div>
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