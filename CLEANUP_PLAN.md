# 🧹 Project Cleanup Plan

## Files/Folders to DELETE (Safe to Remove)

### 📁 Root Directory - Documentation Spam (22 files)
These are old/duplicate documentation files that can be removed:
- ✅ `AI_CHAT_SETUP_GUIDE.md` (duplicate/old)
- ✅ `API_KEY_ROTATION_GUIDE.md` (duplicate/old)
- ✅ `CHANGES.md` (temporary changelog)
- ✅ `CHAT_500_ERROR.md` (old debugging doc)
- ✅ `CHAT_DEBUG_GUIDE.md` (old debugging doc)
- ✅ `CHAT_FLOW_DIAGRAM.txt` (old)
- ✅ `CHAT_GUIDE.md` (duplicate)
- ✅ `CHAT_IMPLEMENTATION.md` (old)
- ✅ `CHAT_INPUT_FIX.md` (old fix doc)
- ✅ `CHAT_SCROLL_FIX.md` (old fix doc)
- ✅ `CHAT_TROUBLESHOOTING.md` (old)
- ✅ `FIX_CORS_ERROR.md` (old fix doc)
- ✅ `GENAI_MIGRATION_COMPLETE.md` (old migration doc)
- ✅ `MODEL_FIX.md` (old fix doc)
- ✅ `PHASE1_COMPLETE.md` (old milestone doc)
- ✅ `PRO_USER_SESSIONS.md` (old feature doc)
- ✅ `QUICK_START_CHAT.md` (duplicate)
- ✅ `STATUS.md` (old status doc)
- ✅ `URGENT_FIX.md` (old fix doc)
- ✅ `VISUALIZATION_FIX.md` (old fix doc)
- ✅ `VISUALIZATION_FIX_FINAL.md` (old fix doc)
- ✅ `test_visualizations.py` (temporary test file)

**Keep these docs:**
- ❌ `README.md` - Main project documentation ✓
- ❌ `QUICKSTART.md` - Quick start guide ✓
- ❌ `DEPLOYMENT.md` - Deployment instructions ✓
- ❌ `GOOGLE_API_KEY_GUIDE.md` - Important API setup ✓

### 📁 Backend Directory - Temporary/Backup Files (15 files)
- ✅ `_chat_overview_endpoint.py` (temporary/old)
- ✅ `add_cache_buster.py` (one-time script)
- ✅ `add_delete_endpoint.py` (one-time script)
- ✅ `add_delete_fe.py` (one-time script)
- ✅ `check_models.py` (temporary test)
- ✅ `emergency_fix.py` (old fix script)
- ✅ `final_fix_js.py` (old fix script)
- ✅ `fix_chart_loader.py` (old fix script)
- ✅ `fix_chat_render.py` (old fix script)
- ✅ `fix_css_link.py` (old fix script)
- ✅ `fix_visuals_logic.py` (old fix script)
- ✅ `fix_visuals_robust.py` (old fix script)
- ✅ `restore_classic_graphs.py` (backup/restore script)
- ✅ `restore_graphs.py` (backup/restore script)
- ✅ `main_minimal.py` (old minimal version)

**Keep these:**
- ❌ `main.py` - Main application entry point ✓
- ❌ `.env` - Environment variables ✓
- ❌ `.env.template` - Template for users ✓
- ❌ `requirements.txt` - Dependencies ✓
- ❌ `analytix.db` - SQLite database ✓

### 📁 Frontend Directory - Old Version Files (6 files)
- ✅ `index.html` (old version, use `index_v2.html`)
- ✅ `script.js` (old version, use `script_v2.js`)
- ✅ `style.css` (old version, use `style_v2.css`)
- ✅ `chat_fix.css` (temporary fix file)
- ✅ `gemini_chat.css` (old/unused)
- ✅ `chat_markdown.js` (old/unused)

**Keep these:**
- ❌ `index_v2.html` - Current main HTML ✓
- ❌ `script_v2.js` - Current main JS ✓
- ❌ `style_v2.css` - Current main CSS ✓
- ❌ `style_v2_additions.css` - CSS additions ✓
- ❌ `style_v2_settings.css` - CSS settings ✓

### 📁 Other Directories
- ✅ `charts/` folder in ROOT (duplicate, backend has its own)
- ✅ All `__pycache__/` folders (regenerated automatically)
- ✅ `backend/demo_data/` (if unused)
- ✅ `backend/logs/` files (old logs)
- ✅ `.venv` in ROOT (duplicate, backend has its own)

### 📁 Keep Important Folders
- ❌ `backend/.venv/` - Virtual environment ✓
- ❌ `backend/charts/` - Generated charts ✓
- ❌ `backend/services/` - Core application logic ✓
- ❌ `backend/auth/` - Authentication ✓
- ❌ `backend/database/` - Database logic ✓
- ❌ `backend/utils/` - Utilities ✓
- ❌ `backend/reports/` - Generated reports ✓
- ❌ `AnalytixAI Data/` - Sample data ✓
- ❌ `master data/` - Master datasets ✓

## Summary
**Total files to delete: ~43**
- Root docs: 22 files
- Backend scripts: 15 files
- Frontend old files: 6 files
- Root folders: 2 (charts/, .venv/)

**Estimated cleanup:** ~50 MB freed

## Action
Run `cleanup.bat` to automatically remove all unnecessary files.
