# CubePlus Trading Simulator - Local Development

Advanced Flask trading simulator with live TradJini API integration, real-time price streaming, short selling, and comprehensive portfolio management.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd Cubeplus-Tool

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your TradJini credentials

# Run locally
python app.py
```

Access at: `http://127.0.0.1:8000`

## ✨ Features

- **Live Trading**: Real-time NSE stock prices via TradJini API
- **Short Selling**: Full short selling support with P&L tracking
- **Portfolio Management**: Track holdings, shorts, realized/unrealized P&L
- **Admin Panel**: User management, TOTP configuration
- **50 Nifty Stocks**: Complete Nifty 50 with correct tokens
- **WebSocket Streaming**: Real-time price updates
- **Closed Position P&L**: Track realized gains/losses

## 🔧 Environment Setup

Create `.env` file:

```env
TRADEJINI_APIKEY=your_api_key_here
TRADEJINI_PASSWORD=your_password_here
TRADEJINI_TWO_FA=123456
TRADEJINI_TWO_FA_TYPE=TOTP
```

## 🎯 Usage

1. **Start Application**: `python app.py`
2. **Admin Login**: `/admin` with `admin@cubeplus.com` / `admin123`
3. **Update TOTP**: Go to "Global TOTP Settings" and enter current 6-digit code
4. **Start Live Prices**: Click "Start Live Prices" button in admin dashboard
5. **User Trading**: Login at `/login` and start trading

## 🔐 Default Access

- **Admin**: admin@cubeplus.com / admin123
- **User Interface**: `/login`
- **Admin Interface**: `/admin`

## 📊 Trading Features

### Long Positions
- **Buy Stocks**: Purchase with ₹1,00,000 starting balance
- **Sell Stocks**: Sell owned shares
- **Real-time P&L**: Live profit/loss calculation

### Short Selling
- **Short Sell**: Sell stocks you don't own
- **Cover Positions**: Buy back to close short positions
- **Collateral Management**: Automatic margin requirements
- **Short P&L**: Real-time unrealized gains/losses

### Portfolio Tracking
- **Current Holdings**: Long positions with live P&L
- **Short Positions**: Active shorts with unrealized P&L
- **Closed P&L**: Realized gains/losses from closed trades
- **Transaction History**: Complete trade log

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, SocketIO
- **Database**: SQLite (local development)
- **API**: TradJini live market data
- **Frontend**: HTML, CSS, JavaScript, WebSocket
- **Real-time**: Live price streaming via WebSocket

## 📝 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your TradJini credentials

# Run with debug
python app.py

# Access application
http://127.0.0.1:8000
```

## 🔄 Trading Simulation Rules

### Initial Setup
- Each user starts with ₹100,000 cash balance
- Admin can create up to 30 users

### Buy Orders
- Deduct cost from balance: `balance -= quantity × price`
- Add shares to portfolio
- If covering short position: Calculate P&L and close short

### Sell Orders
- If shares available: Normal sell, add proceeds to balance
- If insufficient shares: Short sell with collateral requirement
- Collateral reserved: `balance -= quantity × price`

### Short Selling
- Sell without owning shares
- Reserve collateral equal to sale value
- Track average sell price and quantity
- Calculate unrealized P&L: `(sell_price - current_price) × quantity`

### Covering Shorts
- Buy back shares to close short position
- Calculate realized P&L: `(sell_price - buy_price) × quantity`
- Add/deduct P&L from balance
- Record in closed positions

## 🎯 Key Features

- **Real-time Prices**: Live Nifty 50 stock prices
- **Short Selling**: Complete short selling implementation
- **P&L Tracking**: Both unrealized and realized P&L
- **Admin Management**: User creation, TOTP management
- **WebSocket Updates**: Real-time price and P&L updates
- **Search Functionality**: Search through 50 Nifty stocks

Perfect for learning trading concepts with real market data!