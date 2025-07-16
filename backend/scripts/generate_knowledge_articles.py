#!/usr/bin/env python3
"""
Knowledge Article Generation Script

This script analyzes case data and generates comprehensive knowledge articles
based on common issue patterns, grouping similar cases chronologically and
creating structured troubleshooting guides.
"""

import asyncio
import sqlite3
import re
from datetime import datetime
from typing import List, Dict, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeArticleGenerator:
    def __init__(self, db_path: str = "data/kms_v1.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect_db(self):
        """Connect to SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
    def disconnect_db(self):
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
            
    def analyze_case_patterns(self) -> Dict[str, List[Dict]]:
        """Analyze cases and group them by issue patterns."""
        cursor = self.conn.cursor()
        
        # Get all cases with issue patterns
        query = """
        SELECT Case_Number, Subject_Description, Issue_Plain_Text, 
               Resolution_Plain_Text, Status_Text, created_at
        FROM Cases 
        WHERE Subject_Description LIKE '% - %'
        ORDER BY created_at ASC
        """
        
        cursor.execute(query)
        cases = [dict(row) for row in cursor.fetchall()]
        
        # Group cases by issue type
        issue_groups = {}
        
        for case in cases:
            # Extract issue category from subject description
            subject = case['Subject_Description']
            if ' - ' in subject:
                issue_category = subject.split(' - ', 1)[1].strip()
                
                # Normalize similar issues
                normalized_issue = self.normalize_issue_type(issue_category)
                
                if normalized_issue not in issue_groups:
                    issue_groups[normalized_issue] = []
                    
                issue_groups[normalized_issue].append(case)
                
        logger.info(f"Identified {len(issue_groups)} unique issue patterns")
        return issue_groups
        
    def normalize_issue_type(self, issue: str) -> str:
        """Normalize issue types to group similar problems."""
        issue_lower = issue.lower()
        
        # Define normalization patterns
        if 'processor' in issue_lower or 'cpu' in issue_lower:
            return 'processor_errors'
        elif 'network' in issue_lower or 'connectivity' in issue_lower:
            return 'network_issues'
        elif 'raid' in issue_lower or 'controller' in issue_lower:
            return 'raid_controller_issues'
        elif 'hard drive' in issue_lower or 'hdd' in issue_lower or 'disk' in issue_lower:
            return 'hard_drive_failures'
        elif 'bios' in issue_lower or 'firmware' in issue_lower:
            return 'bios_firmware_issues'
        elif 'boot' in issue_lower or 'post' in issue_lower:
            return 'boot_failures'
        elif 'memory' in issue_lower or 'dimm' in issue_lower or 'ram' in issue_lower:
            return 'memory_issues'
        elif 'power' in issue_lower or 'psu' in issue_lower:
            return 'power_supply_issues'
        elif 'overheating' in issue_lower or 'temperature' in issue_lower:
            return 'thermal_issues'
        else:
            return 'other_issues'
            
    def extract_product_info(self, cases: List[Dict]) -> Dict[str, str]:
        """Extract product information from cases."""
        products = set()
        product_lines = set()
        
        for case in cases:
            subject = case['Subject_Description']
            if 'HPE' in subject:
                # Extract product info
                parts = subject.split()
                for i, part in enumerate(parts):
                    if part == 'HPE' and i + 1 < len(parts):
                        product_line = parts[i + 1]
                        product_lines.add(product_line)
                        
                        # Get full product description up to the '-'
                        product_desc = subject.split(' - ')[0].strip()
                        products.add(product_desc)
                        
        return {
            'product_lines': list(product_lines),
            'products': list(products)
        }
        
    def generate_article_content(self, issue_type: str, cases: List[Dict]) -> Dict[str, str]:
        """Generate knowledge article content from case data."""
        
        # Get common resolutions
        resolutions = [case['Resolution_Plain_Text'] for case in cases if case['Resolution_Plain_Text']]
        unique_resolutions = list(set(resolutions))
        
        # Get product info
        product_info = self.extract_product_info(cases)
        
        # Generate title
        title = self.generate_article_title(issue_type, len(cases))
        
        # Generate summary
        summary = self.generate_article_summary(issue_type, len(cases), product_info['product_lines'][:3])
        
        # Generate detailed content
        content = self.generate_detailed_content(issue_type, cases, unique_resolutions, product_info)
        
        # Determine category and metadata
        category = self.determine_category(issue_type)
        
        return {
            'title': title,
            'summary': summary,
            'content': content,
            'category': category,
            'product_line': ', '.join(product_info['product_lines'][:3]),
            'issue_type': issue_type.replace('_', ' ').title(),
            'resolution_type': self.determine_resolution_type(unique_resolutions)
        }
        
    def generate_article_title(self, issue_type: str, case_count: int) -> str:
        """Generate descriptive article title."""
        title_map = {
            'processor_errors': f'HPE Server Processor Error Troubleshooting Guide (Based on {case_count} Cases)',
            'network_issues': f'Network Connectivity Troubleshooting for HPE Servers (Based on {case_count} Cases)',
            'raid_controller_issues': f'RAID Controller Troubleshooting and Resolution Guide (Based on {case_count} Cases)',
            'hard_drive_failures': f'Hard Drive Failure Diagnosis and Replacement Procedures (Based on {case_count} Cases)',
            'bios_firmware_issues': f'BIOS and Firmware Recovery Guide for HPE Servers (Based on {case_count} Cases)',
            'boot_failures': f'Server Boot Failure Troubleshooting and Recovery (Based on {case_count} Cases)',
            'memory_issues': f'Memory (DIMM) Troubleshooting and Replacement Guide (Based on {case_count} Cases)',
            'power_supply_issues': f'Power Supply Failure Diagnosis and Resolution (Based on {case_count} Cases)',
            'thermal_issues': f'Server Overheating Troubleshooting and Thermal Management (Based on {case_count} Cases)'
        }
        
        return title_map.get(issue_type, f'HPE Server {issue_type.replace("_", " ").title()} Guide (Based on {case_count} Cases)')
        
    def generate_article_summary(self, issue_type: str, case_count: int, product_lines: List[str]) -> str:
        """Generate article summary."""
        products_str = ', '.join(product_lines) if product_lines else 'HPE Servers'
        
        summary_map = {
            'processor_errors': f'Comprehensive guide for diagnosing and resolving processor errors on {products_str}. Based on analysis of {case_count} real customer cases.',
            'network_issues': f'Step-by-step troubleshooting for network connectivity problems affecting {products_str}. Compiled from {case_count} customer incidents.',
            'raid_controller_issues': f'Complete RAID controller troubleshooting procedures for {products_str}. Derived from {case_count} field cases.',
            'hard_drive_failures': f'Hard drive failure detection and replacement procedures for {products_str}. Based on {case_count} successful resolutions.',
            'bios_firmware_issues': f'BIOS corruption and firmware recovery procedures for {products_str}. Compiled from {case_count} customer cases.',
            'boot_failures': f'Comprehensive boot failure troubleshooting for {products_str}. Based on {case_count} real-world scenarios.',
            'memory_issues': f'Memory module troubleshooting and replacement guide for {products_str}. Derived from {case_count} customer cases.',
            'power_supply_issues': f'Power supply troubleshooting and replacement procedures for {products_str}. Based on {case_count} field cases.',
            'thermal_issues': f'Server thermal management and overheating resolution for {products_str}. Compiled from {case_count} customer incidents.'
        }
        
        return summary_map.get(issue_type, f'Troubleshooting guide for {issue_type.replace("_", " ")} on {products_str}. Based on {case_count} cases.')
        
    def generate_detailed_content(self, issue_type: str, cases: List[Dict], resolutions: List[str], product_info: Dict) -> str:
        """Generate detailed article content."""
        
        content = f"""# {issue_type.replace('_', ' ').title()} Troubleshooting Guide

## Overview
This article provides comprehensive troubleshooting steps for {issue_type.replace('_', ' ')} issues affecting HPE servers. The procedures in this guide are based on analysis of {len(cases)} real customer cases and proven resolution methods.

## Affected Products
- {chr(10).join(['- ' + product for product in product_info['products'][:10]])}

## Common Symptoms
Based on customer reports, the following symptoms are commonly observed:
"""
        
        # Extract unique symptoms from case descriptions
        symptoms = set()
        for case in cases[:10]:  # Use first 10 cases for symptoms
            issue_text = case['Issue_Plain_Text']
            if issue_text:
                symptoms.add(issue_text.strip())
                
        for symptom in list(symptoms)[:5]:  # Show top 5 symptoms
            content += f"- {symptom}\n"
            
        content += f"""
## Troubleshooting Steps

### Step 1: Initial Diagnosis
1. Verify system power and LED status indicators
2. Check for any error messages or codes
3. Review system logs for relevant entries

### Step 2: Common Resolution Methods
Based on successful case resolutions, try the following methods in order:

"""
        
        # Add resolution steps
        for i, resolution in enumerate(resolutions[:8], 1):  # Show top 8 resolutions
            if resolution and resolution.strip():
                content += f"{i}. {resolution.strip()}\n"
                
        content += f"""
## Case Examples
Here are examples from actual customer cases that demonstrate successful resolutions:

"""
        
        # Add 3 case examples
        for i, case in enumerate(cases[:3], 1):
            content += f"""### Case Example {i}: {case['Case_Number']}
**Issue**: {case['Issue_Plain_Text']}
**Resolution**: {case['Resolution_Plain_Text']}
**Status**: {case['Status_Text']}

"""
        
        content += f"""
## Prevention and Best Practices
To minimize the occurrence of {issue_type.replace('_', ' ')} issues:

1. Maintain regular firmware updates
2. Ensure proper environmental conditions
3. Implement proactive monitoring
4. Follow recommended maintenance schedules

## Related Articles
- HPE Server Hardware Troubleshooting Guide
- System Monitoring and Alerting Best Practices
- Preventive Maintenance Procedures

## Additional Resources
- HPE Support Portal: [support.hpe.com](https://support.hpe.com)
- Product Documentation and QuickSpecs
- HPE Community Forums

---
*This article was automatically generated from analysis of {len(cases)} customer cases on {datetime.now().strftime('%Y-%m-%d')}.*
"""
        
        return content
        
    def determine_category(self, issue_type: str) -> str:
        """Determine article category based on issue type."""
        category_map = {
            'processor_errors': 'Hardware',
            'network_issues': 'Networking',
            'raid_controller_issues': 'Storage',
            'hard_drive_failures': 'Storage',
            'bios_firmware_issues': 'Firmware',
            'boot_failures': 'Hardware',
            'memory_issues': 'Hardware',
            'power_supply_issues': 'Hardware',
            'thermal_issues': 'Environmental'
        }
        
        return category_map.get(issue_type, 'General')
        
    def determine_resolution_type(self, resolutions: List[str]) -> str:
        """Determine primary resolution type."""
        resolution_text = ' '.join(resolutions).lower()
        
        if 'replace' in resolution_text:
            return 'Hardware Replacement'
        elif 'firmware' in resolution_text or 'update' in resolution_text:
            return 'Firmware Update'
        elif 'restart' in resolution_text or 'reboot' in resolution_text:
            return 'System Restart'
        elif 'configure' in resolution_text or 'setting' in resolution_text:
            return 'Configuration Change'
        else:
            return 'General Troubleshooting'
            
    def save_article_to_db(self, article_data: Dict[str, str], article_id: str):
        """Save generated article to Knowledge_Articles table."""
        cursor = self.conn.cursor()
        
        insert_query = """
        INSERT INTO Knowledge_Articles 
        (article_id, title, content, summary, category, product_line, 
         issue_type, resolution_type, created_date, modified_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        values = (
            article_id,
            article_data['title'],
            article_data['content'],
            article_data['summary'],
            article_data['category'],
            article_data['product_line'],
            article_data['issue_type'],
            article_data['resolution_type'],
            current_date,
            current_date,
            'Published'
        )
        
        cursor.execute(insert_query, values)
        self.conn.commit()
        
        logger.info(f"Saved article: {article_id} - {article_data['title']}")
        
    def generate_all_articles(self, min_cases: int = 5):
        """Generate knowledge articles for all issue patterns with sufficient cases."""
        
        self.connect_db()
        
        try:
            # Analyze case patterns
            issue_groups = self.analyze_case_patterns()
            
            articles_created = 0
            
            # Generate articles for groups with sufficient cases
            for issue_type, cases in issue_groups.items():
                if len(cases) >= min_cases:
                    logger.info(f"Generating article for {issue_type} ({len(cases)} cases)")
                    
                    # Generate article content
                    article_data = self.generate_article_content(issue_type, cases)
                    
                    # Create unique article ID
                    article_id = f"AUTO_{issue_type.upper()}_{datetime.now().strftime('%Y%m%d')}"
                    
                    # Save to database
                    self.save_article_to_db(article_data, article_id)
                    
                    articles_created += 1
                    
                else:
                    logger.info(f"Skipping {issue_type} - only {len(cases)} cases (minimum: {min_cases})")
                    
            logger.info(f"Successfully created {articles_created} knowledge articles")
            
        finally:
            self.disconnect_db()
            
    def list_current_articles(self):
        """List current articles in the database."""
        self.connect_db()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT article_id, title, category, created_date FROM Knowledge_Articles ORDER BY created_date DESC")
            articles = cursor.fetchall()
            
            print(f"\nCurrent Knowledge Articles ({len(articles)} total):")
            print("-" * 80)
            for article in articles:
                print(f"{article[0]}: {article[1]}")
                print(f"   Category: {article[2]} | Created: {article[3]}")
                print()
                
        finally:
            self.disconnect_db()

def main():
    """Main execution function."""
    generator = KnowledgeArticleGenerator()
    
    print("=== Knowledge Article Generator ===")
    print("Analyzing case data and generating knowledge articles...")
    
    # List current articles
    generator.list_current_articles()
    
    # Generate new articles
    generator.generate_all_articles(min_cases=5)
    
    print("Article generation complete!")
    
    # List updated articles
    generator.list_current_articles()

if __name__ == "__main__":
    main()