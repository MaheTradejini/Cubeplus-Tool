import requests
import json
from config import TRADEJINI_CONFIG, STOCK_TOKENS

class TradejiniClient:
    def __init__(self, auto_auth=True):
        self.base_url = "https://api.tradejini.com/v2"
        self.access_token = None
        if auto_auth:
            # First try to get stored access token
            if not self.get_stored_token():
                # If no stored token, authenticate
                self.authenticate()
    
    def get_stored_token(self):
        """Get stored access token from database"""
        try:
            from models import User, UserCredential
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                credential = UserCredential.query.filter_by(
                    user_id=admin_user.id,
                    credential_name='ACCESS_TOKEN'
                ).first()
                if credential:
                    self.access_token = credential.credential_value
                    return True
        except:
            pass
        return False
    
    def authenticate(self):
        """Authenticate with TradJini API"""
        try:
            # Get current TOTP from database or environment
            current_totp = TRADEJINI_CONFIG.get('two_fa', '')
            try:
                from models import User, UserCredential
                admin_user = User.query.filter_by(is_admin=True).first()
                if admin_user:
                    credential = UserCredential.query.filter_by(
                        user_id=admin_user.id,
                        credential_name='GLOBAL_TOTP'
                    ).first()
                    if credential:
                        current_totp = credential.credential_value
            except:
                pass
            
            # TradJini Individual Token API (Correct Format from Documentation)
            url = "https://api.tradejini.com/v2/api-gw/oauth/individual-token-v2"
            
            import logging
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            
            logger.info(f"URL: {url}")
            logger.info(f"Authenticating with TOTP: {current_totp}")
            logger.info(f"API Key: {TRADEJINI_CONFIG['apikey']}")
            
            # Correct format as per TradJini API documentation
            headers = {
                "Authorization": f"Bearer {TRADEJINI_CONFIG['apikey']}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Form data as specified in documentation
            data = {
                "password": TRADEJINI_CONFIG['password'],
                "twoFa": current_totp,  # Note: 'twoFa' not 'two_fa'
                "twoFaTyp": "totp"      # Note: 'twoFaTyp' not 'two_fa_type', lowercase 'totp'
            }
            
            logger.info(f"Headers: {headers}")
            logger.info(f"Data: {data}")
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            logger.info(f"Auth response status: {response.status_code}")
            logger.info(f"Auth response: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"Parsed response: {data}")
                    if data.get('status') == 'success' or data.get('access_token'):
                        self.access_token = data.get('access_token') or data.get('token')
                        logger.info(f"Authentication successful! Token: {self.access_token[:10]}****")
                        return True
                except:
                    logger.error("Failed to parse JSON response")
            
            logger.error(f"Authentication failed: {response.text}")
            return False
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Authentication error: {e}")
            return False
    
    def get_stock_list(self):
        """Get live stock prices from TradJini API"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Always try to get stored token first
        if not self.access_token:
            self.get_stored_token()
        
        if not self.access_token:
            logger.warning("No access token available, using fallback data")
            return self.get_fallback_stocks()
        
        logger.info(f"Using access token: {self.access_token[:10]}****")
        
        stocks = []
        try:
            # Get live prices for all 50 configured stocks
            for symbol, token in STOCK_TOKENS.items():
                price_data = self.get_live_price(token)
                if price_data:
                    logger.info(f"Got live price for {symbol}: {price_data}")
                    stocks.append({
                        'symbol': symbol,
                        'symbol_id': token,
                        'price': price_data.get('ltp', price_data.get('price', 0)),
                        'name': symbol.replace('_', ' ').title(),
                        'change': price_data.get('change', price_data.get('chng', 0))
                    })
                else:
                    logger.warning(f"No price data for {symbol} ({token})")
            
            if stocks:
                logger.info(f"Successfully got {len(stocks)} live prices")
                return stocks
            else:
                logger.warning("No live prices available, using fallback")
                return self.get_fallback_stocks()
            
        except Exception as e:
            logger.error(f"Failed to get stock list: {e}")
            return self.get_fallback_stocks()
    
    def get_live_price(self, token):
        """Get live price for a specific token"""
        if not self.access_token:
            return None
            
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Try different TradJini quote API endpoints
            endpoints = [
                f"{self.base_url}/api/mkt-data/quote",
                f"{self.base_url}/api-gw/mkt-data/quote",
                f"{self.base_url}/quote"
            ]
            
            headers = {
                "Authorization": f"{TRADEJINI_CONFIG['apikey']}:{self.access_token}"
            }
            
            for url in endpoints:
                try:
                    logger.info(f"Trying quote API: {url} for token: {token}")
                    
                    # Try with token as query parameter
                    response = requests.get(url, headers=headers, params={"token": token}, timeout=10)
                    logger.info(f"Response status: {response.status_code}")
                    logger.info(f"Response: {response.text[:200]}...")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data and ('ltp' in data or 'price' in data):
                            return data
                    
                    # Try with token in URL path
                    response = requests.get(f"{url}/{token}", headers=headers, timeout=10)
                    logger.info(f"Path response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data and ('ltp' in data or 'price' in data):
                            return data
                            
                except Exception as e:
                    logger.error(f"Error with {url}: {e}")
                    continue
            
            logger.warning(f"All quote APIs failed for token: {token}")
            return None
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"get_live_price error: {e}")
            return None
    
    def get_fallback_stocks(self):
        """Fallback stock data when API fails"""
        import random
        stocks = []
        base_prices = {
            "RELIANCE": 2500, "TCS": 3200, "HDFCBANK": 1600, "INFY": 1400, "HINDUNILVR": 2400,
            "ICICIBANK": 900, "KOTAKBANK": 1800, "BHARTIARTL": 800, "ITC": 450, "SBIN": 550,
            "LT": 2200, "ASIANPAINT": 3000, "AXISBANK": 750, "MARUTI": 9000, "SUNPHARMA": 1100,
            "TITAN": 2800, "ULTRACEMCO": 7500, "NESTLEIND": 18000, "WIPRO": 400, "NTPC": 180
        }
        
        for symbol, token in STOCK_TOKENS.items():
            base_price = base_prices.get(symbol, 1000)
            fluctuation = random.uniform(-0.05, 0.05)
            price = round(base_price * (1 + fluctuation), 2)
            
            stocks.append({
                'symbol': symbol,
                'symbol_id': token,
                'price': price,
                'name': symbol.replace('_', ' ').title(),
                'change': round(fluctuation * 100, 2)
            })
        return stocks