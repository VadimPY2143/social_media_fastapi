import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import { Button, Input, Card } from '../components/common';
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-neutral-950 via-purple-950 to-neutral-950 relative overflow-hidden">
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl"></div>
      </div>
      <Card className="w-full max-w-md">
        <h1 className="text-4xl font-black mb-2 text-center bg-gradient-to-r from-purple-300 via-pink-300 to-purple-300 bg-clip-text text-transparent">Welcome</h1>
        <p className="text-center text-white text-sm mb-8">Sign in to continue</p>
        
        {errors.form && <div className="mb-5 p-4 bg-pink-950/40 border border-pink-500/30 text-pink-200 rounded-xl text-sm font-medium">{errors.form}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
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
          <Button type="submit" loading={isLoading} className="w-full">
            Login
          </Button>
        </form>

        <p className="mt-4 text-center text-gray-600">
          Don't have an account? <Link to="/register" className="text-blue-600 hover:underline">Register</Link>
        </p>
      </Card>
    </div>
  );
};

export default Login;
