#!/bin/bash

# Production deployment script for eThekwini GIS MCP
# This script sets up the MCP server in a production environment

set -e  # Exit on any error

echo "🚀 eThekwini GIS MCP Production Deployment"
echo "========================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root for security reasons"
   exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required, found $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "🔧 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install production dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set production environment variables
echo "🔧 Configuring production settings..."
export ETHEKWINI_LOG_LEVEL="WARNING"
export ETHEKWINI_REFRESH_INTERVAL="900"  # 15 minutes
export ETHEKWINI_TIMEOUT="60"
export ETHEKWINI_MAX_RECORDS="1000"

# Create systemd service file (optional)
if command -v systemctl &> /dev/null; then
    echo "🔧 Creating systemd service..."
    
    cat > ethekwini-gis-mcp.service << EOF
[Unit]
Description=eThekwini GIS MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
Environment=ETHEKWINI_LOG_LEVEL=WARNING
Environment=ETHEKWINI_REFRESH_INTERVAL=900
Environment=ETHEKWINI_TIMEOUT=60
ExecStart=$(pwd)/venv/bin/python src/ethekwini_gis_mcp.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "📋 Systemd service file created: ethekwini-gis-mcp.service"
    echo "   To install: sudo cp ethekwini-gis-mcp.service /etc/systemd/system/"
    echo "   To enable: sudo systemctl enable ethekwini-gis-mcp"
    echo "   To start: sudo systemctl start ethekwini-gis-mcp"
fi

# Run tests
echo "🧪 Running production tests..."
python tests/test_mcp_server.py

# Create startup script
echo "🔧 Creating startup script..."
cat > start_production.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export ETHEKWINI_LOG_LEVEL="WARNING"
export ETHEKWINI_REFRESH_INTERVAL="900"
export ETHEKWINI_TIMEOUT="60"
python src/ethekwini_gis_mcp.py
EOF

chmod +x start_production.sh

echo ""
echo "🎉 Production deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Review and customize environment variables in start_production.sh"
echo "2. Start the server: ./start_production.sh"
echo "3. Configure your MCP client to connect to this server"
echo "4. Monitor logs for any issues"
echo ""
echo "🔧 Production configuration:"
echo "   - Log level: WARNING"
echo "   - Refresh interval: 15 minutes"
echo "   - HTTP timeout: 60 seconds"
echo "   - Virtual environment: ./venv"
echo ""
echo "📖 For more information, see README.md"