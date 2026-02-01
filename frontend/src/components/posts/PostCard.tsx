import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Post, Comment } from '../../types';
import { apiClient } from '../../api/client';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';
import { formatDate } from '../../utils/helpers';
import { Card, Avatar, PremiumButton } from '../common';
import { CommentReplySection, CommentLikeButton } from '../comments';
import EditPostModal from './EditPostModal';

interface PostCardProps {
  post: Post;
  onDelete?: (postId: number) => void;
  onEdit?: (post: Post) => void;
}

const PostCard: React.FC<PostCardProps> = ({ post, onDelete, onEdit }) => {
  const { user } = useAuthStore();
  const { showNotification } = useNotificationStore();
  const [likesCount, setLikesCount] = useState(0);
  const [isLiked, setIsLiked] = useState(false);
  const [commentsCount, setCommentsCount] = useState(0);
  const [comments, setComments] = useState<Comment[]>([]);
  const [showComments, setShowComments] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [currentPost, setCurrentPost] = useState(post);
  const [summarizedText, setSummarizedText] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchLikes();
    fetchComments();
  }, []);

  const fetchLikes = async () => {
    try {
      const data = await apiClient.getPostLikesCount(post.id, user?.id);
      setLikesCount(data.likes_count);
      setIsLiked(data.is_liked);
    } catch {
      setLikesCount(0);
    }
  };

  const fetchComments = async () => {
    try {
      const data = await apiClient.getCommentsByPost(post.id);
      setComments(data.comments || []);
      setCommentsCount(data.comments?.length || 0);
    } catch {
      setCommentsCount(0);
    }
  };

  const handleLike = async () => {
    if (!user) return;
    try {
      if (isLiked) {
        await apiClient.unlikePost(user.id, post.id);
        setLikesCount(likesCount - 1);
        setIsLiked(false);
      } else {
        await apiClient.likePost(user.id, post.id);
        setLikesCount(likesCount + 1);
        setIsLiked(true);
      }
    } catch (error: any) {
      if (error.response?.status === 400 && error.response?.data?.detail?.includes('already liked')) {
        setIsLiked(true);
        showNotification('You already liked this post', 'info');
      } else {
        showNotification('Failed to update like', 'error');
      }
    }
  };

  const canEdit = user?.id === post.author_id;

  const handleEditClick = () => {
    setIsEditModalOpen(true);
  };

  const handleEditSave = (updatedPost: Post) => {
    setCurrentPost(updatedPost);
    onEdit?.(updatedPost);
    setIsEditModalOpen(false);
  };

  const handleDelete = () => {
    onDelete?.(post.id);
  };

  const handleSummarize = async () => {
    if (summarizedText) {
      setSummarizedText(null);
      return;
    }

    try {
      setIsLoading(true);
      const result = await apiClient.summarizePost(post.id);
      setSummarizedText(result.summary || result);
      showNotification('Post summarized', 'success');
    } catch (error: any) {
      showNotification(error.response?.data?.detail || 'Failed to summarize post', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const textLength = currentPost.text.length;
  const shouldShowSummarizeBtn = textLength > 500;

  return (
    <Card className="mb-4">
      <div className="flex items-start gap-4">
        <Link to={`/profile/${post.author_id}`}>
          <Avatar username={post.author_username || 'User'} userId={post.author_id} size="md" />
        </Link>
        <div className="flex-1">
          <div className="flex items-start justify-between">
            <div>
              <Link 
                to={`/profile/${post.author_id}`}
                className="font-semibold text-white hover:text-blue-400 cursor-pointer"
              >
                {post.author_username}
              </Link>
              <p className="text-sm text-white/60">{formatDate(new Date().toISOString())}</p>
            </div>
            {canEdit && (
              <div className="flex gap-2">
                <PremiumButton size="sm" variant="ghost" onClick={handleEditClick}>Edit</PremiumButton>
                <PremiumButton size="sm" variant="secondary" onClick={handleDelete}>Delete</PremiumButton>
              </div>
            )}
          </div>
          
          <h2 className="mt-3 text-lg font-semibold text-white">{currentPost.post_name}</h2>
          <p className="mt-2 text-white/90">{summarizedText ? summarizedText : currentPost.text}</p>
          {shouldShowSummarizeBtn && (
            <button
              onClick={handleSummarize}
              disabled={isLoading}
              className="mt-2 text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Summarizing...' : (summarizedText ? 'Show Full' : 'Summarize')}
            </button>
          )}
          
          {post.picture && !imageError && (
            <div className="mt-3 bg-gray-100 rounded-lg flex items-center justify-center max-w-md">
              <img 
                src={`http://localhost:8000/posts/post/${post.id}/image`} 
                alt="Post Image" 
                className="w-full h-auto max-h-96 object-contain rounded-lg" 
                onError={() => setImageError(true)}
              />
            </div>
          )}

          <div className="mt-4 flex items-center gap-6 text-white/70 text-sm">
            <button onClick={handleLike} className={`flex items-center gap-1 hover:text-blue-400 ${isLiked ? 'text-blue-400' : ''}`}>
              ♥ {likesCount}
            </button>
            <button onClick={() => setShowComments(!showComments)} className="flex items-center gap-1 hover:text-blue-400">
              💬 {commentsCount}
            </button>
            <button className="flex items-center gap-1 hover:text-blue-400">
              ↗ Share
            </button>
          </div>

          {showComments && (
            <CommentSection postId={post.id} comments={comments} onRefresh={fetchComments} />
          )}
          </div>
          </div>

          <EditPostModal
          post={currentPost}
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          onSave={handleEditSave}
          />
          </Card>
          );
          };

const CommentSection: React.FC<{postId: number; comments: Comment[]; onRefresh: () => void}> = ({postId, comments, onRefresh}) => {
  const { user } = useAuthStore();
  const [commentText, setCommentText] = useState('');
  const { showNotification } = useNotificationStore();

  const handleAddComment = async () => {
    if (!user || !commentText.trim()) return;
    try {
      await apiClient.createComment(postId, user.id, commentText);
      setCommentText('');
      onRefresh();
      showNotification('Comment added', 'success');
    } catch {
      showNotification('Failed to add comment', 'error');
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Delete this comment?')) return;
    try {
      await apiClient.deleteComment(commentId);
      onRefresh();
      showNotification('Comment deleted', 'success');
    } catch {
      showNotification('Failed to delete comment', 'error');
    }
  };

  return (
    <div className="mt-4 border-t border-white/20 pt-4">
      <div className="space-y-3 mb-3 max-h-48 overflow-y-auto">
        {comments.map(c => (
          <div key={c.id}>
            <div className="bg-neutral-800/40 p-3 rounded">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <Link 
                    to={`/profile/${c.user_id}`}
                    className="font-sm font-semibold text-white hover:text-blue-400 cursor-pointer"
                  >
                    {c.user}
                  </Link>
                  <p className="text-sm text-white/90">{c.text}</p>
                  <p className="text-xs text-white/60 mt-1">
                    {new Date(c.created_at).toLocaleDateString()}
                  </p>
                </div>
                {user?.id === c.user_id && (
                  <button
                    onClick={() => handleDeleteComment(c.id)}
                    className="text-xs text-red-400 hover:text-red-300 ml-2"
                  >
                    Delete
                  </button>
                )}
              </div>
              {user && (
                <CommentLikeButton commentId={c.id} userId={user.id} />
              )}
            </div>
            <CommentReplySection commentId={c.id} postId={postId} />
          </div>
        ))}
      </div>
      {user && (
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Add a comment..."
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
            className="flex-1 px-4 py-3 border border-purple-500/20 hover:border-purple-500/40 bg-neutral-800/50 rounded-xl text-white text-sm placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all duration-200 backdrop-blur-sm"
          />
          <PremiumButton size="sm" onClick={handleAddComment}>Post</PremiumButton>
        </div>
      )}
    </div>
  );
};

export default PostCard;
