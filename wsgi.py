#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
from app import create_app
import os

# Create Flask app and SocketIO instance
app, socketio = create_app()

# For production with gunicorn (sync worker)
application = app  # Use Flask app directly for sync worker

if __name__ == "__main__":
    # For development
    socketio.run(app, debug=False, host='0.0.0.0', port=8000)