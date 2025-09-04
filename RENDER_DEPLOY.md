# 🚀 Deploy CubePlus Trading Simulator to Render

## Prerequisites
- GitHub account
- Render account (free tier available)
- Your code pushed to GitHub repository

## Step-by-Step Deployment

### 1. Prepare Repository
```bash
# Push your code to GitHub
git add .
git commit -m "Production ready for Render deployment"
git push origin main
```

### 2. Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Authorize Render to access your repositories

### 3. Deploy Database First

#### Create PostgreSQL Database:
1. Click **"New +"** → **"PostgreSQL"**
2. **Name**: `cubeplus-trading-db`
3. **Database**: `cubeplus_trading`
4. **User**: `cubeplus_user`
5. **Region**: Choose closest to your users
6. **Plan**: Free (or Starter for better performance)
7. Click **"Create Database"**
8. **Wait** for database to be ready (2-3 minutes)

### 4. Deploy Web Application

#### Create Web Service:
1. Click **"New +"** → **"Web Service"**
2. **Connect Repository**: Select your GitHub repo
3. **Name**: `cubeplus-trading-app`
4. **Environment**: `Python 3`
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi:application`

### 5. Configure Environment Variables

Add these environment variables in Render dashboard:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `your-random-secret-key-here` |
| `TRADEJINI_APIKEY` | `49ddd64cacba20b25376edb24c1d17ad` |
| `TRADEJINI_PASSWORD` | `Gopal7463@` |
| `TRADEJINI_TWO_FA` | `123456` |
| `TRADEJINI_TWO_FA_TYPE` | `TOTP` |
| `DATABASE_URL` | *Copy from PostgreSQL service* |

#### Get Database URL:
1. Go to your PostgreSQL service
2. Copy **"External Database URL"**
3. Paste as `DATABASE_URL` in web service

### 6. Deploy Application
1. Click **"Create Web Service"**
2. Wait for build and deployment (5-10 minutes)
3. Your app will be available at: `https://your-app-name.onrender.com`

### 7. Initial Setup

#### Access Admin Panel:
1. Go to: `https://your-app-name.onrender.com/admin`
2. Login: `admin@cubeplus.com` / `admin123`
3. Go to **"Global TOTP Settings"**
4. Enter current TOTP code from your authenticator
5. Click **"Start Live Prices"** in dashboard

### 8. Test Application
1. **User Login**: `https://your-app-name.onrender.com/login`
2. **Create Users**: Through admin panel
3. **Live Trading**: Should work with real TradJini data
4. **WebSocket**: Real-time price updates

## 🔧 Troubleshooting

### Build Fails:
- Check `requirements.txt` is correct
- Ensure all dependencies are listed
- Check build logs in Render dashboard

### Database Connection Issues:
- Verify `DATABASE_URL` is correctly set
- Ensure PostgreSQL service is running
- Check database credentials

### Live Prices Not Working:
- Verify TradJini credentials in environment variables
- Check TOTP is current (updates every 30 seconds)
- Look at application logs for API errors

### WebSocket Issues:
- Render supports WebSocket on all plans
- Check browser console for connection errors
- Verify SocketIO is properly configured

## 📊 Render Plans

### Free Tier Limitations:
- **Web Service**: Sleeps after 15 minutes of inactivity
- **Database**: 1GB storage, 97 hours/month
- **Bandwidth**: 100GB/month

### Paid Plans:
- **Starter ($7/month)**: Always on, better performance
- **Standard ($25/month)**: More resources, faster builds

## 🚀 Production Tips

1. **Use Starter Plan** for production (no sleep)
2. **Monitor Logs** regularly for issues
3. **Set up Alerts** for downtime
4. **Backup Database** regularly
5. **Use Custom Domain** for professional look

## 📝 Useful Commands

```bash
# View logs
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.render.com/v1/services/YOUR_SERVICE_ID/logs

# Restart service
curl -X POST -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.render.com/v1/services/YOUR_SERVICE_ID/restart
```

## 🌍 Your Deployed App

After successful deployment:
- **App URL**: `https://cubeplus-trading-app.onrender.com`
- **Admin Panel**: `https://cubeplus-trading-app.onrender.com/admin`
- **Database**: Managed PostgreSQL on Render

All features work: Live streaming, Short selling, Real-time P&L, WebSocket updates!