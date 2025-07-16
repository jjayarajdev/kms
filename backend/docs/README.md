# KMS-V1 Backend

Backend API for the HPE Knowledge Management System V1.

## Current Status: ✅ FULLY OPERATIONAL

The KMS-V1 backend is complete and operational with full React frontend integration. See [CURRENT_STATE.md](./CURRENT_STATE.md) for detailed system status.

## Architecture

- **FastAPI** - Async web framework
- **SQLAlchemy** - ORM with async support  
- **SQLite** - Primary database (migrated from PostgreSQL)
- **ChromaDB** - Vector database for similarity search
- **LangChain** - LLM orchestration
- **React Frontend** - Complete TypeScript UI

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- SQLite (included with Python)

### Quick Start

**Backend:**
```bash
cd backend
python start_server.py
# Server runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm start
# Application runs on http://localhost:3000
```

### Current Setup

The system is pre-configured and ready to run:
- ✅ SQLite database with sample data loaded
- ✅ ChromaDB vector embeddings configured  
- ✅ All 22 API endpoints operational
- ✅ React frontend integrated and working
- ✅ Search functionality fully operational
- ✅ **Real-time case processing system** - automatically generates knowledge articles
- ✅ **Scheduled job system** - monitors database and processes new cases every 30 minutes
- ✅ **Automated vectorization** - new articles immediately searchable

### Installation (if needed)

1. **Backend dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Frontend dependencies:**
```bash
cd frontend
npm install
```

### Running the Application

**Development (Current Setup):**
```bash
# Backend
python start_server.py

# Frontend (separate terminal)
cd ../frontend && npm start
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Real-time Jobs: http://localhost:8000/api/v1/admin/jobs/status
- Pipeline Status: http://localhost:8000/api/v1/admin/pipelines

## Current Data

The system includes comprehensive sample data:

- **510 SFDC cases** with varied issues (hardware failures, performance problems, etc.)
- **4 knowledge articles** with troubleshooting guides
- **Complete product hierarchies** covering HPE ProLiant server lines
- **514 vector embeddings** (510 cases + 4 knowledge articles)
- **Service delivery tasks** and activity tracking data

### Data Structure

**Cases include:**
- Hardware failures (HDD, PSU, memory, CPU)
- Network and performance issues
- Various HPE server models (DL380, DL360, DL385)
- Different generations (Gen8, Gen9, Gen10, Gen10+)
- Realistic customer information and locations
- Complete issue/resolution patterns

**Product hierarchies:**
- ProLiant DL server families
- Multiple generations and models
- Proper categorization

**Knowledge articles:**
- Hardware troubleshooting guides
- Step-by-step resolution procedures
- CFI and KB article types

## Database Schema

### Core Tables

- **Cases** - SFDC case data with full text fields
- **Knowledge_Articles** - CFI documents and KB articles
- **Product_Hierarchy** - Product categorization
- **Service_Delivery_task** - Service delivery tracking
- **Activity_Task** - System activity monitoring

### Key Features

- **Vector embedding support** - ChromaDB integration
- **Full-text search** with SQLite FTS
- **Performance indexes** on commonly queried fields
- **Real-time search** with semantic similarity

## API Endpoints (All Operational)

### Search
- `POST /api/v1/search/` - Unified search (hybrid, vector, text)
- `GET /api/v1/search/suggestions` - Search suggestions

### Knowledge Management  
- `GET /api/v1/knowledge/stats` - Knowledge statistics
- `GET /api/v1/knowledge/categories` - Categories
- `GET /api/v1/knowledge/articles` - Articles listing
- `GET /api/v1/knowledge/articles/{id}` - Article details
- `GET /api/v1/knowledge/search` - Knowledge search

### Admin & Monitoring
- `GET /api/v1/admin/dashboard` - System dashboard
- `GET /api/v1/admin/metrics` - Performance metrics
- `GET /api/v1/admin/pipelines` - Pipeline status
- `GET /api/v1/admin/sql/tables` - Database browser
- `POST /api/v1/admin/sql/query` - SQL query execution
- `GET /api/v1/admin/vectors/status` - Vector database status

### Real-time Processing
- `GET /api/v1/admin/jobs/status` - Job scheduler status
- `POST /api/v1/admin/jobs/{job_id}/trigger` - Manual job execution
- `GET /api/v1/admin/jobs/{job_id}/metrics` - Job performance metrics
- `GET /api/v1/admin/case-monitor/stats` - Case processing statistics
- `POST /api/v1/admin/case-monitor/sync` - Manual case synchronization

See [CURRENT_STATE.md](./CURRENT_STATE.md) for complete API documentation.

## 🔄 Real-time Case Processing System

The KMS-V1 backend includes a **fully automated real-time case processing system** that:

### Key Features
- **🔍 Automated Monitoring**: Continuously monitors database for new case records
- **🧠 Pattern Recognition**: Identifies common issue patterns automatically
- **📝 Knowledge Generation**: Creates comprehensive troubleshooting guides
- **🔧 Vectorization**: Immediately makes new content searchable
- **📊 API Control**: Full programmatic control and monitoring

### Processing Pipeline
1. **Case Sync** (Every 30 minutes): Monitors database for new/updated cases
2. **Knowledge Generation** (Every 2 hours): Analyzes patterns and creates articles
3. **Vectorization** (Every hour): Generates embeddings for semantic search
4. **Health Check** (Every 15 minutes): Monitors system health

### Pattern Recognition
The system automatically identifies these issue patterns:
- Processor/CPU errors
- Network connectivity issues
- BIOS/firmware problems
- Hard drive failures
- Power supply issues
- Thermal management problems
- Memory errors

### Monitoring
- **Job Status**: Real-time job monitoring with metrics
- **Processing Statistics**: Case processing rates and success metrics
- **Error Handling**: Comprehensive retry logic and error tracking
- **Performance Metrics**: Throughput and latency monitoring

For detailed information, see [REAL_TIME_PROCESSING_SYSTEM.md](./REAL_TIME_PROCESSING_SYSTEM.md).

## Data Pipeline

### ETL Process

1. **Extract** - Load SFDC case data
2. **Transform** - Clean and validate data
3. **Load** - Bulk insert with relationship mapping

### Validation

- Data quality checks
- Relationship integrity  
- Content completeness
- Performance metrics

## Scripts

- `scripts/init_db.py` - Database initialization
- `scripts/generate_sample_data.py` - Generate development data
- `scripts/export_sample_sql.py` - Export data as SQL

## Development

### Code Quality

```bash
# Format code
black src/
isort src/

# Type checking  
mypy src/

# Linting
flake8 src/
```

### Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Monitoring

- **Prometheus metrics** on `/metrics` endpoint
- **Health checks** on `/health` endpoint  
- **Database performance** monitoring
- **Search accuracy** tracking