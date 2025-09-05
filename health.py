from flask import Flask

app = Flask(__name__)

@app.route('/')
def health():
    return {'status': 'healthy', 'message': 'CubePlus Trading App is running'}

@app.route('/health')
def health_check():
    return {'status': 'ok'}

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port)