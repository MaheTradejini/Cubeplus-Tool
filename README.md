# CubePlus Trading Simulator

A production-ready Flask-based trading simulator with live price streaming from TradJini API, comprehensive admin panel, and real-time portfolio management.

## 🚀 Features

### Core Trading Features
- **Live Price Streaming**: Real-time stock prices from TradJini API via WebSocket
- **Trading Simulation**: Buy/sell stocks with virtual money (₹1,00,000 starting balance)
- **Portfolio Management**: Track holdings, P&L, and performance with live calculations
- **50 NSE Stocks**: Pre-configured with top NSE stocks by market cap
- **Real-time Notifications**: Popup notifications for trade confirmations

### Admin Management System
- **User Management**: Create, edit, activate/deactivate up to 30 users
- **Global TOTP Management**: Centralized TOTP configuration for all users
- **Dashboard Analytics**: User statistics, transaction volume, and activity monitoring
- **Separate Admin Interface**: Dedicated admin login at `/admin`

### Technical Features
- **Token Caching**: Intelligent caching system for TradJini access tokens
- **WebSocket Integration**: Real-time price updates without page refresh
- **Clean UI**: Professional white background with blue accents
- **Production Ready**: Docker support, Gunicorn configuration, proper logging
- **Security**: Password hashing, session management, and role-based access

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- TradJini API credentials (API Key, Password, TOTP)
- Windows/Linux/macOS

## 🛠️ Installation

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Cubeplus-Tool
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create/update `.env` file with your credentials:
```env
# TradJini API Configuration
TRADEJINI_APIKEY=your_api_key_here
TRADEJINI_PASSWORD=your_password_here
TRADEJINI_TWO_FA=your_6_digit_totp_here
TRADEJINI_TWO_FA_TYPE=totp

# Database Configuration
DATABASE_URL=postgresql://postgres:admin123@localhost:5432/cubeplus_tool_db
SECRET_KEY=your_secret_key_here
```

### 5. Initialize Database
```bash
python app.py
```
The database will be created automatically on first run.

## 🎯 Usage

### Development
```bash
python app.py
```

### Production
```bash
# Using Gunicorn (Recommended)
gunicorn -c gunicorn.conf.py wsgi:app

# Using Docker
docker build -t cubeplus-tool .
docker run -p 5000:5000 cubeplus-tool
```

### Access Points
- **User Interface**: `http://localhost:5000/login`
- **Admin Interface**: `http://localhost:5000/admin`

### Default Admin Access
- **Email**: admin@cubeplus.com
- **Password**: admin123

### Admin Functions
1. **Admin Dashboard**: `/admin/dashboard` - System overview and statistics
2. **User Management**: `/admin/users` - Create, edit, and manage users
3. **Global TOTP**: `/admin/global-totp` - Update system-wide TOTP (expires every 24 hours)
4. **Create User**: `/admin/create-user` - Add new users (max 30)

### User Functions
1. **Login**: `/login` - User authentication
2. **Dashboard**: `/dashboard` - Trading interface with live prices
3. **Portfolio**: `/portfolio` - View holdings, P&L, and transaction history

## 📁 Project Structure

```
Cubeplus-Tool/
├── app.py                 # Main Flask application
├── wsgi.py               # Production WSGI entry point
├── models.py              # Database models
├── forms.py               # User forms
├── admin_forms.py         # Admin forms
├── config.py              # Configuration and stock tokens
├── live_price_stream.py   # WebSocket price streaming
├── tradejini_client.py    # TradJini API client
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── gunicorn.conf.py      # Production server config
├── static/               # Static assets
│   ├── favicon.png
│   └── logo_long.png
├── templates/             # HTML templates
│   ├── layout.html
│   ├── home.html
│   ├── login.html
│   ├── dashboard.html
│   ├── portfolio.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── admin_users.html
│   ├── admin_create_user.html
│   ├── admin_edit_user.html
│   └── admin_global_totp.html
└── python-sdk/            # TradJini SDK
    └── streaming/
        └── nxtradstream.py
```

## 🔧 Configuration

### TOTP Management
- **Global TOTP**: Single TOTP for entire system
- **24-hour Expiry**: Admin updates TOTP when it expires
- **Centralized**: No individual user TOTP required

### Stock Configuration
Update `config.py` to modify the list of 50 NSE stocks:
```python
STOCK_TOKENS = {
    "RELIANCE": "2885_NSE",
    "TCS": "11536_NSE",
    # ... add more stocks
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```
   Solution: Ensure PostgreSQL is running and DATABASE_URL is correct
   ```

2. **TradJini Connection Failed**
   ```
   Solution: Update TOTP in admin panel (/admin/global-totp)
   ```

3. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

4. **Port Already in Use**
   ```bash
   # Change port in wsgi.py or gunicorn.conf.py
   ```

## 🔒 Security Features

- **Separate Admin/User Sessions**: Independent login systems
- **Password Hashing**: Werkzeug security
- **Role-based Access**: Admin-only functions protected
- **Environment Variables**: Sensitive data in .env
- **Production Logging**: Proper error handling and logging

## 📊 Performance

- **Token Caching**: Optimized API access
- **WebSocket Streaming**: Real-time updates
- **PostgreSQL**: Production database
- **Gunicorn**: Multi-worker production server
- **Docker Ready**: Containerized deployment

## 🚀 Deployment

### Production Checklist
- ✅ Debug mode disabled
- ✅ Environment variables configured
- ✅ PostgreSQL database setup
- ✅ Gunicorn configuration
- ✅ Docker support
- ✅ Static files served
- ✅ Logging configured

### Docker Deployment
```bash
docker build -t cubeplus-tool .
docker run -d -p 5000:5000 --env-file .env cubeplus-tool
```

### Server Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn -c gunicorn.conf.py wsgi:app
```

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Verify TradJini credentials and TOTP
3. Ensure PostgreSQL is running
4. Check that the market is open for live data

---

**Note**: This is a trading simulator for educational purposes. Always verify with real market data before making actual trading decisions.