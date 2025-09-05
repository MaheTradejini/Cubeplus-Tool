import os
from app import create_app

# Create Flask app instance
app, socketio = create_app()

# For gunicorn
application = app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)