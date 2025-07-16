#!/usr/bin/env python3
"""
Comprehensive API Test Suite for KMS-V1
Tests all endpoints with various scenarios and validates responses.
"""

import asyncio
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import httpx
import pytest
from dataclasses import dataclass

# Test configuration
BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30.0
API_TOKEN = "test-token"  # Replace with actual token


@dataclass
class TestResult:
    """Test result container."""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None


class KMSAPITestSuite:
    """Comprehensive test suite for KMS-V1 API."""
    
    def __init__(self, base_url: str = BASE_URL, api_token: str = API_TOKEN):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.results: List[TestResult] = []
        self.session_id = f"test-session-{int(time.time())}"
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites and return summary."""
        print("🚀 Starting KMS-V1 API Test Suite")
        print(f"Base URL: {self.base_url}")
        print(f"Session ID: {self.session_id}")
        print("-" * 60)
        
        start_time = time.time()
        
        # Test suites in order
        await self.test_health_endpoints()
        await self.test_search_endpoints()
        await self.test_case_endpoints()
        await self.test_knowledge_endpoints()
        await self.test_legacy_endpoints()
        await self.test_performance()
        await self.test_error_handling()
        
        total_time = time.time() - start_time
        
        # Generate summary
        summary = self.generate_summary(total_time)
        self.print_summary(summary)
        
        return summary
    
    async def make_request(
        self, 
        method: str, 
        endpoint: str, 
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> TestResult:
        """Make HTTP request and return test result."""
        url = f"{self.base_url}{endpoint}"
        
        # Default headers
        request_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        if headers:
            request_headers.update(headers)
            
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    headers=request_headers
                )
                
                response_time = (time.time() - start_time) * 1000
                
                try:
                    response_data = response.json()
                except:
                    response_data = {"text": response.text}
                
                result = TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    success=200 <= response.status_code < 400,
                    response_data=response_data
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time_ms=response_time,
                success=False,
                error_message=str(e)
            )
        
        self.results.append(result)
        return result
    
    async def test_health_endpoints(self):
        """Test health check endpoints."""
        print("🏥 Testing Health Endpoints...")
        
        endpoints = [
            "/api/v1/health/",
            "/api/v1/health/ready",
            "/api/v1/health/live",
            "/api/v1/health/detailed"
        ]
        
        for endpoint in endpoints:
            result = await self.make_request("GET", endpoint)
            status = "✅" if result.success else "❌"
            print(f"   {status} {endpoint}: {result.status_code} ({result.response_time_ms:.0f}ms)")
            
            if result.success and result.response_data:
                if "status" in result.response_data:
                    print(f"      Status: {result.response_data['status']}")
    
    async def test_search_endpoints(self):
        """Test search functionality."""
        print("\n🔍 Testing Search Endpoints...")
        
        # Test basic search
        search_tests = [
            {
                "name": "Hybrid Search - Boot Failure",
                "data": {
                    "query": "server boot failure after firmware update",
                    "search_type": "hybrid",
                    "max_results": 5
                }
            },
            {
                "name": "Vector Search - Memory Issues",
                "data": {
                    "query": "memory errors and system crashes",
                    "search_type": "vector",
                    "max_results": 3,
                    "similarity_threshold": 0.8
                }
            },
            {
                "name": "Text Search with Filters",
                "data": {
                    "query": "network connectivity problems",
                    "search_type": "text",
                    "max_results": 10,
                    "status": "resolved",
                    "session_id": self.session_id
                }
            },
            {
                "name": "Search with Date Range",
                "data": {
                    "query": "hardware diagnostics",
                    "search_type": "hybrid",
                    "date_from": "2023-01-01",
                    "date_to": "2024-01-01"
                }
            }
        ]
        
        for test in search_tests:
            result = await self.make_request("POST", "/api/v1/search/", json_data=test["data"])
            status = "✅" if result.success else "❌"
            print(f"   {status} {test['name']}: {result.status_code} ({result.response_time_ms:.0f}ms)")
            
            if result.success and result.response_data:
                total_results = result.response_data.get('total_results', 0)
                actual_results = len(result.response_data.get('results', []))
                print(f"      Results: {actual_results}/{total_results}")
        
        # Test search suggestions
        result = await self.make_request("GET", "/api/v1/search/suggestions", params={"q": "server", "max_suggestions": 5})
        status = "✅" if result.success else "❌"
        print(f"   {status} Search Suggestions: {result.status_code} ({result.response_time_ms:.0f}ms)")
        
        # Test feedback submission
        feedback_data = {
            "result_id": "test-result-123",
            "helpful": True,
            "session_id": self.session_id
        }
        result = await self.make_request("POST", "/api/v1/search/feedback", json_data=feedback_data)
        status = "✅" if result.success else "❌"
        print(f"   {status} Submit Feedback: {result.status_code} ({result.response_time_ms:.0f}ms)")
    
    async def test_case_endpoints(self):
        """Test case management endpoints."""
        print("\n📋 Testing Case Endpoints...")
        
        # Test case list
        result = await self.make_request("GET", "/api/v1/cases/", params={"page": 1, "page_size": 5})
        status = "✅" if result.success else "❌"
        print(f"   {status} List Cases: {result.status_code} ({result.response_time_ms:.0f}ms)")
        
        if result.success and result.response_data:
            total_cases = result.response_data.get('total', 0)
            cases_returned = len(result.response_data.get('cases', []))
            print(f"      Cases: {cases_returned} returned, {total_cases} total")
            
            # Test individual case lookup if cases exist
            if result.response_data.get('cases'):
                case_id = result.response_data['cases'][0].get('id', 'test-case-123')
                result = await self.make_request("GET", f"/api/v1/cases/{case_id}")
                status = "✅" if result.success else "❌"
                print(f"   {status} Get Case Details: {result.status_code} ({result.response_time_ms:.0f}ms)")
        
        # Test case creation
        new_case_data = {
            "case_number": f"HPE-TEST-{int(time.time())}",
            "subject": "API Test Case",
            "issue_plain_text": "This is a test case created by the API test suite",
            "priority": "medium",
            "status": "open"
        }
        result = await self.make_request("POST", "/api/v1/cases/", json_data=new_case_data)
        status = "✅" if result.success else "❌"
        print(f"   {status} Create Case: {result.status_code} ({result.response_time_ms:.0f}ms)")
    
    async def test_knowledge_endpoints(self):
        """Test knowledge management endpoints."""
        print("\n📚 Testing Knowledge Endpoints...")
        
        # Test knowledge article list
        result = await self.make_request("GET", "/api/v1/knowledge/", params={"page": 1, "page_size": 5})
        status = "✅" if result.success else "❌"
        print(f"   {status} List Knowledge Articles: {result.status_code} ({result.response_time_ms:.0f}ms)")
        
        if result.success and result.response_data:
            total_articles = result.response_data.get('total', 0)
            articles_returned = len(result.response_data.get('articles', []))
            print(f"      Articles: {articles_returned} returned, {total_articles} total")
            
            # Test individual article lookup if articles exist
            if result.response_data.get('articles'):
                article_id = result.response_data['articles'][0].get('id', 'test-kb-123')
                result = await self.make_request("GET", f"/api/v1/knowledge/{article_id}")
                status = "✅" if result.success else "❌"
                print(f"   {status} Get Article Details: {result.status_code} ({result.response_time_ms:.0f}ms)")
        
        # Test article creation
        new_article_data = {
            "title": f"API Test Article {int(time.time())}",
            "content": "This is a test knowledge article created by the API test suite",
            "article_type": "troubleshooting",
            "tags": ["test", "api"],
            "is_published": False
        }
        result = await self.make_request("POST", "/api/v1/knowledge/", json_data=new_article_data)
        status = "✅" if result.success else "❌"
        print(f"   {status} Create Article: {result.status_code} ({result.response_time_ms:.0f}ms)")
    
    async def test_legacy_endpoints(self):
        """Test legacy Coveo compatibility endpoints."""
        print("\n🏛️ Testing Legacy Coveo Endpoints...")
        
        # Test legacy search
        params = {
            "q": "server hardware failure",
            "numberOfResults": 5,
            "firstResult": 0
        }
        result = await self.make_request("GET", "/api/v1/legacy/coveo/search", params=params)
        status = "✅" if result.success else "❌"
        print(f"   {status} Legacy Search: {result.status_code} ({result.response_time_ms:.0f}ms)")
        
        if result.success and result.response_data:
            total_count = result.response_data.get('totalCount', 0)
            results = len(result.response_data.get('results', []))
            print(f"      Results: {results}/{total_count}")
        
        # Test facets
        result = await self.make_request("GET", "/api/v1/legacy/coveo/facets")
        status = "✅" if result.success else "❌"
        print(f"   {status} Get Facets: {result.status_code} ({result.response_time_ms:.0f}ms)")
        
        if result.success and result.response_data:
            facets = result.response_data.get('facets', [])
            print(f"      Facets available: {len(facets)}")
    
    async def test_performance(self):
        """Test API performance with concurrent requests."""
        print("\n⚡ Testing API Performance...")
        
        # Concurrent search requests
        search_data = {
            "query": "performance test query",
            "search_type": "hybrid",
            "max_results": 10
        }
        
        num_requests = 5
        start_time = time.time()
        
        # Run concurrent requests
        tasks = []
        for i in range(num_requests):
            task = self.make_request("POST", "/api/v1/search/", json_data={
                **search_data,
                "query": f"{search_data['query']} {i}",
                "session_id": f"{self.session_id}-perf-{i}"
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful_requests = sum(1 for r in results if r.success)
        avg_response_time = sum(r.response_time_ms for r in results) / len(results)
        
        print(f"   Concurrent Requests: {num_requests}")
        print(f"   Successful: {successful_requests}")
        print(f"   Total Time: {total_time:.3f}s")
        print(f"   Avg Response Time: {avg_response_time:.0f}ms")
        
        if avg_response_time < 2000:
            print("   ✅ Performance target met (<2s)")
        else:
            print("   ⚠️ Performance target missed (>2s)")
    
    async def test_error_handling(self):
        """Test error handling scenarios."""
        print("\n🚨 Testing Error Handling...")
        
        error_tests = [
            {
                "name": "Invalid Search Type",
                "method": "POST",
                "endpoint": "/api/v1/search/",
                "data": {"query": "test", "search_type": "invalid"},
                "expected_status": 422
            },
            {
                "name": "Missing Required Field",
                "method": "POST",
                "endpoint": "/api/v1/search/",
                "data": {"search_type": "hybrid"},
                "expected_status": 422
            },
            {
                "name": "Invalid Case ID",
                "method": "GET",
                "endpoint": "/api/v1/cases/invalid-case-id-12345",
                "expected_status": 404
            },
            {
                "name": "Invalid Knowledge Article ID",
                "method": "GET", 
                "endpoint": "/api/v1/knowledge/invalid-kb-12345",
                "expected_status": 404
            }
        ]
        
        for test in error_tests:
            result = await self.make_request(
                test["method"], 
                test["endpoint"], 
                json_data=test.get("data")
            )
            
            expected_status = test.get("expected_status", 400)
            status_match = result.status_code == expected_status
            status = "✅" if status_match else "❌"
            
            print(f"   {status} {test['name']}: {result.status_code} (expected {expected_status})")
            
            if result.response_data and "error" in result.response_data:
                error_msg = result.response_data["error"].get("message", "")
                print(f"      Error: {error_msg[:50]}...")
    
    def generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate test summary statistics."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        
        if total_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            avg_response_time = sum(r.response_time_ms for r in self.results) / total_tests
        else:
            success_rate = 0
            avg_response_time = 0
        
        # Group by endpoint
        endpoint_stats = {}
        for result in self.results:
            endpoint = result.endpoint
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"total": 0, "success": 0, "avg_time": 0}
            
            endpoint_stats[endpoint]["total"] += 1
            if result.success:
                endpoint_stats[endpoint]["success"] += 1
            endpoint_stats[endpoint]["avg_time"] += result.response_time_ms
        
        # Calculate averages
        for endpoint, stats in endpoint_stats.items():
            stats["avg_time"] /= stats["total"]
            stats["success_rate"] = (stats["success"] / stats["total"]) * 100
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "total_time_seconds": total_time,
            "avg_response_time_ms": avg_response_time,
            "endpoint_stats": endpoint_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print test summary."""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']} ({summary['success_rate']:.1f}%)")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Total Time: {summary['total_time_seconds']:.2f}s")
        print(f"Avg Response Time: {summary['avg_response_time_ms']:.0f}ms")
        
        print(f"\n📈 ENDPOINT PERFORMANCE:")
        for endpoint, stats in summary['endpoint_stats'].items():
            print(f"   {endpoint}")
            print(f"      Success Rate: {stats['success_rate']:.1f}% ({stats['success']}/{stats['total']})")
            print(f"      Avg Response: {stats['avg_time']:.0f}ms")
        
        # Overall health check
        if summary['success_rate'] >= 90:
            print(f"\n✅ API HEALTH: EXCELLENT")
        elif summary['success_rate'] >= 75:
            print(f"\n⚠️ API HEALTH: GOOD")
        elif summary['success_rate'] >= 50:
            print(f"\n🟡 API HEALTH: FAIR") 
        else:
            print(f"\n❌ API HEALTH: POOR")
        
        print("="*60)
    
    def save_results(self, filename: str = "api_test_results.json"):
        """Save test results to file."""
        summary = self.generate_summary(0)
        
        output = {
            "summary": summary,
            "detailed_results": [
                {
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "status_code": r.status_code,
                    "response_time_ms": r.response_time_ms,
                    "success": r.success,
                    "error_message": r.error_message,
                    "response_data": r.response_data
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")


async def main():
    """Run the complete API test suite."""
    try:
        # Initialize test suite
        test_suite = KMSAPITestSuite()
        
        # Check if API is accessible
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{BASE_URL}/api/v1/health/")
                if response.status_code != 200:
                    print(f"❌ API not responding properly: {response.status_code}")
                    return False
                print(f"✅ API is accessible")
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            print(f"   Make sure the API server is running on {BASE_URL}")
            return False
        
        # Run all tests
        summary = await test_suite.run_all_tests()
        
        # Save results
        test_suite.save_results()
        
        # Return success based on test results
        return summary['success_rate'] >= 75
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)