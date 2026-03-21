from fastapi import APIRouter, Depends, HTTPException, status
from auth.dependencies import get_current_user
from database.mongo import users_collection, analysis_collection
from bson import ObjectId
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Dependency to check if current user is admin"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.get("/stats")
def get_admin_stats(admin: dict = Depends(get_admin_user)):
    """Get system-wide statistics"""
    total_users = users_collection.count_documents({})
    pro_users = users_collection.count_documents({"plan": "pro"})
    total_analyses = analysis_collection.count_documents({})
    
    # Recent activity (last 24h)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    new_users_24h = users_collection.count_documents({"created_at": {"$gte": last_24h}})
    analyses_24h = analysis_collection.count_documents({"created_at": {"$gte": last_24h}})
    
    return {
        "total_users": total_users,
        "pro_users": pro_users,
        "total_analyses": total_analyses,
        "new_users_24h": new_users_24h,
        "analyses_24h": analyses_24h
    }

@router.get("/users")
def get_all_users(limit: int = 50, skip: int = 0, admin: dict = Depends(get_admin_user)):
    """Get list of users with pagination"""
    cursor = users_collection.find({}, {"hashed_password": 0}).sort("created_at", -1).skip(skip).limit(limit)
    users = []
    for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

@router.post("/users/{user_id}/toggle-status")
def toggle_user_status(user_id: str, admin: dict = Depends(get_admin_user)):
    """Ban/Unban user"""
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        current_status = user.get("is_active", True)
        new_status = not current_status
        
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": new_status}}
        )
        
        return {"status": "success", "is_active": new_status, "message": f"User {'activated' if new_status else 'deactivated'}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
