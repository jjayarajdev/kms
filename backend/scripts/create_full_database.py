#!/usr/bin/env python3
"""Complete database creation script with all tables and 500 cases."""

import sqlite3
import re
import logging
from pathlib import Path
from typing import List, Dict, Any
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FullDatabaseCreator:
    def __init__(self, db_path: str = "kms_v1_full.db"):
        self.db_path = db_path
        self.sql_files_dir = Path("../db-references/ddl_dml")
        
    def create_complete_schema(self) -> None:
        """Create all tables with complete SFDC schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing tables
        tables_to_drop = [
            'Cases', 'Case_Feed', 'EmailMessage', 'Feed_Comment', 
            'Product_Hierarchy', 'Service_Delivery_task', 'Activity_Task',
            'Service_Delivery_Part_Order', 'Service_Delivery_Part_Order_Line'
        ]
        
        for table in tables_to_drop:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        
        logger.info("Creating complete database schema...")
        
        # 1. Cases table (main table)
        cursor.execute("""
            CREATE TABLE Cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Case_Number TEXT UNIQUE,
                Subject_Description TEXT,
                Description_Description TEXT,
                Issue_Plain_Text TEXT,
                Cause_Plain_Text TEXT,
                Resolution_Plain_Text TEXT,
                Parent_Id TEXT,
                Status_Text TEXT,
                Support_Type TEXT,
                Record_Name TEXT,
                Product_Hierarchy_Id TEXT,
                Case_Internal_Id TEXT,
                Case_Comments_Text TEXT,
                Case_Created_Hour REAL,
                Case_Escalated_Flag INTEGER,
                Cause_Text TEXT,
                Close_Case_Reason_Text TEXT,
                Close_Comments_Text TEXT,
                Closed_Date_Timestamp TEXT,
                Elevated_Flag INTEGER,
                Elevation_ID TEXT,
                Escalated_Reason_Text TEXT,
                Impact_Summary_Text TEXT,
                Order_Type_Code TEXT,
                Origin_Name TEXT,
                GSD_Product_Number TEXT,
                Reason_Text TEXT,
                Type_Text TEXT,
                Any_Customer_Data_Loss TEXT,
                Asset_Serial_Number TEXT,
                Issue_Text TEXT,
                Install_Issue_Text TEXT,
                Resolution_Code TEXT,
                Resolution_Sub_Code_Text TEXT,
                New_Install_Text TEXT,
                Outage_Text TEXT,
                Customer_Impact_Text TEXT,
                Resolution_Text TEXT,
                Product_Series TEXT,
                GSD_Environment_Text TEXT,
                First_Touch_Time REAL,
                Service_Advisory_Text TEXT,
                Error_Codes_Text TEXT,
                Operating_System_Version_Text TEXT,
                Operating_System_Text TEXT,
                Problem_Analysis_Text TEXT,
                Case_Description TEXT,
                Solution_Class_Description_Text TEXT,
                Solution_Class_Name_Text TEXT,
                Asset_Operating_System_Text TEXT,
                Asset_Operating_System_Version_Text TEXT,
                Issue_Category_Text TEXT,
                Issue_Type_Text TEXT,
                Description_For_Others_Issue_Category_Text TEXT,
                Description_For_Others_Issue_Type_Text TEXT,
                Other_Resolution_Sub_Code_Description_Text TEXT,
                Troubleshooting_Steps_Actions_Taken_Text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Case_Feed table
        cursor.execute("""
            CREATE TABLE Case_Feed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Parent_Id TEXT,
                Type_Text TEXT,
                Case_Feed_Internal_Id TEXT,
                Is_Deleted_Flag INTEGER,
                Created_Timestamp TEXT,
                Created_By_Id TEXT,
                Last_Modified_Timestamp TEXT,
                System_Mod_Timestamp TEXT,
                Body_Text TEXT,
                Comment_Count INTEGER,
                Content_Description TEXT,
                Content_File_Name TEXT,
                Content_Size_Number INTEGER,
                Content_Type_Text TEXT,
                Inserted_By_Id TEXT,
                Like_Count INTEGER,
                Link_Url_Text TEXT,
                Network_Scope_Text TEXT,
                Related_Record_Id TEXT,
                Title_Text TEXT,
                Visibility_Text TEXT,
                Insert_GMT_Timestamp TEXT,
                Update_GMT_Timestamp TEXT,
                Is_Rich_Text_Flag INTEGER
            )
        """)
        
        # 3. EmailMessage table
        cursor.execute("""
            CREATE TABLE EmailMessage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Email_Id TEXT,
                ParentId TEXT,
                FromAddress TEXT,
                ToAddress TEXT,
                MessageDate TEXT,
                Subject TEXT,
                TextBody TEXT,
                CreatedDate TEXT
            )
        """)
        
        # 4. Feed_Comment table
        cursor.execute("""
            CREATE TABLE Feed_Comment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Feed_Comment_Internal_Id TEXT,
                Is_Deleted_Flag INTEGER,
                Created_Timestamp TEXT,
                Created_By_Id TEXT,
                Comment_Body_Text TEXT,
                Comment_Type TEXT,
                Feed_Item_Id TEXT,
                Inserted_By_Id TEXT,
                Parent_Id TEXT,
                Related_Record_Id TEXT,
                Insert_GMT_Timestamp TEXT,
                Update_GMT_Timestamp TEXT
            )
        """)
        
        # 5. Product_Hierarchy table (simplified key fields)
        cursor.execute("""
            CREATE TABLE Product_Hierarchy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Product_Hierarchy_Internal_Id TEXT,
                PM_PRODUCT_Number TEXT,
                PM_PRODUCT_Description TEXT,
                PM_PRODUCT_MODEL_Name TEXT,
                PM_PRODUCT_SERIES_Name TEXT,
                PM_PRODUCT_LINE_Name TEXT,
                PM_BUSINESS_UNIT_Name TEXT,
                PM_PLATFORM_Name TEXT,
                PM_LIFECYCLE_STATUS_Code TEXT,
                Insert_GMT_Timestamp TEXT,
                Update_GMT_Timestamp TEXT
            )
        """)
        
        # 6. Service_Delivery_task table
        cursor.execute("""
            CREATE TABLE Service_Delivery_task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Title_Text TEXT,
                Problem_Description TEXT,
                Product_Description TEXT,
                Closing_Summary_Text TEXT,
                Closing_Notes_Text TEXT,
                Case_Internal_Id TEXT,
                Plan_Of_Action_Text TEXT
            )
        """)
        
        # 7. Knowledge Articles table (for knowledge base content)
        cursor.execute("""
            CREATE TABLE Knowledge_Articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT UNIQUE,
                title TEXT,
                content TEXT,
                summary TEXT,
                category TEXT,
                product_line TEXT,
                issue_type TEXT,
                resolution_type TEXT,
                created_date TEXT,
                modified_date TEXT,
                status TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ Complete database schema created with 7 main tables")
    
    def parse_sql_insert_statements(self, sql_content: str) -> List[List[str]]:
        """Parse individual INSERT statements from SQL content."""
        # Pattern to match individual INSERT statements
        insert_pattern = r"INSERT\s+INTO\s+\w+\s*\([^)]+\)\s+VALUES\s*\(([^;]+)\);"
        matches = re.findall(insert_pattern, sql_content, re.DOTALL | re.IGNORECASE)
        
        records = []
        for match in matches:
            values = self.parse_values_string(match.strip())
            if values:
                records.append(values)
        
        return records
    
    def parse_values_string(self, values_str: str) -> List[str]:
        """Parse VALUES string into individual field values."""
        values = []
        current_value = ""
        in_string = False
        escape_next = False
        paren_count = 0
        
        i = 0
        while i < len(values_str):
            char = values_str[i]
            
            if escape_next:
                current_value += char
                escape_next = False
                i += 1
                continue
                
            if char == '\\':
                escape_next = True
                current_value += char
                i += 1
                continue
                
            if char == "'" and not escape_next:
                in_string = not in_string
                if not in_string:
                    # End of string value
                    values.append(current_value)
                    current_value = ""
                    # Skip to next comma
                    while i + 1 < len(values_str) and values_str[i + 1] in ' \t\n':
                        i += 1
                    if i + 1 < len(values_str) and values_str[i + 1] == ',':
                        i += 1
            elif in_string:
                current_value += char
            elif char == ',' and not in_string and paren_count == 0:
                # End of non-string value
                value = current_value.strip()
                if value.upper() == 'NULL':
                    values.append('')
                else:
                    values.append(value)
                current_value = ""
            elif char == '(' and not in_string:
                paren_count += 1
                current_value += char
            elif char == ')' and not in_string:
                paren_count -= 1
                current_value += char
            else:
                current_value += char
                
            i += 1
        
        # Handle last value
        if current_value.strip():
            value = current_value.strip()
            if value.upper() == 'NULL':
                values.append('')
            else:
                values.append(value)
        
        return values
    
    def load_sample_cases_500(self) -> int:
        """Load all 500 cases from sample_cases_500.sql."""
        sql_file = self.sql_files_dir / "sample_cases_500.sql"
        if not sql_file.exists():
            logger.error(f"SQL file not found: {sql_file}")
            return 0
        
        logger.info(f"📄 Loading 500 cases from {sql_file}")
        
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
        except Exception as e:
            logger.error(f"Failed to read SQL file: {e}")
            return 0
        
        # Parse INSERT statements
        records = self.parse_sql_insert_statements(sql_content)
        logger.info(f"📊 Parsed {len(records)} records from SQL file")
        
        if not records:
            logger.warning("No records found to insert")
            return 0
        
        # Insert into database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Define the field order for Cases table (matching the SQL INSERT order)
        case_fields = [
            'case_number', 'subject_description', 'description_description', 'issue_plain_text',
            'cause_plain_text', 'resolution_plain_text', 'parent_id', 'status_text', 'support_type',
            'record_name', 'product_hierarchy_id', 'case_internal_id', 'case_comments_text',
            'case_created_hour', 'case_escalated_flag', 'cause_text', 'close_case_reason_text',
            'close_comments_text', 'closed_date_timestamp', 'elevated_flag', 'elevation_id',
            'escalated_reason_text', 'impact_summary_text', 'order_type_code', 'origin_name',
            'gsd_product_number', 'reason_text', 'type_text', 'any_customer_data_loss',
            'asset_serial_number', 'issue_text', 'install_issue_text', 'resolution_code',
            'resolution_sub_code_text', 'new_install_text', 'outage_text', 'customer_impact_text',
            'resolution_text', 'product_series', 'gsd_environment_text', 'first_touch_time',
            'service_advisory_text', 'error_codes_text', 'operating_system_version_text',
            'operating_system_text', 'problem_analysis_text', 'case_description',
            'solution_class_description_text', 'solution_class_name_text', 'asset_operating_system_text',
            'asset_operating_system_version_text', 'issue_category_text', 'issue_type_text',
            'description_for_others_issue_category_text', 'description_for_others_issue_type_text',
            'other_resolution_sub_code_description_text', 'troubleshooting_steps_actions_taken_text'
        ]
        
        inserted_count = 0
        for record in records:
            try:
                # Ensure we have the right number of fields (57 expected)
                while len(record) < 57:
                    record.append('')
                record = record[:57]  # Truncate if too many
                
                # Create INSERT statement
                placeholders = ', '.join(['?' for _ in range(57)])
                insert_sql = f"""INSERT INTO Cases (
                    {', '.join(case_fields)}
                ) VALUES ({placeholders})"""
                
                cursor.execute(insert_sql, record)
                inserted_count += 1
                
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    logger.debug(f"Skipping duplicate case: {record[0] if record else 'unknown'}")
                else:
                    logger.error(f"Integrity error: {e}")
            except Exception as e:
                logger.error(f"Error inserting record: {e}")
                logger.debug(f"Record: {record[:3]}...")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Inserted {inserted_count} cases into database")
        return inserted_count
    
    def create_sample_related_data(self) -> None:
        """Create sample data for related tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        logger.info("📝 Creating sample related table data...")
        
        # Get some case IDs to reference
        cursor.execute("SELECT case_number, case_internal_id FROM Cases LIMIT 20")
        cases = cursor.fetchall()
        
        if not cases:
            logger.warning("No cases found to create related data")
            return
        
        # Sample Case_Feed entries
        feed_entries = []
        for i, (case_num, case_id) in enumerate(cases[:10]):
            feed_entries.extend([
                (case_id, 'TextPost', f'CFI{case_id}001', 0, '2024-01-15 10:30:00', 
                 'user123', '2024-01-15 10:30:00', '2024-01-15 10:30:00',
                 f'Initial diagnosis for case {case_num}. Investigating hardware failure symptoms.',
                 2, 'Initial case assessment', '', 0, '', 'user123', 0, '', 'InternalUsers', 
                 case_id, f'Case {case_num} - Initial Assessment', 'InternalUsers',
                 '2024-01-15 10:30:00', '2024-01-15 10:30:00', 0),
                
                (case_id, 'TextPost', f'CFI{case_id}002', 0, '2024-01-15 14:20:00',
                 'tech456', '2024-01-15 14:20:00', '2024-01-15 14:20:00',
                 f'Customer provided additional logs for case {case_num}. Analyzing error patterns.',
                 1, 'Technical analysis update', '', 0, '', 'tech456', 0, '', 'InternalUsers',
                 case_id, f'Case {case_num} - Technical Analysis', 'InternalUsers',
                 '2024-01-15 14:20:00', '2024-01-15 14:20:00', 0)
            ])
        
        cursor.executemany("""
            INSERT INTO Case_Feed (
                Parent_Id, Type_Text, Case_Feed_Internal_Id, Is_Deleted_Flag, Created_Timestamp,
                Created_By_Id, Last_Modified_Timestamp, System_Mod_Timestamp, Body_Text,
                Comment_Count, Content_Description, Content_File_Name, Content_Size_Number,
                Content_Type_Text, Inserted_By_Id, Like_Count, Link_Url_Text, Network_Scope_Text,
                Related_Record_Id, Title_Text, Visibility_Text, Insert_GMT_Timestamp,
                Update_GMT_Timestamp, Is_Rich_Text_Flag
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, feed_entries)
        
        # Sample EmailMessage entries
        email_entries = []
        for i, (case_num, case_id) in enumerate(cases[:5]):
            email_entries.append((
                f'EM{case_id}{i:03d}', case_id, 'customer@company.com', 'support@hpe.com',
                '2024-01-15 09:15:00', f'Re: Case {case_num} - Hardware Issue',
                f'Hi HPE Support team,\n\nI am writing regarding case {case_num}. Our server is experiencing intermittent hardware failures. The system logs show multiple error codes that we need help interpreting.\n\nCould you please provide guidance on next steps?\n\nBest regards,\nCustomer',
                '2024-01-15 09:15:00'
            ))
        
        cursor.executemany("""
            INSERT INTO EmailMessage (
                Email_Id, ParentId, FromAddress, ToAddress, MessageDate, Subject, TextBody, CreatedDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, email_entries)
        
        # Sample Feed_Comment entries
        comment_entries = []
        for i, (case_num, case_id) in enumerate(cases[:8]):
            comment_entries.extend([
                (f'FC{case_id}001', 0, '2024-01-15 11:00:00', 'expert789',
                 f'Based on the symptoms for case {case_num}, this appears to be a known issue with this hardware generation. Recommend checking firmware version first.',
                 'TextComment', f'CFI{case_id}001', 'expert789', case_id, case_id,
                 '2024-01-15 11:00:00', '2024-01-15 11:00:00'),
                
                (f'FC{case_id}002', 0, '2024-01-15 15:30:00', 'user123',
                 f'Thanks for the feedback on case {case_num}. Customer confirmed firmware is outdated. Proceeding with update.',
                 'TextComment', f'CFI{case_id}001', 'user123', case_id, case_id,
                 '2024-01-15 15:30:00', '2024-01-15 15:30:00')
            ])
        
        cursor.executemany("""
            INSERT INTO Feed_Comment (
                Feed_Comment_Internal_Id, Is_Deleted_Flag, Created_Timestamp, Created_By_Id,
                Comment_Body_Text, Comment_Type, Feed_Item_Id, Inserted_By_Id, Parent_Id,
                Related_Record_Id, Insert_GMT_Timestamp, Update_GMT_Timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, comment_entries)
        
        # Sample Knowledge Articles
        knowledge_articles = [
            ('KB001', 'ProLiant Server Boot Failure Troubleshooting',
             'This article provides comprehensive troubleshooting steps for ProLiant servers that fail to boot. Common causes include memory issues, power supply problems, and firmware corruption.',
             'Step-by-step guide for diagnosing and resolving ProLiant server boot failures',
             'Server Hardware', 'ProLiant', 'Boot Failure', 'Hardware Replacement',
             '2024-01-01', '2024-01-15', 'Published'),
            
            ('KB002', 'Network Connectivity Issues in Gen10 Servers',
             'Guide for resolving network connectivity problems in HPE ProLiant Gen10 servers. Covers NIC diagnostics, driver updates, and hardware troubleshooting.',
             'Comprehensive network troubleshooting for Gen10 servers',
             'Networking', 'ProLiant Gen10', 'Network Issues', 'Driver Update',
             '2024-01-02', '2024-01-10', 'Published'),
            
            ('KB003', 'Memory Module Failure Detection and Resolution',
             'Instructions for identifying faulty memory modules and proper replacement procedures. Includes memory testing utilities and compatibility guidelines.',
             'Memory diagnostic and replacement procedures',
             'Server Hardware', 'All Series', 'Memory Issues', 'Hardware Replacement',
             '2024-01-03', '2024-01-12', 'Published'),
            
            ('KB004', 'BIOS Firmware Recovery Procedures',
             'Step-by-step process for recovering corrupted BIOS firmware on HPE servers. Includes recovery modes and emergency procedures.',
             'BIOS recovery and firmware restoration guide',
             'Firmware', 'All Series', 'BIOS Corruption', 'Firmware Update',
             '2024-01-04', '2024-01-08', 'Published')
        ]
        
        cursor.executemany("""
            INSERT INTO Knowledge_Articles (
                article_id, title, content, summary, category, product_line, issue_type,
                resolution_type, created_date, modified_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, knowledge_articles)
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Created sample data:")
        logger.info(f"  - {len(feed_entries)} Case_Feed entries")
        logger.info(f"  - {len(email_entries)} EmailMessage entries") 
        logger.info(f"  - {len(comment_entries)} Feed_Comment entries")
        logger.info(f"  - {len(knowledge_articles)} Knowledge_Articles")
    
    def verify_database(self) -> None:
        """Verify the database creation and show statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        logger.info("📊 Database Statistics:")
        
        tables = ['Cases', 'Case_Feed', 'EmailMessage', 'Feed_Comment', 
                 'Product_Hierarchy', 'Service_Delivery_task', 'Knowledge_Articles']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"  {table}: {count} records")
            except sqlite3.OperationalError:
                logger.info(f"  {table}: Table not found")
        
        # Show sample cases
        cursor.execute("SELECT case_number, subject_description FROM Cases LIMIT 5")
        sample_cases = cursor.fetchall()
        
        logger.info("📋 Sample Cases:")
        for case_num, subject in sample_cases:
            logger.info(f"  {case_num}: {subject[:80]}...")
        
        conn.close()

async def main():
    """Main function to create full database."""
    logger.info("🚀 Starting full database creation with 500 cases...")
    
    creator = FullDatabaseCreator()
    
    # Create schema
    creator.create_complete_schema()
    
    # Load 500 cases
    cases_loaded = creator.load_sample_cases_500()
    
    # Create related data
    creator.create_sample_related_data()
    
    # Verify database
    creator.verify_database()
    
    logger.info(f"✅ Full database creation complete! Loaded {cases_loaded} cases")
    
    # Now run ChromaDB ingestion
    logger.info("🔄 Starting ChromaDB ingestion with full dataset...")
    
    try:
        # Import and run the ChromaDB ingestion
        import sys
        sys.path.append('.')
        
        # Use our simple ingestion script but with the full database
        import chromadb
        from chromadb.config import Settings
        from chromadb.utils import embedding_functions
        
        # Connect to the full database
        conn = sqlite3.connect("kms_v1_full.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Cases")
        case_count = cursor.fetchone()[0]
        logger.info(f"📊 Found {case_count} cases for ingestion")
        
        # Initialize ChromaDB
        chroma_client = chromadb.PersistentClient(
            path="./chromadb_data_full",
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Reset collection
        try:
            chroma_client.delete_collection("kms_cases_full")
        except:
            pass
        
        collection = chroma_client.create_collection(
            name="kms_cases_full",
            embedding_function=embedding_function
        )
        
        # Fetch all cases for ingestion
        cursor.execute("""
            SELECT case_number, subject_description, issue_plain_text, 
                   resolution_plain_text, status_text, product_series, 
                   asset_serial_number, problem_analysis_text, 
                   troubleshooting_steps_actions_taken_text, case_comments_text
            FROM Cases
            WHERE case_number IS NOT NULL
        """)
        
        cases = cursor.fetchall()
        conn.close()
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for case in cases:
            (case_number, subject, issue, resolution, status, product, 
             serial, analysis, troubleshooting, comments) = case
            
            # Combine text fields for comprehensive embedding
            combined_text = f"""
            Subject: {subject or ''}
            Issue: {issue or ''}
            Resolution: {resolution or ''}
            Analysis: {analysis or ''}
            Troubleshooting: {troubleshooting or ''}
            Comments: {comments or ''}
            """.strip()
            
            documents.append(combined_text)
            ids.append(f"case_{case_number}")
            metadatas.append({
                "case_number": case_number,
                "status": status or "Unknown",
                "product_series": product or "Unknown", 
                "serial_number": serial or "Unknown",
                "type": "case"
            })
        
        # Batch insert to ChromaDB
        logger.info(f"📥 Ingesting {len(documents)} cases to ChromaDB...")
        
        # Process in batches of 100 to avoid memory issues
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
            logger.info(f"  Processed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        # Verify ingestion
        count = collection.count()
        logger.info(f"✅ ChromaDB ingestion complete! {count} vectors created")
        
        # Test search with a few queries
        test_queries = [
            "power supply failure",
            "network connectivity issues",
            "memory module failure", 
            "hard drive failure",
            "server boot failure"
        ]
        
        logger.info("🔍 Testing search functionality...")
        for query in test_queries:
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            if results['ids'] and results['ids'][0]:
                best_match = results['metadatas'][0][0]
                similarity = 1 - results['distances'][0][0]
                logger.info(f"  '{query}' -> {best_match['case_number']} (similarity: {similarity:.3f})")
        
        logger.info("🎉 Full database and ChromaDB setup complete!")
        
    except Exception as e:
        logger.error(f"❌ ChromaDB ingestion failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())