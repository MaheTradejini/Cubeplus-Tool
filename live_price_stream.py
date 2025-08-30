import time
import threading
import json
from flask_socketio import SocketIO, emit
import requests

# Global price storage
live_prices = {}

class LivePriceStreamer:
    def __init__(self, socketio):
        self.socketio = socketio
        self.is_connected = False
        
        # Top 50 NSE stock tokens (you'll need to get actual tokens from TradJini API)
        self.stock_tokens = {
            "22_NSE": "RELIANCE",
            "3045_NSE": "SBIN", 
            "1594_NSE": "INFY",
            "11536_NSE": "TCS",
            "1333_NSE": "HDFCBANK",
            # Add more tokens for your 50 stocks
        }
        
    def getAccessToken(self, host, apikey, password, twoFa, twoFaType):
        url = f"https://{host}/v2/api-gw/oauth/individual-token-v2"
        headers = {"Authorization": f"Bearer {apikey}"}
        postParams = {'password': password, 'twoFa': twoFa, 'twoFaTyp': twoFaType}
        
        try:
            response = requests.post(url, data=postParams, headers=headers)
            if response.status_code == 200:
                return response.json()['access_token']
        except:
            pass
        return None
    
    def stream_callback(self, data):
        """Handle incoming price data"""
        try:
            if 'tk' in data and 'lp' in data:  # token and last price
                token = data['tk']
                price = float(data['lp'])
                
                if token in self.stock_tokens:
                    symbol = self.stock_tokens[token]
                    live_prices[symbol] = price
                    
                    # Emit to all connected clients
                    self.socketio.emit('price_update', {
                        'symbol': symbol,
                        'price': price
                    })
        except Exception as e:
            print(f"Error processing price data: {e}")
    
    def start_mock_stream(self):
        """Mock price streaming for demo (replace with real TradJini stream)"""
        import random
        
        base_prices = {
            "RELIANCE": 2500, "TCS": 3200, "HDFCBANK": 1600, "INFY": 1400, 
            "HINDUNILVR": 2400, "ICICIBANK": 900, "KOTAKBANK": 1800, 
            "BHARTIARTL": 800, "ITC": 450, "SBIN": 550
        }
        
        def mock_price_generator():
            while True:
                for symbol, base_price in base_prices.items():
                    # Generate price with ±2% fluctuation
                    fluctuation = random.uniform(-0.02, 0.02)
                    new_price = round(base_price * (1 + fluctuation), 2)
                    live_prices[symbol] = new_price
                    
                    self.socketio.emit('price_update', {
                        'symbol': symbol,
                        'price': new_price
                    })
                
                time.sleep(1)  # Update every second
        
        thread = threading.Thread(target=mock_price_generator, daemon=True)
        thread.start()
    
    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        return live_prices.get(symbol, 0.0)