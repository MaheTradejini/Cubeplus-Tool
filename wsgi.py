import os
from app import create_app

app, socketio = create_app()
application = app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)