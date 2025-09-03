import os
from app import create_app

# Cloudflare Workers WSGI application
app, socketio = create_app()

# WSGI application for Cloudflare
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)