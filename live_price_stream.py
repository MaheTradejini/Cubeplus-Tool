import sys
import os
import time
import threading
import requests

# Import TradJini SDK
try:
    from nxtradstream import NxtradStream
    SDK_AVAILABLE = True
    print("TradJini SDK loaded successfully")
except ImportError as e:
    SDK_AVAILABLE = False
    NxtradStream = None
    print(f"TradJini SDK not available: {e}")

from config import TRADEJINI_CONFIG, STOCK_TOKENS

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
        """Get access token - reuse stored token if valid (24hrs)"""
        try:
            from models import User, UserCredential
            admin_user = User.query.filter_by(is_admin=True).first()
            if admin_user:
                # Check for existing valid access token
                token_credential = UserCredential.query.filter_by(
                    user_id=admin_user.id,
                    credential_name='ACCESS_TOKEN'
                ).first()
                
                if token_credential and not token_credential.credential_value.startswith('MOCK_'):
                    self.access_token = token_credential.credential_value
                    print(f"Using stored access token: {self.access_token[:10]}****")
                    return self.access_token
                
                print("No valid stored token found, generating new one...")
                return None
            
        except Exception as e:
            print(f"Error getting stored access token: {e}")
            return None
    
    def connect_callback(self, nx_stream, event):
        """Handle TradJini WebSocket connection events"""
        print(f"Connection event: {event}")
        
        if event['s'] == "connected":
            self.is_connected = True
            print("TradJini WebSocket connected successfully")
            
            # Subscribe to live data for all stocks using SDK format
            stock_token_list = list(STOCK_TOKENS.values())
            try:
                # Subscribe using proper SDK methods
                nx_stream.subscribeL1SnapShot(stock_token_list)  # Get snapshot first
                nx_stream.subscribeL1(stock_token_list)          # Then live updates
                print(f"Subscribed to {len(stock_token_list)} stocks for live prices")
            except Exception as e:
                print(f"Subscription error: {e}")
                
        elif event['s'] == "closed":
            self.is_connected = False
            reason = event.get("reason", "Unknown")
            print(f"WebSocket closed: {reason}")
            
            # Reconnect if not unauthorized
            if reason != "Unauthorized Access":
                print("Attempting to reconnect in 30 seconds...")
                time.sleep(30)
                try:
                    nx_stream.reconnect()
                except Exception as e:
                    print(f"Reconnection error: {e}")
                
        elif event['s'] == "error":
            self.is_connected = False
            print(f"WebSocket error: {event}")
    
    def stream_callback(self, nx_stream, data):
        """Handle incoming live price data from TradJini"""
        try:
            # Handle L1 (live price) data
            if isinstance(data, dict) and data.get('msgType') == 'L1':
                symbol_token = data.get('symbol')  # Format: "token_exchange"
                if symbol_token:
                    # Extract just the token part
                    token = symbol_token.split('_')[0] + '_NSE'
                    symbol = self.token_to_symbol.get(token)
                    
                    if symbol:
                        price = data.get('ltp', 0.0)
                        if price > 0:
                            live_prices[symbol] = float(price)
                            
                            # Emit price update via WebSocket to frontend
                            self.socketio.emit('price_update', {
                                'symbol': symbol,
                                'price': float(price)
                            })
                            
                            global price_update_count
                            price_update_count += 1
                            
                            if price_update_count % 10 == 0:  # Log every 10th update
                                print(f"Price update #{price_update_count}: {symbol} = ₹{price}")
                                
        except Exception as e:
            print(f"Stream callback error: {e}")
    
    def start_live_stream(self):
        """Start TradJini SDK live price streaming"""
        if not SDK_AVAILABLE:
            print("TradJini SDK not available")
            return False
        
        # Get access token (stored or generate new)
        if not self.get_access_token():
            print("Failed to get access token")
            return False
        
        try:
            # Create auth token in SDK format: apikey:access_token
            auth_token = f"{TRADEJINI_CONFIG['apikey']}:{self.access_token}"
            print(f"Starting WebSocket with auth token: {auth_token[:30]}****")
            
            # Initialize NxtradStream with callbacks
            self.nx_stream = NxtradStream(
                'api.tradejini.com',
                stream_cb=self.stream_callback,
                connect_cb=self.connect_callback
            )
            
            # Connect in background thread
            def connect_stream():
                try:
                    self.nx_stream.connect(auth_token)
                except Exception as e:
                    print(f"Stream connection error: {e}")
            
            stream_thread = threading.Thread(target=connect_stream, daemon=True)
            stream_thread.start()
            
            print("Live streaming started successfully")
            return True
            
        except Exception as e:
            print(f"Failed to start streaming: {e}")
            return False
    
    def get_current_price(self, symbol):
        """Get current live price for a symbol"""
        return live_prices.get(symbol, 0.0)
    
    def is_market_open(self):
        """Check if market is open and receiving live data"""
        return self.is_connected and len(live_prices) > 0
    
    def get_connection_status(self):
        """Get detailed connection status"""
        return {
            'connected': self.is_connected,
            'stocks_with_prices': len(live_prices),
            'total_stocks': len(STOCK_TOKENS),
            'sdk_available': SDK_AVAILABLE,
            'price_updates': price_update_count
        }
    
    def stop_stream(self):
        """Stop the live stream"""
        if self.nx_stream:
            self.nx_stream.disconnect()
        self.is_connected = False