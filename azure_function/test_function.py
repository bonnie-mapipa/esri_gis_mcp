"""
Test script for eThekwini GIS Azure Function
Run this to test the deployed function endpoints
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class AzureFunctionTester:
    def __init__(self, base_url: str, function_key: str = None):
        """
        Initialize tester with function app URL
        
        Args:
            base_url: Base URL of the deployed function (e.g., https://func-ethekwini-gis-mcp.azurewebsites.net/api)
            function_key: Function key for authentication (optional for local testing)
        """
        self.base_url = base_url.rstrip('/')
        self.function_key = function_key
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'eThekwini-GIS-Function-Tester/1.0'
        }
        if function_key:
            self.headers['x-functions-key'] = function_key

    async def test_endpoint(self, session: aiohttp.ClientSession, method: str, endpoint: str, data: dict = None):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"\n🧪 Testing {method} {endpoint}")
            
            if method.upper() == 'GET':
                async with session.get(url, headers=self.headers) as response:
                    result = await response.json()
                    status = response.status
            else:
                async with session.post(url, headers=self.headers, json=data) as response:
                    result = await response.json()
                    status = response.status
            
            if status == 200:
                print(f"   ✅ Status: {status}")
                if 'datasets' in result:
                    print(f"   📊 Found {len(result['datasets'])} datasets")
                elif 'search_results' in result:
                    print(f"   🔍 Found {len(result['search_results'])} search results")
                elif 'query_result' in result:
                    features = result['query_result'].get('features', [])
                    print(f"   📍 Query returned {len(features)} features")
                else:
                    print(f"   ℹ️  Response keys: {list(result.keys())}")
            else:
                print(f"   ❌ Status: {status}")
                print(f"   🚨 Error: {result}")
                
            return status == 200, result
            
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
            return False, {"error": str(e)}

    async def run_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting eThekwini GIS Azure Function Tests")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"⏰ Started: {datetime.now()}")
        
        results = {}
        
        async with aiohttp.ClientSession() as session:
            
            # Test 1: Health Check
            success, result = await self.test_endpoint(session, 'GET', '/health')
            results['health'] = success
            
            # Test 2: API Documentation
            success, result = await self.test_endpoint(session, 'GET', '/')
            results['docs'] = success
            
            # Test 3: List Datasets
            success, result = await self.test_endpoint(session, 'GET', '/datasets')
            results['list_datasets'] = success
            
            if success and 'datasets' in result and result['datasets']:
                # Get first dataset ID for further testing
                first_dataset = result['datasets'][0]
                dataset_id = first_dataset['id']
                print(f"   🎯 Using dataset '{dataset_id}' for subsequent tests")
                
                # Test 4: Dataset Info
                success, result = await self.test_endpoint(session, 'GET', f'/datasets/{dataset_id}/info')
                results['dataset_info'] = success
                
                # Test 5: Query Dataset
                query_data = {
                    "where": "1=1",
                    "max_records": 5,
                    "fields": "*"
                }
                success, result = await self.test_endpoint(session, 'POST', f'/datasets/{dataset_id}/query', query_data)
                results['query_dataset'] = success
                
                # Test 6: Dataset Statistics
                success, result = await self.test_endpoint(session, 'GET', f'/datasets/{dataset_id}/stats')
                results['dataset_stats'] = success
                
            else:
                print("   ⚠️  No datasets available for detailed testing")
                results['dataset_info'] = False
                results['query_dataset'] = False
                results['dataset_stats'] = False
            
            # Test 7: Search Datasets
            success, result = await self.test_endpoint(session, 'GET', '/search?q=transport')
            results['search_datasets'] = success
            
            # Test 8: Refresh Datasets (Admin)
            success, result = await self.test_endpoint(session, 'POST', '/admin/refresh')
            results['refresh_datasets'] = success
        
        # Summary
        print("\n" + "="*50)
        print("📋 TEST RESULTS SUMMARY")
        print("="*50)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name:20} {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Your Azure Function is working perfectly.")
        elif passed_tests > total_tests * 0.7:
            print("⚠️  Most tests passed. Check failed tests above.")
        else:
            print("🚨 Many tests failed. Please check your deployment and configuration.")
        
        return results

async def main():
    """Main test runner"""
    
    # Configuration - Update these for your deployment
    LOCAL_URL = "http://localhost:7071/api"
    AZURE_URL = "https://func-ethekwini-gis-mcp.azurewebsites.net/api"
    FUNCTION_KEY = None  # Add your function key here if testing production
    
    print("Choose testing mode:")
    print("1. Local development (func start)")
    print("2. Azure deployment")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        tester = AzureFunctionTester(LOCAL_URL)
    elif choice == "2":
        if not FUNCTION_KEY:
            print("⚠️  Function key not provided. Some tests may fail due to authentication.")
            print("To get your function key, run:")
            print("az functionapp keys list --name func-ethekwini-gis-mcp --resource-group rg-ethekwini-gis-mcp")
        tester = AzureFunctionTester(AZURE_URL, FUNCTION_KEY)
    else:
        print("Invalid choice. Defaulting to local testing.")
        tester = AzureFunctionTester(LOCAL_URL)
    
    # Run the tests
    await tester.run_tests()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())