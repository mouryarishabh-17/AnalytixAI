import os
from pathlib import Path
from fastapi.responses import JSONResponse, FileResponse
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from auth.routes import router as auth_router
from auth.dependencies import get_current_user
from database.mongo import analysis_collection
from datetime import datetime
import uuid
from bson.objectid import ObjectId
from services.field_service import field_service
from services.report_service import report_service
from services.ml_service import ml_service
from dotenv import load_dotenv
from typing import Dict
from pydantic import BaseModel

import pandas as pd



# Load environment variables
load_dotenv()

app = FastAPI(title="AnalytixAI Backend")

# Register Error Handlers
from middleware.error_handler import global_exception_handler, validation_exception_handler
from fastapi.exceptions import RequestValidationError
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 🔥 FIX: CORS must be added BEFORE including routers
# Allow common development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers AFTER CORS middleware
from admin.routes import router as admin_router
app.include_router(auth_router)
app.include_router(admin_router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

app.mount("/charts", StaticFiles(directory=CHARTS_DIR), name="charts")

# Configuration
MAX_FILE_SIZE_MB = 50  # Maximum file size in MB
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
ALLOWED_DOMAINS = ['sales', 'finance', 'student', 'employee']
REQUIRED_COLUMNS = {
    'sales': {
        'amount': ['amount', 'sales', 'revenue', 'price', 'value'],
        'date': ['date', 'time', 'year', 'month']
    },
    'finance': {
        'amount': ['amount', 'income', 'expense', 'cost', 'profit', 'revenue', 'budget'],
        'date': ['date', 'time', 'period', 'year', 'month']
    }
}


@app.get("/")
def home():
    return {"message": "AnalytixAI backend running", "status": "healthy"}


@app.get("/api/history")
async def get_analysis_history(current_user: dict = Depends(get_current_user)):
    """
    Get all previous analysis records for the logged-in user
    """
    try:
        # Find all records for this user, sorted by newest first
        cursor = analysis_collection.find(
            {"user_email": current_user["email"]}
        ).sort("created_at", -1)
        
        history = []
        for doc in cursor:
            # Convert ObjectId to string and remove it for JSON serialization
            doc["_id"] = str(doc["_id"])
            # 🛡️ SANITIZE: Ensure no NaN/Inf values reach JSON serialization
            sanitized_doc = field_service._sanitize_dict(doc)
            history.append(sanitized_doc)
            
        return {"status": "success", "history": history}
    except Exception as e:
        print(f"❌ HISTORY ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

@app.get("/api/dashboard")
def get_dashboard_data():
    """
    Get statistics for the main dashboard (Mock Data)
    """
    return {
        "status": "success",
        "conversations_chart": {
            "weekly": [65, 59, 80, 81, 56, 55, 40],
            "monthly": [28, 48, 40, 19, 86, 27, 90],
            "yearly": [18, 48, 77, 90, 100, 27, 40]
        },
        "time_saved_chart": {
            "values": [300, 50, 100],
            "total": "60m"
        },
        "responses_chart": {
            "unanswered": [40, 50, 45, 60, 35, 45, 55, 80, 45, 60, 55, 50],
            "answered": [30, 25, 35, 20, 30, 25, 30, 15, 40, 25, 30, 35]
        }
    }

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Simple test endpoint to verify upload works"""
    try:
        content = await file.read()
        return {
            "status": "success",
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/upload")
async def upload_file(
    domain: str = Form(...),
    mapping: str = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and analyze data file (CSV or Excel)
    
    - **domain**: Type of data (sales, finance, student, employee)
    - **file**: CSV or Excel file with data
    """
    
    print(f"\n🔥 UPLOAD STARTED - Domain: {domain}, File: {file.filename}")
    
    try:
        print("✅ Step 1: Validating domain...")
        # Validate domain
        if domain.lower() not in ALLOWED_DOMAINS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported domain. Allowed: {', '.join(ALLOWED_DOMAINS)}"
            )
        
        # Validate file extension
        filename = file.filename.lower()
        file_ext = Path(filename).suffix
        
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content to check size
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
            )
        
        # Reset file pointer after reading
        await file.seek(0)
        
        # Parse file based on extension
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file.file)
            elif file_ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file.file)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse file: {str(e)}"
            )
        
        
        # 0. Apply Mapping if provided
        if mapping:
            try:
                print(f"Applying mapping: {mapping}")
                map_dict = json.loads(mapping)
                df.rename(columns=map_dict, inplace=True)
            except Exception as e:
                print(f"Mapping error: {e}")

        # 1. Check Required Columns
        if domain.lower() in REQUIRED_COLUMNS and not mapping:
            reqs = REQUIRED_COLUMNS[domain.lower()]
            missing_concepts = []
            
            for concept, keywords in reqs.items():
                found = False
                for col in df.columns:
                    if any(k in col.lower() for k in keywords):
                        found = True
                        break
                if not found:
                    # Provide helpful label
                    label = f"{concept.title()} (e.g. {', '.join(keywords[:3])})"
                    missing_concepts.append(label)
            
            if missing_concepts:
                 return JSONResponse(
                     status_code=200, 
                     content={
                         "status": "mapping_needed",
                         "missing_concepts": missing_concepts,
                         "columns": df.columns.tolist(),
                         "filename": file.filename,
                         "domain": domain
                     }
                 )

        # Validate dataframe is not empty
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file contains no data"
            )

        # 1. Clean data based on domain
        print(f"🧹 Cleaning and Quantizing {domain} data...")
        df, cleaning_summary = field_service.clean_data(df, domain.lower())

        # 2. Use the new Unified Field Service for Deep Analysis & ML
        print(f"✅ Executing Field-Work Intelligence for {domain}...")
        analytics = field_service.deep_analyze(df, domain.lower())
        
        # 💳 PAYWALL LOGIC: Remove ML insights for Free users
        user_plan = current_user.get("plan", "free")
        if user_plan == "free":
            print(f"🔒 Hiding ML insights for FREE user: {current_user['email']}")
            analytics["ml_insights"] = {
                "status": "locked", 
                "message": "Upgrade to Pro to unlock ML-powered Predictive Analysis & Feature Importance."
            }
            analytics["key_insights"] = analytics["key_insights"][:1] # Limit observations

        charts = field_service.generate_field_charts(df, domain.lower())

        # 💬 CREATE CHAT SESSION (Re-enabled)
        from services.chat.session_manager import SessionManager
        session_id = SessionManager.create_session(
            user_id=current_user["email"],
            df=df,
            domain=domain.lower(),
            filename=file.filename
        )
        print(f"✅ Chat session created: {session_id}")

        # 💾 LOG TO MONGODB (User History)
        try:
            # Record the full history: metadata + results
            analysis_record = {
                "user_email": current_user["email"],
                "filename": file.filename,
                "domain": domain,
                "file_size_mb": round(file_size_mb, 2),
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
                "cleaning_summary": cleaning_summary,
                "analytics": analytics,
                "charts": charts,
                "created_at": datetime.utcnow()
            }
            
            res = analysis_collection.insert_one(analysis_record)
            report_id = str(res.inserted_id)
            print(f"✅ Analysis for {current_user['email']} saved to MongoDB History (ID: {report_id})")
        except Exception as e:
            print(f"⚠️ Failed to save to MongoDB (Non-critical): {e}")
            report_id = None

        return {
            "status": "success",
            "domain": domain,
            "filename": file.filename,
            "file_size_mb": round(file_size_mb, 2),
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "cleaning_summary": cleaning_summary,
            "analytics": analytics,
            "charts": charts,
            "session_id": session_id,
            "report_id": report_id  # 🆕 Mongo ID for PDF download
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error (you might want to use proper logging here)
        print(f"❌ PIPELINE ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the file: {str(e)}"
        )


@app.post("/chat/overview")
async def get_data_overview(
    session_id: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Get an automatic AI-generated overview of the uploaded data
    
    - **session_id**: Session ID from upload response
    """
    from services.chat.session_manager import SessionManager
    from services.chat.data_context import DataContextBuilder
    from services.chat.ai_service import gemini_service
    
    try:
        # Validate session exists
        if not SessionManager.session_exists(session_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired. Please upload your file again."
            )
        
        # Get DataFrame and metadata
        df = SessionManager.get_dataframe(session_id)
        metadata = SessionManager.get_metadata(session_id)
        
        # Verify user owns this session
        if metadata['user_id'] != current_user.get('email'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        # Build data context
        domain = metadata['domain']
        data_context = DataContextBuilder.build_context(df, domain)
        
        # Create automatic overview prompt
        overview_prompt = f"""Please provide a brief, friendly overview of this {domain} dataset. Include:
1. What type of data this appears to be
2. Key columns and what they represent
3. The size of the dataset (rows/columns)
4. 2-3 interesting initial observations or patterns you notice
5. Suggest 2-3 questions the user might want to ask about this data

Keep it conversational and helpful, like you're introducing the data to someone for the first time."""
        
        # Get AI response
        ai_response = gemini_service.generate_response(
            user_question=overview_prompt,
            data_context=data_context,
            domain=domain
        )
        
        if not ai_response['success']:
            # Fallback to basic summary if AI fails
            return {
                "status": "success",
                "response": f"""📊 **Data Overview**

I've analyzed your {domain} dataset:

**Dataset Size:** {metadata['rows']} rows × {len(metadata['columns'])} columns

**Columns:** {', '.join(metadata['columns'][:5])}{'...' if len(metadata['columns']) > 5 else ''}

You can now ask me questions about this data! For example:
- "What are the key trends in this data?"
- "Show me summary statistics"
- "What insights can you find?"
""",
                "session_id": session_id
            }
        
        return {
            "status": "success",
            "response": ai_response['response'],
            "session_id": session_id,
            "metadata": {
                "domain": domain,
                "filename": metadata['filename'],
                "rows": metadata['rows']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ OVERVIEW ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Overview generation error: {str(e)}"
        )


@app.post("/chat")
async def chat_with_data(
    session_id: str = Form(...),
    message: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Chat with your uploaded data using AI
    
    - **session_id**: Session ID from upload response
    - **message**: Your question about the data
    """
    from services.chat.session_manager import SessionManager
    from services.chat.data_context import DataContextBuilder
    from services.chat.ai_service import gemini_service
    
    try:
        # Validate session exists
        if not SessionManager.session_exists(session_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired. Please upload your file again."
            )
        
        # Get DataFrame and metadata
        df = SessionManager.get_dataframe(session_id)
        metadata = SessionManager.get_metadata(session_id)
        
        # Verify user owns this session
        if metadata['user_id'] != current_user.get('email'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this session"
            )
        
        # Build data context
        domain = metadata['domain']
        data_context = DataContextBuilder.build_context(df, domain)
        
        # Get AI response
        ai_response = gemini_service.generate_response(
            user_question=message,
            data_context=data_context,
            domain=domain
        )
        
        if not ai_response['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ai_response.get('response', 'AI service error')
            )
        
        return {
            "status": "success",
            "response": ai_response['response'],
            "session_id": session_id,
            "metadata": {
                "domain": domain,
                "filename": metadata['filename'],
                "rows": metadata['rows']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ CHAT ERROR: {str(e)}")
        print(f"📋 Full traceback:")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )

@app.get("/api/report/download/{report_id}")
async def download_report(report_id: str):
    try:
        # Find record in MongoDB
        record = None
        try:
            record = analysis_collection.find_one({"_id": ObjectId(report_id)})
        except:
            pass

        if not record:
            raise HTTPException(status_code=404, detail="Analysis record not found")

        # Use absolute path — Render's filesystem is ephemeral, so ALWAYS regenerate.
        # Never rely on a cached file existing across restarts.
        pdf_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")

        # Convert chart URL paths (e.g. '/charts/sales/foo.png') to
        # absolute filesystem paths (e.g. '/app/backend/charts/sales/foo.png')
        charts = record.get('charts', {})
        clean_charts = {}
        for k, v in charts.items():
            relative = v.lstrip('/')          # strip leading /
            abs_chart = os.path.join(BASE_DIR, relative)
            clean_charts[k] = abs_chart       # always pass absolute path

        generated_path = report_service.generate_pdf(record, clean_charts, report_id)
        if not generated_path:
            raise HTTPException(status_code=500, detail="PDF Generation Failed")

        return FileResponse(
            generated_path,
            filename=f"Analytix_Report_{report_id}.pdf",
            media_type='application/pdf'
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Download Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.delete("/api/history/{item_id}")
async def delete_history_item(item_id: str, current_user: dict = Depends(get_current_user)):
    try:
        # Validate ID
        if not ObjectId.is_valid(item_id):
             raise HTTPException(status_code=400, detail="Invalid ID")

        # Optional: Verify ownership? 
        # The history query filters by email, so we should too.
        query = {"_id": ObjectId(item_id)}
        if "email" in current_user:
             query["user_email"] = current_user["email"]
        
        result = analysis_collection.delete_one(query)
        
        if result.deleted_count == 1:
            return {"status": "success", "message": "Analysis deleted"}
        else:
            raise HTTPException(status_code=404, detail="Item not found or access denied")
            
    except Exception as e:
        print(f"Delete Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ChartRegenRequest(BaseModel):
    session_id: str
    domain: str
    chart_name: str
    chart_type: str

@app.post("/api/visuals/regenerate")
async def regenerate_chart(request: ChartRegenRequest, current_user: dict = Depends(get_current_user)):
    from services.chat.session_manager import SessionManager
    
    print(f"🔄 Regenerating: {request.chart_name} as {request.chart_type} (Session: {request.session_id})")
    
    # 1. Get DataFrame
    df = SessionManager.get_dataframe(request.session_id)
    if df is None:
        print("❌ Session Not Found")
        raise HTTPException(status_code=404, detail="Session expired or not found. Please re-upload your file.")

    # 2. Dispatch to domain logic
    url = field_service.regenerate_specific_chart(df, request.domain, request.chart_name, request.chart_type)
    
    if not url:
         print("❌ Chart Generation Logic Failed")
         raise HTTPException(status_code=400, detail="Chart generation failed")
         
class CustomReportRequest(BaseModel):
    report_id: str
    preferences: Dict[str, str]

@app.post("/api/report/custom_download")
async def custom_download_report(request: CustomReportRequest):
    try:
        # Find Record
        try:
            record = analysis_collection.find_one({"_id": ObjectId(request.report_id)})
        except:
            record = None

        if not record:
            raise HTTPException(status_code=404, detail="Analysis record not found")

        # Build absolute chart paths, respecting user's chart-type preferences
        charts = record.get('charts', {})
        new_charts = {}

        for k, v in charts.items():
            # Convert URL path → absolute filesystem path
            base_rel_path   = v.lstrip('/')
            full_base_path  = os.path.join(BASE_DIR, base_rel_path)
            final_path      = full_base_path  # default

            if k in request.preferences:
                pref = request.preferences[k]  # 'pie', 'line', or 'bar'
                candidate = full_base_path
                if pref == 'pie':
                    candidate = full_base_path.replace('.png', '_pie.png')
                elif pref == 'line':
                    candidate = full_base_path.replace('.png', '_line.png')
                elif pref == 'bar':
                    candidate = full_base_path.replace('.png', '_bar.png')

                if os.path.exists(candidate):
                    final_path = candidate
                else:
                    print(f"Requested variant '{pref}' for '{k}' not found, using default")

            new_charts[k] = final_path

        # Generate PDF with unique timestamped name
        timestamp      = datetime.now().strftime("%Y%m%d%H%M%S")
        custom_filename = f"{request.report_id}_{timestamp}.pdf"

        generated_path = report_service.generate_pdf(
            record, new_charts, request.report_id, output_filename=custom_filename
        )

        if not generated_path:
            raise HTTPException(status_code=500, detail="PDF Generation Failed")

        return FileResponse(
            generated_path,
            filename=f"Analytix_Report_{timestamp}.pdf",
            media_type='application/pdf'
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Custom Download Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



