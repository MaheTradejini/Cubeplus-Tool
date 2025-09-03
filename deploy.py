#!/usr/bin/env python3
"""
CubePlus Trading Simulator - Universal Deployment Script
Supports: Railway, Render, Vercel, Docker, Local Development
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class CubePlusDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_vars = {
            'TRADEJINI_APIKEY': 'your_api_key_here',
            'TRADEJINI_PASSWORD': 'your_password_here', 
            'TRADEJINI_TWO_FA': '123456',
            'TRADEJINI_TWO_FA_TYPE': 'TOTP',
            'DATABASE_URL': 'sqlite:///app.db',
            'SECRET_KEY': 'your-secret-key-change-this'
        }
    
    def create_env_file(self):
        """Create .env file with default values"""
        env_content = '\n'.join([f'{k}={v}' for k, v in self.env_vars.items()])
        with open(self.project_root / '.env', 'w') as f:
            f.write(env_content)
        print("Created .env file")
    
    def create_requirements(self):
        """Create production requirements.txt"""
        requirements = [
            'Flask==2.3.3',
            'Werkzeug==2.3.7', 
            'python-dotenv==1.0.0',
            'Flask-SQLAlchemy==3.0.5',
            'Flask-Login==0.6.3',
            'Flask-WTF==1.1.1',
            'WTForms==3.0.1',
            'Flask-Bcrypt==1.0.1',
            'Flask-SocketIO==5.3.6',
            'requests==2.32.0',
            'websocket-client==1.6.1',
            'eventlet==0.35.2',
            'email-validator==2.0.0',
            'python-socketio==5.8.0',
            'gunicorn==21.2.0'
        ]
        with open(self.project_root / 'requirements.txt', 'w') as f:
            f.write('\n'.join(requirements))
        print("Updated requirements.txt")
    
    def create_dockerfile(self):
        """Create optimized Dockerfile"""
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p instance

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]"""
        
        with open(self.project_root / 'Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        print("Created Dockerfile")
    
    def create_railway_config(self):
        """Create Railway deployment config"""
        config = {
            "build": {"builder": "NIXPACKS"},
            "deploy": {
                "startCommand": "gunicorn -c gunicorn.conf.py wsgi:app",
                "restartPolicyType": "ON_FAILURE"
            }
        }
        with open(self.project_root / 'railway.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("Created railway.json")
    
    def create_render_config(self):
        """Create Render deployment config"""
        config = {
            "services": [{
                "type": "web",
                "name": "cubeplus-trading-simulator",
                "env": "python",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "gunicorn -c gunicorn.conf.py wsgi:app",
                "envVars": [
                    {"key": k, "value": v} for k, v in self.env_vars.items()
                ]
            }]
        }
        with open(self.project_root / 'render.yaml', 'w') as f:
            json.dump(config, f, indent=2)
        print("Created render.yaml")
    
    def create_vercel_config(self):
        """Create Vercel deployment config"""
        config = {
            "version": 2,
            "builds": [{"src": "wsgi.py", "use": "@vercel/python"}],
            "routes": [{"src": "/(.*)", "dest": "wsgi.py"}],
            "env": self.env_vars
        }
        with open(self.project_root / 'vercel.json', 'w') as f:
            json.dump(config, f, indent=2)
        print("Created vercel.json")
    
    def update_gunicorn_config(self):
        """Update gunicorn configuration"""
        config_content = """import os

bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = 1
worker_class = "eventlet"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True"""
        
        with open(self.project_root / 'gunicorn.conf.py', 'w') as f:
            f.write(config_content)
        print("Updated gunicorn.conf.py")
    
    def deploy_railway(self):
        """Deploy to Railway"""
        print("Deploying to Railway...")
        print("1. Push code to GitHub")
        print("2. Go to railway.app and connect your repo")
        print("3. Set environment variables in Railway dashboard")
        print("4. Deploy automatically!")
    
    def deploy_render(self):
        """Deploy to Render"""
        print("Deploying to Render...")
        print("1. Push code to GitHub")
        print("2. Connect repo to Render")
        print("3. Use render.yaml for automatic configuration")
        print("4. Update environment variables in dashboard")
    
    def deploy_vercel(self):
        """Deploy to Vercel"""
        print("Deploying to Vercel...")
        try:
            subprocess.run(['vercel', '--prod'], check=True)
            print("Deployed to Vercel!")
        except:
            print("Install Vercel CLI: npm i -g vercel")
            print("Then run: vercel --prod")
    
    def deploy_docker(self):
        """Deploy with Docker"""
        print("Building Docker image...")
        try:
            subprocess.run(['docker', 'build', '-t', 'cubeplus-tool', '.'], check=True)
            print("Docker image built!")
            print("Run: docker run -p 8000:8000 --env-file .env cubeplus-tool")
        except:
            print("Install Docker and try again")
    
    def run_local(self):
        """Run locally"""
        print("Starting local development server...")
        try:
            subprocess.run([sys.executable, 'app.py'], check=True)
        except KeyboardInterrupt:
            print("\nServer stopped")
    
    def setup_all(self):
        """Setup all deployment configurations"""
        print("Setting up CubePlus Trading Simulator deployment...")
        self.create_env_file()
        self.create_requirements()
        self.create_dockerfile()
        self.update_gunicorn_config()
        self.create_railway_config()
        self.create_render_config()
        self.create_vercel_config()
        print("\nAll deployment configurations created!")
        print("\nAvailable deployment options:")
        print("1. Railway (Recommended): python deploy.py railway")
        print("2. Render: python deploy.py render") 
        print("3. Vercel: python deploy.py vercel")
        print("4. Docker: python deploy.py docker")
        print("5. Local: python deploy.py local")

def main():
    deployer = CubePlusDeployer()
    
    if len(sys.argv) < 2:
        deployer.setup_all()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        deployer.setup_all()
    elif command == 'railway':
        deployer.deploy_railway()
    elif command == 'render':
        deployer.deploy_render()
    elif command == 'vercel':
        deployer.deploy_vercel()
    elif command == 'docker':
        deployer.deploy_docker()
    elif command == 'local':
        deployer.run_local()
    else:
        print("Usage: python deploy.py [setup|railway|render|vercel|docker|local]")

if __name__ == '__main__':
    main()