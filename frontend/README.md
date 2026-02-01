# SocMed Frontend

A modern React/TypeScript frontend for the Social Media FastAPI application.

## Features

- User Authentication (Login/Register)
-  Create, Read, Update, Delete Posts
-  Like Posts & Comments
-  Add Comments to Posts
-  User Profiles & Follow System
-  Twitter Integration & Search
-  Responsive Design with Tailwind CSS
-  State Management with Zustand
-  Type-safe with TypeScript

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local`:
```bash
VITE_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Project Structure

```
src/
├── api/              # API client
├── components/       # Reusable UI components
│   ├── common/      # Common components (Button, Input, etc.)
│   ├── layout/      # Layout components (Header, etc.)
│   └── posts/       # Post components
├── pages/           # Page components
├── store/           # Zustand stores (auth, posts, notifications)
├── types/           # TypeScript types
├── utils/           # Helper functions
├── App.tsx          # Main app component
└── main.tsx         # Entry point
```

## Available Pages

- `/` - Home
- `/login` - User login
- `/register` - User registration
- `/feed` - Posts feed
- `/profile/:userId` - User profile
- `/explore` - Twitter search

## API Integration

All API calls are handled through `src/api/client.ts`. The client automatically:
- Manages JWT token in localStorage
- Adds Authorization headers
- Handles 401 responses
- Provides type-safe methods for all endpoints

## State Management

Stores are managed with Zustand:
- `authStore` - User authentication state
- `postStore` - Posts data and operations
- `notificationStore` - Toast notifications

## Technologies

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand (state management)
- Axios (HTTP client)
- React Router (routing)
