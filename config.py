import os
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file (local development)
    load_dotenv()
except ImportError:
    # In production, environment variables are set directly
    pass

# TradJini API Configuration - only API key needed for direct token flow
TRADEJINI_CONFIG = {
    'apikey': os.getenv('TRADEJINI_APIKEY', ''),
    'access_token': None  # Will be set via admin panel
}

# Database and App Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'development-secret-key-change-in-production')

# Exact Nifty 50 Stock tokens (50 stocks only)
STOCK_TOKENS = {
    "M&M": "2031_NSE",
    "BAJFINANCE": "317_NSE",
    "BAJAJFINSV": "16675_NSE",
    "TRENT": "1964_NSE",
    "APOLLOHOSP": "157_NSE",
    "EICHERMOT": "910_NSE",
    "NESTLEIND": "17963_NSE",
    "GRASIM": "1232_NSE",
    "ITC": "1660_NSE",
    "ICICIBANK": "4963_NSE",
    "HDFCBANK": "1333_NSE",
    "HEROMOTOCO": "1348_NSE",
    "ASIANPAINT": "236_NSE",
    "HINDUNILVR": "1394_NSE",
    "BAJAJ-AUTO": "16669_NSE",
    "DRREDDY": "881_NSE",
    "SHRIRAMFIN": "4306_NSE",
    "TATAMOTORS": "3456_NSE",
    "COALINDIA": "20374_NSE",
    "ADANIPORTS": "15083_NSE",
    "TCS": "11536_NSE",
    "TITAN": "3506_NSE",
    "CIPLA": "694_NSE",
    "ULTRACEMCO": "11532_NSE",
    "JSWSTEEL": "11723_NSE",
    "ADANIENT": "25_NSE",
    "NTPC": "11630_NSE",
    "HINDALCO": "1363_NSE",
    "SBIN": "3045_NSE",
    "BHARTIARTL": "10604_NSE",
    "LT": "11483_NSE",
    "TECHM": "13538_NSE",
    "AXISBANK": "5900_NSE",
    "TATASTEEL": "3499_NSE",
    "KOTAKBANK": "1922_NSE",
    "RELIANCE": "2885_NSE",
    "SUNPHARMA": "3351_NSE",
    "JIOFIN": "18143_NSE",
    "INFY": "1594_NSE",
    "ETERNAL": "5097_NSE",
    "WIPRO": "3787_NSE",
    "MARUTI": "10999_NSE",
    "SBILIFE": "21808_NSE",
    "HCLTECH": "7229_NSE",
    "ONGC": "2475_NSE",
    "BEL": "383_NSE",
    "INDUSINDBK": "5258_NSE",
    "POWERGRID": "14977_NSE",
    "HDFCLIFE": "467_NSE",
    "TATACONSUM": "3432_NSE"
}