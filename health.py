from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'healthy', 'message': 'CubePlus Trading App is running', 'port': os.getenv('PORT', '8000')}

@app.route('/health')
def health_check():
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    print(f"Starting health check app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)