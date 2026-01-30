import React, { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';
import { useNotificationStore } from '../../store/notificationStore';

interface CommentLikeButtonProps {
  commentId: number;
  userId: number;
}

const CommentLikeButton: React.FC<CommentLikeButtonProps> = ({ commentId, userId }) => {
  const { showNotification } = useNotificationStore();
  const [likesCount, setLikesCount] = useState(0);
  const [isLiked, setIsLiked] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLikes();
  }, []);

  const fetchLikes = async () => {
    try {
      const data = await apiClient.getCommentLikesCount(commentId, userId);
      setLikesCount(data.likes_count);
      setIsLiked(data.is_liked);
    } catch {
      setLikesCount(0);
    }
  };

  const handleLike = async () => {
    setLoading(true);
    try {
      if (isLiked) {
        await apiClient.unlikeComment(userId, commentId);
        setLikesCount(likesCount - 1);
        setIsLiked(false);
      } else {
        await apiClient.likeComment(userId, commentId);
        setLikesCount(likesCount + 1);
        setIsLiked(true);
      }
    } catch (error: any) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('already liked')) {
        setIsLiked(true);
        showNotification('You already liked this comment', 'info');
      } else {
        showNotification('Failed to update like', 'error');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleLike}
      disabled={loading}
      className={`text-xs mt-2 flex items-center gap-1 hover:text-red-600 transition-colors ${
        isLiked ? 'text-red-600' : 'text-gray-500'
      }`}
    >
      ♥ {likesCount}
    </button>
  );
};

export default CommentLikeButton;
