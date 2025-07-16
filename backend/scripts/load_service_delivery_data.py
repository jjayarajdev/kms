#!/usr/bin/env python3
"""
Script to load sample data into Service_Delivery tables
"""
import sqlite3
import sys
from pathlib import Path

def load_service_delivery_data():
    """Load sample data into Service_Delivery tables"""
    
    # Get database path
    db_path = Path(__file__).parent.parent / "data" / "kms_v1.db"
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Sample Service_Delivery_Part_Order data
        cursor.execute("""
        INSERT INTO Service_Delivery_Part_Order (
            Service_Delivery_Part_Order_Internal_Id,
            Owner_Id,
            Is_Deleted_Flag,
            Service_Delivery_Part_Order_Internal_Name,
            Currency_ISO_Code,
            Created_Timestamp,
            Created_By_Id,
            System_Mod_Timestamp,
            Last_Modified_Timestamp,
            Last_Modified_By_Id,
            Company_Name,
            Contact_First_Name,
            Contact_Last_Name,
            Country,
            Order_Status_Code,
            Part_Order_Identifier,
            Case_Internal_Id,
            Insert_GMT_Timestamp,
            Update_GMT_Timestamp
        ) VALUES 
        ('aEv1V0000017qf0SAA', '00527000005k8AuAAI', 0, '5327500468-531-1', 'USD', 
         '2018-03-02 14:49:06.000', '00527000005k8AuAAI', '2018-03-02 14:49:06.000',
         '2018-03-02 14:49:06.000', '00527000005k8AuAAI', 'HPE Customer Service',
         'John', 'Smith', 'US', 'OPEN', 'PO-001', '5001V00001ABC123',
         '2018-03-02 14:49:06.000', '2018-03-02 14:49:06.000'),
        ('aEv1V0000017qf1SAA', '00527000005k8AuAAI', 0, '5327500469-531-1', 'USD',
         '2018-03-03 10:30:15.000', '00527000005k8AuAAI', '2018-03-03 10:30:15.000',
         '2018-03-03 10:30:15.000', '00527000005k8AuAAI', 'Tech Solutions Inc',
         'Jane', 'Doe', 'US', 'SHIPPED', 'PO-002', '5001V00001ABC124',
         '2018-03-03 10:30:15.000', '2018-03-03 10:30:15.000'),
        ('aEv1V0000017qf2SAA', '00527000005k8AuAAI', 0, '5327500470-531-1', 'EUR',
         '2018-03-04 08:15:30.000', '00527000005k8AuAAI', '2018-03-04 08:15:30.000',
         '2018-03-04 08:15:30.000', '00527000005k8AuAAI', 'Global Enterprise Ltd',
         'Bob', 'Wilson', 'DE', 'DELIVERED', 'PO-003', '5001V00001ABC125',
         '2018-03-04 08:15:30.000', '2018-03-04 08:15:30.000')
        """)
        
        # Sample Service_Delivery_Part_Order_Line data
        cursor.execute("""
        INSERT INTO Service_Delivery_Part_Order_Line (
            Service_Delivery_Part_Order_Line_Internal_Id,
            Is_Deleted_Flag,
            Service_Delivery_Part_Order_Line_Internal_Name,
            Currency_ISO_Code,
            Created_Timestamp,
            Created_By_Id,
            Last_Modified_Timestamp,
            Last_Modified_By_Id,
            Part_Identifier,
            Part_Description,
            Part_Line_Status,
            Line_Number,
            Case_Number,
            Insert_GMT_Timestamp,
            Update_GMT_Timestamp,
            Part_Order_Header_Number_Id
        ) VALUES
        ('aEu4o00000159fbCAA', 0, 'aEu4o00000159fb', 'USD', '2023-06-20 14:39:20.000',
         '0051V000004w1gtQAA', '2023-06-21 12:37:03.000', '00527000006XelaAAk',
         'P44441-001', 'SPS-CPU Xeon-G 6326 2.9G, 16C, 185W', 'POD', 1.0,
         '5374000894', '2023-06-20 19:37:26.000', '2023-09-14 13:48:51.210',
         'aEv1V0000017qf0SAA'),
        ('aEu4o000000ibjbCAA', 0, 'aEu4o000000ibjb', 'USD', '2023-07-04 13:41:13.000',
         '0051V000006o3KAQAQ', '2023-07-10 08:27:11.000', '0051V000006o3kAQAQ',
         '793443-001', 'SPS-16Gb SFP+SW Industrial XCVR 1 Pack', 'POD', 1.0,
         '5374475397', '2023-07-04 17:01:04.000', '2023-09-14 13:48:51.210',
         'aEv1V0000017qf1SAA'),
        ('aEu4o000000DzRgCAK', 0, 'aEu4o000000DzRg', 'USD', '2023-07-11 08:06:54.000',
         '0051V000005AT8mQAG', '2023-07-11 08:07:14.000', '005G0000003nXrllA2',
         'P23625-001', 'SPS-TPM PCA W/Cover', 'Recommended', 2.0,
         '5374734444', '2023-07-11 14:50:01.000', '2023-09-14 13:48:51.210',
         'aEv1V0000017qf2SAA')
        """)
        
        # Commit changes
        conn.commit()
        
        # Verify data was loaded
        cursor.execute("SELECT COUNT(*) FROM Service_Delivery_Part_Order")
        part_order_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Service_Delivery_Part_Order_Line") 
        part_order_line_count = cursor.fetchone()[0]
        
        print(f"✅ Successfully loaded data:")
        print(f"   - Service_Delivery_Part_Order: {part_order_count} records")
        print(f"   - Service_Delivery_Part_Order_Line: {part_order_line_count} records")
        
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
    success = load_service_delivery_data()
    sys.exit(0 if success else 1)