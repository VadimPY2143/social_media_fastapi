import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { Card, Input, PremiumButton, Avatar } from '../components/common';
import { apiClient } from '../api/client';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';
import { ChatMessage, ChatUser } from '../types';

const Chat: React.FC = () => {
  const { user, token } = useAuthStore();
  const { showNotification } = useNotificationStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [users, setUsers] = useState<ChatUser[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [otherUserName, setOtherUserName] = useState<string | null>(null);
  const [chatId, setChatId] = useState<number | null>(null);
  const [otherUserId, setOtherUserId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [messageText, setMessageText] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [wsStatus, setWsStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const [otherUserOnline, setOtherUserOnline] = useState<boolean | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const wsBaseUrl = useMemo(() => {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    if (apiBase.startsWith('https://')) return apiBase.replace('https://', 'wss://');
    if (apiBase.startsWith('http://')) return apiBase.replace('http://', 'ws://');
    return `ws://${apiBase}`;
  }, []);

  const apiBaseUrl = useMemo(() => {
    return import.meta.env.VITE_API_URL || 'http://localhost:8000';
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (!imageFile) {
      setImagePreview(null);
      return;
    }

    const previewUrl = URL.createObjectURL(imageFile);
    setImagePreview(previewUrl);
    return () => URL.revokeObjectURL(previewUrl);
  }, [imageFile]);

  useEffect(() => {
    if (!chatId || !token) return;

    const wsUrl = `${wsBaseUrl}/chat/ws/${chatId}?token=${encodeURIComponent(token)}`;
    setWsStatus('connecting');
    const socket = new WebSocket(wsUrl);
    wsRef.current = socket;

    socket.onopen = () => setWsStatus('connected');
    socket.onclose = () => setWsStatus('disconnected');
    socket.onerror = () => setWsStatus('disconnected');

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data?.chat_id !== chatId) return;
        if (data?.type === 'presence') {
          if (data.user_id === otherUserId) {
            setOtherUserOnline(data.status === 'online');
          }
          return;
        }
        if (data?.type === 'message') {
          const incoming: ChatMessage = {
            id: data.id,
            chat_id: data.chat_id,
            from_user_id: data.from_user_id,
            to_user_id: data.to_user_id,
            text: data.text,
            has_image: data.has_image,
            created_at: data.created_at,
          };
          setMessages((prev) => [...prev, incoming]);
        }
      } catch {
        // ignore invalid messages
      }
    };

    const heartbeat = setInterval(() => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'ping' }));
      }
    }, 20000);

    return () => {
      clearInterval(heartbeat);
      socket.close();
      wsRef.current = null;
      setWsStatus('disconnected');
    };
  }, [chatId, token, wsBaseUrl, otherUserId]);

  useEffect(() => {
    let isMounted = true;
    setIsSearching(true);
    const handle = setTimeout(async () => {
      try {
        const result = await apiClient.searchUsers(searchQuery.trim(), 30);
        if (isMounted) {
          setUsers(result.users || []);
        }
      } catch {
        if (isMounted) {
          setUsers([]);
        }
      } finally {
        if (isMounted) {
          setIsSearching(false);
        }
      }
    }, 250);

    return () => {
      isMounted = false;
      clearTimeout(handle);
    };
  }, [searchQuery]);

  const handleSelectUser = async (selectedUser: ChatUser) => {
    try {
      const result = await apiClient.createChat(selectedUser.id);
      const newChatId = result.chat_id as number;
      setChatId(newChatId);
      setOtherUserId(selectedUser.id);
      setOtherUserName(selectedUser.username);
      setOtherUserOnline(null);
      setMessages([]);

      const history = await apiClient.getChatMessages(newChatId);
      const normalized = (history.messages || []).map((msg: any) => ({
        id: msg.id,
        chat_id: msg.chat_id,
        from_user_id: msg.user_id,
        text: msg.message,
        has_image: msg.has_image,
        created_at: msg.created_at,
      }));
      setMessages(normalized.reverse());
    } catch (error: any) {
      showNotification(error.response?.data?.detail || 'Failed to start chat', 'error');
    }
  };

  const handleSendMessage = async () => {
    if (!chatId || !otherUserId || !user) return;
    const text = messageText.trim();
    if (!text && !imageFile) return;
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      showNotification('Chat connection is not ready', 'error');
      return;
    }

    let imageBase64: string | null = null;
    if (imageFile) {
      imageBase64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = () => reject(new Error('Failed to read image'));
        reader.readAsDataURL(imageFile);
      });
    }

    wsRef.current.send(
      JSON.stringify({
        to_user_id: otherUserId,
        text,
        image: imageBase64,
      })
    );

    setMessageText('');
    setImageFile(null);
  };

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
        <Card className="p-0 overflow-hidden">
          <div className="p-4 border-b border-purple-500/20 bg-neutral-900/70">
            <Input
              placeholder="Search people"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="mt-3 text-xs text-white/60">
              {isSearching ? 'Searching...' : `${users.length} results`}
            </div>
          </div>
          <div className="max-h-[580px] overflow-y-auto">
            {users.length === 0 && !isSearching && (
              <div className="py-8 text-center text-white/60 text-sm">No users found</div>
            )}
            {users.map((candidate) => {
              const isActive = candidate.id === otherUserId;
              return (
                <button
                  key={candidate.id}
                  onClick={() => handleSelectUser(candidate)}
                  className={`w-full flex items-center gap-3 px-4 py-3 border-b border-purple-500/10 text-left transition-colors ${
                    isActive ? 'bg-purple-500/15' : 'hover:bg-neutral-800/60'
                  }`}
                >

                  <Avatar username={candidate.username} userId={candidate.id} size="sm" />
                  <div className="flex-1">
                    <div className="text-sm text-white font-semibold">
                      <Link
                        to={`/profile/${candidate.id}`}
                        onClick={(event) => event.stopPropagation()}
                        className="hover:text-sky-200 transition-colors"
                      >
                        {candidate.username}
                      </Link>
                    </div>
                    <div className="text-xs text-white/50">{candidate.email}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </Card>

        <Card className="p-0 overflow-hidden flex flex-col min-h-[640px]">
          <div className="px-6 py-4 border-b border-purple-500/20 bg-neutral-900/70 flex items-center gap-3">
            {otherUserId ? (
              <>
                <Avatar username={otherUserName || 'User'} userId={otherUserId} size="sm" />
                <div className="flex-1">
                  <div className="text-white font-semibold">
                    <Link
                      to={`/profile/${otherUserId}`}
                      className="hover:text-sky-200 transition-colors"
                    >
                      {otherUserName || `User ${otherUserId}`}
                    </Link>
                  </div>
                  <div className="text-xs text-white/50">
                    {wsStatus !== 'connected'
                      ? 'Connecting...'
                      : otherUserOnline === null
                        ? 'Checking status...'
                        : otherUserOnline
                          ? 'Online'
                          : 'Offline'}
                  </div>
                </div>
                <div className="text-xs text-white/50">Chat #{chatId ?? '-'}</div>
              </>
            ) : (
              <div className="text-white/60 text-sm">Select a user to start chatting</div>
            )}
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto px-6 py-5 bg-neutral-950/60">
            {messages.length === 0 && (
              <div className="text-center text-white/60 py-10">
                {otherUserId ? 'Say hello 👋' : 'Pick a conversation to begin'}
              </div>
            )}
            {messages.map((msg, index) => {
              const isOwn = msg.from_user_id === user?.id;
              return (
                <div
                  key={`${msg.created_at}-${index}`}
                  className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] px-4 py-2.5 rounded-2xl text-sm ${
                      isOwn
                        ? 'bg-neutral-800/90 text-white border border-white/20'
                        : 'bg-neutral-900/70 text-white/80 border border-white/10'
                    }`}
                  >
                    {msg.text && <div>{msg.text}</div>}
                    {msg.has_image && msg.id && (
                      <img
                        src={`${apiBaseUrl}/chat/message/${msg.id}/image`}
                        alt="Chat upload"
                        className="mt-2 rounded-xl max-h-64 object-cover"
                      />
                    )}
                    <div className="text-[10px] opacity-70 mt-1">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={bottomRef} />
          </div>

          <div className="px-6 py-4 border-t border-purple-500/20 bg-neutral-900/70">
            <div className="flex gap-3">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                className="hidden"
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={!otherUserId}
                className="px-3 py-2 rounded-xl border border-purple-500/20 bg-neutral-800/50 text-white/80 hover:text-white hover:border-purple-500/40 transition-all disabled:opacity-60"
              >
                📷
              </button>
              <input
                type="text"
                placeholder="Message..."
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSendMessage();
                }}
                disabled={!otherUserId}
                className="flex-1 px-4 py-3 border border-purple-500/20 hover:border-purple-500/40 bg-neutral-800/50 rounded-xl text-white text-sm placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all duration-200 backdrop-blur-sm disabled:opacity-60"
              />
              <PremiumButton onClick={handleSendMessage} variant="gradient" disabled={!otherUserId}>
                Send
              </PremiumButton>
            </div>
            {imagePreview && (
              <div className="mt-3 flex items-center gap-3">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="h-16 w-16 rounded-lg object-cover border border-purple-500/20"
                />
                <button
                  type="button"
                  onClick={() => setImageFile(null)}
                  className="text-xs text-white/60 hover:text-white"
                >
                  Remove image
                </button>
              </div>
            )}
          </div>
        </Card>
      </div>
    </Layout>
  );
};

export default Chat;
