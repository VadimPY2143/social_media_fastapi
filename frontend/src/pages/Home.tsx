import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/common';

const Home: React.FC = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (isAuthenticated) navigate('/feed');
  }, [isAuthenticated]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center">
      <div className="text-center text-white max-w-2xl px-4">
        <h1 className="text-5xl font-bold mb-6">Welcome to SocMed</h1>
        <p className="text-xl mb-8 opacity-90">
          Connect with friends, share your thoughts, and discover what's happening in the world.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/register">
            <Button size="lg" variant="secondary">Create Account</Button>
          </Link>
          <Link to="/login">
            <Button size="lg" variant="ghost" className="text-white hover:bg-blue-700">Sign In</Button>
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-8">
          <div>
            <h3 className="text-2xl font-bold mb-2">📝</h3>
            <p>Share your thoughts with friends</p>
          </div>
          <div>
            <h3 className="text-2xl font-bold mb-2">👥</h3>
            <p>Follow interesting people</p>
          </div>
          <div>
            <h3 className="text-2xl font-bold mb-2">💬</h3>
            <p>Engage in conversations</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
