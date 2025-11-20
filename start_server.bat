@echo off
echo 🚀 Starting eThekwini GIS MCP Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "src\ethekwini_gis_mcp.py" (
    echo ❌ Please run this script from the eThekwini GIS MCP root directory
    echo Expected file: src\ethekwini_gis_mcp.py
    pause
    exit /b 1
)

REM Install dependencies if needed
echo 📦 Checking dependencies...
python -c "import mcp, httpx" >nul 2>&1
if errorlevel 1 (
    echo Installing missing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo ✅ Dependencies OK
echo.
echo 🌐 Discovering eThekwini GIS services...
echo 📊 This may take a moment to scan all available datasets...
echo.
echo 🔗 Starting MCP server (press Ctrl+C to stop)
echo.

REM Start the MCP server
python src\ethekwini_gis_mcp.py

echo.
echo 🏁 MCP Server stopped
pause