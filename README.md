# 📊 AnalytixAI - Automated Data Analytics Platform

A powerful full-stack data analytics application that automatically analyzes Excel/CSV files across multiple business domains (Sales, Finance, Student, Employee) and generates insightful visualizations and reports.

## 🌟 Features

- **Multi-Domain Support**: Analyze Sales, Finance, Student, or Employee data
- **Automatic Data Cleaning**: Handles missing values, duplicates, and data type conversions
- **Smart Analytics**: Generates domain-specific insights and statistics
- **Beautiful Visualizations**: Creates interactive charts using Matplotlib and Seaborn
- **User Authentication**: Secure JWT-based authentication system
- **Modern UI**: Responsive design with glassmorphism effects and dark/light themes
- **Real-time Processing**: Fast data processing and analysis pipeline

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **MongoDB** - NoSQL database for user data
- **Pandas** - Data manipulation and analysis
- **Matplotlib/Seaborn** - Data visualization
- **JWT** - Secure authentication
- **Python 3.8+**

### Frontend
- **HTML5/CSS3** - Modern web standards
- **JavaScript (ES6+)** - Interactive functionality
- **Glassmorphism UI** - Premium design aesthetic
- **Responsive Design** - Mobile-first approach

## 📁 Project Structure

```
Demo AutoDataAnalytics/
├── backend/
│   ├── auth/              # Authentication modules
│   ├── database/          # MongoDB connection
│   ├── services/          # Domain-specific services
│   │   ├── sales/         # Sales data processing
│   │   ├── finance/       # Finance data processing
│   │   ├── student/       # Student data processing
│   │   └── employee/      # Employee data processing
│   ├── utils/             # Utility functions
│   ├── charts/            # Generated chart images
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   ├── .env               # Environment variables (DO NOT COMMIT)
│   └── .env.template      # Environment template
│
└── frontend/
    ├── index.html         # Main HTML file
    ├── style.css          # Styling
    └── script.js          # Frontend logic
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB)
- Modern web browser

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.template` to `.env`
   - Update the values in `.env`:
     ```env
     MONGO_URL=your_mongodb_connection_string
     DB_NAME=analytixai
     SECRET_KEY=your_secret_key_here
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
     ```

5. **Run the backend server**
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

   The API will be available at: `http://127.0.0.1:8000`
   
   API Documentation: `http://127.0.0.1:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Update API URL (if needed)**
   - Open `script.js`
   - Ensure `API_BASE_URL` matches your backend URL:
     ```javascript
     const API_BASE_URL = "http://127.0.0.1:8000";
     ```

3. **Run the frontend**
   
   Option 1: Using Live Server (VS Code Extension)
   - Install "Live Server" extension in VS Code
   - Right-click `index.html` → "Open with Live Server"

   Option 2: Using Python HTTP Server
   ```bash
   python -m http.server 5500
   ```
   
   Option 3: Open directly in browser
   - Simply open `index.html` in your browser

## 📖 Usage Guide

### 1. **Register/Login**
   - Click "Register" to create a new account
   - Or click "Login" to access existing account
   - Authentication is required to upload files

### 2. **Select Domain**
   - Choose from: Student Data, Sales Data, Employee Data, or Financial Data
   - Each domain has specialized analytics

### 3. **Upload File**
   - Click "Choose File" or drag & drop
   - Accepted formats: `.csv`, `.xlsx`, `.xls`
   - Maximum file size: 50MB

### 4. **View Results**
   - Automatic data cleaning report
   - Key analytics and insights
   - Interactive visualizations
   - Suggested analysis questions

### 5. **Explore Insights**
   - Click suggested questions to see specific insights
   - View charts and graphs
   - Navigate back to upload new data

## 🔒 Security Features

- ✅ Environment variables for sensitive data
- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ CORS restrictions
- ✅ File upload validation (type & size)
- ✅ Input sanitization
- ✅ MongoDB injection prevention

## 🎨 UI Features

- **Theme Toggle**: Switch between dark and light modes
- **Glassmorphism**: Modern frosted glass effects
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Micro-interactions for better UX
- **Loading States**: Visual feedback during processing

## 📊 Supported Data Types

### Sales Data
- Regional performance analysis
- Sales trends over time
- Profit analysis
- Top-performing products/regions

### Finance Data
- Expense categorization
- Profit/loss trends
- Budget analysis
- Financial forecasting

### Student Data
- Performance metrics
- Stress factor analysis
- Study hours correlation
- Screen time impact

### Employee Data
- Attrition analysis
- Department performance
- Employee satisfaction metrics
- Performance evaluation

## 🔧 Configuration

### File Upload Limits
Edit in `backend/main.py`:
```python
MAX_FILE_SIZE_MB = 50  # Change as needed
```

### CORS Settings
Update `.env` file:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:5500
```

### JWT Token Expiry
Update `.env` file:
```env
ACCESS_TOKEN_EXPIRE_MINUTES=30  # Change as needed
```

## 🐛 Troubleshooting

### Backend won't start
- Ensure MongoDB is accessible
- Check `.env` file exists and is configured
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check `API_BASE_URL` in `script.js`
- Ensure CORS is properly configured in `.env`

### File upload fails
- Check file size (<50MB)
- Ensure file format is `.csv`, `.xlsx`, or `.xls`
- Verify you're logged in

### Charts not displaying
- Ensure `charts/` directory exists in backend
- Check browser console for errors
- Verify static files are mounted correctly

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Data Processing
- `GET /` - Health check
- `POST /upload` - Upload and analyze file (requires authentication)

### Static Files
- `GET /charts/{filename}` - Retrieve generated charts

## 🤝 Contributing

This is a college final year project. For suggestions or improvements:
1. Document the issue or enhancement
2. Test thoroughly
3. Follow existing code style

## 📄 License

Educational project - All rights reserved

## 👨‍💻 Author

**Rishabh Mourya**
- College Final Year Project
- Data Analysis System

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- Pandas team for data manipulation tools
- MongoDB for flexible database solution
- Google Fonts for Outfit typography

---

**Note**: This is an educational project created as a college final year project. It demonstrates full-stack development, data analytics, and modern web technologies.

## 🔮 Future Enhancements

- [ ] Export reports as PDF
- [ ] Real-time collaboration features
- [ ] More data domains (Marketing, HR, etc.)
- [ ] AI-powered insights using LLMs
- [ ] Custom report templates
- [ ] Data comparison across time periods
- [ ] Advanced filtering and search
- [ ] Multi-language support

---

Made with ❤️ for data analytics enthusiasts
