#!/bin/bash

echo "🚀 Starting eThekwini GIS MCP Server..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed or not in PATH"
        echo "Please install Python 3.8+ and try again"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

# Check if we're in the right directory
if [ ! -f "src/ethekwini_gis_mcp.py" ]; then
    echo "❌ Please run this script from the eThekwini GIS MCP root directory"
    echo "Expected file: src/ethekwini_gis_mcp.py"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
$PYTHON_CMD -c "import mcp, httpx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing missing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo "✅ Dependencies OK"
echo
echo "🌐 Discovering eThekwini GIS services..."
echo "📊 This may take a moment to scan all available datasets..."
echo
echo "🔗 Starting MCP server (press Ctrl+C to stop)"
echo

# Start the MCP server
$PYTHON_CMD src/ethekwini_gis_mcp.py

echo
echo "🏁 MCP Server stopped"