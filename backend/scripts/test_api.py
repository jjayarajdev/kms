#!/usr/bin/env python3
"""Test API endpoints with sample requests."""

import asyncio
import sys
import json
from pathlib import Path
import httpx
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30.0


async def test_health_endpoints():
    """Test health check endpoints."""
    print("🏥 Testing Health Endpoints...")
    
    endpoints = [
        "/api/v1/health",
        "/api/v1/health/ready", 
        "/api/v1/health/live",
        "/api/v1/health/detailed"
    ]
    
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"{BASE_URL}{endpoint}")
                print(f"   {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if "status" in data:
                        print(f"      Status: {data['status']}")
                else:
                    print(f"      Error: {response.text}")
                    
            except Exception as e:
                print(f"   {endpoint}: ❌ Failed - {e}")


async def test_search_endpoints():
    """Test search API endpoints."""
    print("\n🔍 Testing Search Endpoints...")
    
    # Test basic search
    search_requests = [
        {
            "query": "hard drive failure",
            "search_type": "hybrid",
            "max_results": 5
        },
        {
            "query": "power supply error DL380",
            "search_type": "vector", 
            "max_results": 3,
            "similarity_threshold": 0.7
        },
        {
            "query": "memory issue",
            "search_type": "text",
            "max_results": 5,
            "status": "Closed"
        }
    ]
    
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        for i, search_request in enumerate(search_requests):
            try:
                print(f"\n   Test {i+1}: {search_request['search_type']} search")
                print(f"   Query: '{search_request['query']}'")
                
                response = await client.post(
                    f"{BASE_URL}/api/v1/search",
                    json=search_request
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Results: {data['total_results']}")
                    print(f"   Response time: {data['response_time_ms']}ms")
                    print(f"   Session ID: {data['session_id']}")
                    
                    # Show top result
                    if data['results']:
                        top_result = data['results'][0]
                        print(f"   Top result: {top_result['title'][:50]}...")
                        print(f"   Confidence: {top_result['confidence_level']}")
                        print(f"   Similarity: {top_result['similarity_score']:.3f}")
                else:
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"   Test {i+1}: ❌ Failed - {e}")


async def test_suggestions_endpoint():
    """Test search suggestions endpoint."""
    print("\n💡 Testing Search Suggestions...")
    
    partial_queries = ["hard", "power", "memory", "network"]
    
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        for query in partial_queries:
            try:
                response = await client.get(
                    f"{BASE_URL}/api/v1/search/suggestions",
                    params={"q": query, "max_suggestions": 3}
                )
                
                print(f"   '{query}' -> {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    suggestions = data.get('suggestions', [])
                    print(f"      Suggestions: {suggestions}")
                else:
                    print(f"      Error: {response.text}")
                    
            except Exception as e:
                print(f"   '{query}': ❌ Failed - {e}")


async def test_cases_endpoints():
    """Test cases API endpoints."""
    print("\n📋 Testing Cases Endpoints...")
    
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        # Test case list
        try:
            print("   Testing case list...")
            response = await client.get(
                f"{BASE_URL}/api/v1/cases",
                params={"page": 1, "page_size": 5}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Total cases: {data['total']}")
                print(f"   Cases returned: {len(data['cases'])}")
                
                # Test individual case lookup if we have cases
                if data['cases']:
                    case_id = data['cases'][0]['id']
                    print(f"\n   Testing case detail for ID {case_id}...")
                    
                    detail_response = await client.get(f"{BASE_URL}/api/v1/cases/{case_id}")
                    print(f"   Case detail status: {detail_response.status_code}")
                    
                    if detail_response.status_code == 200:
                        case_data = detail_response.json()
                        print(f"   Case number: {case_data['case_number']}")
                        print(f"   Status: {case_data['status']}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   Cases test: ❌ Failed - {e}")


async def test_knowledge_endpoints():
    """Test knowledge management endpoints."""
    print("\n📚 Testing Knowledge Endpoints...")
    
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        # Test knowledge article list
        try:
            print("   Testing knowledge article list...")
            response = await client.get(
                f"{BASE_URL}/api/v1/knowledge",
                params={"page": 1, "page_size": 3, "is_published": True}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Total articles: {data['total']}")
                print(f"   Articles returned: {len(data['articles'])}")
                
                # Test individual article lookup if we have articles
                if data['articles']:
                    article_id = data['articles'][0]['id']
                    print(f"\n   Testing article detail for ID {article_id}...")
                    
                    detail_response = await client.get(f"{BASE_URL}/api/v1/knowledge/{article_id}")
                    print(f"   Article detail status: {detail_response.status_code}")
                    
                    if detail_response.status_code == 200:
                        article_data = detail_response.json()
                        print(f"   Article title: {article_data['title'][:50]}...")
                        print(f"   Type: {article_data['article_type']}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   Knowledge test: ❌ Failed - {e}")


async def test_legacy_endpoints():
    """Test legacy Coveo compatibility endpoints."""
    print("\n🏛️ Testing Legacy Coveo Endpoints...")
    
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        # Test legacy search
        try:
            print("   Testing legacy Coveo search...")
            response = await client.get(
                f"{BASE_URL}/api/v1/legacy/coveo/search",
                params={
                    "q": "server hardware failure",
                    "numberOfResults": 5,
                    "firstResult": 0
                }
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Total count: {data.get('totalCount', 0)}")
                print(f"   Results: {len(data.get('results', []))}")
                print(f"   Duration: {data.get('duration', 0)}ms")
                
                # Show first result structure
                if data.get('results'):
                    result = data['results'][0]
                    print(f"   First result title: {result.get('title', '')[:50]}...")
                    print(f"   Score: {result.get('score', 0)}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   Legacy search test: ❌ Failed - {e}")
        
        # Test legacy facets
        try:
            print("\n   Testing legacy facets...")
            response = await client.get(f"{BASE_URL}/api/v1/legacy/coveo/facets")
            
            print(f"   Facets status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                facets = data.get('facets', [])
                print(f"   Facets available: {len(facets)}")
                for facet in facets:
                    print(f"      - {facet.get('displayName', 'Unknown')}")
            else:
                print(f"   Facets error: {response.text}")
                
        except Exception as e:
            print(f"   Legacy facets test: ❌ Failed - {e}")


async def test_api_performance():
    """Test API performance."""
    print("\n⚡ Testing API Performance...")
    
    async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
        # Performance test with multiple concurrent requests
        search_request = {
            "query": "hardware troubleshooting",
            "search_type": "hybrid",
            "max_results": 10
        }
        
        num_requests = 5
        start_time = datetime.now()
        
        try:
            # Run concurrent requests
            tasks = []
            for i in range(num_requests):
                task = client.post(f"{BASE_URL}/api/v1/search", json=search_request)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = datetime.now()
            
            total_time = (end_time - start_time).total_seconds()
            successful_requests = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
            
            print(f"   Concurrent requests: {num_requests}")
            print(f"   Successful: {successful_requests}")
            print(f"   Total time: {total_time:.3f}s")
            print(f"   Average time per request: {total_time / num_requests:.3f}s")
            
            # Check individual response times
            response_times = []
            for response in responses:
                if not isinstance(response, Exception) and response.status_code == 200:
                    data = response.json()
                    response_times.append(data.get('response_time_ms', 0))
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                print(f"   Average API response time: {avg_response_time:.0f}ms")
                
                if avg_response_time < 2000:
                    print("   ✅ Performance target met (<2s)")
                else:
                    print("   ⚠️ Performance target missed (>2s)")
            
        except Exception as e:
            print(f"   Performance test: ❌ Failed - {e}")


async def main():
    """Run all API tests."""
    try:
        print("🚀 Starting API Tests...")
        print(f"Testing against: {BASE_URL}")
        print(f"Started at: {datetime.now()}")
        
        # Check if API is running
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{BASE_URL}/")
                if response.status_code != 200:
                    print(f"❌ API not responding: {response.status_code}")
                    return False
                print(f"✅ API is running: {response.json()['name']}")
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            print("   Make sure the API server is running with: uvicorn src.api.main:app --reload")
            return False
        
        # Run test suites
        await test_health_endpoints()
        await test_search_endpoints()
        await test_suggestions_endpoint()
        await test_cases_endpoints()
        await test_knowledge_endpoints()
        await test_legacy_endpoints()
        await test_api_performance()
        
        print(f"\n✅ All API tests completed at: {datetime.now()}")
        return True
        
    except Exception as e:
        print(f"❌ API tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)