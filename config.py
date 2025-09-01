import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# TradJini API Configuration - loaded from environment variables
TRADEJINI_CONFIG = {
    'apikey': os.getenv('TRADEJINI_APIKEY', ''),
    'password': os.getenv('TRADEJINI_PASSWORD', ''),
    'two_fa': os.getenv('TRADEJINI_TWO_FA', ''),
    'two_fa_type': os.getenv('TRADEJINI_TWO_FA_TYPE', 'TOTP')
}

# Database and App Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:admin123@localhost:5432/cubeplus_tool_db')
SECRET_KEY = os.getenv('SECRET_KEY', 'APPSECRECTKEY')

# Stock tokens - you need to get these from TradJini symbol master API
STOCK_TOKENS = {
    "RELIANCE": "22_NSE",
    "SBIN": "3045_NSE", 
    "INFY": "1594_NSE",
    "TCS": "11536_NSE",
    "HDFCBANK": "1333_NSE",
    "ICICIBANK": "4963_NSE",
    "KOTAKBANK": "1922_NSE",
    "BHARTIARTL": "10604_NSE",
    "ITC": "424_NSE",
    "HINDUNILVR": "356_NSE",
    "LT": "17963_NSE",
    "ASIANPAINT": "3718_NSE",
    "AXISBANK": "5900_NSE",
    "MARUTI": "10999_NSE",
    "SUNPHARMA": "3351_NSE",
    "TITAN": "3506_NSE",
    "ULTRACEMCO": "11532_NSE",
    "NESTLEIND": "17963_NSE",
    "WIPRO": "3787_NSE",
    "NTPC": "11630_NSE",
    "TECHM": "13538_NSE",
    "HCLTECH": "7229_NSE",
    "POWERGRID": "14977_NSE",
    "BAJFINANCE": "317_NSE",
    "M&M": "519_NSE",
    "TATASTEEL": "895_NSE",
    "ADANIPORTS": "15083_NSE",
    "COALINDIA": "20374_NSE",
    "BAJAJFINSV": "16675_NSE",
    "DRREDDY": "881_NSE",
    "EICHERMOT": "910_NSE",
    "GRASIM": "1232_NSE",
    "HEROMOTOCO": "1348_NSE",
    "HINDALCO": "1363_NSE",
    "INDUSINDBK": "1394_NSE",
    "JSWSTEEL": "11723_NSE",
    "ONGC": "2475_NSE",
    "SHREECEM": "3512_NSE",
    "TATAMOTORS": "3456_NSE",
    "UPL": "11287_NSE",
    "BRITANNIA": "547_NSE",
    "CIPLA": "694_NSE",
    "DIVISLAB": "10940_NSE",
    "GODREJCP": "10099_NSE",
    "HDFC": "1330_NSE",
    "HINDPETRO": "1406_NSE",
    "IOC": "1624_NSE",
    "SBILIFE": "21808_NSE",
    "TATACONSUM": "18096_NSE",
    "VEDL": "3063_NSE"
}