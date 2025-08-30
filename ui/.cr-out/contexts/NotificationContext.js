import { jsx as _jsx } from "react/jsx-runtime";
import { createContext, useContext, useState } from 'react';
const NotificationContext = createContext(undefined);
export const useNotification = () => {
    const context = useContext(NotificationContext);
    if (context === undefined) {
        throw new Error('useNotification must be used within a NotificationProvider');
    }
    return context;
};
export const NotificationProvider = ({ children }) => {
    const [notifications, setNotifications] = useState([]);
    const addNotification = (notification) => {
        const id = Math.random().toString(36).substring(2, 9);
        const newNotification = { ...notification, id };
        setNotifications((prev) => [...prev, newNotification]);
        // Auto-dismiss notification if duration is provided
        if (notification.duration) {
            setTimeout(() => {
                removeNotification(id);
            }, notification.duration);
        }
    };
    const removeNotification = (id) => {
        setNotifications((prev) => prev.filter((notification) => notification.id !== id));
    };
    return (_jsx(NotificationContext.Provider, { value: { notifications, addNotification, removeNotification }, children: children }));
};
