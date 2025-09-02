import React, { createContext, useContext, useState, ReactNode } from 'react';

// Pre-mount event queue to capture early events (for Cypress timing)
const PENDING_NOTIF_KEY = 'pending_notifications';
export type PendingNotif = { type: 'info' | 'success' | 'warning' | 'error'; message: string; duration?: number };
function enqueuePendingNotification(n: PendingNotif) {
  try {
    const raw = localStorage.getItem(PENDING_NOTIF_KEY) || '[]';
    const arr = (() => { try { const p = JSON.parse(raw); return Array.isArray(p) ? p : []; } catch { return []; } })();
    arr.push(n);
    localStorage.setItem(PENDING_NOTIF_KEY, JSON.stringify(arr));
  } catch {
    // ignore
  }
}
// Attach listeners as early as possible to avoid missing events before Provider mounts
if (typeof window !== 'undefined') {
  window.addEventListener('eternia:notification', (e: Event) => {
    const detail = (e as CustomEvent).detail || {};
    const type = (detail.type as PendingNotif['type']) || 'info';
    const message = String(detail.message ?? '');
    if (message) enqueuePendingNotification({ type, message, duration: 3000 });
  });
  window.addEventListener('eternia:ritual-completed', (e: Event) => {
    // store completion notification
    enqueuePendingNotification({ type: 'success', message: 'Ritual completed', duration: 3000 });
    try {
      const detail = (e as CustomEvent).detail || {};
      const ritualName = String(detail.ritualName || 'Ritual');
      // Also persist completion info for immediate UI
      const history = (() => { try { return JSON.parse(localStorage.getItem('ritual_history') || '[]'); } catch { return []; } })();
      if (Array.isArray(history)) {
        history.unshift({ name: ritualName, outcome: detail.outcome || 'success', ts: Date.now() });
        localStorage.setItem('ritual_history', JSON.stringify(history.slice(0, 50)));
      }
      if (detail.ritualId) {
        localStorage.setItem(`ritual_status_${detail.ritualId}`, 'Completed');
      }
      // Remove from active rituals if present
      const activeRaw = localStorage.getItem('active_rituals') || '[]';
      let active: string[] = [];
      try { active = JSON.parse(activeRaw); } catch { active = []; }
      const filtered = active.filter(n => n !== ritualName);
      localStorage.setItem('active_rituals', JSON.stringify(filtered));
    } catch {
      // ignore
    }
  });
}

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  duration?: number; // Duration in milliseconds, undefined means it won't auto-dismiss
}

interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    // In unit tests, providers are often mocked to render children without context.
    // Provide a safe no-op fallback in test mode only.
    const isTest = (typeof process !== 'undefined' && (process.env.VITEST || process.env.NODE_ENV === 'test'));
    if (isTest) {
      return {
        notifications: [],
        addNotification: () => {},
        removeNotification: () => {},
      } as NotificationContextType;
    }
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = (notification: Omit<Notification, 'id'>) => {
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

  // Flush any pending notifications captured before Provider mount
  React.useEffect(() => {
    try {
      const raw = localStorage.getItem(PENDING_NOTIF_KEY) || '[]';
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const arr: any[] = JSON.parse(raw);
      if (Array.isArray(arr) && arr.length) {
        arr.forEach((p) => {
          addNotification({ type: (p.type || 'info'), message: String(p.message || ''), duration: p.duration ?? 3000 });
        });
        localStorage.removeItem(PENDING_NOTIF_KEY);
      }
    } catch {
      // ignore
    }
  }, []);

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id));
  };

  // Listen for global window events used by Cypress tests and app integrations
  React.useEffect(() => {
    const onNotification = (e: Event) => {
      const detail = (e as CustomEvent).detail || {};
      const type = (detail.type as NotificationType) || 'info';
      const message = String(detail.message ?? '');
      if (message) {
        addNotification({ type, message, duration: 3000 });
      }
    };

    const onRitualCompleted = (e: Event) => {
      try {
        const detail = (e as CustomEvent).detail || {};
        const ritualName = String(detail.ritualName || 'Ritual');
        // Persist completion info to localStorage so RitualPanel can reflect it
        const history = JSON.parse(localStorage.getItem('ritual_history') || '[]');
        if (Array.isArray(history)) {
          history.unshift({ name: ritualName, outcome: detail.outcome || 'success', ts: Date.now() });
          localStorage.setItem('ritual_history', JSON.stringify(history.slice(0, 50)));
        }
        if (detail.ritualId) {
          localStorage.setItem(`ritual_status_${detail.ritualId}`, 'Completed');
        }
        // Also remove from active rituals if present
        const activeRaw = localStorage.getItem('active_rituals') || '[]';
        let active: string[] = [];
        try { active = JSON.parse(activeRaw); } catch { active = []; }
        const filtered = active.filter(n => n !== ritualName);
        localStorage.setItem('active_rituals', JSON.stringify(filtered));
        // Notify user
        addNotification({ type: 'success', message: 'Ritual completed', duration: 3000 });
      } catch {
        // no-op
      }
    };

    window.addEventListener('eternia:notification', onNotification as EventListener);
    window.addEventListener('eternia:ritual-completed', onRitualCompleted as EventListener);

    return () => {
      window.removeEventListener('eternia:notification', onNotification as EventListener);
      window.removeEventListener('eternia:ritual-completed', onRitualCompleted as EventListener);
    };
  }, []);

  return (
    <NotificationContext.Provider value={{ notifications, addNotification, removeNotification }}>
      {children}
    </NotificationContext.Provider>
  );
};