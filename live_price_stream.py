import sys
import os
import time
import threading

# Import TradJini SDK with proper error handling
try:
    from nxtradstream import NxtradStream
    SDK_AVAILABLE = True
    print("TradJini SDK loaded successfully")
except ImportError as e:
    SDK_AVAILABLE = False
    NxtradStream = None
    print(f"TradJini SDK not available: {e}")

from config import TRADEJINI_CONFIG, STOCK_TOKENS
# Remove token_cache dependency - using database tokens now
# from token_cache import token_cache

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
        """Get access token from database (stored by admin)"""
        try:
            from flask import current_app
            with current_app.app_context():
                from models import User, UserCredential
                admin_user = User.query.filter_by(is_admin=True).first()
                if admin_user:
                    credential = UserCredential.query.filter_by(
                        user_id=admin_user.id,
                        credential_name='ACCESS_TOKEN'
                    ).first()
                    if credential and not credential.credential_value.startswith('MOCK_'):
                        self.access_token = credential.credential_value
                        print(f"Using access token: {self.access_token[:10]}****")
                        return True
        except Exception as e:
            print(f"Error getting access token: {e}")
        return False
    
    def connect_callback(self, nx_stream, event):
        """Handle TradJini WebSocket connection events"""
        if event['s'] == "connected":
            self.is_connected = True
            print("TradJini WebSocket connected")
            
            # Subscribe to live data for all stocks (TradJini format)
            stock_token_list = list(STOCK_TOKENS.values())
            try:
                # Subscribe to L1 data (live prices) - order matters
                nx_stream.subscribeL1SnapShot(stock_token_list)  # Get snapshot first
                nx_stream.subscribeL1(stock_token_list)          # Then live updates
                print(f"Subscribed to {len(stock_token_list)} stocks for live prices")
            except Exception as e:
                print(f"Subscription error: {e}")
                
        elif event['s'] == "closed":
            self.is_connected = False
            reason = event.get("reason", "Unknown")
            print(f"WebSocket closed: {reason}")
            
            if reason != "Unauthorized Access":
                # Try to reconnect after 30 seconds
                time.sleep(30)
                if self.get_access_token():
                    auth_token = f"{TRADEJINI_CONFIG['apikey']}:{self.access_token}"
                    try:
                        nx_stream.reconnect()
                    except Exception as e:
                        print(f"Reconnection error: {e}")
                
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
            
            if NxtradStream is not None:
                self.nx_stream = NxtradStream(
                    'api.tradejini.com',
                    stream_cb=self.stream_callback,
                    connect_cb=self.connect_callback
                )
            else:
                return False
            
            def connect_stream():
                try:
                    self.nx_stream.connect(auth_token)
                except Exception as e:
                    print(f"Stream connection error: {e}")
            
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
    
    def start_price_simulation(self):
        """Start simulated price updates when live stream unavailable"""
        import random
        
        def simulate_prices():
            while True:
                try:
                    # Update prices for random stocks every 2-5 seconds
                    symbols = list(STOCK_TOKENS.keys())
                    symbol = random.choice(symbols)
                    
                    # Get current price or generate base price
                    current_price = live_prices.get(symbol, 500 + random.randint(0, 2000))
                    
                    # Generate realistic price movement (-2% to +2%)
                    change_percent = random.uniform(-0.02, 0.02)
                    new_price = current_price * (1 + change_percent)
                    new_price = max(1.0, round(new_price, 2))  # Minimum ₹1
                    
                    live_prices[symbol] = new_price
                    
                    # Emit price update via WebSocket
                    self.socketio.emit('price_update', {
                        'symbol': symbol,
                        'price': new_price
                    })
                    
                    # Random delay between updates
                    time.sleep(random.uniform(2, 5))
                    
                except Exception as e:
                    print(f"Price simulation error: {e}")
                    time.sleep(5)
        
        # Start simulation in background thread
        sim_thread = threading.Thread(target=simulate_prices, daemon=True)
        sim_thread.start()
        self.is_connected = True
        print("Started price simulation - prices will fluctuate every 2-5 seconds")
    
    def stop_stream(self):
        """Stop the live stream"""
        if self.nx_stream:
            self.nx_stream.disconnect()
        self.is_connected = False