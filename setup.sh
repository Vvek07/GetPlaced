#!/bin/bash

# Student ATS Development Setup Script

echo "🚀 Setting up Student ATS Development Environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.9+ first."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Setup Backend
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv || python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Create uploads directory
mkdir -p uploads

# Copy environment file
if [ ! -f ".env" ]; then
    echo "Creating environment file..."
    cp .env.example .env
fi

cd ..

# Setup Frontend
echo "🎨 Setting up Frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo "🐳 Starting services with Docker..."

# Start PostgreSQL with Docker Compose
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Visit http://localhost:3000 to access the application"
echo "4. Visit http://localhost:8000/docs to access the API documentation"
echo ""
echo "🔧 Default credentials:"
echo "   Student: student@example.com / password"
echo "   Recruiter: recruiter@company.com / password"
echo "   Faculty: faculty@university.edu / password"