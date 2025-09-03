#!/bin/bash
# Cloudflare deployment script

echo "🚀 Deploying to Cloudflare Workers..."

# Try deploying with explicit entry point
npx wrangler deploy src/index.js

# If that fails, try with wrangler.toml
if [ $? -ne 0 ]; then
    echo "Trying with wrangler.toml configuration..."
    npx wrangler deploy
fi

echo "✅ Deployment complete!"
echo "🌐 Your app will show deployment guidance at the Cloudflare URL"