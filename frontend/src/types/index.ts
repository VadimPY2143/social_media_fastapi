// User Types
export interface User {
  id: number;
  username: string;
  email: string;
  password?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UpdateUser {
  new_username?: string;
  new_email?: string;
  old_password: string;
  new_password?: string;
}

// Post Types
export interface Post {
  id: number;
  post_name: string;
  author: number | string;
  text: string;
  picture: boolean;
  picture_data?: string;
  author_username?: string;
  author_id?: number;
  likes_count?: number;
  comments_count?: number;
  is_liked?: boolean;
}

export interface PostCreate {
  post_name: string;
  text: string;
  file?: File;
}

export interface PostUpdate {
  post_name: string;
  text: string;
}

// Comment Types
export interface Comment {
  id: number;
  post_id: number;
  user: string;
  text: string;
  created_at: string;
  user_id?: number;
  likes_count?: number;
  is_liked?: boolean;
  replies_count?: number;
}

export interface CommentReply {
  id: number;
  comment_id: number;
  user: string;
  text: string;
  created_at: string;
  user_id?: number;
}

export interface CommentCreate {
  post_id: number;
  user_id: number;
  text: string;
}

export interface CommentUpdate {
  id: number;
  text: string;
}

// Chat Types
export interface ChatMessage {
  id?: number;
  chat_id: number;
  from_user_id: number;
  to_user_id?: number;
  text: string;
  has_image?: boolean;
  created_at: string;
}

export interface ChatUser {
  id: number;
  username: string;
  email: string;
}

// Follower Types
export interface Follower {
  id: number;
  username: string;
}

export interface FollowStats {
  followers: number;
  following: number;
}

export interface FollowResponse {
  user_id: number;
  followers_count?: number;
  followers?: Follower[];
  following_count?: number;
  following?: Follower[];
}

// Tweet Types
export interface TweetQuery {
  query: string;
  tweets: number;
  lang: string;
}

export interface Tweet {
  tweet_text: string;
  likes: number;
  created_at: string;
  post_id: number;
  author_id: number;
  author_name?: string;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

// Auth State
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// UI State
export interface NotificationState {
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}
