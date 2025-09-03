# Cloudflare Deployment Guide

## Prerequisites
1. Install Cloudflare CLI: `npm install -g wrangler`
2. Login to Cloudflare: `wrangler login`

## Deployment Steps

### 1. Install Dependencies
```bash
pip install -r requirements-cloudflare.txt
```

### 2. Set Environment Variables
```bash
wrangler secret put TRADEJINI_APIKEY
wrangler secret put TRADEJINI_PASSWORD
wrangler secret put TRADEJINI_TWO_FA
wrangler secret put SECRET_KEY
```

### 3. Deploy to Cloudflare
```bash
wrangler deploy
```

## Configuration
- **Database**: SQLite (file-based)
- **WebSocket**: Limited on Cloudflare Workers
- **Static Files**: Served via Cloudflare CDN

## Environment Variables
- `TRADEJINI_APIKEY`: 49ddd64cacba20b25376edb24c1d17ad
- `TRADEJINI_PASSWORD`: Gopal7463@
- `TRADEJINI_TWO_FA_TYPE`: TOTP
- `SECRET_KEY`: Your secret key

## Limitations
- WebSocket streaming may be limited
- File uploads restricted
- Database persistence limited

## Alternative: Use Cloudflare Pages + Functions
For full functionality, consider using Cloudflare Pages with Functions for API endpoints.