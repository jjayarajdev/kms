#!/usr/bin/env python3
"""Load SQL data files into SQLite database for ingestion."""

import asyncio
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SQLDataLoader:
    def __init__(self, db_path: str = "kms_v1.db"):
        self.db_path = db_path
        self.sql_files_dir = Path("../db-references/ddl_dml")
        
    def create_cases_table(self) -> None:
        """Create the Cases table with proper schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS Cases")
        
        # Create Cases table with all required fields
        create_table_sql = """
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
            Case_Created_Hour TEXT,
            Case_Escalated_Flag TEXT,
            Cause_Text TEXT,
            Close_Case_Reason_Text TEXT,
            Close_Comments_Text TEXT,
            Closed_Date_Timestamp TEXT,
            Elevated_Flag TEXT,
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
            First_Touch_Time TEXT,
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
            Troubleshooting_Steps_Actions_Taken_Text TEXT
        )
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()
        logger.info("✅ Created Cases table with full schema")
    
    def parse_sql_values(self, sql_content: str) -> List[List[str]]:
        """Parse SQL INSERT VALUES into list of records."""
        # Find all INSERT statements and extract VALUES
        insert_pattern = r'INSERT\s+INTO\s+\w+\s*\([^)]+\)\s+VALUES\s*\n\s*\(([^;]+)\);'
        matches = re.findall(insert_pattern, sql_content, re.DOTALL | re.IGNORECASE)
        
        if not matches:
            # Try the batch VALUES format
            values_match = re.search(r'VALUES\s*\n(.*)', sql_content, re.DOTALL | re.IGNORECASE)
            if not values_match:
                logger.error("No VALUES section found in SQL")
                return []
            values_section = values_match.group(1)
        else:
            # Individual INSERT statements - parse each one
            records = []
            for match in matches:
                record_values = self.parse_record_values(match.strip())
                if record_values:
                    records.append(record_values)
            logger.info(f"✅ Parsed {len(records)} records from individual INSERT statements")
            return records
        
        values_section = values_match.group(1) if 'values_section' in locals() else ""
        
        # Split into individual records - look for ),\s*( pattern
        records = []
        current_record = ""
        paren_count = 0
        in_string = False
        escape_next = False
        
        i = 0
        while i < len(values_section):
            char = values_section[i]
            
            if escape_next:
                current_record += char
                escape_next = False
                i += 1
                continue
                
            if char == '\\':
                escape_next = True
                current_record += char
                i += 1
                continue
                
            if char == "'" and not escape_next:
                in_string = not in_string
                current_record += char
            elif not in_string:
                if char == '(':
                    paren_count += 1
                    if paren_count == 1:
                        current_record = ""  # Start new record
                    else:
                        current_record += char
                elif char == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        # End of record
                        if current_record.strip():
                            records.append(self.parse_record_values(current_record.strip()))
                        current_record = ""
                    else:
                        current_record += char
                else:
                    current_record += char
            else:
                current_record += char
                
            i += 1
        
        # Handle last record if it doesn't end with ),
        if current_record.strip() and paren_count == 0:
            records.append(self.parse_record_values(current_record.strip()))
            
        logger.info(f"✅ Parsed {len(records)} records from SQL")
        return records
    
    def parse_record_values(self, record_str: str) -> List[str]:
        """Parse individual record values from string."""
        values = []
        current_value = ""
        in_string = False
        escape_next = False
        
        i = 0
        while i < len(record_str):
            char = record_str[i]
            
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
                    # Skip to next comma or end
                    while i + 1 < len(record_str) and record_str[i + 1] in ' \t\n':
                        i += 1
                    if i + 1 < len(record_str) and record_str[i + 1] == ',':
                        i += 1  # Skip comma
                # Don't include quotes in the value
            elif in_string:
                current_value += char
            elif char == ',' and not in_string:
                # Non-string value (NULL, number, etc.)
                value = current_value.strip()
                if value.upper() == 'NULL':
                    values.append('')
                else:
                    values.append(value)
                current_value = ""
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
    
    def load_sql_file(self, sql_file: Path) -> int:
        """Load a specific SQL file into the database."""
        logger.info(f"📄 Loading SQL file: {sql_file}")
        
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
        except Exception as e:
            logger.error(f"❌ Failed to read {sql_file}: {e}")
            return 0
        
        records = self.parse_sql_values(sql_content)
        if not records:
            logger.warning(f"⚠️ No records found in {sql_file}")
            return 0
        
        # Insert records into database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        inserted_count = 0
        for record in records:
            try:
                # Create placeholder string for all 58 fields
                placeholders = ', '.join(['?' for _ in range(58)])
                insert_sql = f"INSERT INTO Cases ({', '.join([
                    'Case_Number', 'Subject_Description', 'Description_Description', 'Issue_Plain_Text',
                    'Cause_Plain_Text', 'Resolution_Plain_Text', 'Parent_Id', 'Status_Text', 'Support_Type',
                    'Record_Name', 'Product_Hierarchy_Id', 'Case_Internal_Id', 'Case_Comments_Text',
                    'Case_Created_Hour', 'Case_Escalated_Flag', 'Cause_Text', 'Close_Case_Reason_Text',
                    'Close_Comments_Text', 'Closed_Date_Timestamp', 'Elevated_Flag', 'Elevation_ID',
                    'Escalated_Reason_Text', 'Impact_Summary_Text', 'Order_Type_Code', 'Origin_Name',
                    'GSD_Product_Number', 'Reason_Text', 'Type_Text', 'Any_Customer_Data_Loss',
                    'Asset_Serial_Number', 'Issue_Text', 'Install_Issue_Text', 'Resolution_Code',
                    'Resolution_Sub_Code_Text', 'New_Install_Text', 'Outage_Text', 'Customer_Impact_Text',
                    'Resolution_Text', 'Product_Series', 'GSD_Environment_Text', 'First_Touch_Time',
                    'Service_Advisory_Text', 'Error_Codes_Text', 'Operating_System_Version_Text',
                    'Operating_System_Text', 'Problem_Analysis_Text', 'Case_Description',
                    'Solution_Class_Description_Text', 'Solution_Class_Name_Text', 'Asset_Operating_System_Text',
                    'Asset_Operating_System_Version_Text', 'Issue_Category_Text', 'Issue_Type_Text',
                    'Description_For_Others_Issue_Category_Text', 'Description_For_Others_Issue_Type_Text',
                    'Other_Resolution_Sub_Code_Description_Text', 'Troubleshooting_Steps_Actions_Taken_Text'
                ])}) VALUES ({placeholders})"
                
                # Pad record to 58 fields if necessary
                while len(record) < 58:
                    record.append('')
                
                cursor.execute(insert_sql, record[:58])
                inserted_count += 1
                
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed" in str(e):
                    logger.debug(f"⚠️ Skipping duplicate case: {record[0] if record else 'unknown'}")
                else:
                    logger.error(f"❌ Integrity error inserting record: {e}")
            except Exception as e:
                logger.error(f"❌ Error inserting record: {e}")
                logger.debug(f"Record data: {record[:3]}...")  # Log first 3 fields for debugging
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Inserted {inserted_count} records from {sql_file.name}")
        return inserted_count
    
    def load_all_sql_files(self) -> int:
        """Load all SQL files from the db-references directory."""
        total_loaded = 0
        
        # Create the Cases table first
        self.create_cases_table()
        
        # Look for SQL files
        sql_files = [
            self.sql_files_dir / "Case.sql",
            self.sql_files_dir / "sample_cases_500.sql"
        ]
        
        for sql_file in sql_files:
            if sql_file.exists():
                loaded = self.load_sql_file(sql_file)
                total_loaded += loaded
            else:
                logger.warning(f"⚠️ SQL file not found: {sql_file}")
        
        # Show final stats
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Cases")
        total_cases = cursor.fetchone()[0]
        conn.close()
        
        logger.info(f"🎉 Total cases in database: {total_cases}")
        return total_loaded

async def main():
    """Main function to load SQL data."""
    logger.info("🚀 Starting SQL data loading process...")
    
    loader = SQLDataLoader()
    total_loaded = loader.load_all_sql_files()
    
    logger.info(f"✅ SQL data loading complete! Loaded {total_loaded} new records")
    
    # Now run the ingestion pipeline
    logger.info("🔄 Starting ChromaDB ingestion...")
    
    try:
        from src.data.ingestion_pipeline import IngestionPipeline
        
        pipeline = IngestionPipeline()
        result = await pipeline.ingest_all_data(reset_collection=True)
        
        logger.info(f"✅ ChromaDB ingestion complete!")
        logger.info(f"Cases ingested: {result.get('cases_ingested', 0)}")
        logger.info(f"Articles ingested: {result.get('articles_ingested', 0)}")
        logger.info(f"Total vectors: {result.get('total_vectors', 0)}")
        
    except Exception as e:
        logger.error(f"❌ ChromaDB ingestion failed: {e}")
        logger.info("You can run the ingestion manually later with: python scripts/run_full_ingestion.py")

if __name__ == "__main__":
    asyncio.run(main())