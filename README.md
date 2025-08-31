# GetPlaced - Student ATS Platform

> **AI-powered resume analysis and job matching platform designed for students, recruiters, and faculty.**

GetPlaced revolutionizes the job application process through intelligent resume analysis, ATS scoring, and smart job matching using advanced NLP techniques.

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18.0+
- **Python** 3.9+
- **Git**

### 1. Clone & Setup
```bash
git clone <repository-url>
cd studentats
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Run the Application
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 5. Access the Application
- **Frontend**: http://localhost:3001
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## 🏗️ Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|----------|
| **Backend** | FastAPI | 0.104.1 | High-performance API framework |
| **Frontend** | Next.js | 14.2.5 | React framework with SSR |
| **Database** | SQLite | Default | Lightweight database (PostgreSQL optional) |
| **Authentication** | JWT | 3.3.0 | Secure token-based auth |
| **Styling** | Tailwind CSS | 3.4.1 | Utility-first CSS framework |
| **NLP** | spaCy | Latest | Natural language processing |
| **ML** | scikit-learn | Latest | Machine learning algorithms |
| **Password Hash** | Bcrypt | 1.7.4 | Secure password hashing |

## 📁 Project Structure

```
studentats/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── core/          # Config & database
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # Reusable components
│   │   └── contexts/      # React contexts
│   └── package.json       # Node dependencies
└── README.md
```

## ✨ Key Features

- **🤖 AI-Powered Resume Analysis** - Extract skills, experience, and insights
- **📊 ATS Scoring** - Real-time compatibility scoring with detailed feedback
- **🎯 Smart Job Matching** - Personalized recommendations based on resume analysis
- **👥 Role-Based Access** - Student, recruiter, and faculty dashboards
- **📄 Multi-Format Support** - PDF, DOC, DOCX, TXT resume parsing
- **🔐 Secure Authentication** - JWT-based with role management
- **📱 Responsive Design** - Modern, mobile-first interface

## 🛠️ Development

### Environment Variables
Create `.env` in backend directory:
```env
DATABASE_URL=sqlite:///./ats.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Docker Setup (Optional)
```bash
docker-compose up --build
```

## 🔧 Troubleshooting

### Common Issues

**Port Conflicts**
- Backend: Change port in uvicorn command `--port 8001`
- Frontend: Next.js will auto-detect and suggest alternative ports

**CORS Errors**
- Ensure frontend port is included in `CORS_ORIGINS` in `backend/app/core/config.py`

**Missing Dependencies**
```bash
# Backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Frontend
npm install
```

**Database Issues**
- SQLite database is created automatically
- For PostgreSQL: Update `DATABASE_URL` in `.env`

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🚀 Production Deployment

```bash
# Frontend build
cd frontend
npm run build
npm start

# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for students and developers worldwide**