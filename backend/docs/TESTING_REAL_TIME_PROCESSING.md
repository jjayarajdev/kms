# Testing the Real-time Case Processing System

## 🧪 Testing Overview

This guide provides comprehensive instructions for testing the KMS-V1 real-time case processing system, including job monitoring, manual triggers, and data flow verification.

## 📋 Prerequisites

1. **Server Running**: Ensure the backend server is running
   ```bash
   python start_server.py
   ```

2. **Database Access**: SQLite database should be accessible
3. **API Access**: Port 8000 should be available

## 🔍 Test Scenarios

### 1. Verify System Status

#### Check Scheduler Status
```bash
# Check if all jobs are scheduled and running
curl -s "http://localhost:8000/api/v1/admin/jobs/status" | python -m json.tool
```

**Expected Response:**
```json
{
  "scheduler_status": "running",
  "total_jobs": 4,
  "jobs": {
    "case_sync": {
      "name": "Database Case Sync",
      "status": "scheduled",
      "next_run": "2025-07-15T16:30:03.758965+05:30",
      "run_count": 0,
      "error_count": 0
    },
    "knowledge_generation": {
      "name": "Knowledge Article Generation",
      "status": "scheduled"
    },
    "vectorization": {
      "name": "Knowledge Vectorization",
      "status": "scheduled"
    },
    "health_check": {
      "name": "System Health Check",
      "status": "scheduled"
    }
  }
}
```

#### Check Pipeline Status
```bash
curl -s "http://localhost:8000/api/v1/admin/pipelines" | python -m json.tool
```

### 2. Test Manual Job Execution

#### Trigger Case Sync Job
```bash
# Manually trigger case synchronization
curl -X POST "http://localhost:8000/api/v1/admin/jobs/case_sync/trigger"
```

**Monitor the logs to see:**
- "Starting case sync job..."
- "Case Data Monitor initialized successfully"
- Case processing results

#### Trigger Knowledge Generation
```bash
# Manually trigger knowledge article generation
curl -X POST "http://localhost:8000/api/v1/admin/jobs/knowledge_generation/trigger"
```

#### Trigger Vectorization
```bash
# Manually trigger vectorization of new articles
curl -X POST "http://localhost:8000/api/v1/admin/jobs/vectorization/trigger"
```

### 3. Test Case Monitor Statistics

```bash
# Check case processing statistics
curl -s "http://localhost:8000/api/v1/admin/case-monitor/stats" | python -m json.tool
```

**Expected Response:**
```json
{
  "total_cases": 1250,
  "new_cases_24h": 45,
  "processed_cases": 1180,
  "unprocessed_cases": 70,
  "processing_rate": 94.4,
  "last_sync": "2025-07-15T18:00:03.809210"
}
```

### 4. Test End-to-End Processing

#### Step 1: Insert Test Cases
```sql
-- Insert test cases that will trigger pattern recognition
INSERT INTO Cases (
    Case_Number, 
    Subject_Description, 
    Issue_Plain_Text, 
    Resolution_Plain_Text, 
    Status_Text, 
    created_at,
    Product_Hierarchy_ID
) VALUES 
    ('TEST001', 'Server CPU Overheating', 'Processor temperature exceeding threshold', 'Replaced thermal paste and fan', 'Closed', datetime('now'), 1),
    ('TEST002', 'CPU Core Failure', 'Multiple processor cores offline', 'Replaced processor unit', 'Closed', datetime('now'), 1),
    ('TEST003', 'Processor Performance Issues', 'CPU throttling under load', 'Updated BIOS settings', 'Closed', datetime('now'), 1),
    ('TEST004', 'CPU Error Messages', 'Machine check exceptions in logs', 'Replaced faulty processor', 'Closed', datetime('now'), 1),
    ('TEST005', 'Thermal Shutdown Events', 'Server shutting down due to CPU temperature', 'Improved cooling system', 'Closed', datetime('now'), 1);
```

#### Step 2: Trigger Case Sync
```bash
curl -X POST "http://localhost:8000/api/v1/admin/case-monitor/sync"
```

#### Step 3: Trigger Knowledge Generation
```bash
curl -X POST "http://localhost:8000/api/v1/admin/jobs/knowledge_generation/trigger"
```

#### Step 4: Check for New Articles
```bash
# List knowledge articles to see if new ones were created
curl -s "http://localhost:8000/api/v1/knowledge/articles?limit=10" | python -m json.tool
```

#### Step 5: Search for Generated Content
```bash
# Search for the pattern-generated article
curl -X POST "http://localhost:8000/api/v1/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "processor errors",
    "search_type": "knowledge",
    "limit": 5
  }' | python -m json.tool
```

### 5. Monitor Job Metrics

#### Get Specific Job Metrics
```bash
# Get metrics for case sync job
curl -s "http://localhost:8000/api/v1/admin/jobs/case_sync/metrics" | python -m json.tool

# Get metrics for knowledge generation
curl -s "http://localhost:8000/api/v1/admin/jobs/knowledge_generation/metrics" | python -m json.tool
```

### 6. Test Error Handling

#### Test Database Connection Error
1. Temporarily rename the database file
2. Trigger a job and observe error handling
3. Restore the database file

#### Test Pattern Threshold
Insert fewer than 5 cases for a pattern and verify no article is generated:
```sql
-- Only 3 cases - below threshold
INSERT INTO Cases VALUES 
    ('TEST006', 'Network timeout', 'Connection drops randomly', 'Reset switch', 'Closed', datetime('now'), 1),
    ('TEST007', 'Network slow', 'Poor throughput', 'Updated firmware', 'Closed', datetime('now'), 1),
    ('TEST008', 'Network errors', 'Packet loss detected', 'Replaced cable', 'Closed', datetime('now'), 1);
```

## 🔧 Testing Tools

### Python Test Script
Create `test_realtime_processing.py`:

```python
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_job_status():
    """Test job status endpoint"""
    response = requests.get(f"{BASE_URL}/api/v1/admin/jobs/status")
    data = response.json()
    
    print("=== Job Status ===")
    print(f"Scheduler: {data['scheduler_status']}")
    print(f"Total Jobs: {data['total_jobs']}")
    
    for job_id, job_info in data['jobs'].items():
        print(f"\n{job_id}:")
        print(f"  Status: {job_info['status']}")
        print(f"  Next Run: {job_info.get('next_run', 'N/A')}")
        print(f"  Run Count: {job_info.get('run_count', 0)}")
        print(f"  Errors: {job_info.get('error_count', 0)}")

def test_manual_sync():
    """Test manual case sync"""
    print("\n=== Testing Manual Case Sync ===")
    response = requests.post(f"{BASE_URL}/api/v1/admin/jobs/case_sync/trigger")
    print(f"Response: {response.json()}")

def test_case_monitor_stats():
    """Test case monitor statistics"""
    print("\n=== Case Monitor Stats ===")
    response = requests.get(f"{BASE_URL}/api/v1/admin/case-monitor/stats")
    data = response.json()
    
    if data:
        print(f"Total Cases: {data.get('total_cases', 0)}")
        print(f"New Cases (24h): {data.get('new_cases_24h', 0)}")
        print(f"Processing Rate: {data.get('processing_rate', 0)}%")
        print(f"Last Sync: {data.get('last_sync', 'Never')}")

def test_pipeline_status():
    """Test pipeline status"""
    print("\n=== Pipeline Status ===")
    response = requests.get(f"{BASE_URL}/api/v1/admin/pipelines")
    data = response.json()
    
    print(f"Scheduler Status: {data.get('scheduler_status', 'Unknown')}")
    print(f"Total Pipelines: {len(data.get('pipelines', []))}")
    
    for pipeline in data.get('pipelines', []):
        print(f"\n{pipeline['name']}:")
        print(f"  Status: {pipeline['status']}")
        print(f"  Last Run: {pipeline.get('last_run', 'Never')}")
        metrics = pipeline.get('metrics', {})
        print(f"  Processed: {metrics.get('processed', 0)}")
        print(f"  Errors: {metrics.get('errors', 0)}")

def test_search_for_articles():
    """Test searching for auto-generated articles"""
    print("\n=== Testing Search for Generated Articles ===")
    
    search_queries = [
        "processor errors",
        "network issues",
        "power supply failure"
    ]
    
    for query in search_queries:
        response = requests.post(
            f"{BASE_URL}/api/v1/search/",
            json={
                "query": query,
                "search_type": "knowledge",
                "limit": 3
            }
        )
        
        data = response.json()
        print(f"\nSearch: '{query}'")
        print(f"Results: {data.get('total_results', 0)}")
        
        for result in data.get('results', [])[:2]:
            print(f"  - {result.get('title', 'Untitled')}")
            print(f"    Score: {result.get('similarity_score', 0):.2f}")

def run_all_tests():
    """Run all tests"""
    print("Starting Real-time Processing Tests...")
    print("=" * 50)
    
    test_job_status()
    time.sleep(1)
    
    test_case_monitor_stats()
    time.sleep(1)
    
    test_pipeline_status()
    time.sleep(1)
    
    test_manual_sync()
    time.sleep(2)
    
    test_search_for_articles()
    
    print("\n" + "=" * 50)
    print("Tests completed!")

if __name__ == "__main__":
    run_all_tests()
```

### Bash Test Script
Create `test_realtime.sh`:

```bash
#!/bin/bash

echo "=== Real-time Processing System Test ==="
echo

# Check if server is running
echo "1. Checking server health..."
curl -s "http://localhost:8000/health" | python -m json.tool
echo

# Check job status
echo "2. Checking job scheduler status..."
curl -s "http://localhost:8000/api/v1/admin/jobs/status" | python -m json.tool
echo

# Check case monitor stats
echo "3. Checking case monitor statistics..."
curl -s "http://localhost:8000/api/v1/admin/case-monitor/stats" | python -m json.tool
echo

# Trigger manual sync
echo "4. Triggering manual case sync..."
curl -X POST "http://localhost:8000/api/v1/admin/jobs/case_sync/trigger"
echo
echo

# Wait for processing
echo "5. Waiting 5 seconds for processing..."
sleep 5

# Check pipeline status
echo "6. Checking pipeline status..."
curl -s "http://localhost:8000/api/v1/admin/pipelines" | python -m json.tool | head -50
echo

echo "Test completed!"
```

## 📊 Monitoring During Tests

### Watch Server Logs
```bash
# In a separate terminal, watch the server logs
tail -f server.log | grep -E "(job|sync|generation|vector|pattern)"
```

### Check Database Changes
```sql
-- Check recently added knowledge articles
SELECT article_id, title, created_date 
FROM Knowledge_Articles 
WHERE article_id LIKE 'AUTO_%' 
ORDER BY created_date DESC 
LIMIT 10;

-- Check case processing status
SELECT COUNT(*) as processed_count
FROM Case_Knowledge_Mapping;

-- Check vector metadata
SELECT article_id, vector_id, created_date 
FROM Knowledge_Vectors 
ORDER BY created_date DESC 
LIMIT 10;
```

## 🎯 Expected Test Results

### Successful Case Sync
- Log: "Starting case sync job..."
- Log: "Retrieved X new/updated cases from database"
- Status: "completed" in API response

### Successful Knowledge Generation
- Log: "Identified X patterns with sufficient cases"
- Log: "Generated knowledge article AUTO_PATTERN_TIMESTAMP"
- New articles visible in knowledge listing

### Successful Vectorization
- Log: "Found X articles requiring vectorization"
- Log: "Created vector embedding vec_ARTICLE_TIMESTAMP"
- Articles searchable via vector search

## 🐛 Troubleshooting Test Issues

### Common Issues

1. **"No new cases found"**
   - This is normal if no new cases exist
   - Insert test cases to trigger processing

2. **"Pattern threshold not met"**
   - Need at least 5 cases per pattern
   - Insert more test cases for the pattern

3. **"Database table not found"**
   - Some tables may not exist in test environment
   - This is expected for demo systems

4. **"Job already running"**
   - Wait for current job to complete
   - Check job status before triggering

### Debug Commands

```bash
# Check if scheduler is actually running
ps aux | grep python | grep start_server

# Check port availability
lsof -i :8000

# Test basic connectivity
curl -I http://localhost:8000/health

# Check Python dependencies
pip list | grep apscheduler
```

## 📝 Test Checklist

- [ ] Server starts without errors
- [ ] Scheduler initializes with all 4 jobs
- [ ] Job status endpoint returns valid data
- [ ] Manual job triggers work
- [ ] Case monitor stats are accessible
- [ ] Pipeline status shows real-time jobs
- [ ] Test cases trigger pattern recognition
- [ ] Knowledge articles are generated
- [ ] Articles are vectorized
- [ ] Generated articles are searchable
- [ ] Error handling works correctly
- [ ] Logs show expected processing flow

## 🚀 Performance Testing

### Load Test Script
```python
# Test with larger batches
import sqlite3
import random
from datetime import datetime, timedelta

def insert_test_cases(count=100):
    """Insert multiple test cases"""
    conn = sqlite3.connect('kms_v1_full.db')
    cursor = conn.cursor()
    
    patterns = ['processor', 'network', 'memory', 'disk', 'power']
    
    for i in range(count):
        pattern = random.choice(patterns)
        case_data = (
            f'LOAD{i:04d}',
            f'{pattern.title()} Issue #{i}',
            f'System experiencing {pattern} related problems',
            f'Applied standard {pattern} troubleshooting',
            'Closed',
            datetime.now() - timedelta(days=random.randint(0, 30)),
            random.randint(1, 4)
        )
        
        cursor.execute("""
            INSERT INTO Cases (
                Case_Number, Subject_Description, Issue_Plain_Text,
                Resolution_Plain_Text, Status_Text, created_at,
                Product_Hierarchy_ID
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, case_data)
    
    conn.commit()
    conn.close()
    print(f"Inserted {count} test cases")

# Run load test
insert_test_cases(100)
```

This testing guide provides comprehensive coverage of the real-time processing system functionality.