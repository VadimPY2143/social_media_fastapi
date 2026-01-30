import React, { useState } from 'react';
import { Post } from '../../types';
import { apiClient } from '../../api/client';
import { useNotificationStore } from '../../store/notificationStore';
import { Button } from '../common';

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

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-bold mb-4 text-gray-900">Edit Post</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Post Title
            </label>
            <input
              type="text"
              value={postName}
              onChange={(e) => setPostName(e.target.value)}
              maxLength={20}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter post title"
              required
            />
            <p className="text-xs text-gray-500 mt-1">{postName.length}/20</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Post Content
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              maxLength={100}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              placeholder="Enter post content"
              required
            />
            <p className="text-xs text-gray-500 mt-1">{text.length}/100</p>
          </div>

          <div className="flex gap-3 justify-end pt-4">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditPostModal;
