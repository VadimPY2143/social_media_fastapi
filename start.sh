#!/bin/bash

echo "🚀 Starting Social Media Application..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js is not installed. Please install Node.js 18+${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 is not installed. Please install Python 3.11+${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating one...${NC}"
    cat > .env << EOF
MYSQL=mysql+pymysql://root:root@localhost:3306/social_media
SECRET_KEY=your-secret-key-change-this-in-production
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Start Backend
echo ""
echo -e "${BLUE}Starting Backend Server (Port 8000)...${NC}"
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

uvicorn main:app --reload &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Start Frontend
echo ""
echo -e "${BLUE}Starting Frontend Server (Port 3000)...${NC}"

if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Create .env.local if it doesn't exist
if [ ! -f "frontend/.env.local" ]; then
    echo -e "${YELLOW}Creating frontend/.env.local${NC}"
    echo "VITE_API_URL=http://localhost:8000" > frontend/.env.local
fi

cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Application Started Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📱 Frontend:   ${NC}http://localhost:3000"
echo -e "${BLUE}🔧 Backend:    ${NC}http://localhost:8000"
echo -e "${BLUE}📚 API Docs:   ${NC}http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
