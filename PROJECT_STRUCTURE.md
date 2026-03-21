# ✨ Project Structure - After Cleanup

## 📂 Root Directory
```
Demo AutoDataAnalytics/
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md                # Quick start guide  
├── 📄 DEPLOYMENT.md                # Deployment guide
├── 📄 GOOGLE_API_KEY_GUIDE.md      # API setup instructions
├── 📄 CLEANUP_PLAN.md              # This cleanup plan
├── 📄 .gitignore                   # Git ignore rules
├── 🔧 setup.bat                    # Initial setup script
├── 🔧 start-backend.bat            # Start backend server
├── 🔧 start-frontend.bat           # Start frontend server
├── 🔧 cleanup.bat                  # Cleanup script
│
├── 📁 backend/                     # Backend application
│   ├── 📄 main.py                  # Main FastAPI app
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 .env                     # Environment variables
│   ├── 📄 .env.template            # Environment template
│   ├── 📄 analytix.db              # SQLite database
│   ├── 📁 .venv/                   # Python virtual environment
│   ├── 📁 auth/                    # Authentication module
│   ├── 📁 database/                # Database connections
│   ├── 📁 services/                # Core business logic
│   │   ├── 📁 chat/                # AI chat service
│   │   ├── 📁 employee/            # Employee domain
│   │   ├── 📁 finance/             # Finance domain
│   │   ├── 📁 sales/               # Sales domain
│   │   ├── 📁 student/             # Student domain
│   │   └── 📄 field_service.py     # Field orchestrator
│   ├── 📁 utils/                   # Utility functions
│   ├── 📁 charts/                  # Generated visualizations
│   └── 📁 reports/                 # Generated PDF reports
│
├── 📁 frontend/                    # Frontend application
│   ├── 📄 index_v2.html            # Main HTML (current)
│   ├── 📄 script_v2.js             # Main JavaScript (current)
│   ├── 📄 style_v2.css             # Main CSS (current)
│   ├── 📄 style_v2_additions.css   # Additional styles
│   └── 📄 style_v2_settings.css    # Settings styles
│
├── 📁 AnalytixAI Data/             # Sample datasets
│   ├── 📄 student_domain.csv
│   ├── 📄 employee_domain.csv
│   ├── 📄 sales_domain.csv
│   └── 📄 finance_domain.csv
│
└── 📁 master data/                 # Master datasets
    ├── 📄 Student_Data_874rows.csv
    ├── 📄 Employee_Data_909rows.csv
    ├── 📄 Sales_Data_690rows.csv
    └── 📄 Finance_Data_1370rows.csv
```

## 🗂️ Key Components

### Backend Services
- **Authentication** (`auth/`) - User registration, login, JWT
- **Chat Service** (`services/chat/`) - AI-powered data analysis chat
- **Domain Services** (`services/{domain}/`) - Specialized logic for each data domain
  - Analytics - Statistical analysis
  - Cleaning - Data preprocessing
  - ML Model - Machine learning insights
  - Visuals - Chart generation
- **Field Service** - Orchestrates all domain operations
- **Report Service** - PDF report generation

### Frontend
- **V2 Files** (current version)
  - `index_v2.html` - Main UI
  - `script_v2.js` - Application logic
  - `style_v2.css` - Main styles
- **Features**
  - Data upload & preview
  - Domain selection (Student/Employee/Sales/Finance)
  - Analytics visualization
  - AI chat interface
  - Report generation
  - User authentication

## 📊 Data Flow
1. **Upload** → Frontend sends CSV to backend
2. **Cleaning** → Domain-specific data cleaning
3. **Analysis** → Statistical analysis + ML insights
4. **Visualization** → Chart generation (3 per domain)
5. **Chat** → AI-powered Q&A using Gemini API
6. **Report** → PDF generation with insights

## 🚀 Quick Start
```bash
# 1. Setup (first time only)
setup.bat

# 2. Start backend
start-backend.bat

# 3. Start frontend (in new terminal)
start-frontend.bat

# 4. Open browser
http://localhost:5500/index_v2.html
```

## 🧹 Maintenance
- **Cleanup**: Run `cleanup.bat` to remove temporary files
- **Charts**: Auto-regenerated on each upload
- **Reports**: Stored in `backend/reports/`
- **Logs**: Check `backend/logs/` for errors

## ⚙️ Configuration
- **Backend**: `backend/.env` - API keys, database, JWT
- **Frontend**: No configuration needed
- **API Keys**: See `GOOGLE_API_KEY_GUIDE.md`

## 📖 Documentation
- `README.md` - Project overview
- `QUICKSTART.md` - Getting started guide
- `DEPLOYMENT.md` - Deployment instructions
- `GOOGLE_API_KEY_GUIDE.md` - API setup

---

**Last Updated**: After cleanup (43 unnecessary files removed)
