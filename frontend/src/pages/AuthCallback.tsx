import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';

const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const { setToken } = useAuthStore();
  const { showNotification } = useNotificationStore();
  const handledRef = useRef(false);

  useEffect(() => {
    if (handledRef.current) return;
    handledRef.current = true;

    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');

    if (token) {
      setToken(token);
      showNotification('Login successful!', 'success');
      navigate('/feed', { replace: true });
    } else if (localStorage.getItem('access_token')) {
      navigate('/feed', { replace: true });
    } else {
      showNotification('OAuth login failed', 'error');
      navigate('/login', { replace: true });
    }
  }, [navigate, setToken, showNotification]);

  return (
    <div className="min-h-screen flex items-center justify-center text-white/70">
      Finishing sign in...
    </div>
  );
};

export default AuthCallback;
