# 🐳 Deploy CubePlus Trading Simulator to Render with Docker

## Docker Deployment Options

Render supports **both** deployment methods:

### Option 1: Native Python (Simpler)
- Uses `requirements.txt` directly
- Faster builds
- Less resource usage
- **Recommended for most cases**

### Option 2: Docker Container (More Control)
- Uses `Dockerfile.render`
- Full environment control
- Better for complex dependencies
- **Use if you need specific system packages**

## 🚀 Docker Deployment Steps

### 1. Choose Docker Deployment
When creating web service in Render:
1. **Environment**: Select `Docker`
2. **Dockerfile Path**: `./Dockerfile.render`

### 2. Render Configuration

#### Using render.yaml (Automatic):
```yaml
services:
  - type: web
    name: cubeplus-trading-app
    env: docker
    dockerfilePath: ./Dockerfile.render
    envVars:
      - key: FLASK_ENV
        value: production
      # ... other env vars
```

#### Manual Configuration:
- **Environment**: `Docker`
- **Dockerfile**: `./Dockerfile.render`
- **Build Context**: `.` (root directory)

### 3. Docker vs Python Comparison

| Feature | Docker | Native Python |
|---------|--------|---------------|
| **Build Time** | 3-5 minutes | 1-2 minutes |
| **Resource Usage** | Higher | Lower |
| **Customization** | Full control | Limited |
| **Dependencies** | System packages | Python only |
| **Debugging** | Container logs | Direct logs |
| **Caching** | Docker layers | pip cache |

### 4. Docker Benefits for This App

✅ **System Dependencies**: PostgreSQL client, curl  
✅ **Security**: Non-root user, minimal base image  
✅ **Health Checks**: Built-in container health monitoring  
✅ **Consistency**: Same environment locally and in production  
✅ **Isolation**: Complete environment isolation  

### 5. Docker Deployment Commands

```bash
# Test locally first
docker build -f Dockerfile.render -t cubeplus-trading .
docker run -p 8000:8000 --env-file .env cubeplus-trading

# Push to GitHub (Render will build automatically)
git add .
git commit -m "Docker deployment ready"
git push origin main
```

### 6. Environment Variables (Same for Both)

Set in Render dashboard:
- `FLASK_ENV` = `production`
- `SECRET_KEY` = `your-random-key`
- `TRADEJINI_APIKEY` = `49ddd64cacba20b25376edb24c1d17ad`
- `TRADEJINI_PASSWORD` = `Gopal7463@`
- `TRADEJINI_TWO_FA` = `123456`
- `DATABASE_URL` = *From PostgreSQL service*

## 🔧 Docker-Specific Features

### Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1
```

### Security
```dockerfile
# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
```

### Optimized Layers
```dockerfile
# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy app code last
COPY . .
```

## 📊 Performance Comparison

### Build Times:
- **Docker**: 3-5 minutes (first build), 1-2 minutes (cached)
- **Python**: 1-2 minutes consistently

### Memory Usage:
- **Docker**: ~200MB base + app
- **Python**: ~150MB app only

### Cold Start:
- **Docker**: 2-3 seconds
- **Python**: 1-2 seconds

## 🚀 Recommendation

**Use Native Python** unless you need:
- Custom system packages
- Specific OS configuration
- Container orchestration features
- Exact environment replication

**Use Docker** if you want:
- Maximum control
- System-level dependencies
- Container-native deployment
- Local/production parity

## 🌍 Both Work Perfectly!

Either deployment method gives you:
✅ **Live TradJini Streaming**  
✅ **Short Selling Features**  
✅ **Real-time P&L Updates**  
✅ **WebSocket Support**  
✅ **PostgreSQL Database**  
✅ **Auto-scaling**  
✅ **SSL/HTTPS**  

Choose based on your preference and requirements!