import React, { useEffect, useState } from 'react';
import { usePostStore } from '../store/postStore';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import { apiClient } from '../api/client';
import Layout from '../components/layout/Layout';
import { LoadingSpinner, Button } from '../components/common';
import CreatePostForm from '../components/posts/CreatePostForm';
import PostCard from '../components/posts/PostCard';

const Feed: React.FC = () => {
  const { posts, isLoading, fetchAllPosts } = usePostStore();
  const { user } = useAuthStore();
  const { showNotification } = useNotificationStore();

  useEffect(() => {
    fetchAllPosts();
  }, [fetchAllPosts]);

  const handleDeletePost = async (postId: number) => {
    if (!confirm('Delete this post?')) return;
    try {
      await apiClient.deletePost(postId);
      showNotification('Post deleted', 'success');
      // Wait for cache to be cleared on backend
      await new Promise(resolve => setTimeout(resolve, 200));
      await fetchAllPosts();
    } catch (error: any) {
      showNotification(error.response?.data?.detail || 'Failed to delete post', 'error');
    }
  };

  const handleEditPost = async (post: any) => {
    // Small delay in case cache is still being cleared
    await new Promise(resolve => setTimeout(resolve, 500));
    await fetchAllPosts();
  };

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CreatePostForm onPostCreated={() => fetchAllPosts()} />
          
          {isLoading && <LoadingSpinner />}
          
          {!isLoading && posts.length === 0 && (
            <div className="text-center py-20">
              <div className="text-6xl mb-4">📝</div>
              <p className="text-white text-lg font-medium">No posts yet. Be the first to share your mood!</p>
            </div>
          )}
          
          {posts.map(post => (
            <PostCard
              key={post.id}
              post={post}
              onDelete={handleDeletePost}
              onEdit={handleEditPost}
            />
          ))}
        </div>

        <div className="hidden lg:block">
          <div className="bg-neutral-900/50 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 sticky top-24 shadow-2xl hover:border-purple-500/40 transition-all duration-300">
            <h3 className="font-black text-xl mb-6 text-white uppercase tracking-wide">Trends</h3>
            {user && (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-neutral-800/50 rounded-xl border border-purple-500/20 hover:border-purple-500/40 transition-all duration-200">
                  <div>
                    <p className="font-semibold text-white">John Doe</p>
                    <p className="text-xs text-neutral-300 mt-1">@johndoe</p>
                  </div>
                  <Button size="sm">Follow</Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Feed;
