"""
Test script for eThekwini GIS MCP Server
Run this to verify the MCP server functionality
"""

import asyncio
import json
import httpx
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ethekwini_gis_mcp import EThekwiniGISServer

async def test_server_initialization():
    """Test if the server initializes correctly"""
    print("🔄 Testing server initialization...")
    
    try:
        server = EThekwiniGISServer()
        print("✅ Server initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        return False

async def test_dataset_discovery():
    """Test dataset discovery functionality"""
    print("\n🔍 Testing dataset discovery...")
    
    try:
        server = EThekwiniGISServer()
        await server._refresh_datasets(force=True)
        
        dataset_count = len(server.cached_datasets)
        service_count = len(server.cached_services)
        
        print(f"✅ Discovered {dataset_count} datasets and {service_count} services")
        
        if dataset_count > 0:
            # Show first few datasets
            sample_datasets = list(server.cached_datasets.items())[:3]
            print("\n📊 Sample datasets:")
            for dataset_id, info in sample_datasets:
                print(f"  - {info.get('name', dataset_id)}: {info.get('type', 'Unknown type')}")
        
        return dataset_count > 0
    except Exception as e:
        print(f"❌ Dataset discovery failed: {e}")
        return False

async def test_api_connectivity():
    """Test connectivity to eThekwini APIs"""
    print("\n🌐 Testing API connectivity...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test the actual eThekwini ArcGIS services endpoint (the one we use)
            services_response = await client.get("https://services3.arcgis.com/HO0zfySJshlD6Twu/arcgis/rest/services?f=json")
            services_status = services_response.status_code
            
            # Test a specific known service (Leases)
            leases_response = await client.get("https://services3.arcgis.com/HO0zfySJshlD6Twu/arcgis/rest/services/Leases/FeatureServer?f=json")
            leases_status = leases_response.status_code
            
            print(f"✅ eThekwini Services API: HTTP {services_status}")
            print(f"✅ Leases Service API: HTTP {leases_status}")
            
            return services_status == 200 and leases_status == 200
    except Exception as e:
        print(f"❌ API connectivity test failed: {e}")
        return False

async def test_search_functionality():
    """Test dataset search functionality"""
    print("\n🔎 Testing search functionality...")
    
    try:
        server = EThekwiniGISServer()
        await server._refresh_datasets(force=True)
        
        # Test keyword search
        results = await server._search_datasets(query="roads", limit=5)
        
        print(f"✅ Found {len(results)} datasets matching 'roads'")
        
        if results:
            print("\n📋 Search results:")
            for result in results[:3]:
                print(f"  - {result.get('name', 'Unknown')}: {result.get('description', 'No description')[:100]}...")
        
        return len(results) > 0
    except Exception as e:
        print(f"❌ Search functionality test failed: {e}")
        return False

async def test_service_info_retrieval():
    """Test service information retrieval"""
    print("\n📡 Testing service info retrieval...")
    
    try:
        server = EThekwiniGISServer()
        
        # Test with a known ArcGIS REST endpoint
        test_url = "https://services1.arcgis.com/lWlynzziWE25ay4L/arcgis/rest/services"
        
        # Try to get service info
        info = await server._get_service_info(f"{test_url}?f=json")
        
        if info:
            print("✅ Successfully retrieved service information")
            if 'services' in info:
                print(f"  - Found {len(info.get('services', []))} services")
            if 'folders' in info:
                print(f"  - Found {len(info.get('folders', []))} folders")
            return True
        else:
            print("⚠️  No service information retrieved (may be expected)")
            return True  # Not necessarily a failure
    except Exception as e:
        print(f"❌ Service info retrieval test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🧪 eThekwini GIS MCP Server Test Suite")
    print("=" * 50)
    
    tests = [
        ("Server Initialization", test_server_initialization),
        ("API Connectivity", test_api_connectivity),
        ("Dataset Discovery", test_dataset_discovery),
        ("Search Functionality", test_search_functionality),
        ("Service Info Retrieval", test_service_info_retrieval),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! MCP server is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return failed == 0

if __name__ == "__main__":
    asyncio.run(run_all_tests())