# 🚀 Quick Start Guide - AnalytixAI

## First Time Setup (5 minutes)

### Step 1: Configure Environment
1. Open `backend/.env` in a text editor
2. Update your MongoDB URL if needed (current one is already set)
3. Optionally change the SECRET_KEY for production use

### Step 2: Run Setup Script
```bash
# Double-click this file
setup.bat
```
This will:
- Create virtual environment
- Install all dependencies
- Check your configuration

### Step 3: Start Backend
```bash
# Double-click this file
start-backend.bat
```
Server runs at: http://127.0.0.1:8000

### Step 4: Open Frontend
Navigate to `frontend` folder and open `index.html` in your browser

OR use Live Server in VS Code (recommended)

---

## Daily Usage

### Starting the Application

1. **Start Backend**
   ```bash
   # Method 1: Use the script
   start-backend.bat
   
   # Method 2: Manual
   cd backend
   venv\Scripts\activate
   uvicorn main:app --reload
   ```

2. **Start Frontend**
   - Open `frontend/index.html` in browser
   - OR use Live Server extension in VS Code

---

## Common Commands

### Backend

```bash
# Activate virtual environment
cd backend
venv\Scripts\activate

# Install new package
pip install package-name
pip freeze > requirements.txt

# Run server
uvicorn main:app --reload

# Run with specific host/port
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# View API docs
# Open: http://127.0.0.1:8000/docs
```

### Database

```bash
# The MongoDB connection is configured in .env
# No local installation needed (using MongoDB Atlas)
```

---

## Troubleshooting

### ❌ "ModuleNotFoundError"
**Solution**: Install dependencies
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### ❌ "MongoDB connection failed"
**Solution**: Check your `.env` file
1. Open `backend/.env`
2. Verify `MONGO_URL` is correct
3. Test connection at: https://cloud.mongodb.com

### ❌ "CORS error" in browser console
**Solution**: Add frontend URL to CORS
1. Open `backend/.env`
2. Add your frontend URL to `ALLOWED_ORIGINS`
   ```
   ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
   ```

### ❌ "File upload failed"
**Solutions**:
- Check file is `.csv`, `.xlsx`, or `.xls`
- Ensure file size < 50MB
- Make sure you're logged in
- Check backend console for errors

### ❌ Charts not showing
**Solutions**:
1. Check `backend/charts/` folder exists
2. Look for errors in backend console
3. Refresh the page

---

## File Upload Guidelines

### Supported Formats
- ✅ CSV (`.csv`)
- ✅ Excel (`.xlsx`, `.xls`)

### Size Limits
- Maximum: 50MB per file
- Recommended: < 10MB for faster processing

### Data Requirements

**Sales Data** should include:
- Date, Region, Product, Sales, Profit columns

**Finance Data** should include:
- Date, Category, Amount, Type columns

**Student Data** should include:
- Student ID, Name, Scores, Hours columns

**Employee Data** should include:
- Employee ID, Department, Performance columns

---

## Project Structure Quick Reference

```
Demo AutoDataAnalytics/
│
├── setup.bat              ← Run this first (one-time setup)
├── start-backend.bat      ← Run this to start server
├── README.md              ← Full documentation
│
├── backend/
│   ├── .env              ← Configuration (IMPORTANT!)
│   ├── .env.template     ← Template for .env
│   ├── main.py           ← Main API file
│   ├── requirements.txt  ← Python packages
│   └── ...
│
└── frontend/
    ├── index.html        ← Open this in browser
    ├── script.js         ← Frontend logic
    └── style.css         ← Styling
```

---

## Testing Your Setup

### 1. Test Backend
```bash
# Start backend
start-backend.bat

# In browser, visit:
http://127.0.0.1:8000
```
Should see: `{"message": "AnalytixAI backend running", "status": "healthy"}`

### 2. Test API Docs
Visit: http://127.0.0.1:8000/docs

You should see interactive API documentation

### 3. Test Frontend
1. Open `frontend/index.html`
2. Click "Register" - create test account
3. Select a domain (e.g., Sales Data)
4. Upload a sample CSV file
5. View results

---

## Development Tips

### Making Changes

**Backend Changes**:
- Edit Python files
- Server auto-reloads (if using `--reload` flag)
- Check console for errors

**Frontend Changes**:
- Edit HTML/CSS/JS files
- Refresh browser to see changes
- Use browser DevTools (F12)

### Adding New Dependencies

```bash
cd backend
venv\Scripts\activate
pip install new-package
pip freeze > requirements.txt
```

### Environment Variables

Always use `.env` for:
- Database credentials
- Secret keys
- API URLs
- Configuration values

Never commit `.env` to Git! ✋

---

## Getting Help

1. **Check README.md** - Full documentation
2. **Check Backend Logs** - Terminal where backend is running
3. **Check Browser Console** - F12 → Console tab
4. **Check API Docs** - http://127.0.0.1:8000/docs

---

## Security Reminders ⚠️

- ✅ Never commit `.env` files
- ✅ Use strong SECRET_KEY in production
- ✅ Keep dependencies updated
- ✅ Use HTTPS in production
- ✅ Validate user inputs
- ✅ Regular database backups

---

## Next Steps

1. ✅ Complete setup
2. ✅ Test with sample data
3. ✅ Customize for your needs
4. ✅ Deploy to production (optional)

---

**Need more help?** Check the full README.md in the project root.

**Happy Analyzing! 📊✨**
