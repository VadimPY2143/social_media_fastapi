import React, { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import { apiClient } from '../api/client';
import Layout from '../components/layout/Layout';
import { Button, Input, Card, LoadingSpinner } from '../components/common';
import { Tweet } from '../types';

const Explore: React.FC = () => {
  const { user } = useAuthStore();
  const { showNotification } = useNotificationStore();
  
  const [query, setQuery] = useState('');
  const [tweets, setTweets] = useState<Record<string, Tweet>>({});
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await apiClient.searchTweets(query, 10, 'en');
      setTweets(data);
      showNotification('Tweets loaded', 'success');
    } catch {
      showNotification('Failed to load tweets', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Explore Twitter</h1>
        
        <form onSubmit={handleSearch} className="flex gap-2 mb-6">
          <Input
            placeholder="Search tweets..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1"
          />
          <Button type="submit" loading={loading}>Search</Button>
        </form>

        {loading && <LoadingSpinner />}

        <div className="space-y-4">
          {Object.values(tweets).map((tweet, idx) => (
            <Card key={idx}>
              <p className="text-sm text-gray-500 mb-2">Tweet #{tweet.post_id}</p>
              <p className="text-gray-900 mb-3">{tweet.tweet_text}</p>
              <div className="flex gap-6 text-sm text-gray-600">
                <span>❤️ {tweet.likes}</span>
                <span>📅 {tweet.created_at}</span>
              </div>
            </Card>
          ))}
        </div>

        {!loading && Object.keys(tweets).length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">Search for tweets to explore</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Explore;
