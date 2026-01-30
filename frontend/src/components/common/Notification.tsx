import React, { useEffect } from 'react';
import { useNotificationStore } from '../../store/notificationStore';

const Notification: React.FC = () => {
  const { notification, clearNotification } = useNotificationStore();

  useEffect(() => {
    if (notification && notification.duration && notification.duration > 0) {
      const timer = setTimeout(clearNotification, notification.duration);
      return () => clearTimeout(timer);
    }
  }, [notification, clearNotification]);

  if (!notification) return null;

  const typeClasses = {
    success: 'bg-green-50 text-green-800 border-green-200',
    error: 'bg-red-50 text-red-800 border-red-200',
    info: 'bg-blue-50 text-blue-800 border-blue-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
  };

  const iconClasses = {
    success: '✓',
    error: '✕',
    info: 'ⓘ',
    warning: '⚠',
  };

  return (
    <div
      className={`fixed top-4 right-4 p-4 rounded-lg border ${typeClasses[notification.type]} shadow-lg max-w-md z-50`}
    >
      <div className="flex items-start gap-3">
        <span className="text-xl font-bold">{iconClasses[notification.type]}</span>
        <div className="flex-1">
          <p className="font-medium">{notification.message}</p>
        </div>
        <button
          onClick={clearNotification}
          className="text-lg font-bold opacity-50 hover:opacity-100 transition-opacity"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default Notification;
