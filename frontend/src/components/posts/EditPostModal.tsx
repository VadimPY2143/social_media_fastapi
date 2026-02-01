import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import { Post } from '../../types';
import { apiClient } from '../../api/client';
import { useNotificationStore } from '../../store/notificationStore';
import { PremiumButton } from '../common';

interface EditPostModalProps {
  post: Post;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedPost: Post) => void;
}

const EditPostModal: React.FC<EditPostModalProps> = ({ post, isOpen, onClose, onSave }) => {
  const [postName, setPostName] = useState(post.post_name);
  const [text, setText] = useState(post.text);
  const [isLoading, setIsLoading] = useState(false);
  const { showNotification } = useNotificationStore();

  React.useEffect(() => {
    setPostName(post.post_name);
    setText(post.text);
  }, [post, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const updatedPost = await apiClient.updatePost(post.id, postName, text);
      showNotification('Post updated. Verifying content...', 'info');
      onClose();
      
      // Wait for AI verification (3 seconds) + cache clear + buffer (1 second)
      await new Promise(resolve => setTimeout(resolve, 4000));
      
      // Trigger parent to refetch actual data from server
      onSave(post);
    } catch (error: any) {
      let errorMsg = 'Failed to update post';
      
      if (error.response?.data?.detail) {
        errorMsg = typeof error.response.data.detail === 'string' 
          ? error.response.data.detail 
          : error.response.data.detail[0]?.msg || 'Failed to update post';
      }
      
      showNotification(errorMsg, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const modalContent = (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-[9999] p-4 overflow-y-auto">
      <div className="bg-gradient-to-br from-neutral-900/95 to-neutral-950/95 backdrop-blur-xl rounded-2xl shadow-2xl shadow-purple-500/40 p-8 max-w-md w-full my-auto border border-purple-500/30">
        <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-purple-300 to-pink-300 bg-clip-text text-transparent">Edit Post</h2>
        
        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <div>
            <label className="block text-sm font-semibold text-white/90 mb-2">
              Post Title
            </label>
            <input
              type="text"
              value={postName}
              onChange={(e) => setPostName(e.target.value)}
              maxLength={20}
              className="w-full px-4 py-2.5 bg-white/5 border border-purple-500/30 hover:border-purple-500/50 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all duration-200"
              placeholder="Enter post title"
              required
            />
            <p className="text-xs text-white/60 mt-1">{postName.length}/20</p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-white/90 mb-2">
              Post Content
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              maxLength={100}
              rows={4}
              className="w-full px-4 py-2.5 bg-white/5 border border-purple-500/30 hover:border-purple-500/50 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all duration-200 resize-none"
              placeholder="Enter post content"
              required
            />
            <p className="text-xs text-white/60 mt-1">{text.length}/100</p>
          </div>

          <div className="flex gap-3 justify-end pt-4">
            <PremiumButton
              type="button"
              variant="ghost"
              size="md"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </PremiumButton>
            <PremiumButton
              type="submit"
              variant="gradient"
              size="md"
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </PremiumButton>
          </div>
        </form>
      </div>
    </div>
  );

  return ReactDOM.createPortal(modalContent, document.body);
};

export default EditPostModal;
