import os
import sys

try:
    from app import create_app
    
    # Create Flask app instance for gunicorn
    app, socketio = create_app()
    
    # WSGI application for gunicorn
    application = app
    
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)