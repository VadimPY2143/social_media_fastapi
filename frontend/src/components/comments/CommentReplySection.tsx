import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { CommentReply } from '../../types';
import { apiClient } from '../../api/client';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';
import { Button } from '../common';

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
    <div className="ml-8 mt-3 border-l-2 border-gray-200 pl-3">
      <button
        onClick={() => setShowReplies(!showReplies)}
        className="text-xs text-blue-600 hover:text-blue-700 font-medium"
      >
        {showReplies ? 'Hide' : 'Show'} replies ({replies.length})
      </button>

      {showReplies && (
        <div className="mt-3 space-y-2">
          {replies.map((reply) => (
            <div key={reply.id} className="bg-gray-50 p-2 rounded text-sm">
              <Link 
                to={`/profile/${reply.user_id}`}
                className="font-semibold text-gray-900 hover:text-blue-600 cursor-pointer"
              >
                {reply.user}
              </Link>
              <p className="text-gray-700">{reply.text}</p>
              <p className="text-xs text-gray-500 mt-1">
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
                className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <Button
                size="sm"
                onClick={handleReply}
                loading={loading}
                disabled={!replyText.trim()}
              >
                Reply
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CommentReplySection;
