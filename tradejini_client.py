import random

class TradejiniClient:
    def __init__(self):
        # Top 50 NSE stocks with mock data
        self.top_stocks = [
            ("RELIANCE", "Reliance Industries Ltd"),
            ("TCS", "Tata Consultancy Services"),
            ("HDFCBANK", "HDFC Bank Ltd"),
            ("INFY", "Infosys Ltd"),
            ("HINDUNILVR", "Hindustan Unilever Ltd"),
            ("ICICIBANK", "ICICI Bank Ltd"),
            ("KOTAKBANK", "Kotak Mahindra Bank"),
            ("BHARTIARTL", "Bharti Airtel Ltd"),
            ("ITC", "ITC Ltd"),
            ("SBIN", "State Bank of India"),
            ("LT", "Larsen & Toubro Ltd"),
            ("ASIANPAINT", "Asian Paints Ltd"),
            ("AXISBANK", "Axis Bank Ltd"),
            ("MARUTI", "Maruti Suzuki India Ltd"),
            ("SUNPHARMA", "Sun Pharmaceutical Industries"),
            ("TITAN", "Titan Company Ltd"),
            ("ULTRACEMCO", "UltraTech Cement Ltd"),
            ("NESTLEIND", "Nestle India Ltd"),
            ("WIPRO", "Wipro Ltd"),
            ("NTPC", "NTPC Ltd"),
            ("TECHM", "Tech Mahindra Ltd"),
            ("HCLTECH", "HCL Technologies Ltd"),
            ("POWERGRID", "Power Grid Corporation"),
            ("BAJFINANCE", "Bajaj Finance Ltd"),
            ("M&M", "Mahindra & Mahindra Ltd"),
            ("TATASTEEL", "Tata Steel Ltd"),
            ("ADANIPORTS", "Adani Ports & SEZ Ltd"),
            ("COALINDIA", "Coal India Ltd"),
            ("BAJAJFINSV", "Bajaj Finserv Ltd"),
            ("DRREDDY", "Dr Reddys Laboratories"),
            ("EICHERMOT", "Eicher Motors Ltd"),
            ("GRASIM", "Grasim Industries Ltd"),
            ("HEROMOTOCO", "Hero MotoCorp Ltd"),
            ("HINDALCO", "Hindalco Industries Ltd"),
            ("INDUSINDBK", "IndusInd Bank Ltd"),
            ("JSWSTEEL", "JSW Steel Ltd"),
            ("ONGC", "Oil & Natural Gas Corp"),
            ("SHREECEM", "Shree Cement Ltd"),
            ("TATAMOTORS", "Tata Motors Ltd"),
            ("UPL", "UPL Ltd"),
            ("BRITANNIA", "Britannia Industries Ltd"),
            ("CIPLA", "Cipla Ltd"),
            ("DIVISLAB", "Divis Laboratories Ltd"),
            ("GODREJCP", "Godrej Consumer Products"),
            ("HDFC", "Housing Development Finance Corp"),
            ("HINDPETRO", "Hindustan Petroleum Corp"),
            ("IOC", "Indian Oil Corporation Ltd"),
            ("SBILIFE", "SBI Life Insurance Company"),
            ("TATACONSUM", "Tata Consumer Products Ltd"),
            ("VEDL", "Vedanta Ltd")
        ]
    
    def get_stock_list(self):
        """Return list of 50 stocks with mock prices"""
        stocks = []
        base_prices = {
            "RELIANCE": 2500, "TCS": 3200, "HDFCBANK": 1600, "INFY": 1400, "HINDUNILVR": 2400,
            "ICICIBANK": 900, "KOTAKBANK": 1800, "BHARTIARTL": 800, "ITC": 450, "SBIN": 550,
            "LT": 2200, "ASIANPAINT": 3000, "AXISBANK": 750, "MARUTI": 9000, "SUNPHARMA": 1100,
            "TITAN": 2800, "ULTRACEMCO": 7500, "NESTLEIND": 18000, "WIPRO": 400, "NTPC": 180,
            "TECHM": 1200, "HCLTECH": 1150, "POWERGRID": 220, "BAJFINANCE": 6500, "M&M": 1400,
            "TATASTEEL": 120, "ADANIPORTS": 750, "COALINDIA": 200, "BAJAJFINSV": 1600, "DRREDDY": 5200,
            "EICHERMOT": 3500, "GRASIM": 1800, "HEROMOTOCO": 2800, "HINDALCO": 400, "INDUSINDBK": 1000,
            "JSWSTEEL": 700, "ONGC": 150, "SHREECEM": 24000, "TATAMOTORS": 450, "UPL": 550,
            "BRITANNIA": 4500, "CIPLA": 1000, "DIVISLAB": 3500, "GODREJCP": 900, "HDFC": 2600,
            "HINDPETRO": 250, "IOC": 85, "SBILIFE": 1300, "TATACONSUM": 800, "VEDL": 250
        }
        
        for symbol, name in self.top_stocks:
            base_price = base_prices.get(symbol, 1000)
            # Add random fluctuation of ±5%
            fluctuation = random.uniform(-0.05, 0.05)
            price = round(base_price * (1 + fluctuation), 2)
            
            stocks.append({
                'symbol': symbol,
                'symbol_id': f"EQT_{symbol}_EQ_NSE",
                'price': price,
                'name': name
            })
        return stocks