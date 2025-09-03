export default {
  async fetch(request, env, ctx) {
    return new Response(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>CubePlus Trading Simulator</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
          .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
          .error { background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; border-left: 4px solid #dc3545; }
          .info { background: #d1ecf1; color: #0c5460; padding: 20px; border-radius: 5px; margin-top: 20px; border-left: 4px solid #17a2b8; }
          .success { background: #d4edda; color: #155724; padding: 20px; border-radius: 5px; margin-top: 20px; border-left: 4px solid #28a745; }
          h1 { color: #333; margin-bottom: 30px; }
          h3 { margin-top: 0; }
          ul { margin: 15px 0; }
          li { margin: 8px 0; }
          .btn { display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
          .btn:hover { background: #0056b3; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>🚀 CubePlus Trading Simulator</h1>
          
          <div class="error">
            <h3>⚠️ Cloudflare Workers Limitation</h3>
            <p>Cloudflare Workers doesn't support Python Flask applications directly. Your trading simulator needs a Python runtime environment.</p>
          </div>
          
          <div class="success">
            <h3>✅ Ready for Deployment</h3>
            <p>Your Python Flask trading simulator is fully prepared and can be deployed to platforms that support Python:</p>
            <ul>
              <li><strong>Railway:</strong> Best for Python Flask apps</li>
              <li><strong>Render:</strong> Free tier available</li>
              <li><strong>Vercel:</strong> Serverless Python functions</li>
              <li><strong>Heroku:</strong> Classic Python hosting</li>
            </ul>
          </div>
          
          <div class="info">
            <h3>🎯 Recommended Solution</h3>
            <p><strong>Deploy to Railway + Cloudflare CDN:</strong></p>
            <ol>
              <li>Deploy Python app to Railway</li>
              <li>Get custom domain</li>
              <li>Use Cloudflare as DNS/CDN</li>
              <li>Enjoy global performance + full Python features</li>
            </ol>
            
            <a href="https://railway.app" class="btn">Deploy to Railway</a>
            <a href="https://render.com" class="btn">Deploy to Render</a>
          </div>
          
          <div class="info">
            <h3>📋 Your App Features</h3>
            <ul>
              <li>✅ Live TradJini API integration</li>
              <li>✅ Real-time price streaming</li>
              <li>✅ 50 NSE stocks trading</li>
              <li>✅ Admin panel with TOTP management</li>
              <li>✅ Portfolio tracking with P&L</li>
              <li>✅ SQLite database</li>
              <li>✅ WebSocket real-time updates</li>
            </ul>
          </div>
        </div>
      </body>
      </html>
    `, {
      headers: {
        'Content-Type': 'text/html',
      },
    });
  },
};