import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import { apiClient } from '../api/client';
import { useCallback } from 'react';
import Layout from '../components/layout/Layout';
import { User, FollowStats, Post } from '../types';
import { Button, Avatar, LoadingSpinner, Card, AvatarUpload } from '../components/common';
import PostCard from '../components/posts/PostCard';

const Profile: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();
  const { user: currentUser } = useAuthStore();
  const { showNotification } = useNotificationStore();
  const navigate = useNavigate();
  
  const [profileUser, setProfileUser] = useState<User | null>(null);
  const [stats, setStats] = useState<FollowStats | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [isFollowing, setIsFollowing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);

  useEffect(() => {
    if (userId) fetchProfile();
  }, [userId]);

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const user = await apiClient.getUser(parseInt(userId!));
      setProfileUser(user);
      const followStats = await apiClient.getFollowerStats(parseInt(userId!));
      setStats(followStats);
      
      if (currentUser && parseInt(userId!) !== currentUser.id) {
        const followStatus = await apiClient.checkIfFollowing(currentUser.id, parseInt(userId!));
        setIsFollowing(followStatus.is_following);
      }
      
      const userPostsData = await apiClient.getUserPosts(parseInt(userId!));
      setPosts(userPostsData.posts || []);
    } catch {
      showNotification('Failed to load profile', 'error');
      navigate('/feed');
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async () => {
    if (!currentUser || !profileUser || !stats) return;
    try {
      if (isFollowing) {
        await apiClient.unfollowUser(currentUser.id, profileUser.id);
        setIsFollowing(false);
        setStats({ ...stats, followers: stats.followers - 1 });
        showNotification(`Unfollowed ${profileUser.username}`, 'success');
      } else {
        await apiClient.followUser(currentUser.id, profileUser.id);
        setIsFollowing(true);
        setStats({ ...stats, followers: stats.followers + 1 });
        showNotification(`Now following ${profileUser.username}`, 'success');
      }
    } catch (error) {
      showNotification('Failed to update follow status', 'error');
    }
  };

  const handleAvatarUpload = useCallback(async (file: File) => {
    try {
      await apiClient.uploadUserAvatar(file);
      showNotification('Avatar updated successfully!', 'success');
      setAvatarFile(null);
      fetchProfile();
    } catch (error) {
      showNotification('Failed to update avatar', 'error');
    }
  }, [showNotification]);

  const handleDeleteAvatar = async () => {
    if (!confirm('Delete your avatar?')) return;
    try {
      await apiClient.deleteUserAvatar();
      showNotification('Avatar deleted successfully!', 'success');
      setAvatarFile(null);
      fetchProfile();
    } catch (error) {
      showNotification('Failed to delete avatar', 'error');
    }
  };

  const handleDeletePost = async (postId: number) => {
    if (!confirm('Delete this post?')) return;
    try {
      await apiClient.deletePost(postId);
      showNotification('Post deleted', 'success');
      // Wait for cache to be cleared on backend
      await new Promise(resolve => setTimeout(resolve, 200));
      fetchProfile();
    } catch (error: any) {
      showNotification(error.response?.data?.detail || 'Failed to delete post', 'error');
    }
  };

  const handleEditPost = async () => {
    // Small delay in case cache is still being cleared
    await new Promise(resolve => setTimeout(resolve, 500));
    await fetchProfile();
  };

  if (loading) return <Layout><LoadingSpinner fullScreen /></Layout>;
  if (!profileUser) return <Layout><p>User not found</p></Layout>;

  const isOwnProfile = currentUser?.id === profileUser.id;

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="mb-6">
            <div className="flex items-start gap-6">
              <div className="flex flex-col items-center">
                {isOwnProfile ? (
                  <AvatarUpload
                    username={profileUser.username}
                    userId={profileUser.id}
                    onAvatarSelected={setAvatarFile}
                    selectedFile={avatarFile}
                    showConfirmButton={true}
                    uploadFunction={handleAvatarUpload}
                  />
                ) : (
                  <Avatar username={profileUser.username} userId={profileUser.id} size="lg" />
                )}
                {isOwnProfile && (
                  <Button onClick={handleDeleteAvatar} variant="danger" size="sm" className="mt-3">
                    Delete Avatar
                  </Button>
                )}
              </div>
              <div className="flex-1">
                <h1 className="text-3xl font-bold">{profileUser.username}</h1>
                <p className="text-gray-600 mt-1">@{profileUser.username.toLowerCase()}</p>
                <div className="flex gap-6 mt-4">
                  <div>
                    <p className="text-2xl font-bold">{posts.length}</p>
                    <p className="text-gray-600 text-sm">Posts</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats?.followers || 0}</p>
                    <p className="text-gray-600 text-sm">Followers</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stats?.following || 0}</p>
                    <p className="text-gray-600 text-sm">Following</p>
                  </div>
                </div>
                {!isOwnProfile && (
                   <Button onClick={handleFollow} variant={isFollowing ? 'secondary' : 'primary'} className="mt-4">
                     {isFollowing ? 'Following' : 'Follow'}
                   </Button>
                )}
              </div>
            </div>
          </Card>

          <div>
            <h2 className="text-2xl font-bold mb-4">Posts</h2>
            {posts.length === 0 ? (
              <p className="text-gray-500">No posts yet</p>
            ) : (
              posts.map(post => (
                <PostCard 
                  key={post.id} 
                  post={post}
                  onDelete={handleDeletePost}
                  onEdit={handleEditPost}
                />
              ))
            )}
          </div>
        </div>

        <div>
          {!isOwnProfile && (
            <Card className="mb-6">
              <h3 className="font-semibold mb-3">User Info</h3>
              <p className="text-sm text-gray-600 mb-4">{profileUser.email}</p>
            </Card>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Profile;
