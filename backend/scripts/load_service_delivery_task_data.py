#!/usr/bin/env python3
"""
Script to load Service_Delivery_task data
"""
import sqlite3
import sys
from pathlib import Path

def load_service_delivery_task_data():
    """Load sample data into Service_Delivery_task table"""
    
    # Get database path
    db_path = Path(__file__).parent.parent / "data" / "kms_v1.db"
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Sample Service_Delivery_task data
        cursor.execute("""
        INSERT INTO Service_Delivery_task (
            Case_Internal_Id,
            Title_Text,
            Problem_Description,
            Product_Description,
            Closing_Summary_Text,
            Closing_Notes_Text,
            Plan_Of_Action_Text
        ) VALUES 
        ('5004o00000MtyNjAAJ', 
         'HPE ProLiant DL385 Gen10 Server Models/ DIMM FAILURE',
         'HPE ProLiant DL385 Gen10 Server Models experiencing DIMM FAILURE with memory modules in CPU slots',
         'HPE ProLiant DL385 Gen10 8SFF TAA-compliant Configure-to-order Server',
         'Replaced Dimms pn 868841-001 in slots - cpu2 dimm5, cpu2 dimm6, Customer verified system operational',
         'Memory modules replaced successfully. System POST completed. Customer acceptance received.',
         'Schedule onsite visit to replace faulty DIMM modules. Follow COVID-19 safety protocols. Verify CPU torque if needed.'),
        
        ('5004o00000MtyNkAAJ',
         'ProLiant DL380 Server Power Supply Replacement', 
         'Customer reported power supply failure alarm. Server running on single PSU redundancy lost.',
         'HPE ProLiant DL380 Gen10 Server',
         'Replaced faulty power supply unit. Restored redundancy. System monitoring normal.',
         'Power supply hot-swap completed successfully. No downtime required.',
         'Replace faulty PSU during maintenance window. Test redundancy after replacement.'),
         
        ('5004o00000MtyNlAAJ',
         'Storage Controller Firmware Update',
         'Storage controller requires firmware update to resolve performance issues and security vulnerabilities.',
         'HPE Smart Array P440ar Controller',
         'Firmware updated from version 2.65 to 2.71. Performance tests completed successfully.',
         'Update completed without data loss. All logical drives verified.',
         'Schedule maintenance window for firmware update. Backup critical data before procedure.'),
         
        ('5004o00000MtyNmAAJ',
         'Network Interface Card Replacement',
         'Intermittent network connectivity issues traced to faulty NIC port.',
         'HPE Ethernet 10Gb 2-port 562FLR-SFP+ Adapter',
         'Replaced NIC adapter. Network connectivity restored. Performance monitoring normal.',
         'Physical replacement completed. Network team verified all connections.',
         'Replace faulty NIC during scheduled maintenance. Coordinate with network team for cable management.'),
         
        ('5004o00000MtyNnAAJ',
         'Server Memory Expansion',
         'Customer requires memory upgrade to support increased workload and virtualization requirements.',
         'HPE ProLiant DL360 Gen10 Server', 
         'Installed additional 64GB memory modules. System configuration updated. Performance validated.',
         'Memory expansion completed successfully. All modules recognized and operational.',
         'Install additional memory modules during maintenance window. Update system configuration and verify compatibility.')
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify data was loaded
        cursor.execute("SELECT COUNT(*) FROM Service_Delivery_task")
        task_count = cursor.fetchone()[0]
        
        # Show sample data
        cursor.execute("SELECT Title_Text, Problem_Description FROM Service_Delivery_task LIMIT 3")
        sample_data = cursor.fetchall()
        
        print(f"✅ Successfully loaded Service_Delivery_task data: {task_count} records")
        print("\n📋 Sample records:")
        for i, (title, problem) in enumerate(sample_data, 1):
            print(f"   {i}. {title}")
            print(f"      Problem: {problem[:80]}...")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    success = load_service_delivery_task_data()
    sys.exit(0 if success else 1)