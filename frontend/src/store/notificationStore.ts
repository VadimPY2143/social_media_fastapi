import { create } from 'zustand';
import { NotificationState } from '../types';

interface NotificationStore {
  notification: NotificationState | null;
  showNotification: (message: string, type: 'success' | 'error' | 'info' | 'warning', duration?: number) => void;
  clearNotification: () => void;
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  notification: null,

  showNotification: (message: string, type: 'success' | 'error' | 'info' | 'warning', duration = 3000) => {
    set({ notification: { message, type, duration } });
    
    if (duration > 0) {
      setTimeout(() => {
        set({ notification: null });
      }, duration);
    }
  },

  clearNotification: () => {
    set({ notification: null });
  },
}));
