#!/usr/bin/env python3
"""
Knowledge Article Vectorization Script

This script vectorizes knowledge articles and adds them to ChromaDB for semantic search.
It processes both existing and newly generated articles.
"""

import asyncio
import sqlite3
import chromadb
from chromadb.config import Settings
import logging
from typing import List, Dict
from datetime import datetime
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeVectorizer:
    def __init__(self, db_path: str = "data/kms_v1.db", chroma_path: str = "data/chromadb_data_comprehensive"):
        self.db_path = db_path
        self.chroma_path = chroma_path
        self.conn = None
        self.chroma_client = None
        self.collection = None
        
    def connect_db(self):
        """Connect to SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
    def disconnect_db(self):
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
            
    def setup_chroma(self):
        """Setup ChromaDB client and collection."""
        try:
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection for knowledge articles
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_embeddings",
                metadata={"description": "Knowledge articles embeddings for semantic search"}
            )
            
            logger.info(f"ChromaDB collection setup complete. Current count: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Error setting up ChromaDB: {e}")
            raise
            
    def get_articles_to_vectorize(self) -> List[Dict]:
        """Get knowledge articles from database."""
        cursor = self.conn.cursor()
        
        query = """
        SELECT article_id, title, content, summary, category, 
               product_line, issue_type, resolution_type, 
               created_date, modified_date, status
        FROM Knowledge_Articles 
        WHERE status = 'Published'
        ORDER BY created_date ASC
        """
        
        cursor.execute(query)
        articles = [dict(row) for row in cursor.fetchall()]
        
        logger.info(f"Found {len(articles)} published articles to vectorize")
        return articles
        
    def check_if_vectorized(self, article_id: str) -> bool:
        """Check if article is already vectorized in ChromaDB."""
        try:
            # Try to get the document
            result = self.collection.get(ids=[article_id])
            return len(result['ids']) > 0
        except Exception:
            return False
            
    def create_document_text(self, article: Dict) -> str:
        """Create comprehensive text for vectorization."""
        # Combine title, summary, and content for better semantic representation
        doc_text = f"""Title: {article['title']}

Summary: {article['summary']}

Category: {article['category']}
Product Line: {article['product_line']}
Issue Type: {article['issue_type']}
Resolution Type: {article['resolution_type']}

Content:
{article['content']}"""
        
        return doc_text
        
    def create_metadata(self, article: Dict) -> Dict:
        """Create metadata for ChromaDB storage."""
        return {
            'title': article['title'],
            'category': article['category'],
            'product_line': article['product_line'] or '',
            'issue_type': article['issue_type'] or '',
            'resolution_type': article['resolution_type'] or '',
            'created_date': article['created_date'],
            'modified_date': article['modified_date'] or article['created_date'],
            'document_type': 'knowledge_article',
            'vectorized_at': datetime.now().isoformat()
        }
        
    def vectorize_articles(self, articles: List[Dict]):
        """Vectorize articles and add to ChromaDB."""
        
        new_articles = []
        updated_articles = []
        skipped_articles = []
        
        for article in articles:
            article_id = article['article_id']
            
            # Check if already vectorized
            if self.check_if_vectorized(article_id):
                logger.info(f"Article {article_id} already vectorized, skipping")
                skipped_articles.append(article_id)
                continue
                
            # Prepare document text and metadata
            doc_text = self.create_document_text(article)
            metadata = self.create_metadata(article)
            
            try:
                # Add to ChromaDB
                self.collection.add(
                    documents=[doc_text],
                    metadatas=[metadata],
                    ids=[article_id]
                )
                
                new_articles.append(article_id)
                logger.info(f"Vectorized article: {article_id} - {article['title'][:60]}...")
                
            except Exception as e:
                logger.error(f"Error vectorizing article {article_id}: {e}")
                
        logger.info(f"Vectorization complete:")
        logger.info(f"  - New articles vectorized: {len(new_articles)}")
        logger.info(f"  - Articles skipped (already vectorized): {len(skipped_articles)}")
        logger.info(f"  - Total articles in collection: {self.collection.count()}")
        
        return {
            'new_articles': new_articles,
            'skipped_articles': skipped_articles,
            'total_count': self.collection.count()
        }
        
    def test_search(self, query: str = "processor error troubleshooting", limit: int = 3):
        """Test semantic search on vectorized articles."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            
            print(f"\n=== Test Search Results for: '{query}' ===")
            
            if results['ids'] and len(results['ids'][0]) > 0:
                for i, (doc_id, distance, metadata) in enumerate(zip(
                    results['ids'][0], 
                    results['distances'][0], 
                    results['metadatas'][0]
                )):
                    similarity_score = 1 - distance  # Convert distance to similarity
                    print(f"\n{i+1}. {metadata['title']}")
                    print(f"   ID: {doc_id}")
                    print(f"   Category: {metadata['category']}")
                    print(f"   Similarity: {similarity_score:.3f}")
                    print(f"   Issue Type: {metadata.get('issue_type', 'N/A')}")
            else:
                print("No results found")
                
        except Exception as e:
            logger.error(f"Error testing search: {e}")
            
    def get_collection_stats(self):
        """Get statistics about the vectorized collection."""
        try:
            total_count = self.collection.count()
            
            # Get sample of metadata to analyze categories
            sample_data = self.collection.get(
                include=['metadatas'],
                limit=min(total_count, 100)  # Sample up to 100 documents
            )
            
            categories = {}
            document_types = {}
            
            for metadata in sample_data['metadatas']:
                # Count categories
                category = metadata.get('category', 'Unknown')
                categories[category] = categories.get(category, 0) + 1
                
                # Count document types
                doc_type = metadata.get('document_type', 'unknown')
                document_types[doc_type] = document_types.get(doc_type, 0) + 1
                
            print(f"\n=== Collection Statistics ===")
            print(f"Total documents: {total_count}")
            print(f"\nCategories:")
            for category, count in sorted(categories.items()):
                print(f"  - {category}: {count}")
                
            print(f"\nDocument Types:")
            for doc_type, count in sorted(document_types.items()):
                print(f"  - {doc_type}: {count}")
                
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            
    def run_vectorization(self):
        """Main execution method."""
        
        self.connect_db()
        
        try:
            # Setup ChromaDB
            self.setup_chroma()
            
            # Get articles to vectorize
            articles = self.get_articles_to_vectorize()
            
            if not articles:
                logger.info("No articles found to vectorize")
                return
                
            # Vectorize articles
            results = self.vectorize_articles(articles)
            
            # Display collection statistics
            self.get_collection_stats()
            
            # Test search functionality
            self.test_search("network connectivity issues")
            self.test_search("server boot failure")
            
            return results
            
        finally:
            self.disconnect_db()

def main():
    """Main execution function."""
    vectorizer = KnowledgeVectorizer()
    
    print("=== Knowledge Article Vectorization ===")
    print("Processing knowledge articles for semantic search...")
    
    try:
        results = vectorizer.run_vectorization()
        
        if results:
            print(f"\n✅ Vectorization completed successfully!")
            print(f"   - New articles added: {len(results['new_articles'])}")
            print(f"   - Total vectors in database: {results['total_count']}")
        
    except Exception as e:
        logger.error(f"Vectorization failed: {e}")
        raise

if __name__ == "__main__":
    main()