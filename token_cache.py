import json
import time
import os
import requests
from config import TRADEJINI_CONFIG

CACHE_FILE = 'tradejini_token_cache.json'
TOKEN_VALIDITY_HOURS = 8

class TokenCache:
    def __init__(self):
        self.cache_data = self.load_cache()
    
    def load_cache(self):
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_cache(self):
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(self.cache_data, f)
        except:
            pass
    
    def is_token_valid(self):
        if 'access_token' not in self.cache_data or 'timestamp' not in self.cache_data:
            return False
        
        token_age = time.time() - self.cache_data['timestamp']
        max_age = TOKEN_VALIDITY_HOURS * 3600
        
        return token_age < max_age
    
    def get_fresh_token(self):
        try:
            url = "https://api.tradejini.com/v2/api-gw/oauth/individual-token-v2"
            headers = {"Authorization": f"Bearer {TRADEJINI_CONFIG['apikey']}"}
            data = {
                'password': TRADEJINI_CONFIG['password'],
                'twoFa': TRADEJINI_CONFIG['two_fa'],
                'twoFaTyp': TRADEJINI_CONFIG['two_fa_type']
            }
            
            response = requests.post(url, data=data, headers=headers)
            if response.status_code == 200:
                resp_data = response.json()
                if 'access_token' in resp_data:
                    self.cache_data = {
                        'access_token': resp_data['access_token'],
                        'timestamp': time.time()
                    }
                    self.save_cache()
                    return resp_data['access_token']
        except:
            pass
        return None
    
    def get_access_token(self):
        if self.is_token_valid():
            return self.cache_data['access_token']
        else:
            return self.get_fresh_token()
    
    def invalidate_cache(self):
        self.cache_data = {}
        if os.path.exists(CACHE_FILE):
            try:
                os.remove(CACHE_FILE)
            except:
                pass

token_cache = TokenCache()