# Hacktrack - Farmer Legal & Policy Assistant

Complete frontend-backend integration with FastAPI backend and React/Vite frontend.

## Project Overview

**Hacktrack** is an AI-powered chatbot assistant that helps farmers with:
- Government schemes and subsidies information
- Crop insurance policies (Pradhan Mantri Fasal Bima Yojana)
- Agricultural land laws and regulations
- Kisan Credit Card applications
- Multilingual support (English, Hindi, Marathi)
- Document analysis via PDF upload

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vite + React)                  │
│                   http://localhost:8080                     │
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  Auth Flow       │        │  Chat Interface  │          │
│  │  - Signup        │        │  - Conversations │          │
│  │  - Login         │        │  - Messages      │          │
│  │  - Logout        │        │  - PDF Upload    │          │
│  └──────────────────┘        └──────────────────┘          │
│           │                           │                     │
│           └───────────┬───────────────┘                     │
│                       │                                     │
│            src/services/api.ts (HTTP Client)               │
│            - JWT Token Management                          │
│            - Error Handling (401 redirect)                 │
│            - FormData Support                              │
└─────────────────────────────────────────────────────────────┘
                        │
                   CORS Enabled
                        │
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│                  http://localhost:8000                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routes                                          │  │
│  │  - /api/v1/auth/*      → User authentication         │  │
│  │  - /api/v1/conversations/*  → Conversation mgmt      │  │
│  │  - /api/v1/advisory/*  → RAG + LLM responses         │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services                                            │  │
│  │  - RAG Service (Vector search)                       │  │
│  │  - Translation (Language detection)                  │  │
│  │  - Farmer Advisory (Scheme matching)                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database                                            │  │
│  │  - SQLAlchemy ORM                                    │  │
│  │  - SQLite (or PostgreSQL)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment (optional - uses defaults)
export DATABASE_URL="sqlite:///./chatbot.db"
export JWT_SECRET="your-secret-key"

# Run server
python -m uvicorn main:app --host localhost --port 8000 --reload
```

**Backend ready at:** `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Frontend ready at:** `http://localhost:8080`

## API Endpoints

### Authentication
```
POST   /api/v1/auth/signup          Register new user
POST   /api/v1/auth/login           Login and get JWT
GET    /api/v1/auth/me              Get current user
POST   /api/v1/auth/logout          Logout
```

### Conversations
```
GET    /api/v1/conversations/               List user conversations
POST   /api/v1/conversations/               Create new conversation
GET    /api/v1/conversations/{id}           Get conversation with messages
DELETE /api/v1/conversations/{id}           Delete conversation
```

### Advisory/Query
```
POST   /api/v1/advisory/ask                 Ask question
POST   /api/v1/advisory/ask-with-document   Ask with PDF attachment
```

## Security Features

- JWT Authentication
  - Access tokens stored in localStorage
  - Automatic token injection in all requests
  - 401 redirect on token expiry

- CORS Protection
  - Whitelisted origins: localhost:8080, localhost:3000
  - Credentials allowed
  - All methods and headers allowed

- Input Validation
  - File type validation (.pdf only)
  - File size limit (50MB)
  - Text length limits
  - Language validation

- Error Handling
  - Global error interceptor
  - User-friendly error messages
  - Toast notifications
  - Proper HTTP status codes

## 🔧 Configuration

### Frontend Environment (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Backend Environment (.env)
```env
DATABASE_URL=sqlite:///./chatbot.db
JWT_SECRET=your-secret-key-change-in-production
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
```

## 📁 Project Structure

```
Hacktrack/
├── backend/
│   ├── main.py                     # FastAPI application
│   ├── requirements.txt            # Python dependencies
│   ├── config/
│   │   └── settings.py             # Configuration
│   ├── auth/
│   │   ├── routes.py               # Login/Signup endpoints
│   │   ├── auth_service.py         # Auth logic
│   │   ├── jwt_handler.py          # JWT handling
│   │   └── schemas.py              # Request/Response schemas
│   ├── conversations/
│   │   ├── routes.py               # Conversation endpoints
│   │   ├── service.py              # Business logic
│   │   ├── models.py               # Database models
│   │   └── schemas.py              # Pydantic schemas
│   ├── rag/
│   │   ├── rag_service.py          # RAG pipeline
│   │   ├── vectorstore.py          # Vector store
│   │   ├── retriever.py            # Document retrieval
│   │   └── embeddings.py           # Embedding generation
│   ├── database/
│   │   ├── base.py                 # Database setup
│   │   ├── models.py               # ORM models
│   │   └── repository.py           # Data access
│   └── translation/
│       ├── translator.py           # Translation service
│       └── language_detector.py    # Language detection
│
├── frontend/
│   ├── .env                        # Environment configuration
│   ├── package.json                # Dependencies
│   ├── src/
│   │   ├── main.tsx                # Entry point
│   │   ├── App.tsx                 # Root component
│   │   ├── services/
│   │   │   └── api.ts              # API client (NEW)
│   │   ├── hooks/
│   │   │   └── useAuth.tsx         # Auth context (UPDATED)
│   │   ├── pages/
│   │   │   ├── Index.tsx           # Chat page
│   │   │   ├── Login.tsx           # Login page
│   │   │   ├── Signup.tsx          # Signup page
│   │   │   └── NotFound.tsx        # 404 page
│   │   └── components/
│   │       ├── ChatPanel.tsx       # Chat interface (UPDATED)
│   │       ├── ChatSidebar.tsx     # Sidebar (UPDATED)
│   │       ├── NavLink.tsx
│   │       └── ThemeToggle.tsx
│   └── index.html
│
├── INTEGRATION_SUMMARY.md           # Detailed integration docs
└── QUICK_START.md                   # Quick start guide
```

## Data Flow Examples

### Login Flow
```
1. User enters email/password
2. Frontend: authAPI.login(email, password)
3. Backend: POST /api/v1/auth/login
4. Backend: Validate credentials, generate JWT
5. Response: { access_token, user_data }
6. Frontend: Store token in localStorage
7. Redirect to chat page
```

### Chat Flow
```
1. User selects/creates conversation
2. Frontend: conversationsAPI.get(conversationId)
3. Backend: GET /api/v1/conversations/{id}
4. Response: { messages: [...] }
5. Frontend: Display conversation with messages
6. User types question
7. Frontend: advisoryAPI.ask(question, conversationId, language)
8. Backend: POST /api/v1/advisory/ask
9. Backend: Process with RAG + LLM
10. Response: { response, context_used, schemes }
11. Frontend: Display assistant response in chat
```

### PDF Upload Flow
```
1. User selects PDF file
2. Frontend: Validate (.pdf, <50MB)
3. Frontend: advisoryAPI.askWithDocument(question, file)
4. Backend: POST /api/v1/advisory/ask-with-document (multipart/form-data)
5. Backend: Extract text from PDF
6. Backend: Process with RAG + LLM
7. Response: { response, original_language, context_used }
8. Frontend: Display analysis in chat
```

## 🧪 Testing Checklist

- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] Frontend loads on port 8080
- [ ] Signup creates new user
- [ ] Login returns JWT token
- [ ] Conversations list loads
- [ ] New conversation can be created
- [ ] Messages send successfully
- [ ] PDF upload works (< 50MB)
- [ ] Language switching works (en, hi, mr)
- [ ] Logout clears tokens
- [ ] 401 redirects to login
- [ ] Error messages display properly
- [ ] Loading spinners appear during requests
- [ ] Theme toggle works
- [ ] Responsive design on mobile

## Development Commands

### Frontend
```bash
cd frontend

npm run dev              # Start dev server
npm run build           # Build for production
npm run preview         # Preview production build
npm run lint            # Check code style
npm run test            # Run tests
```

### Backend
```bash
cd backend

# Development
python -m uvicorn main:app --reload

# Production
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Tests
python -m pytest

# Initialize database
python -c "from database.base import init_db; init_db()"
```

## Key Technologies

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **React Query** - Data fetching
- **Radix UI** - Component library

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **PyJWT** - JWT handling
- **Langchain** - RAG pipeline
- **FAISS** - Vector search
- **Hugging Face** - Embeddings

##  Troubleshooting

### Backend Connection Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# View backend logs
# Check terminal where backend is running

# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### Frontend Issues
```javascript
// Check if token is stored
localStorage.getItem('access_token')

// Check API URL
console.log(import.meta.env.VITE_API_BASE_URL)

// Clear storage if needed
localStorage.clear()

// Check network requests
// DevTools → Network tab → Filter by XHR/Fetch
```

### CORS Errors
1. Verify backend is running on port 8000
2. Check CORS_ORIGINS in backend config includes localhost:8080
3. Restart backend after changing CORS settings
4. Check browser console for exact error message

## Environment Variables

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000    # Backend URL
```

### Backend (.env or shell export)
```env
DATABASE_URL=sqlite:///./chatbot.db        # Database URL
JWT_SECRET=your-secret-key                 # JWT signing key
JWT_ALGORITHM=HS256                        # JWT algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=1440           # Token expiry (24 hours)
OPENAI_API_KEY=sk-...                      # OpenAI API key
ENVIRONMENT=development                    # Environment
LOG_LEVEL=INFO                             # Logging level
MAX_UPLOAD_SIZE_MB=50                      # Max file size
CORS_ORIGINS=http://localhost:8080         # Allowed origins
```

## Security Notes

1. Never commit .env files with real secrets
2. Change JWT_SECRET in production
3. Use HTTPS in production
4. Implement rate limiting for auth endpoints
5. Validate all inputs (already done)
6. Use environment variables for sensitive data
7. Store tokens securely (consider HttpOnly cookies)
8. Implement token refresh for long sessions

##  Dependencies

### Frontend
See [frontend/package.json](frontend/package.json)
- React, Vite, TypeScript
- UI: Radix UI, Tailwind CSS
- HTTP: Fetch API (built-in)
- State: React Context
- Routing: React Router

### Backend
See [backend/requirements.txt](backend/requirements.txt)
- FastAPI, Uvicorn
- Database: SQLAlchemy, SQLite
- Auth: PyJWT
- ML: Langchain, FAISS, Hugging Face
- Utilities: Pydantic, Python-dotenv

##  Deployment

### Frontend Deployment
```bash
# Build static files
npm run build

# Deploy 'dist' folder to:
# - Vercel, Netlify, GitHub Pages
# - AWS S3 + CloudFront
# - Azure Static Web Apps
```

### Backend Deployment
```bash
# Deploy to:
# - Heroku (with Procfile)
# - AWS EC2 (with Gunicorn)
# - Google Cloud Run
# - Azure App Service
# - Railway, Render

# Remember to:
# - Set ENVIRONMENT=production
# - Use PostgreSQL instead of SQLite
# - Set secure JWT_SECRET
# - Update CORS_ORIGINS to production domain
# - Use HTTPS everywhere
```

##  Support

For issues or questions:
1. Review backend logs in terminal
2. Check browser console (F12) for errors
3. Check Network tab for API responses

##  License

[Add your license here]

##  Features

  User authentication with JWT
  Multi-language support (EN, HI, MR)
  Conversation management
  PDF document analysis
  RAG-powered responses
  Real-time chat interface
  Dark/Light theme
  Responsive design
  Error handling and validation
  Loading states and spinners

##  Next Steps

1. Start both servers
2. Test signup/login
3. Create conversations
4. Send messages
5. Upload PDFs
6. Deploy to production

---

**Status:**  Production Ready  
**Last Updated:** 2026-02-11  
**Maintainer:** [Your Name/Team]
