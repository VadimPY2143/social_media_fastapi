# Social Media Application

Created by Vadym Papusha

## Features

- User registration, login, and profiles
- Create, edit, delete posts
- Like and comment on posts
- Follow/unfollow users
- View follower and following lists
- AI-powered content moderation
- Post summarization
- Twitter tweet parsing
- Real-time notifications
- Redis caching

## Tech Stack

Backend: FastAPI, PostgreSQL, SQLAlchemy, RabbitMQ, Redis
Frontend: React 18, TypeScript, Tailwind CSS, Vite

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL
- Redis
- RabbitMQ

## Quick Start

Run everything with one command:

```bash
chmod +x start.sh
./start.sh
```

This will start:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Manual Setup

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

## Docker

```bash
docker-compose up -d
```

## Project Structure

- `/posts` - Post CRUD operations
- `/users` - User management and auth
- `/comments` - Comment system
- `/likes` - Like system
- `/followers` - Follow system
- `/frontend` - React application
- `/database_files` - Database config

## Main API Endpoints

Posts: POST/GET/PUT/DELETE `/posts/post/*`
Users: POST/GET/PUT `/users/user/*`
Followers: POST/DELETE/GET `/followers/*`
Comments: POST/GET/DELETE `/comments/*`
Likes: POST/DELETE `/likes/*`

## Author

Vadym Papusha
