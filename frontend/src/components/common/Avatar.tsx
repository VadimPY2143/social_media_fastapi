import React, { useState, useEffect } from 'react';
import { getInitials } from '../../utils/helpers';

interface AvatarProps {
  username: string;
  userId?: number;
  size?: 'sm' | 'md' | 'lg';
}

const Avatar: React.FC<AvatarProps> = ({ username = 'User', userId, size = 'md' }) => {
  const [hasAvatar, setHasAvatar] = useState(false);
  const [imageError, setImageError] = useState(false);
  
  const sizes = { sm: 'w-8 h-8 text-xs', md: 'w-10 h-10 text-sm', lg: 'w-12 h-12 text-lg' };
  const colors = ['bg-blue-500', 'bg-green-500', 'bg-red-500', 'bg-purple-500', 'bg-yellow-500'];
  const color = colors[(username || 'U').charCodeAt(0) % colors.length];

  useEffect(() => {
    if (userId) {
      // Try to fetch avatar, if 404 it means no avatar
      setHasAvatar(true);
    }
  }, [userId]);

  const getInitial = () => (username || 'U').charAt(0).toUpperCase();

  // If we have userId and avatar hasn't failed to load, try to show image
  if (userId && hasAvatar && !imageError) {
    return (
      <img
        src={`http://localhost:8000/users/user/${userId}/avatar`}
        alt={username}
        className={`${sizes[size]} rounded-full object-cover`}
        onError={() => setImageError(true)}
      />
    );
  }

  // Fallback to initial with background color
  return (
    <div className={`${sizes[size]} ${color} rounded-full flex items-center justify-center text-white font-bold`}>
      {getInitial()}
    </div>
  );
};

export default Avatar;
