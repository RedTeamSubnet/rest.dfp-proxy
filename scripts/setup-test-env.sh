#!/bin/bash

set -e

# Determine project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$SCRIPT_DIR" == */scripts ]]; then
    # Script is in scripts folder, go up one level
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
else
    # Script is in project root
    PROJECT_ROOT="$SCRIPT_DIR"
fi

# Change to project root
cd "$PROJECT_ROOT"

echo "🚀 Setting up testing environment..."

# 1. Copy compose.override.dev.yml to root as compose.override.yml
echo "📋 Copying compose override file..."
cp templates/compose/compose.override.dev.yml compose.override.yml
echo "✅ Copied templates/compose/compose.override.dev.yml to compose.override.yml"

# 2. Copy .env.example as .env
echo "⚙️  Setting up environment file..."
cp .env.example .env
echo "✅ Copied .env.example to .env"

# 3. Generate 10-digit random number for DFP_CHALLENGE_API_KEY
echo "🔑 Generating API key..."
RANDOM_API_KEY=$(shuf -i 1000000000-9999999999 -n 1)
sed -i.bak "s/DFP_CHALLENGE_API_KEY=\"your_api_key_here\"/DFP_CHALLENGE_API_KEY=\"$RANDOM_API_KEY\"/" .env
rm .env.bak
echo "✅ Set DFP_CHALLENGE_API_KEY to: $RANDOM_API_KEY"

# 4. Run docker compose up --build -d
echo "🐳 Starting Docker containers..."
docker compose up --build -d
echo "✅ Docker containers started"

# 5. Get the port from .env file
DFP_PROXY_API_PORT=$(grep "^DFP_PROXY_API_PORT=" .env | cut -d'=' -f2)
if [ -z "$DFP_PROXY_API_PORT" ]; then
    DFP_PROXY_API_PORT=8000
fi

# 6. Log endpoints
echo ""
echo "🌐 Testing Environment Ready!"
echo "=================================="
echo "Local endpoint: http://0.0.0.0:$DFP_PROXY_API_PORT/_web?order_id=1"
echo "Localhost endpoint: http://localhost:$DFP_PROXY_API_PORT/_web?order_id=1"

# Get network interface IP for local network access
NETWORK_IP=$(ifconfig en0 | grep 'inet ' | awk '{print $2}' 2>/dev/null || ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | awk '{print $2}' | head -1)

echo ""
echo "Network Access URLs:"
if [ -n "$NETWORK_IP" ]; then
    echo "Network IP: http://$NETWORK_IP:$DFP_PROXY_API_PORT/_web?order_id=1"
fi
echo ""
echo "🎯 Use the Network IP URL to share with devices on the same network"
echo "=================================="
