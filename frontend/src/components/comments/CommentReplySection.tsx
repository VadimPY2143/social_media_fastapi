import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { CommentReply } from '../../types';
import { apiClient } from '../../api/client';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';
import { PremiumButton } from '../common';

interface CommentReplySectionProps {
  commentId: number;
  postId: number;
  onRepliesLoaded?: (count: number) => void;
}

const CommentReplySection: React.FC<CommentReplySectionProps> = ({ commentId, postId, onRepliesLoaded }) => {
  const { user } = useAuthStore();
  const { showNotification } = useNotificationStore();
  const [replies, setReplies] = useState<CommentReply[]>([]);
  const [showReplies, setShowReplies] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (showReplies) {
      fetchReplies();
    }
  }, [showReplies]);

  const fetchReplies = async () => {
    try {
      const data = await apiClient.getCommentReplies(commentId);
      const repliesData = data.replies || [];
      setReplies(repliesData);
      onRepliesLoaded?.(repliesData.length);
    } catch {
      showNotification('Failed to load replies', 'error');
    }
  };

  const handleReply = async () => {
    if (!user || !replyText.trim()) return;

    setLoading(true);
    try {
      await apiClient.replyToComment(commentId, user.id, postId, replyText);
      setReplyText('');
      showNotification('Reply posted successfully!', 'success');
      await fetchReplies();
    } catch (error) {
      showNotification('Failed to post reply', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ml-8 mt-3 border-l-2 border-white/20 pl-3">
      <button
        onClick={() => setShowReplies(!showReplies)}
        className="text-xs text-blue-400 hover:text-blue-300 font-medium"
      >
        {showReplies ? 'Hide' : 'Show'} replies ({replies.length})
      </button>

      {showReplies && (
        <div className="mt-3 space-y-2">
          {replies.map((reply) => (
            <div key={reply.id} className="bg-neutral-800/40 p-2 rounded text-sm">
              <Link 
                to={`/profile/${reply.user_id}`}
                className="font-semibold text-white hover:text-blue-400 cursor-pointer"
              >
                {reply.user}
              </Link>
              <p className="text-white/90">{reply.text}</p>
              <p className="text-xs text-white/60 mt-1">
                {new Date(reply.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}

          {user && (
            <div className="flex gap-2 mt-3">
              <input
                type="text"
                placeholder="Write a reply..."
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                className="flex-1 px-4 py-3 border border-purple-500/20 hover:border-purple-500/40 bg-neutral-800/50 rounded-xl text-white text-sm placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all duration-200 backdrop-blur-sm"
              />
              <PremiumButton
                size="sm"
                variant="accent"
                onClick={handleReply}
                loading={loading}
                disabled={!replyText.trim()}
                className="whitespace-nowrap"
              >
                Reply
              </PremiumButton>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CommentReplySection;
