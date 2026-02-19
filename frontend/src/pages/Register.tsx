import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import { PremiumButton, Input, Card, AvatarUpload } from '../components/common';
import { DarkVeil } from '../components/backgrounds';
import { getErrorMessage } from '../utils/helpers';
import { apiClient } from '../api/client';

const Register: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [avatar, setAvatar] = useState<File | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { isLoading: authLoading } = useAuthStore();
  const { showNotification } = useNotificationStore();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (username.length < 5) newErrors.username = 'Username must be at least 5 characters';
    if (password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    if (password !== confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
    return newErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors = validate();
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    setIsLoading(true);
    try {
      await apiClient.registerWithAvatar(username, email, password, avatar || undefined);
      showNotification('Registration successful! Please login.', 'success');
      navigate('/login');
    } catch (error) {
      const message = getErrorMessage(error);
      setErrors({ form: message });
      showNotification(message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <DarkVeil
        speed={1.2}
        warpAmount={0.25}
      />
      
      <Card className="w-full max-w-md relative z-10">
        <h1 className="text-4xl font-black mb-2 text-center bg-gradient-to-r from-purple-300 via-pink-300 to-purple-300 bg-clip-text text-transparent">Join MoodShare</h1>
        <p className="text-center text-white/70 text-sm mb-8">Create your account and start sharing</p>
        
        {errors.form && <div className="mb-5 p-4 bg-red-950/40 border border-red-500/30 text-red-200 rounded-xl text-sm font-medium">{errors.form}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-5">
          <AvatarUpload
            username={username}
            onAvatarSelected={setAvatar}
            selectedFile={avatar}
          />
          
          <Input
            label="Username"
            placeholder="john_doe"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            error={errors.username}
            required
          />
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
            error={errors.password}
            required
          />
          <Input
            label="Confirm Password"
            type="password"
            placeholder="••••••••"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            error={errors.confirmPassword}
            required
          />
          <PremiumButton 
           type="submit" 
           loading={isLoading || authLoading} 
           variant="gradient"
           size="lg"
           className="w-full"
          >
           {isLoading || authLoading ? 'Creating Account...' : 'Create Account'}
          </PremiumButton>
          </form>

          <p className="mt-6 text-center text-white/60 text-sm">
          Already have an account? <Link to="/login" className="text-purple-400 hover:text-purple-300 font-semibold transition-colors">Sign in</Link>
          </p>
      </Card>
    </div>
  );
};

export default Register;
