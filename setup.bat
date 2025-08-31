@echo off
REM Student ATS Development Setup Script for Windows

echo 🚀 Setting up Student ATS Development Environment...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    exit /b 1
)

echo ✅ Prerequisites check passed!

REM Setup Backend
echo 📦 Setting up Backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Download spaCy model
echo Downloading spaCy model...
python -m spacy download en_core_web_sm

REM Create uploads directory
if not exist "uploads" mkdir uploads

REM Copy environment file
if not exist ".env" (
    echo Creating environment file...
    copy .env.example .env
)

cd ..

REM Setup Frontend
echo 🎨 Setting up Frontend...
cd frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

cd ..

echo 🐳 Starting services with Docker...

REM Start PostgreSQL with Docker Compose
docker-compose up -d postgres

REM Wait for PostgreSQL to be ready
echo ⏳ Waiting for PostgreSQL to be ready...
timeout /t 10 /nobreak >nul

echo ✅ Setup complete!
echo.
echo 🎯 Next steps:
echo 1. Start the backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload
echo 2. Start the frontend: cd frontend ^&^& npm run dev
echo 3. Visit http://localhost:3000 to access the application
echo 4. Visit http://localhost:8000/docs to access the API documentation
echo.
echo 🔧 Default credentials:
echo    Student: student@example.com / password
echo    Recruiter: recruiter@company.com / password
echo    Faculty: faculty@university.edu / password

pause