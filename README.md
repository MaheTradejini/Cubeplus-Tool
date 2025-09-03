# CubePlus Trading Simulator

Production-ready Flask trading simulator with live TradJini API integration, real-time price streaming, and comprehensive admin panel.

## 🚀 Quick Deploy

```bash
# Setup all deployment configs
python deploy.py

# Deploy to specific platform
python deploy.py railway    # Recommended
python deploy.py render
python deploy.py vercel
python deploy.py docker
python deploy.py local
```

## ✨ Features

- **Live Trading**: Real-time NSE stock prices via TradJini API
- **Portfolio Management**: Track holdings, P&L, performance
- **Admin Panel**: User management, TOTP configuration
- **50 NSE Stocks**: Pre-configured top stocks
- **WebSocket Streaming**: Real-time price updates
- **Production Ready**: Docker, Gunicorn, SQLite/PostgreSQL

## 🔧 Environment Variables

```env
TRADEJINI_APIKEY=your_api_key_here
TRADEJINI_PASSWORD=your_password_here
TRADEJINI_TWO_FA=123456
TRADEJINI_TWO_FA_TYPE=TOTP
DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key
```

## 🎯 Deployment Options

### Railway (Recommended)
1. `python deploy.py railway`
2. Push to GitHub
3. Connect repo to Railway
4. Set environment variables
5. Deploy automatically

### Render
1. `python deploy.py render`
2. Connect GitHub repo
3. Uses render.yaml config
4. Update env vars in dashboard

### Vercel
1. `python deploy.py vercel`
2. Automatic serverless deployment

### Docker
1. `python deploy.py docker`
2. `docker run -p 8000:8000 --env-file .env cubeplus-tool`

### Local Development
1. `python deploy.py local`
2. Access at `http://localhost:8000`

## 🔐 Default Access

- **Admin**: admin@cubeplus.com / admin123
- **User Interface**: `/login`
- **Admin Interface**: `/admin`

## 📊 Core Features

- **Trading Simulation**: ₹1,00,000 starting balance
- **Live Prices**: Real-time TradJini API integration
- **Portfolio Tracking**: Holdings, P&L, transaction history
- **Admin Management**: Up to 30 users, TOTP management
- **Real-time Updates**: WebSocket price streaming
- **Production Database**: SQLite/PostgreSQL support

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, SocketIO
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **API**: TradJini live market data
- **Deployment**: Docker, Gunicorn, multiple platforms
- **Frontend**: HTML, CSS, JavaScript, WebSocket

## 📝 Usage

1. Run `python deploy.py` to setup all configs
2. Choose deployment platform
3. Update environment variables with your TradJini credentials
4. Deploy and start trading simulation

The deployment script handles all platform-specific configurations automatically.