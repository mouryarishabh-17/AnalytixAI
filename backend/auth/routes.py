from fastapi import APIRouter, HTTPException, status, Depends, Body
from auth.schemas import (
    UserRegister, 
    UserLogin, 
    UserUpdate, 
    UserUpgrade, 
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from auth.utils import hash_password, verify_password
from database.mongo import users_collection
from datetime import datetime, timedelta
from auth.utils import create_access_token
from auth.dependencies import get_current_user
import uuid
from services.email_service import send_verification_email, send_password_reset_email, send_welcome_email

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register_user(user: UserRegister):
    print(f"📝 MONGO REGISTER ATTEMPT: {user.email}")
    
    # Check if user exists in MongoDB
    existing = users_collection.find_one({"email": user.email})
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_pwd = hash_password(user.password)

    # Generate verification token
    verification_token = str(uuid.uuid4())

    # Insert user into MongoDB
    users_collection.insert_one({
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_pwd,
        "bio": "",
        "phone": "",
        "plan": "free",  # Default plan
        "created_at": datetime.utcnow(),
        "is_verified": False,
        "verification_token": verification_token
    })
    
    # Send verification email
    try:
        send_verification_email(user.email, user.name, verification_token)
    except Exception as e:
        print(f"❌ Failed to send verification email: {e}")
        # Continue registration but log error - user can request resend later
    
    print(f"✅ User registered in Mongo: {user.email}")
    return {
        "message": "Registration successful! Please check your email to verify your account.", 
        "status": "success",
        "email_sent": True
    }


@router.get("/verify-email/{token}")
def verify_email(token: str):
    user = users_collection.find_one({"verification_token": token})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
        
    if user.get("is_verified", False):
        return {"message": "Email already verified", "status": "success"}
    
    # Update user verification status
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"is_verified": True, "verification_token": None}}
    )
    
    # Send welcome email
    try:
        send_welcome_email(user["email"], user["name"])
    except Exception:
        pass  # Non-critical functionality
        
    return {"message": "Email verified successfully!", "status": "success"}


@router.post("/resend-verification")
def resend_verification(request: ResendVerificationRequest):
    user = users_collection.find_one({"email": request.email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.get("is_verified", False):
        return {"message": "Email already verified", "status": "info"}
        
    # Generate new token
    new_token = str(uuid.uuid4())
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"verification_token": new_token}}
    )
    
    # Send email
    try:
        send_verification_email(user["email"], user["name"], new_token)
        return {"message": "Verification email sent", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    user = users_collection.find_one({"email": request.email})
    
    if not user:
        # Don't reveal user existence for security
        return {"message": "If an account exists, a password reset link has been sent.", "status": "success"}
        
    # Generate reset token
    reset_token = str(uuid.uuid4())
    expiry = datetime.utcnow() + timedelta(hours=1)
    
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_expiry": expiry
        }}
    )
    
    # Send email
    try:
        send_password_reset_email(user["email"], user["name"], reset_token)
    except Exception as e:
        print(f"Failed to send reset email: {e}")
        # Still return success to user for security
        
    return {"message": "If an account exists, a password reset link has been sent.", "status": "success"}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest):
    # Find user with token
    user = users_collection.find_one({
        "reset_token": request.token,
        "reset_token_expiry": {"$gt": datetime.utcnow()}  # Must not be expired
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
        
    # Update password
    new_hashed_pwd = hash_password(request.new_password)
    
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "hashed_password": new_hashed_pwd,
            "reset_token": None,
            "reset_token_expiry": None
        }}
    )
    
    return {"message": "Password reset successfully. You can now login.", "status": "success"}


@router.post("/login")
def login_user(user: UserLogin):
    print(f"🔑 MONGO LOGIN ATTEMPT: {user.email}")
    
    # Find user in MongoDB
    db_user = users_collection.find_one({"email": user.email})

    if not db_user:
        print("❌ Login failed: User not found in Mongo")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not verify_password(user.password, db_user["hashed_password"]):
        print("❌ Login failed: Wrong password")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Optional: Enforce email verification
    # if not db_user.get("is_verified", False):
    #     raise HTTPException(status_code=403, detail="Email not verified. Please check your inbox.")

    # Create token
    access_token = create_access_token(
        data={"sub": db_user["email"]}
    )
    
    is_verified = db_user.get("is_verified", False)

    print(f"✅ Login successful: {user.email}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": db_user.get("name", ""),
        "user_email": db_user.get("email", ""),
        "user_bio": db_user.get("bio", ""),
        "user_plan": db_user.get("plan", "free"),
        "is_verified": is_verified,
        "is_admin": db_user.get("is_admin", False),
        "message": "Login successful"
    }

@router.post("/upgrade")
def upgrade_user(data: UserUpgrade, current_user: dict = Depends(get_current_user)):
    print(f"💰 PAYMENT RECEIVED: {data.amount} from {current_user['email']}")
    
    try:
        users_collection.update_one(
            {"email": current_user['email']},
            {"$set": {"plan": "pro", "updated_at": datetime.utcnow()}}
        )
        print(f"🌟 User {current_user['email']} upgraded to PRO")
    except Exception as e:
        print(f"❌ Upgrade Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment successful but database update failed")
        
    return {"status": "success", "message": "Successfully upgraded to PRO", "new_plan": "pro"}

@router.put("/update-profile")
def update_user_profile(user_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    print(f"📝 MONGO UPDATE PROFILE: {current_user['email']}")
    
    try:
        users_collection.update_one(
            {"email": current_user['email']},
            {"$set": {
                "name": user_data.name,
                "bio": user_data.bio,
                "phone": user_data.phone,
                "updated_at": datetime.utcnow()
            }}
        )
        print("✅ Mongo Profile updated")
    except Exception as e:
        print(f"❌ Mongo Update Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update profile in MongoDB")
        
    return {"status": "success", "message": "Profile updated successfully"}
