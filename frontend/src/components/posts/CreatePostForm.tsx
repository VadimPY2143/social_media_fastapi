import React, { useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';
import { usePostStore } from '../../store/postStore';
import { PremiumButton, Textarea, Input, Card, Avatar } from '../common';

interface CreatePostFormProps {
  onPostCreated?: () => void;
}

const CreatePostForm: React.FC<CreatePostFormProps> = ({ onPostCreated }) => {
  const [postName, setPostName] = useState('');
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const { user } = useAuthStore();
  const { showNotification } = useNotificationStore();
  const { createPost } = usePostStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setLoading(true);
    try {
      await createPost(user.id, postName, text, file || undefined);
      setPostName('');
      setText('');
      setFile(null);
      showNotification('Post created successfully!', 'success');
      onPostCreated?.();
    } catch (error: any) {
      showNotification(error.response?.data?.detail || 'Failed to create post', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mb-6">
      <div className="flex gap-4">
        <Avatar username={user?.username || 'User'} userId={user?.id} size="md" />
        <form onSubmit={handleSubmit} className="flex-1 space-y-4">
          <Input
            placeholder="Give your post a title..."
            value={postName}
            onChange={(e) => setPostName(e.target.value)}
            required
          />
          <Textarea
            placeholder="What's on your mind?"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            required
          />
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer text-blue-600 hover:text-blue-700">
              📷 Add image
              <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] || null)} className="hidden" />
            </label>
            {file && <span className="text-sm text-gray-600">{file.name}</span>}
          </div>
          <PremiumButton 
           type="submit" 
           loading={loading} 
           variant="gradient"
           size="lg"
           className="w-full"
          >
           {loading ? 'Posting...' : 'Post'}
          </PremiumButton>
        </form>
      </div>
    </Card>
  );
};

export default CreatePostForm;
