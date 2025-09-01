import sys
import os
import time
import threading

# Add the streaming SDK path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python-sdk', 'streaming'))

try:
    from nxtradstream import NxtradStream
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("TradJini SDK not available")

from config import TRADEJINI_CONFIG, STOCK_TOKENS
from token_cache import token_cache

# Global price storage
live_prices = {}
price_update_count = 0

class LivePriceStreamer:
    def __init__(self, socketio):
        self.socketio = socketio
        self.nx_stream = None
        self.is_connected = False
        self.access_token = None
        
        # Create token to symbol mapping
        self.token_to_symbol = {}
        for symbol, token in STOCK_TOKENS.items():
            self.token_to_symbol[token] = symbol
        
    def get_access_token(self):
        """Get access token using cached token system"""
        try:
            self.access_token = token_cache.get_access_token()
            return self.access_token is not None
        except:
            return False
    
    def connect_callback(self, nx_stream, event):
        """Handle TradJini WebSocket connection events"""
        if event['s'] == "connected":
            self.is_connected = True
            print("TradJini WebSocket connected")
            
            stock_token_list = list(STOCK_TOKENS.values())
            try:
                nx_stream.subscribeL1(stock_token_list)
                nx_stream.subscribeL1SnapShot(stock_token_list)
                print(f"Subscribed to {len(stock_token_list)} stocks")
            except:
                pass
                
        elif event['s'] == "closed":
            self.is_connected = False
            reason = event.get("reason", "Unknown")
            
            if reason != "Unauthorized Access":
                time.sleep(30)
                token_cache.invalidate_cache()
                if self.get_access_token():
                    auth_token = f"{TRADEJINI_CONFIG['apikey']}:{self.access_token}"
                    nx_stream.reconnect(auth_token)
            else:
                token_cache.invalidate_cache()
                
        elif event['s'] == "error":
            self.is_connected = False
    
    def stream_callback(self, nx_stream, data):
        """Handle incoming live price data from TradJini"""
        try:
            if isinstance(data, dict) and data.get('msgType') == 'L1' and 'symbol' in data:
                symbol_token = data['symbol']
                symbol = self.token_to_symbol.get(symbol_token)
                if symbol:
                    price = data.get('ltp', 0.0)
                    if price > 0:
                        live_prices[symbol] = float(price)
                        
                        self.socketio.emit('price_update', {
                            'symbol': symbol,
                            'price': float(price)
                        })
                        
                        global price_update_count
                        price_update_count += 1
        except:
            pass
    
    def start_live_stream(self):
        """Start TradJini SDK live price streaming"""
        if not SDK_AVAILABLE:
            return False
        
        if not self.get_access_token():
            return False
        
        try:
            auth_token = f"{TRADEJINI_CONFIG['apikey']}:{self.access_token}"
            
            self.nx_stream = NxtradStream(
                'api.tradejini.com',
                stream_cb=self.stream_callback,
                connect_cb=self.connect_callback
            )
            
            def connect_stream():
                try:
                    self.nx_stream.connect(auth_token)
                except:
                    token_cache.invalidate_cache()
            
            stream_thread = threading.Thread(target=connect_stream, daemon=True)
            stream_thread.start()
            
            return True
            
        except:
            return False
    
    def get_current_price(self, symbol):
        """Get current live price for a symbol"""
        price = live_prices.get(symbol, 0.0)
        return price
    
    def is_market_open(self):
        """Check if market is open and receiving live data"""
        return self.is_connected and len(live_prices) > 0
    
    def get_connection_status(self):
        """Get detailed connection status"""
        return {
            'connected': self.is_connected,
            'stocks_with_prices': len(live_prices),
            'total_stocks': len(STOCK_TOKENS),
            'sdk_available': SDK_AVAILABLE
        }
    
    def stop_stream(self):
        """Stop the live stream"""
        if self.nx_stream:
            self.nx_stream.disconnect()
        self.is_connected = False