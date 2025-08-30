import json
import time
import os
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self, token_file='access_token.json'):
        self.token_file = token_file
    
    def save_token(self, access_token):
        """Save access token with expiry time"""
        token_data = {
            'access_token': access_token,
            'expires_at': (datetime.now() + timedelta(hours=24)).timestamp()
        }
        
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f)
        except Exception as e:
            print(f"Error saving token: {e}")
    
    def get_valid_token(self):
        """Get token if still valid"""
        try:
            if not os.path.exists(self.token_file):
                return None
            
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            # Check if token is still valid
            if datetime.now().timestamp() < token_data['expires_at']:
                return token_data['access_token']
            else:
                # Token expired, remove file
                os.remove(self.token_file)
                return None
                
        except Exception as e:
            print(f"Error reading token: {e}")
            return None
    
    def clear_token(self):
        """Clear stored token"""
        try:
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
        except Exception as e:
            print(f"Error clearing token: {e}")