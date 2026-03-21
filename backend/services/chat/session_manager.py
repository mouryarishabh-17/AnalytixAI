"""
Session Manager - Handles data caching and session management
WITH PRO USER SUPPORT (Unlimited Sessions)
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd
from cachetools import TTLCache

# Separate caches for Free and Pro users
# Free users: 1 hour expiry
free_user_data_cache = TTLCache(maxsize=50, ttl=3600)  # 1 hour
free_user_metadata_cache = TTLCache(maxsize=50, ttl=3600)

# Pro users: 30 days expiry (effectively unlimited)
pro_user_data_cache = TTLCache(maxsize=200, ttl=2592000)  # 30 days
pro_user_metadata_cache = TTLCache(maxsize=200, ttl=2592000)


class SessionManager:
    """Manages user sessions and data storage with PRO user support"""
    
    @staticmethod
    def _is_pro_user(user_id: str) -> bool:
        """
        Check if user has PRO subscription
        
        This would typically check your database, but for now we can check:
        1. Email domain (e.g., @company.com)
        2. User metadata
        3. Subscription table
        
        For demo: You can mark yourself as PRO by checking email
        """
        # TODO: Replace with actual database check
        # Example: Check if user has active subscription in MongoDB
        
        # For now, simple check - you can customize this:
        pro_emails = [
            'rishabhmourya018@gmail.com',  # Your email
            # Add more PRO users here
        ]
        
        return user_id.lower() in [email.lower() for email in pro_emails]
    
    @staticmethod
    def _get_user_caches(user_id: str) -> tuple:
        """Get the appropriate caches based on user subscription"""
        if SessionManager._is_pro_user(user_id):
            return pro_user_data_cache, pro_user_metadata_cache, True
        else:
            return free_user_data_cache, free_user_metadata_cache, False
    
    @staticmethod
    def create_session(user_id: str, df: pd.DataFrame, domain: str, filename: str) -> str:
        """
        Create a new session and store the DataFrame
        
        Args:
            user_id: User ID from authentication
            df: Pandas DataFrame to store
            domain: Data domain (sales, finance, etc.)
            filename: Original filename
            
        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())
        
        # Get appropriate cache based on user subscription
        data_cache, metadata_cache, is_pro = SessionManager._get_user_caches(user_id)
        
        # Store DataFrame
        data_cache[session_id] = df
        
        # Store metadata
        metadata_cache[session_id] = {
            'user_id': user_id,
            'domain': domain,
            'filename': filename,
            'created_at': datetime.now(),
            'rows': len(df),
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'subscription': 'PRO' if is_pro else 'FREE',
            'expiry': '30 days' if is_pro else '1 hour'
        }
        
        # Log session creation with subscription info
        subscription_type = "PRO (30 days)" if is_pro else "FREE (1 hour)"
        print(f"💎 Session created for {subscription_type} user: {session_id}")
        
        return session_id
    
    @staticmethod
    def get_dataframe(session_id: str) -> Optional[pd.DataFrame]:
        """Retrieve DataFrame from cache"""
        # Check both caches
        if session_id in pro_user_data_cache:
            return pro_user_data_cache[session_id]
        elif session_id in free_user_data_cache:
            return free_user_data_cache[session_id]
        return None
    
    @staticmethod
    def get_metadata(session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session metadata"""
        # Check both caches
        if session_id in pro_user_metadata_cache:
            return pro_user_metadata_cache[session_id]
        elif session_id in free_user_metadata_cache:
            return free_user_metadata_cache[session_id]
        return None
    
    @staticmethod
    def session_exists(session_id: str) -> bool:
        """Check if session exists in either cache"""
        return (session_id in pro_user_data_cache or 
                session_id in free_user_data_cache)
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a session from cache"""
        deleted = False
        
        if session_id in pro_user_data_cache:
            del pro_user_data_cache[session_id]
            del pro_user_metadata_cache[session_id]
            deleted = True
        elif session_id in free_user_data_cache:
            del free_user_data_cache[session_id]
            del free_user_metadata_cache[session_id]
            deleted = True
        
        return deleted
    
    @staticmethod
    def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information including subscription type and expiry
        """
        metadata = SessionManager.get_metadata(session_id)
        if not metadata:
            return None
        
        created_at = metadata['created_at']
        is_pro = metadata.get('subscription') == 'PRO'
        
        if is_pro:
            expires_at = created_at + timedelta(days=30)
            time_left = expires_at - datetime.now()
        else:
            expires_at = created_at + timedelta(hours=1)
            time_left = expires_at - datetime.now()
        
        return {
            'session_id': session_id,
            'user_id': metadata['user_id'],
            'subscription': metadata.get('subscription', 'FREE'),
            'created_at': created_at.isoformat(),
            'expires_at': expires_at.isoformat(),
            'time_left_seconds': int(time_left.total_seconds()),
            'time_left_formatted': str(time_left).split('.')[0]
        }
    
    @staticmethod
    def get_all_sessions_for_user(user_id: str) -> list:
        """Get all active sessions for a user"""
        sessions = []
        
        # Check both caches
        for cache_metadata, cache_data in [
            (pro_user_metadata_cache, pro_user_data_cache),
            (free_user_metadata_cache, free_user_data_cache)
        ]:
            for session_id, metadata in cache_metadata.items():
                if metadata['user_id'] == user_id:
                    sessions.append({
                        'session_id': session_id,
                        'filename': metadata['filename'],
                        'domain': metadata['domain'],
                        'created_at': metadata['created_at'].isoformat(),
                        'subscription': metadata.get('subscription', 'FREE')
                    })
        
        return sessions
