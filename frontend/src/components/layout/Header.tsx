import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { PremiumButton } from '../common';
import Avatar from '../common/Avatar';

const Header: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 backdrop-blur-xl bg-gradient-to-b from-neutral-950/90 to-neutral-950/70 border-b border-purple-500/20 shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group hover:opacity-80 transition-opacity duration-300">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl blur opacity-60 group-hover:opacity-100 transition-all duration-300"></div>
            <div className="relative px-3 py-2 bg-neutral-950 rounded-xl border border-purple-500/30">
              <span className="text-xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">M</span>
            </div>
          </div>
          <span className="text-2xl font-black bg-gradient-to-r from-purple-300 via-pink-300 to-purple-300 bg-clip-text text-transparent hidden sm:block">MoodShare</span>
        </Link>

        <nav className="hidden lg:flex items-center gap-8">
          {isAuthenticated ? (
            <>
              <Link to="/feed" className="text-white/80 hover:text-white transition-colors duration-200 font-medium text-sm">Feed</Link>
              <Link to="/explore" className="text-white/80 hover:text-white transition-colors duration-200 font-medium text-sm">Explore</Link>
              <Link to="/chat" className="text-white/80 hover:text-white transition-colors duration-200 font-medium text-sm">Chat</Link>
              <Link to={`/profile/${user?.id}`} className="text-white/80 hover:text-white transition-colors duration-200 font-medium text-sm">Profile</Link>
            </>
          ) : null}
        </nav>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <Link to={`/profile/${user?.id}`} className="flex items-center gap-2.5 group/profile hover:opacity-80 transition-opacity">
                <Avatar username={user?.username || ''} userId={user?.id} size="sm" />
                <span className="hidden sm:inline text-xs font-semibold text-white group-hover/profile:text-purple-300 transition-colors">{user?.username}</span>
              </Link>
              <div className="w-px h-6 bg-purple-500/20"></div>
              <PremiumButton 
                size="sm" 
                variant="ghost" 
                onClick={handleLogout}
                className="text-xs"
              >
                Logout
              </PremiumButton>
            </>
          ) : (
            <>
              <Link to="/login">
                <PremiumButton size="sm" variant="ghost">Login</PremiumButton>
              </Link>
              <Link to="/register">
                <PremiumButton size="sm" variant="primary">Join</PremiumButton>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
