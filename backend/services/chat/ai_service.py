"""
Gemini AI Service - NEW GOOGLE GENAI PACKAGE
Migrated from deprecated google.generativeai to google.genai
"""
import os
import random
from google import genai
from google.genai import types
from dotenv import load_dotenv, dotenv_values
from typing import Optional, List

load_dotenv(override=True)


class APIKeyRotator:
    """Smart API key rotation manager"""
    
    def __init__(self):
        """Initialize with API keys from environment"""
        self.api_keys = self._load_api_keys()
        self.total_keys = len(self.api_keys)
        self.failed_keys = set()  # Track failed key indices
        self.current_key_index = None
        
        print(f"🔑 Loaded {self.total_keys} API keys for rotation")
        
        # All available keys should be in Block 1, picking randomly.
        self.block1_indices = [i for i in range(self.total_keys)]

    def _load_api_keys(self) -> List[str]:
        """
        Load all API keys.
        Priority: os.environ (Render/cloud platform env vars) > .env file (local dev)
        
        IMPORTANT: dotenv_values() only reads the .env FILE and ignores real
        environment variables set by Render or any cloud hosting platform.
        We must use os.environ (which load_dotenv() already merges .env into)
        so that both local and deployed environments work correctly.
        """
        keys = []
        
        # os.environ contains BOTH real platform env vars (Render) AND
        # local .env values merged by load_dotenv() at the top of this file.
        # This is the correct source for all environments.
        env_vars = os.environ

        # Load primary key
        primary_key = env_vars.get("GEMINI_API_KEY")
        if primary_key and primary_key != "YOUR_GEMINI_API_KEY_HERE":
            keys.append(primary_key)
        
        # Load additional keys (GEMINI_API_KEY_1 through GEMINI_API_KEY_10)
        for i in range(1, 11):
            key = env_vars.get(f"GEMINI_API_KEY_{i}")
            if key and key != "YOUR_GEMINI_API_KEY_HERE":
                keys.append(key)
        
        if not keys:
            print("WARNING: No Gemini API keys found in environment!")
            print("  -> On Render: Add GEMINI_API_KEY_1 ... in the Environment tab")
            print("  -> Locally  : Add them to backend/.env")
        else:
            print(f"Loaded {len(keys)} Gemini API key(s) from environment")
        
        return keys
    
    def get_next_key(self) -> Optional[str]:
        """
        Get next available API key using a Randomized Strategy:
        1. All keys act as Block 1: Pick random available key.
        2. If all keys fail, Reset and start over.
        """
        if not self.api_keys:
            return None
            
        # Check availablity in Block 1
        available_b1 = [i for i in self.block1_indices if i not in self.failed_keys]
        
        if not available_b1:
            print("🔄 All keys exhausted. Resetting rotation cycle...")
            self.failed_keys.clear()
            # After reset, B1 is available again
            available_b1 = self.block1_indices
        
        # Select Key
        if available_b1:
            self.current_key_index = random.choice(available_b1)
            print(f"🎲 Block 1 Active: Using key #{self.current_key_index + 1}")
        else:
            self.current_key_index = 0
            
        return self.api_keys[self.current_key_index]
    
    def mark_failed(self):
        """Mark current key as failed"""
        if self.current_key_index is not None:
            self.failed_keys.add(self.current_key_index)
            print(f"❌ Key #{self.current_key_index + 1} failed and removed from current cycle.")


class GeminiService:
    """Service for interacting with Google Gemini AI with NEW API"""
    
    def __init__(self):
        """Initialize Gemini service with key rotator"""
        self.key_rotator = APIKeyRotator()
        self.client = None
        self.enabled = len(self.key_rotator.api_keys) > 0
        
        if not self.enabled:
            print("⚠️  Chat feature disabled: No API keys configured")
        else:
            print("✅ Chat feature enabled with NEW Google Genai API")
    
    def _initialize_client_with_next_key(self) -> bool:
        """Initialize client with next available API key"""
        api_key = self.key_rotator.get_next_key()
        if not api_key:
            return False
        
        try:
            # Initialize the new Google Genai client
            self.client = genai.Client(api_key=api_key)
            return True
        except Exception as e:
            print(f"❌ Failed to initialize client: {e}")
            return False
    
    def generate_response(
        self, 
        user_question: str, 
        data_context: str,
        domain: str,
        chat_history: Optional[list] = None,
        max_retries: int = None
    ) -> dict:
        """
        Generate AI response with automatic key rotation on failure
        
        Args:
            user_question: User's question
            data_context: Prepared data context
            domain: Data domain (sales, finance, etc.)
            chat_history: Previous chat messages (optional)
            max_retries: Maximum retry attempts with different keys
            
        Returns:
            dict: {'success': bool, 'response': str}
        """
        if not self.enabled:
            return {
                'success': False,
                'response': '⚠️ Gemini API is not configured. Please add API keys to .env file.'
            }
        
        # Default max_retries to total keys to ensure we try all blocks
        if max_retries is None:
            max_retries = max(5, self.key_rotator.total_keys)

        # Try with multiple keys if needed
        for attempt in range(max_retries):
            try:
                # Get next key and initialize client
                if not self._initialize_client_with_next_key():
                    return {
                        'success': False,
                        'response': '❌ No valid API keys available'
                    }
                
                # Build prompt
                system_instruction = self._get_domain_prompt(domain)
                full_prompt = f"{system_instruction}\n\nData Context:\n{data_context}\n\n"
                
                if chat_history:
                    full_prompt += "Previous conversation:\n"
                    for msg in chat_history[-5:]:  # Last 5 messages
                        full_prompt += f"{msg['role']}: {msg['content']}\n"
                    full_prompt += "\n"
                
                full_prompt += f"User Question: {user_question}\n\nAnswer:"
                
                # Generate response using NEW API
                response = self.client.models.generate_content(
                    model='gemini-3.1-flash-lite-preview',  # Updated to 3.1 Flash-Lite Preview as per March 2026 release notes
                    contents=full_prompt
                )
                
                # Extract text from response
                response_text = response.text
                
                return {
                    'success': True,
                    'response': response_text
                }
                
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️  Attempt {attempt + 1}/{max_retries} failed: {error_msg}")
                
                # Check if it's a rate limit error
                if "quota" in error_msg.lower() or "rate" in error_msg.lower() or "429" in error_msg:
                    print("📊 Rate limit detected. Trying next API key...")
                    self.key_rotator.mark_failed()
                    continue
                
                # Check if it's an invalid key error
                if "invalid" in error_msg.lower() or "api" in error_msg.lower() or "401" in error_msg:
                    print("🔑 Invalid API key. Trying next key...")
                    self.key_rotator.mark_failed()
                    continue
                
                # If last attempt, return error
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'response': f'❌ AI service error after {max_retries} attempts: {error_msg}'
                    }
        
        return {
            'success': False,
            'response': '❌ Failed to generate response after multiple retries'
        }
    
    def _get_domain_prompt(self, domain: str) -> str:
        """Get domain-specific system prompt"""
        prompts = {
            'sales': "You are a sales data analyst. Analyze sales trends, revenue, customer behavior. Provide clear, actionable insights.",
            'finance': "You are a financial analyst. Focus on financial metrics, budgets, expenses. Provide data-driven recommendations.",
            'employee': "You are an HR analyst. Analyze employee data, performance, demographics. Provide insights on workforce trends.",
            'student': "You are an education analyst. Focus on academic performance, study patterns. Provide insights to improve learning outcomes.",
            'healthcare': "You are a healthcare analyst. Analyze patient data, medical trends. Focus on data-driven healthcare insights.",
            'marketing': "You are a marketing analyst. Focus on campaigns, engagement, ROI. Provide actionable marketing insights.",
        }
        
        return prompts.get(
            domain.lower(),
            "You are a data analyst. Provide clear, actionable insights from the data. Be concise and helpful."
        )
    
    def check_status(self) -> dict:
        """Check if service is configured and working"""
        if not self.enabled:
            return {
                'status': 'disabled',
                'message': 'No API keys configured',
                'keys_available': 0
            }
        
        return {
            'status': 'enabled',
            'message': 'Google Genai API configured (NEW package)',
            'keys_available': self.key_rotator.total_keys,
            'keys_used_in_cycle': len(self.key_rotator.failed_keys)
        }


# Global service instance
gemini_service = GeminiService()
