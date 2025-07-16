#!/usr/bin/env python3
"""Generate sample data for KMS-V1 development and testing."""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the backend src directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.data.database import get_db
from src.data.postgres_connector import PostgresConnector
from src.data.etl_pipeline import ETLPipeline
from src.data.models import ProductHierarchy, KnowledgeArticle


async def generate_product_hierarchies(connector: PostgresConnector):
    """Generate sample product hierarchies."""
    print("Generating product hierarchies...")
    
    hierarchies = [
        {
            "id": "aGS27000000L8DDGA0",
            "product_name": "HPE ProLiant DL380 G5",
            "product_family": "ProLiant DL", 
            "product_line": "DL380",
            "product_category": "Rack Servers",
            "level": 1
        },
        {
            "id": "aGS27000000NvFXGA0", 
            "product_name": "HPE ProLiant DL380 Gen10",
            "product_family": "ProLiant DL",
            "product_line": "DL380", 
            "product_category": "Rack Servers",
            "level": 1
        },
        {
            "id": "aGS27000000LtF3GAK",
            "product_name": "HPE ProLiant DL380 Gen9",
            "product_family": "ProLiant DL",
            "product_line": "DL380",
            "product_category": "Rack Servers", 
            "level": 1
        },
        {
            "id": "aGS27000000fzo1WAA",
            "product_name": "HPE ProLiant DL385 Gen10 Plus",
            "product_family": "ProLiant DL",
            "product_line": "DL385",
            "product_category": "Rack Servers",
            "level": 1
        },
        {
            "id": "aGS27000000CbTPGA0",
            "product_name": "HPE ProLiant DL360 Gen10",
            "product_family": "ProLiant DL", 
            "product_line": "DL360",
            "product_category": "Rack Servers",
            "level": 1
        },
        {
            "id": "aGS27000000CbBiGAK",
            "product_name": "HPE ProLiant DL360 Gen10",
            "product_family": "ProLiant DL",
            "product_line": "DL360", 
            "product_category": "Rack Servers",
            "level": 1
        },
        {
            "id": "aGS27000000Lyj8GAC",
            "product_name": "HPE ProLiant DL360p Gen8",
            "product_family": "ProLiant DL",
            "product_line": "DL360",
            "product_category": "Rack Servers",
            "level": 1
        },
        {
            "id": "aGS27000000yttGAC", 
            "product_name": "HPE ProLiant DL380p Gen8",
            "product_family": "ProLiant DL",
            "product_line": "DL380",
            "product_category": "Rack Servers",
            "level": 1
        }
    ]
    
    for hierarchy_data in hierarchies:
        hierarchy = ProductHierarchy(**hierarchy_data)
        connector.session.add(hierarchy)
    
    await connector.session.flush()
    print(f"✅ Generated {len(hierarchies)} product hierarchies")


async def generate_knowledge_articles(connector: PostgresConnector):
    """Generate sample knowledge articles."""
    print("Generating knowledge articles...")
    
    articles = [
        {
            "title": "Hard Drive Failure Troubleshooting Guide",
            "content": """
# Hard Drive Failure Troubleshooting

## Symptoms
- Drive LED blinking orange/amber
- SMART errors in system logs
- Array degraded status
- System performance issues

## Diagnosis Steps
1. Check drive LED status indicators
2. Review system event logs
3. Run SMART diagnostics
4. Check array configuration

## Resolution
1. Identify failed drive location
2. Order replacement drive (same model/capacity)
3. Replace drive following hot-swap procedures
4. Verify array rebuild completion
5. Test system performance

## Prevention
- Monitor SMART statistics regularly
- Maintain proper environmental conditions
- Schedule predictive replacements
            """,
            "summary": "Comprehensive guide for diagnosing and resolving hard drive failures in HPE servers",
            "article_type": "KB",
            "category": "Hardware",
            "tags": ["hard drive", "failure", "troubleshooting", "SMART", "replacement"],
            "status": "published",
            "is_published": True,
            "created_by": "system",
            "product_hierarchy_id": "aGS27000000NvFXGA0"
        },
        {
            "title": "Power Supply Failure Resolution",
            "content": """
# Power Supply Failure Resolution

## Identification
- Power supply fault LED
- System shutdown or instability
- Audible alarms
- Redundancy lost alerts

## Immediate Actions
1. Check power cable connections
2. Verify input power quality
3. Test with different power source
4. Check environmental conditions

## Replacement Procedure
1. Identify correct replacement part
2. Power down system if non-redundant
3. Remove failed PSU
4. Install new PSU
5. Verify operation and redundancy

## Validation
- All LEDs green
- No error messages
- Full redundancy restored
            """,
            "summary": "Step-by-step guide for power supply failure diagnosis and replacement",
            "article_type": "CFI",
            "category": "Power",
            "tags": ["power supply", "PSU", "failure", "redundancy", "replacement"],
            "status": "published", 
            "is_published": True,
            "created_by": "system",
            "product_hierarchy_id": "aGS27000000NvFXGA0"
        },
        {
            "title": "Memory Module Troubleshooting",
            "content": """
# Memory Module Troubleshooting

## Common Symptoms
- System fails to POST
- Memory errors in logs
- Blue screen/kernel panic
- Performance degradation

## Diagnostic Process
1. Run memory diagnostic tests
2. Check DIMM seating
3. Review error logs
4. Test individual modules

## Resolution Steps
1. Power down system
2. Reseat memory modules
3. Replace failed DIMMs
4. Update BIOS if needed
5. Run full memory test

## Best Practices
- Use HPE qualified memory
- Follow population guidelines
- Maintain proper grounding
            """,
            "summary": "Memory module failure diagnosis and resolution procedures",
            "article_type": "KB", 
            "category": "Memory",
            "tags": ["memory", "DIMM", "POST", "diagnostic", "replacement"],
            "status": "published",
            "is_published": True,
            "created_by": "system",
            "product_hierarchy_id": "aGS27000000CbTPGA0"
        },
        {
            "title": "RAID Controller Configuration", 
            "content": """
# RAID Controller Configuration

## Overview
Configure RAID arrays for optimal performance and redundancy.

## Supported RAID Levels
- RAID 0: Performance (no redundancy)
- RAID 1: Mirroring
- RAID 5: Distributed parity
- RAID 6: Dual parity
- RAID 10: Mirrored stripes

## Configuration Steps
1. Access RAID BIOS/UEFI
2. Select controller
3. Create logical drive
4. Choose RAID level
5. Select physical drives
6. Set stripe size
7. Initialize array

## Performance Tuning
- Choose appropriate stripe size
- Enable write cache (with BBU)
- Configure read-ahead
- Monitor array health
            """,
            "summary": "RAID controller configuration guide for HPE servers",
            "article_type": "CFI",
            "category": "Storage",
            "tags": ["RAID", "controller", "configuration", "performance", "redundancy"],
            "status": "published",
            "is_published": True, 
            "created_by": "system",
            "product_hierarchy_id": "aGS27000000LtF3GAK"
        },
        {
            "title": "iLO Troubleshooting Guide",
            "content": """
# iLO Troubleshooting Guide

## Common Issues
- iLO not responding
- Network connectivity problems
- Authentication failures
- Firmware corruption

## Basic Troubleshooting
1. Check network cables
2. Verify IP configuration
3. Test with different browser
4. Clear browser cache

## Advanced Resolution
1. Reset iLO to defaults
2. Update iLO firmware
3. Reconfigure network settings
4. Check license status

## Network Configuration
- Dedicated management port
- Shared network port options
- VLAN configuration
- IPv6 support

## Security Best Practices
- Change default passwords
- Enable secure authentication
- Configure SSL certificates
- Regular firmware updates
            """,
            "summary": "Comprehensive iLO troubleshooting and configuration guide",
            "article_type": "KB",
            "category": "Management",
            "tags": ["iLO", "management", "network", "troubleshooting", "security"],
            "status": "published",
            "is_published": True,
            "created_by": "system", 
            "product_hierarchy_id": "aGS27000000NvFXGA0"
        }
    ]
    
    for article_data in articles:
        article = KnowledgeArticle(**article_data)
        connector.session.add(article)
    
    await connector.session.flush()
    print(f"✅ Generated {len(articles)} knowledge articles")


async def main():
    """Main function to generate all sample data."""
    try:
        print("🚀 Starting sample data generation...")
        
        async for session in get_db():
            connector = PostgresConnector(session)
            
            # Generate product hierarchies
            await generate_product_hierarchies(connector)
            
            # Generate knowledge articles  
            await generate_knowledge_articles(connector)
            
            # Generate case data using ETL pipeline
            print("Generating case data...")
            pipeline = ETLPipeline(connector)
            total_cases = await pipeline.run_full_etl(generate_count=500, batch_size=50)
            
            # Commit all changes
            await session.commit()
            
            print(f"\n✅ Sample data generation completed!")
            print(f"📊 Generated:")
            print(f"   - 8 Product Hierarchies")
            print(f"   - 5 Knowledge Articles") 
            print(f"   - {total_cases} Case Records")
            
            # Validate data
            validation = await pipeline.validate_data_quality()
            print(f"\n📈 Data Quality Report:")
            print(f"   - Total Cases: {validation['total_cases']}")
            print(f"   - Status Distribution: {validation['status_distribution']}")
            
            return True
            
    except Exception as e:
        print(f"❌ Sample data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)