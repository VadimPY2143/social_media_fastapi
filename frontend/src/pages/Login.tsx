import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import { PremiumButton, Input, Card } from '../components/common';
import { DarkVeil } from '../components/backgrounds';
import { getErrorMessage } from '../utils/helpers';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { login, isLoading } = useAuthStore();
  const { showNotification } = useNotificationStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    try {
      await login(email, password);
      showNotification('Login successful!', 'success');
      navigate('/feed');
    } catch (error) {
      console.error('Login error:', error);
      const message = getErrorMessage(error);
      setErrors({ form: message });
      showNotification(message, 'error');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <DarkVeil
        speed={1.2}
        warpAmount={0.25}
      />
      
      <Card className="w-full max-w-md relative z-10">
        <h1 className="text-4xl font-black mb-2 text-center bg-gradient-to-r from-purple-300 via-pink-300 to-purple-300 bg-clip-text text-transparent">Welcome Back</h1>
        <p className="text-center text-white/70 text-sm mb-8">Sign in to continue to MoodShare</p>
        
        {errors.form && <div className="mb-5 p-4 bg-red-950/40 border border-red-500/30 text-red-200 rounded-xl text-sm font-medium">{errors.form}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-5">
          <Input
            label="Email"
            type="email"
            placeholder="your@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button
            type="submit"
            disabled={isLoading}
            className="w-full h-12 rounded-lg border border-white/20 bg-white/10 hover:bg-white/15 transition-colors flex items-center justify-center text-white font-semibold disabled:opacity-60"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-5">
          <a
            href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/users/auth/login/google`}
            className="block"
          >
            <button
              type="button"
              className="w-full h-12 rounded-lg border border-white/20 bg-white/10 hover:bg-white/15 transition-colors flex items-center justify-center gap-3 text-white font-semibold"
            >
              <img
                src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                alt="Google"
                className="w-5 h-5"
              />
              Continue with Google
            </button>
          </a>
        </div>

        <p className="mt-6 text-center text-white/60 text-sm">
          Don't have an account? <Link to="/register" className="text-purple-400 hover:text-purple-300 font-semibold transition-colors">Create one</Link>
        </p>
      </Card>
    </div>
  );
};

export default Login;
