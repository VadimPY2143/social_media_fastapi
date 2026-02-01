import axios, { AxiosInstance, AxiosError } from 'axios';
import { Token, ApiResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load token from localStorage on initialization
    this.token = localStorage.getItem('access_token');
    if (this.token) {
      this.setAuthHeader(this.token);
    }

    // Response interceptor for handling 401
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  setAuthHeader(token: string) {
    this.token = token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  clearAuth() {
    this.token = null;
    delete this.client.defaults.headers.common['Authorization'];
  }

  // Auth endpoints
  async register(username: string, email: string, password: string) {
    const response = await this.client.post('/users/user/create', {
      username,
      email,
      password,
    });
    return response.data;
  }

  async login(email: string, password: string): Promise<Token> {
    const response = await this.client.post('/users/user/login', {
      email,
      password,
    });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/users/user/me');
    return response.data;
  }

  async getUser(userId: number) {
    const response = await this.client.get(`/users/user/${userId}`);
    return response.data;
  }

  async updateUser(updateData: any) {
    const response = await this.client.put('/users/user/update', updateData);
    return response.data;
  }

  async deleteUser() {
    const response = await this.client.delete('/users/user/delete');
    return response.data;
  }

  async registerWithAvatar(username: string, email: string, password: string, avatar?: File) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('email', email);
    formData.append('password', password);
    if (avatar) {
      formData.append('avatar', avatar);
    }

    const response = await axios.post(
      `${API_BASE_URL}/users/user/create`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async uploadUserAvatar(avatar: File) {
    const formData = new FormData();
    formData.append('avatar', avatar);

    const response = await axios.put(
      `${API_BASE_URL}/users/user/avatar`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  }

  async deleteUserAvatar() {
    const response = await axios.delete(
      `${API_BASE_URL}/users/user/avatar`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      }
    );
    return response.data;
  }

  // Posts endpoints
  async createPost(authorId: number, postName: string, text: string, file?: File) {
    const formData = new FormData();
    formData.append('post_name', postName);
    formData.append('text', text);
    if (file) {
      formData.append('file', file);
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}/posts/post/create/${authorId}`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${this.token}`,
          },
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('Create post error:', error.response?.data || error.message);
      throw error;
    }
  }

  async getPost(postId: number) {
    const response = await this.client.post('/posts/post/get', null, {
      params: { post_id: postId },
    });
    return response.data;
  }

  async getAllPosts() {
    const response = await this.client.get('/posts/post/get_all');
    return response.data;
  }

  async getUserPosts(userId: number) {
    const response = await this.client.get(`/posts/post/${userId}`);
    return response.data;
  }

  async updatePost(postId: number, postName: string, text: string) {
    const formData = new FormData();
    formData.append('post_name', postName);
    formData.append('text', text);

    const response = await axios.put(
      `${API_BASE_URL}/posts/post/update/${postId}`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      }
    );
    return response.data;
  }

  async deletePost(postId: number) {
    const response = await axios.delete(
      `${API_BASE_URL}/posts/post/delete/${postId}`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      }
    );
    return response.data;
  }

  // Comments endpoints
  async createComment(postId: number, userId: number, text: string) {
    const formData = new FormData();
    formData.append('text', text);
    
    const response = await axios.post(
      `${API_BASE_URL}/comments/${postId}/${userId}`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      }
    );
    return response.data;
  }

  async getCommentsByPost(postId: number) {
    const response = await this.client.get(`/comments/post/${postId}`);
    return response.data;
  }

  async getComment(commentId: number) {
    const response = await this.client.get(`/comments/${commentId}`);
    return response.data;
  }

  async updateComment(commentId: number, text: string) {
    const response = await this.client.put(`/comments/${commentId}`, {
      id: commentId,
      text,
    });
    return response.data;
  }

  async deleteComment(commentId: number) {
    const response = await this.client.delete(`/comments/${commentId}`);
    return response.data;
  }

  async replyToComment(commentId: number, userId: number, postId: number, text: string) {
    const response = await axios.post(
      `${API_BASE_URL}/comments/${commentId}`,
      {
        post_id: postId,
        user_id: userId,
        text: text,
      },
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  }

  async getCommentReplies(commentId: number) {
    const response = await this.client.get(`/comments/${commentId}/replies`);
    return response.data;
  }

  // Likes endpoints
  async likePost(userId: number, postId: number) {
    const response = await this.client.post(`/likes/post/like/${userId}/${postId}`);
    return response.data;
  }

  async unlikePost(userId: number, postId: number) {
    const response = await this.client.delete(`/likes/post/unlike/${userId}/${postId}`);
    return response.data;
  }

  async getPostLikesCount(postId: number, userId?: number) {
    const response = await this.client.get('/likes/post/count', {
      params: { post_id: postId, user_id: userId },
    });
    return response.data;
  }

  async likeComment(userId: number, commentId: number) {
    const response = await this.client.post(`/likes/comment/like/${userId}/${commentId}`);
    return response.data;
  }

  async unlikeComment(userId: number, commentId: number) {
    const response = await this.client.delete(`/likes/comment/unlike/${userId}/${commentId}`);
    return response.data;
  }

  async getCommentLikesCount(commentId: number, userId?: number) {
    const response = await this.client.get('/likes/comment/count', {
      params: { comment_id: commentId, user_id: userId },
    });
    return response.data;
  }

  // Followers endpoints
  async followUser(followerId: number, followingId: number) {
    const response = await this.client.post('/followers/follow', {
      follower_id: followerId,
      following_id: followingId,
    });
    return response.data;
  }

  async unfollowUser(followerId: number, followingId: number) {
    const response = await this.client.delete(
      `/followers/unfollow/${followerId}/${followingId}`
    );
    return response.data;
  }

  async getFollowers(userId: number) {
    const response = await this.client.get(`/followers/${userId}`);
    return response.data;
  }

  async getFollowing(userId: number) {
    const response = await this.client.get(`/followers/following/${userId}`);
    return response.data;
  }

  async getFollowerStats(userId: number) {
    const response = await this.client.get(`/followers/stats/${userId}`);
    return response.data;
  }

  async checkIfFollowing(followerId: number, followingId: number) {
    try {
      const response = await this.client.get(`/followers/check/${followerId}/${followingId}`);
      return response.data;
    } catch {
      return { is_following: false };
    }
  }

  async summarizePost(postId: number) {
    const response = await this.client.get(`/posts/post/summary/${postId}`);
    return response.data;
  }

  async searchTweets(query: string, tweets: number = 10, lang: string = 'en') {
    const response = await this.client.get('/twitter/tweet/get', {
      params: { query, tweets, lang },
    });
    return response.data;
  }
}

export const apiClient = new ApiClient();
