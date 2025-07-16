#!/usr/bin/env python3
"""Test search functionality with sample queries."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add the backend src directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.data.database import get_db
from src.data.postgres_connector import PostgresConnector
from src.embeddings.pinecone_client import get_pinecone_client
from src.embeddings.vectorizer import get_embedding_generator
from src.search.similarity_engine import create_similarity_engine, SearchType, SearchConfig
from src.search.query_processor import query_processor


async def test_query_processing():
    """Test query processing functionality."""
    print("🧪 Testing Query Processing...")
    
    test_queries = [
        "hard drive failure DL380 Gen10",
        "power supply error last week",
        "memory issue serial CZ2046028W",
        "network connectivity problem closed cases",
        "BIOS update proliant servers",
        "performance degradation 2024-01-15",
        "fan failure open cases",
        "disk error P1234 yesterday"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        
        try:
            parsed = query_processor.parse_query(query)
            
            print(f"   Type: {parsed.query_type}")
            print(f"   Keywords: {parsed.keywords}")
            print(f"   Technical terms: {parsed.technical_terms}")
            print(f"   Product hints: {parsed.product_hints}")
            print(f"   Issue hints: {parsed.issue_category_hints}")
            print(f"   Filters: {len(parsed.filters)}")
            print(f"   Confidence: {parsed.confidence:.2f}")
            
            for filter_obj in parsed.filters:
                print(f"     - {filter_obj.filter_type.value}: {filter_obj.field} {filter_obj.operator} {filter_obj.value}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Query processing tests completed")


async def test_similarity_search():
    """Test similarity search functionality."""
    print("\n🔍 Testing Similarity Search...")
    
    try:
        # Initialize components
        pinecone_client = await get_pinecone_client()
        embedding_generator = await get_embedding_generator()
        
        async for session in get_db():
            postgres_connector = PostgresConnector(session)
            
            # Create similarity engine
            search_engine = await create_similarity_engine(
                pinecone_client, postgres_connector, embedding_generator
            )
            
            # Configure search
            config = SearchConfig(
                similarity_threshold=0.6,
                max_results=5,
                include_knowledge=True,
                boost_recent_cases=True,
                boost_successful_resolutions=True
            )
            
            test_scenarios = [
                {
                    "query": "hard drive failure orange LED",
                    "type": SearchType.VECTOR_SIMILARITY,
                    "context": {}
                },
                {
                    "query": "power supply error DL380",
                    "type": SearchType.TEXT_SEARCH,
                    "context": {"product_hierarchy_id": "aGS27000000NvFXGA0"}
                },
                {
                    "query": "memory issue blinking lights",
                    "type": SearchType.HYBRID,
                    "context": {"status": "Closed"}
                }
            ]
            
            for i, scenario in enumerate(test_scenarios):
                print(f"\n🎯 Test {i+1}: {scenario['type'].value.upper()} search")
                print(f"   Query: '{scenario['query']}'")
                print(f"   Context: {scenario['context']}")
                
                try:
                    results = await search_engine.search(
                        query_text=scenario["query"],
                        search_type=scenario["type"],
                        query_context=scenario["context"],
                        config=config
                    )
                    
                    print(f"   Found {len(results)} results:")
                    
                    for j, result in enumerate(results[:3]):  # Show top 3
                        print(f"     {j+1}. {result.title[:60]}...")
                        print(f"        Type: {result.result_type}")
                        print(f"        Similarity: {result.similarity_score:.3f}")
                        print(f"        Relevance: {result.relevance_score:.3f}")
                        print(f"        Confidence: {result.confidence_level}")
                        
                        if result.ranking_factors:
                            factors = ", ".join([
                                f"{k}:{v:.2f}" for k, v in result.ranking_factors.items()
                            ])
                            print(f"        Factors: {factors}")
                        
                        print(f"        Preview: {result.content_preview[:100]}...")
                
                except Exception as e:
                    print(f"   ❌ Search failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            break  # Exit after first session
        
        print("\n✅ Similarity search tests completed")
        
    except Exception as e:
        print(f"❌ Similarity search test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_search_suggestions():
    """Test search suggestions functionality."""
    print("\n💡 Testing Search Suggestions...")
    
    try:
        pinecone_client = await get_pinecone_client()
        embedding_generator = await get_embedding_generator()
        
        async for session in get_db():
            postgres_connector = PostgresConnector(session)
            
            search_engine = await create_similarity_engine(
                pinecone_client, postgres_connector, embedding_generator
            )
            
            partial_queries = [
                "hard",
                "power",
                "memory",
                "network",
                "boot"
            ]
            
            for partial in partial_queries:
                suggestions = await search_engine.get_search_suggestions(partial)
                print(f"   '{partial}' → {suggestions}")
            
            break
        
        print("\n✅ Search suggestions tests completed")
        
    except Exception as e:
        print(f"❌ Search suggestions test failed: {e}")


async def performance_test():
    """Test search performance."""
    print("\n⚡ Testing Search Performance...")
    
    try:
        pinecone_client = await get_pinecone_client()
        embedding_generator = await get_embedding_generator()
        
        async for session in get_db():
            postgres_connector = PostgresConnector(session)
            
            search_engine = await create_similarity_engine(
                pinecone_client, postgres_connector, embedding_generator
            )
            
            test_query = "server hardware failure troubleshooting"
            num_tests = 5
            
            total_time = 0
            
            for i in range(num_tests):
                start_time = datetime.now()
                
                results = await search_engine.search(
                    query_text=test_query,
                    search_type=SearchType.HYBRID
                )
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                total_time += duration
                
                print(f"   Test {i+1}: {duration:.3f}s ({len(results)} results)")
            
            avg_time = total_time / num_tests
            print(f"\n   Average response time: {avg_time:.3f}s")
            
            if avg_time < 2.0:
                print("   ✅ Performance target met (< 2s)")
            else:
                print("   ⚠️ Performance target missed (> 2s)")
            
            break
        
        print("\n✅ Performance tests completed")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")


async def main():
    """Run all search tests."""
    try:
        print("🚀 Starting Search Engine Tests...")
        print(f"Started at: {datetime.now()}")
        
        # Test query processing
        await test_query_processing()
        
        # Test similarity search
        await test_similarity_search()
        
        # Test search suggestions
        await test_search_suggestions()
        
        # Test performance
        await performance_test()
        
        print(f"\n✅ All search tests completed at: {datetime.now()}")
        return True
        
    except Exception as e:
        print(f"❌ Search tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)