#!/usr/bin/env python3
"""
Setup SQLite database for KMS-V1 testing
Creates database with sample data for immediate testing
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
from typing import List, Dict

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from data.models import Base, Case, KnowledgeArticle, ProductHierarchy
from data.database import DatabaseManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SQLiteSetup:
    """Setup SQLite database with sample data."""
    
    def __init__(self, db_path: str = "./kms_v1.db"):
        self.db_path = db_path
        self.db_url = f"sqlite:///{db_path}"
        
    def create_tables(self):
        """Create all database tables."""
        print("🗄️ Creating SQLite database tables...")
        
        # Create engine and tables
        engine = create_engine(self.db_url, echo=False)
        Base.metadata.create_all(engine)
        
        print(f"✅ Database created at: {self.db_path}")
        return engine
    
    def insert_sample_data(self, engine):
        """Insert sample data for testing."""
        print("📝 Inserting sample data...")
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Insert product hierarchies
            products = [
                ProductHierarchy(
                    id="proliant-001",
                    product_name="HPE ProLiant DL380 Gen10 Plus",
                    product_category="Server",
                    product_family="ProLiant",
                    product_line="DL380"
                ),
                ProductHierarchy(
                    id="synergy-001", 
                    product_name="HPE Synergy 480 Gen10",
                    product_category="Server",
                    product_family="Synergy",
                    product_line="480"
                ),
                ProductHierarchy(
                    id="storage-001",
                    product_name="HPE MSA 2050",
                    product_category="Storage",
                    product_family="MSA",
                    product_line="2050"
                )
            ]
            
            for product in products:
                session.merge(product)
            
            # Insert sample cases
            cases = [
                Case(
                    case_number="HPE-2024-001234",
                    subject_description="ProLiant DL380 Gen10 Plus boot failure after firmware update",
                    issue_plain_text="Server fails to boot after updating iLO firmware to version 2.78. System shows POST error code 1762 and stops at 'Initializing Storage Subsystem'. No changes to hardware configuration. Server was working normally before firmware update. Customer reports similar issues on 3 other identical servers in their environment.",
                    resolution_plain_text="1. Boot server to iLO web interface\n2. Reset iLO to factory defaults via jumper\n3. Re-flash iLO firmware using SPP 2024.03.0\n4. Clear NVRAM using F9 setup\n5. Restore BIOS settings from backup\n6. Verify all storage controllers are detected\n7. Boot to OS successfully\n\nRoot cause: Corrupted iLO firmware causing storage controller initialization failure.",
                    status_text="Resolved",
                    product_hierarchy_id="proliant-001",
                    created_at=datetime.now() - timedelta(days=30),
                    closed_date_timestamp=datetime.now() - timedelta(days=29),
                    issue_embedding_id="emb-case-001-issue",
                    resolution_embedding_id="emb-case-001-resolution"
                ),
                Case(
                    case_number="HPE-2024-001189", 
                    subject_description="DL360 Gen10 intermittent boot issues after power outage",
                    issue_plain_text="Customer reports intermittent boot failures on DL360 Gen10 servers following facility power outage. Approximately 30% boot failure rate. Servers that fail show various POST codes including 1762, 1764, and sometimes boot to OS normally. UPS systems were functioning during outage.",
                    resolution_plain_text="1. Performed comprehensive hardware diagnostics\n2. Updated BIOS to latest version\n3. Reseated all memory modules\n4. Checked power supply voltages\n5. Replaced faulty DIMM in slot A1\n6. Updated system firmware bundle\n7. Configured memory mirroring for redundancy\n\nIssue resolved - memory module failure was causing intermittent issues.",
                    status_text="Closed",
                    product_hierarchy_id="proliant-001",
                    created_at=datetime.now() - timedelta(days=20),
                    closed_date_timestamp=datetime.now() - timedelta(days=18),
                    issue_embedding_id="emb-case-002-issue",
                    resolution_embedding_id="emb-case-002-resolution"
                ),
                Case(
                    case_number="HPE-2024-002045",
                    subject_description="Synergy 480 Gen10 network connectivity issues",
                    issue_plain_text="Network connectivity randomly drops on Synergy 480 Gen10 compute modules. Issue occurs approximately every 2-3 hours and requires network interface reset. No changes to network configuration. Issue started after recent OneView update.",
                    resolution_plain_text="1. Analyzed OneView logs and found driver incompatibility\n2. Updated network adapter drivers to latest version\n3. Reconfigured network profiles in OneView\n4. Applied firmware updates to interconnect modules\n5. Tested for 48 hours with no connectivity drops\n\nRoot cause: Driver incompatibility with new OneView version.",
                    status_text="Resolved",
                    product_hierarchy_id="synergy-001", 
                    created_at=datetime.now() - timedelta(days=15),
                    closed_date_timestamp=datetime.now() - timedelta(days=14),
                    issue_embedding_id="emb-case-003-issue",
                    resolution_embedding_id="emb-case-003-resolution"
                ),
                Case(
                    case_number="HPE-2024-002156",
                    subject_description="MSA 2050 storage array performance degradation",
                    issue_plain_text="Customer experiencing significant performance degradation on MSA 2050 storage array. IOPS dropped from 15,000 to 3,000 over past week. No hardware changes. All drives showing healthy status in management interface.",
                    resolution_plain_text="1. Analyzed storage array performance logs\n2. Found controller cache configuration issue\n3. Reconfigured read/write cache ratios\n4. Updated storage controller firmware\n5. Optimized disk group configurations\n6. Performance restored to normal levels\n\nRoot cause: Suboptimal cache configuration after firmware update.",
                    status_text="Resolved",
                    product_hierarchy_id="storage-001",
                    created_at=datetime.now() - timedelta(days=10),
                    closed_date_timestamp=datetime.now() - timedelta(days=8),
                    issue_embedding_id="emb-case-004-issue",
                    resolution_embedding_id="emb-case-004-resolution"
                ),
                Case(
                    case_number="HPE-2024-002289",
                    subject_description="ProLiant server memory errors and system crashes",
                    issue_plain_text="ProLiant DL380 Gen10 Plus experiencing frequent memory errors and system crashes. Error logs show correctable and uncorrectable memory errors. System crashes approximately every 6-8 hours during high memory usage.",
                    resolution_plain_text="1. Ran comprehensive memory diagnostics\n2. Identified faulty DIMM in slot A2\n3. Replaced defective memory module\n4. Configured memory mirroring for redundancy\n5. Stress tested system for 72 hours\n6. No further crashes or memory errors\n\nRoot cause: Hardware failure in memory module.",
                    status_text="Closed",
                    product_hierarchy_id="proliant-001",
                    created_at=datetime.now() - timedelta(days=5),
                    closed_date_timestamp=datetime.now() - timedelta(days=3),
                    issue_embedding_id="emb-case-005-issue", 
                    resolution_embedding_id="emb-case-005-resolution"
                )
            ]
            
            for case in cases:
                session.merge(case)
            
            # Insert sample knowledge articles
            articles = [
                KnowledgeArticle(
                    title="iLO Firmware Recovery Procedures",
                    content="This document provides step-by-step procedures for recovering corrupted iLO firmware on HPE ProLiant servers...",
                    article_type="CFI",
                    is_published=True,
                    created_at=datetime.now() - timedelta(days=60),
                    updated_at=datetime.now() - timedelta(days=30),
                    content_embedding_id="emb-kb-001"
                ),
                KnowledgeArticle(
                    title="ProLiant Boot Issues Troubleshooting Guide",
                    content="Comprehensive troubleshooting guide for ProLiant server boot issues including POST codes, firmware problems, and hardware diagnostics...",
                    article_type="KB",
                    is_published=True,
                    created_at=datetime.now() - timedelta(days=45),
                    updated_at=datetime.now() - timedelta(days=20),
                    content_embedding_id="emb-kb-002"
                ),
                KnowledgeArticle(
                    title="Memory Diagnostics and Replacement Guide", 
                    content="Detailed procedures for diagnosing memory issues, running memory tests, and replacing memory modules in HPE servers...",
                    article_type="KB",
                    is_published=True,
                    created_at=datetime.now() - timedelta(days=40),
                    updated_at=datetime.now() - timedelta(days=15),
                    content_embedding_id="emb-kb-003"
                )
            ]
            
            for article in articles:
                session.merge(article)
            
            session.commit()
            print(f"✅ Inserted {len(products)} products, {len(cases)} cases, {len(articles)} knowledge articles")
            
        except Exception as e:
            print(f"❌ Error inserting data: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def verify_data(self):
        """Verify data was inserted correctly."""
        print("🔍 Verifying database data...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   Tables created: {', '.join(tables)}")
        
        # Check data counts
        cursor.execute("SELECT COUNT(*) FROM cases")
        case_count = cursor.fetchone()[0]
        print(f"   Cases: {case_count}")
        
        cursor.execute("SELECT COUNT(*) FROM knowledge_articles")
        kb_count = cursor.fetchone()[0] 
        print(f"   Knowledge Articles: {kb_count}")
        
        cursor.execute("SELECT COUNT(*) FROM product_hierarchies")
        product_count = cursor.fetchone()[0]
        print(f"   Products: {product_count}")
        
        conn.close()
        
        if case_count > 0 and kb_count > 0:
            print("✅ Database verification successful!")
            return True
        else:
            print("❌ Database verification failed!")
            return False


def main():
    """Main setup function."""
    print("🚀 Setting up SQLite database for KMS-V1...")
    
    # Initialize setup
    db_setup = SQLiteSetup()
    
    # Remove existing database
    if os.path.exists(db_setup.db_path):
        os.remove(db_setup.db_path)
        print(f"🗑️ Removed existing database: {db_setup.db_path}")
    
    try:
        # Create tables
        engine = db_setup.create_tables()
        
        # Insert sample data
        db_setup.insert_sample_data(engine)
        
        # Verify data
        if db_setup.verify_data():
            print("\n🎉 SQLite database setup complete!")
            print(f"📍 Database location: {os.path.abspath(db_setup.db_path)}")
            print(f"🔗 Connection string: sqlite:///{db_setup.db_path}")
            print("\n📝 Next steps:")
            print("   1. Update .env file: DATABASE_URL=sqlite+aiosqlite:///./kms_v1.db")
            print("   2. Restart the API server")
            print("   3. Test search endpoints")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)