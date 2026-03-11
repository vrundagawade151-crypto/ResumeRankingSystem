# AI-Based Resume Screening and Ranking System

A full-stack web application for intelligent resume parsing, skill matching, and candidate ranking using NLP. Built with React, Flask, MySQL, and Python NLP libraries.

## Technology Stack

- **Frontend**: React.js (Vite)
- **Backend**: Python Flask
- **Database**: MySQL
- **AI/NLP**: NLTK, PyPDF2, python-docx for resume parsing and ranking

## Project Structure

```
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/                  # Flask API
│   ├── ai_engine/           # NLP resume parsing & ranking
│   │   ├── resume_parser.py
│   │   └── ranking_engine.py
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API endpoints
│   ├── config.py
│   ├── app.py
│   ├── run.py
│   └── requirements.txt
├── database/
│   └── schema.sql           # MySQL schema
├── uploads/                 # Resume files (created on run)
└── README.md
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- npm or yarn

## Installation

### 1. MySQL Setup

1. Install MySQL and start the service.
2. Open MySQL and create the database:

```bash
mysql -u root -p < database/schema.sql
```

Or manually:

```sql
CREATE DATABASE resume_screening_db;
USE resume_screening_db;
-- Then run the rest of schema.sql
```

3. Note your MySQL credentials (user, password, host, port).

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data (first run)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Set environment variables (or use defaults)
# Windows PowerShell
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_password"
$env:MYSQL_HOST="localhost"
$env:MYSQL_DB="resume_screening_db"

# Optional: Use SQLite for quick testing (no MySQL needed)
$env:USE_SQLITE="1"

# Run the backend
python run.py
```

Backend runs at `http://localhost:5000`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Default Credentials

- **Admin**: `admin@resumescreen.com` / `admin123`
- **Recruiter/Candidate**: Register via OTP flow (OTP is shown in response for demo)

## Usage

### Candidate Flow
1. Go to Login → Select Candidate
2. Enter email and name → Receive OTP (shown in response for demo)
3. Enter OTP → Access Candidate Dashboard
4. Browse jobs → Click Apply → Fill form + upload resume (PDF/DOCX)

### Recruiter Flow
1. Login as Recruiter (OTP)
2. Post jobs from Dashboard
3. View applicants for each job
4. Click "Extract & Rank Resumes (AI)" to run NLP screening
5. View ranked candidates by match score

### Admin Flow
1. Login as Admin (email + password)
2. View statistics, recruiters, candidates, jobs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/send-otp | Send OTP for login |
| POST | /api/auth/verify-otp | Verify OTP and get token |
| POST | /api/auth/login | Admin direct login |
| GET | /api/jobs | List all jobs (public) |
| POST | /api/jobs | Create job (recruiter) |
| POST | /api/applications | Apply for job (candidate) |
| GET | /api/applications/job/:id | Get applicants (recruiter) |
| POST | /api/ai-screening/extract | Extract & rank resumes (recruiter) |
| GET | /api/admin/statistics | Admin statistics |

## AI Ranking Formula

- **60%** Skill match (required skills vs extracted skills)
- **20%** Experience match
- **20%** Education match

## Database Schema

See `database/schema.sql` for full schema. Main tables:
- `users` - Authentication
- `candidates` - Candidate profiles
- `recruiters` - Recruiter profiles  
- `jobs` - Job postings
- `applications` - Job applications
- `resumes` - Extracted/AI-processed resume data

## Test Data

1. **Create Recruiter**: Login → Recruiter → Enter email (e.g. recruiter@test.com), name, company → Get OTP
2. **Create Job**: Recruiter Dashboard → Post New Job
3. **Create Candidate**: Login → Candidate → Register
4. **Apply**: Candidate Dashboard → Apply → Upload resume

## Troubleshooting

- **MySQL connection error**: Check MYSQL_* env vars and that MySQL is running. Or use `USE_SQLITE=1` for SQLite (no MySQL required).
- **NLTK download**: Run `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`
- **CORS**: Ensure backend allows `http://localhost:3000`
- **Resume upload fails**: Check `uploads/` folder exists and is writable

## License

MIT

## Running commands
cd backend
venv312\Scripts\activate
python app.py
