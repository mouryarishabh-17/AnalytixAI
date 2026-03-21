from datetime import datetime

def user_document(email: str, hashed_password: str):
    return {
        "email": email,
        "password": hashed_password,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
