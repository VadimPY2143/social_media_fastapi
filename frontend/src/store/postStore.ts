import { create } from 'zustand';
import { Post } from '../types';
import { apiClient } from '../api/client';

interface PostStore {
  posts: Post[];
  currentPost: Post | null;
  isLoading: boolean;
  error: string | null;
  
  setPosts: (posts: Post[]) => void;
  setCurrentPost: (post: Post | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  fetchAllPosts: () => Promise<void>;
  fetchPost: (postId: number) => Promise<void>;
  createPost: (authorId: number, postName: string, text: string, file?: File) => Promise<Post>;
  updatePost: (postId: number, postName: string, text: string) => Promise<void>;
  deletePost: (postId: number) => Promise<void>;
  addPostToList: (post: Post) => void;
  removePostFromList: (postId: number) => void;
  updatePostInList: (post: Post) => void;
}

export const usePostStore = create<PostStore>((set, get) => ({
  posts: [],
  currentPost: null,
  isLoading: false,
  error: null,

  setPosts: (posts: Post[]) => {
    const sortedPosts = [...posts].sort((a, b) => (b.id ?? 0) - (a.id ?? 0));
    set({ posts: sortedPosts });
  },

  setCurrentPost: (post: Post | null) => {
    set({ currentPost: post });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  fetchAllPosts: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await apiClient.getAllPosts();
      console.log('API response:', data);
      
      let postsArray: Post[] = [];
      if (Array.isArray(data)) {
        postsArray = data;
      } else if (typeof data === 'object' && data !== null) {
        postsArray = Object.values(data).map((post: any) => ({
          id: post.id,
          post_name: post.post_name,
          author_id: post.author_id ?? post.author,
          author_username: post.author_username ?? post.author,
          text: post.text,
          picture: Boolean(post.picture),
          likes_count: post.likes_count,
          comments_count: post.comments_count,
          is_liked: post.is_liked,
        }));
      }

      const sortedPosts = postsArray.sort((a, b) => (b.id ?? 0) - (a.id ?? 0));
      set({ posts: sortedPosts, isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to fetch posts';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  fetchPost: async (postId: number) => {
    set({ isLoading: true, error: null });
    try {
      const post = await apiClient.getPost(postId);
      set({ currentPost: post, isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to fetch post';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  createPost: async (authorId: number, postName: string, text: string, file?: File) => {
    set({ isLoading: true, error: null });
    try {
      const post = await apiClient.createPost(authorId, postName, text, file);
      const newPost: Post = {
        id: post.id,
        post_name: post.post_name,
        author_id: post.author_id ?? authorId,
        author_username: post.author_username,
        text: post.text,
        picture: Boolean(post.picture),
        likes_count: post.likes_count ?? 0,
        comments_count: post.comments_count ?? 0,
        is_liked: post.is_liked ?? false,
      };
      get().addPostToList(newPost);
      set({ isLoading: false });
      return newPost;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to create post';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  updatePost: async (postId: number, postName: string, text: string) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await apiClient.updatePost(postId, postName, text);
      get().updatePostInList({
        ...updated,
        id: postId,
      });
      set({ isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to update post';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  deletePost: async (postId: number) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.deletePost(postId);
      get().removePostFromList(postId);
      set({ isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to delete post';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  addPostToList: (post: Post) => {
    const existingPosts = get().posts.filter((p) => p.id !== post.id);
    const posts = [post, ...existingPosts].sort((a, b) => (b.id ?? 0) - (a.id ?? 0));
    set({ posts });
  },

  removePostFromList: (postId: number) => {
    const posts = get().posts.filter((p) => p.id !== postId);
    set({ posts });
  },

  updatePostInList: (post: Post) => {
    const posts = get().posts.map((p) => (p.id === post.id ? post : p));
    set({ posts });
  },
}));
