#!/usr/bin/env python3
"""
Installation script for eThekwini ESRI GIS MCP Server
Use this to quickly set up the development environment
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    print("🚀 eThekwini GIS MCP Server Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("\n💡 If pip install fails, try:")
        print("   pip install --user -r requirements.txt")
        print("   or")
        print("   python -m pip install -r requirements.txt")
        return False
    
    # Test imports
    print("\n🔍 Testing imports...")
    try:
        import mcp
        import httpx
        print("✅ All required packages imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Run tests
    print("\n🧪 Running tests...")
    if run_command("python tests/test_mcp_server.py", "Running MCP server tests"):
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Configure your MCP client with the settings in mcp-config.json")
        print("2. Run the server with: python src/ethekwini_gis_mcp.py")
        print("3. Check the README.md for usage examples")
        return True
    else:
        print("\n⚠️  Setup completed but tests failed")
        print("The server may still work, but some features might have issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)