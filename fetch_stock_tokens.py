import requests
import json
from config import TRADEJINI_CONFIG
from token_cache import token_cache

def get_symbol_master():
    """Get symbol master data from TradJini"""
    access_token = token_cache.get_access_token()
    if not access_token:
        return None
    
    try:
        url = "https://api.tradejini.com/api/mkt-data/scrips/symbol-store/Securities"
        headers = {
            "Authorization": f"{TRADEJINI_CONFIG['apikey']}:{access_token}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def extract_top_50_nse_stocks():
    """Extract top 50 NSE stocks and their tokens"""
    
    # Top 50 NSE stocks by market cap
    top_50_symbols = [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR", "ICICIBANK", 
        "KOTAKBANK", "BHARTIARTL", "ITC", "SBIN", "LT", "ASIANPAINT", 
        "AXISBANK", "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "NESTLEIND", 
        "WIPRO", "NTPC", "TECHM", "HCLTECH", "POWERGRID", "BAJFINANCE", 
        "M&M", "TATASTEEL", "ADANIPORTS", "COALINDIA", "BAJAJFINSV", "DRREDDY", 
        "EICHERMOT", "GRASIM", "HEROMOTOCO", "HINDALCO", "INDUSINDBK", 
        "JSWSTEEL", "ONGC", "SHREECEM", "TATAMOTORS", "UPL", "BRITANNIA", 
        "CIPLA", "DIVISLAB", "GODREJCP", "HDFC", "HINDPETRO", "IOC", 
        "SBILIFE", "TATACONSUM", "VEDL"
    ]
    
    symbol_data = get_symbol_master()
    if not symbol_data:
        print("Could not fetch symbol master data")
        return generate_mock_tokens(top_50_symbols)
    
    stock_tokens = {}
    
    try:
        # Parse symbol master data (format may vary)
        if isinstance(symbol_data, list):
            for item in symbol_data:
                if isinstance(item, dict):
                    symbol = item.get('symbol', '').upper()
                    token = item.get('token', '')
                    exchange = item.get('exchange', '').upper()
                    
                    # Match NSE equity stocks
                    if symbol in top_50_symbols and exchange == 'NSE':
                        stock_tokens[symbol] = f"{token}_NSE"
        
        elif isinstance(symbol_data, str):
            # If CSV format, parse it
            lines = symbol_data.strip().split('\n')
            for line in lines[1:]:  # Skip header
                parts = line.split(',')
                if len(parts) >= 4:
                    token = parts[0].strip()
                    symbol = parts[1].strip().upper()
                    exchange = parts[3].strip().upper()
                    
                    if symbol in top_50_symbols and exchange == 'NSE':
                        stock_tokens[symbol] = f"{token}_NSE"
        
        # Fill missing stocks with mock tokens
        for symbol in top_50_symbols:
            if symbol not in stock_tokens:
                stock_tokens[symbol] = f"MOCK_{symbol}_NSE"
        
        return stock_tokens
        
    except:
        return generate_mock_tokens(top_50_symbols)

def generate_mock_tokens(symbols):
    """Generate mock tokens for testing"""
    return {symbol: f"MOCK_{symbol}_NSE" for symbol in symbols}

def update_config_file(stock_tokens):
    """Update config.py with new stock tokens"""
    try:
        # Read current config
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Generate new STOCK_TOKENS dictionary
        tokens_str = "STOCK_TOKENS = {\n"
        for symbol, token in stock_tokens.items():
            tokens_str += f'    "{symbol}": "{token}",\n'
        tokens_str += "}"
        
        # Replace the STOCK_TOKENS section
        import re
        pattern = r'STOCK_TOKENS = \{[^}]*\}'
        new_content = re.sub(pattern, tokens_str, content, flags=re.DOTALL)
        
        # Write updated config
        with open('config.py', 'w') as f:
            f.write(new_content)
        
        pass
        
    except:
        pass

if __name__ == "__main__":
    stock_tokens = extract_top_50_nse_stocks()
    if stock_tokens:
        update_config_file(stock_tokens)
        print(f"Updated {len(stock_tokens)} stock tokens")
    else:
        print("Failed to fetch stock tokens")