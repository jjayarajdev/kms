# KMS-V1 API Documentation

## 🚀 Overview

The KMS-V1 (Knowledge Management System Version 1) API provides AI-powered case similarity search and knowledge discovery capabilities. Built with FastAPI, it offers high-performance vector similarity search using advanced embeddings and natural language processing for intelligent knowledge retrieval.

## 📍 Base URLs

| Environment | URL | Status |
|-------------|-----|--------|
| **Development** | `http://localhost:8000` | ✅ Active |
| **Testing** | `https://kms-api.dev.hpe.com` | 🔄 Planned |
| **Production** | `https://kms-api.prod.hpe.com` | 🔄 Planned |

## 🔐 Authentication

All API endpoints support Bearer token authentication (currently optional in development):

```http
Authorization: Bearer <your-api-token>
```

> **Note**: Authentication is currently disabled in development mode. Contact your system administrator for production API credentials.

## 📖 Interactive Documentation

- **Swagger UI**: [`/docs`](http://localhost:8000/docs) - Interactive API documentation with test capabilities
- **ReDoc**: [`/redoc`](http://localhost:8000/redoc) - Alternative documentation interface  
- **OpenAPI Schema**: [`/openapi.json`](http://localhost:8000/openapi.json) - Machine-readable API specification

## 🏥 Health Check & Monitoring

### GET `/api/v1/health/`
**Basic health check with system status**

**Response:**
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2025-07-14T09:00:00Z",
  "version": "1.0.0",
  "database": "healthy|unhealthy: <details>",
  "vector_db": "healthy|unhealthy: <details>",
  "search_engine": "healthy|unhealthy: <details>",
  "response_time_ms": 15,
  "uptime_seconds": 3600
}
```

### GET `/api/v1/health/detailed`
**Comprehensive health information with component statistics**

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-14T09:00:00Z",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "case_count": 1250,
      "connection_pool": "active"
    },
    "vector_db": {
      "status": "healthy", 
      "vector_count": 2500,
      "collections": ["kms_cases_comprehensive"],
      "index_size_mb": 7.7
    },
    "search_engine": {
      "status": "healthy",
      "cache_hit_rate": 0.87,
      "avg_response_time_ms": 45
    }
  },
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "disk_percent": 12.5
  },
  "performance": {
    "requests_per_minute": 156,
    "cache_hit_rate": 87.3,
    "error_rate": 0.1
  }
}
```

### GET `/api/v1/health/ready`
**Kubernetes readiness probe**

### GET `/api/v1/health/live`
**Kubernetes liveness probe**

### GET `/api/v1/health/metrics`
**Prometheus metrics endpoint**

## 🔍 Search API

### POST `/api/v1/search/`
**Main similarity search endpoint with AI-powered ranking**

**Request Body:**
```json
{
  "query": "server crashes during boot",
  "search_type": "hybrid",
  "max_results": 10,
  "similarity_threshold": 0.7,
  "filters": {
    "product_hierarchy": ["ProLiant", "iLO"],
    "status": ["Closed", "Resolved"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    }
  },
  "include_knowledge": true,
  "session_id": "optional-session-uuid"
}
```

**Parameters:**
- `query` (required): Search query text
- `search_type` (optional): `vector|text|hybrid|semantic` (default: `hybrid`)
- `max_results` (optional): 1-100 results (default: 10)
- `similarity_threshold` (optional): 0.0-1.0 (default: 0.7)
- `filters` (optional): Filter criteria
- `include_knowledge` (optional): Include knowledge articles (default: true)
- `session_id` (optional): Session tracking UUID

**Response:**
```json
{
  "results": [
    {
      "id": "case_123456",
      "type": "case",
      "case_number": "5350123456",
      "title": "ProLiant server boot failure",
      "summary": "Server fails to boot after firmware update...",
      "similarity_score": 0.92,
      "confidence": "high",
      "metadata": {
        "product_hierarchy": "ProLiant DL380",
        "status": "Closed",
        "priority": "High",
        "created_at": "2024-06-15T10:30:00Z",
        "resolved_at": "2024-06-16T14:20:00Z"
      },
      "ranking_factors": {
        "text_similarity": 0.85,
        "semantic_similarity": 0.94,
        "recency_boost": 0.12,
        "resolution_quality": 0.88
      }
    }
  ],
  "query_analysis": {
    "processed_query": "server crashes boot firmware",
    "detected_entities": ["server", "boot", "firmware"],
    "query_type": "technical_issue",
    "suggested_expansions": ["startup", "initialization"]
  },
  "search_metadata": {
    "total_found": 156,
    "search_time_ms": 45,
    "search_type_used": "hybrid",
    "cache_hit": false,
    "session_id": "session-uuid"
  },
  "facets": {
    "product_hierarchy": {"ProLiant": 89, "iLO": 34, "Storage": 23},
    "status": {"Closed": 134, "Resolved": 22},
    "priority": {"High": 45, "Medium": 78, "Low": 33}
  }
}
```

### GET `/api/v1/search/suggestions`
**Auto-complete search suggestions**

**Parameters:**
- `q` (required): Partial query text
- `limit` (optional): 1-20 suggestions (default: 10)

**Response:**
```json
{
  "suggestions": [
    {
      "text": "server boot failure",
      "type": "query",
      "frequency": 156,
      "confidence": 0.89
    },
    {
      "text": "ProLiant server issues",
      "type": "product_query", 
      "frequency": 94,
      "confidence": 0.76
    }
  ],
  "total": 2,
  "response_time_ms": 12
}
```

### POST `/api/v1/search/feedback`
**Submit search result feedback for ML improvement**

**Request Body:**
```json
{
  "session_id": "session-uuid",
  "query": "original search query",
  "result_id": "case_123456",
  "feedback_type": "helpful|not_helpful|irrelevant",
  "rating": 4,
  "comments": "This case solved my issue perfectly"
}
```

### GET `/api/v1/search/analytics/metrics`
**Search performance analytics**

**Response:**
```json
{
  "period": "last_30_days",
  "metrics": {
    "total_searches": 15847,
    "avg_response_time_ms": 45,
    "success_rate": 0.94,
    "cache_hit_rate": 0.87,
    "user_satisfaction": 4.2
  },
  "trends": {
    "searches_per_day": [523, 678, 445, 789],
    "popular_queries": ["server boot", "network issues", "storage problems"]
  }
}
```

### GET `/api/v1/search/analytics/popular`
**Popular search queries and trends**

### GET `/api/v1/search/analytics/insights`
**Search insights and recommendations**

## 📋 Cases Management

### GET `/api/v1/cases/`
**List cases with pagination and filtering**

**Parameters:**
- `page` (optional): Page number (default: 1)
- `size` (optional): Items per page, 1-100 (default: 20)
- `status` (optional): Filter by case status
- `product_hierarchy` (optional): Filter by product
- `search` (optional): Full-text search
- `sort` (optional): `created_at|priority|status` (default: `created_at`)
- `order` (optional): `asc|desc` (default: `desc`)

**Response:**
```json
{
  "items": [
    {
      "id": "case_123456",
      "case_number": "5350123456", 
      "subject": "ProLiant server boot failure",
      "status": "Closed",
      "priority": "High",
      "product_hierarchy": "ProLiant DL380",
      "created_at": "2024-06-15T10:30:00Z",
      "updated_at": "2024-06-16T14:20:00Z",
      "summary": "Brief case description..."
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 1250,
    "pages": 63,
    "has_next": true,
    "has_prev": false
  }
}
```

### GET `/api/v1/cases/{case_id}`
**Get detailed case information**

**Response:**
```json
{
  "id": "case_123456",
  "case_number": "5350123456",
  "subject": "ProLiant server boot failure",
  "issue_description": "Detailed issue description...",
  "resolution": "Detailed resolution steps...",
  "status": "Closed",
  "priority": "High", 
  "product_hierarchy": "ProLiant DL380",
  "issue_category": "Hardware",
  "created_at": "2024-06-15T10:30:00Z",
  "resolved_at": "2024-06-16T14:20:00Z",
  "customer_info": {
    "account": "Enterprise Customer",
    "contact": "redacted"
  },
  "technical_details": {
    "operating_system": "RHEL 8.5",
    "firmware_version": "U32 v2.65",
    "error_codes": ["POST-001", "BIOS-ERR"]
  },
  "resolution_steps": [
    "Updated system firmware to latest version",
    "Reset BIOS to default settings", 
    "Verified system stability"
  ]
}
```

### GET `/api/v1/cases/number/{case_number}`
**Get case by case number (alternative lookup)**

### GET `/api/v1/cases/{case_id}/similar`
**Find similar cases using AI**

**Parameters:**
- `limit` (optional): 1-20 results (default: 5)
- `threshold` (optional): 0.0-1.0 similarity threshold (default: 0.7)

**Response:**
```json
{
  "similar_cases": [
    {
      "id": "case_789012",
      "case_number": "5350789012",
      "subject": "Similar boot issue resolved",
      "similarity_score": 0.89,
      "resolution_summary": "Updated firmware and reset BIOS"
    }
  ],
  "total_found": 12,
  "search_time_ms": 67
}
```

### GET `/api/v1/cases/statistics/overview`
**Case statistics overview**

**Response:**
```json
{
  "total_cases": 1250,
  "by_status": {
    "Open": 45,
    "In Progress": 78,
    "Closed": 1127
  },
  "by_priority": {
    "Critical": 12,
    "High": 156,
    "Medium": 789,
    "Low": 293
  },
  "resolution_metrics": {
    "avg_resolution_time_hours": 18.5,
    "first_call_resolution_rate": 0.67
  }
}
```

## 📚 Knowledge Management

### GET `/api/v1/knowledge/`
**List knowledge articles with filtering**

**Parameters:**
- `page`, `size` (pagination)
- `category` (optional): Filter by category
- `tags` (optional): Filter by tags
- `published_only` (optional): Only published articles (default: true)
- `search` (optional): Full-text search

**Response:**
```json
{
  "items": [
    {
      "id": "kb_001234",
      "title": "ProLiant Server Troubleshooting Guide",
      "summary": "Comprehensive guide for common issues...",
      "category": "Hardware",
      "article_type": "Guide",
      "tags": ["server", "troubleshooting", "hardware"],
      "is_published": true,
      "created_at": "2024-05-01T09:00:00Z",
      "updated_at": "2024-06-01T15:30:00Z",
      "view_count": 1547,
      "rating": 4.6
    }
  ],
  "pagination": { /* same as cases */ }
}
```

### POST `/api/v1/knowledge/`
**Create new knowledge article**

**Request Body:**
```json
{
  "title": "New Troubleshooting Guide",
  "content": "Detailed article content in markdown...",
  "summary": "Brief article summary",
  "category": "Hardware",
  "article_type": "Guide",
  "tags": ["server", "troubleshooting"],
  "is_published": false
}
```

### GET `/api/v1/knowledge/{article_id}`
**Get specific knowledge article**

### PUT `/api/v1/knowledge/{article_id}`
**Update knowledge article**

### DELETE `/api/v1/knowledge/{article_id}`
**Delete knowledge article**

### POST `/api/v1/knowledge/{article_id}/publish`
**Publish knowledge article**

### POST `/api/v1/knowledge/{article_id}/feedback`
**Submit article feedback**

**Request Body:**
```json
{
  "rating": 5,
  "feedback_type": "helpful|not_helpful|needs_update",
  "comments": "Very helpful guide, solved my issue",
  "user_id": "optional-user-id"
}
```

### GET `/api/v1/knowledge/categories/list`
**Get knowledge article categories**

**Response:**
```json
{
  "categories": [
    {"name": "Hardware", "count": 156, "description": "Hardware-related articles"},
    {"name": "Software", "count": 234, "description": "Software troubleshooting"},
    {"name": "Network", "count": 89, "description": "Network configuration guides"}
  ]
}
```

### GET `/api/v1/knowledge/tags/popular`
**Get popular tags**

## 🔄 Legacy API Compatibility

### GET `/legacy/coveo/search`
**Coveo Case Search replacement (backward compatible)**

**Parameters:**
- `q` (required): Search query
- `numberOfResults` (optional): Result count (default: 10)
- `firstResult` (optional): Starting index (default: 0)
- `sortCriteria` (optional): Sort criteria

**Response:** *Maintains exact Coveo response format*

### GET `/legacy/coveo/facets`
**Legacy facets endpoint**

### POST `/legacy/coveo/analytics/click`
**Click analytics tracking**

### GET `/legacy/health`
**Legacy API health check**

## 📊 Response Models

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid query parameter",
    "details": {
      "field": "similarity_threshold",
      "value": "1.5",
      "constraint": "Must be between 0.0 and 1.0"
    }
  },
  "timestamp": "2025-07-14T09:00:00Z",
  "request_id": "req_123456789"
}
```

### Standard HTTP Status Codes
- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Service temporarily unavailable

## 🔧 Configuration & Environment

### Environment Variables
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Database
DATABASE_URL="postgresql://user:pass@localhost/kms_v1"
CHROMA_PERSIST_DIRECTORY="./data/chromadb_data_comprehensive"

# API Keys
OPENAI_API_KEY="your-openai-key"
PINECONE_API_KEY="your-pinecone-key"  # Optional

# CORS & Security
CORS_ORIGINS=["http://localhost:3000", "https://*.hpe.com"]
TRUSTED_HOSTS=["localhost", "*.hpe.com"]

# Performance
ENABLE_CACHING=true
CACHE_TTL_SECONDS=300
MAX_RESULTS_LIMIT=100
```

## ⚡ Performance & Limits

### Rate Limiting
- **Default**: 100 requests/minute per IP
- **Authenticated**: 1000 requests/minute per user
- **Search Heavy**: 500 requests/hour for complex searches

### Response Times (SLA)
- **Health checks**: < 50ms
- **Simple searches**: < 200ms
- **Complex searches**: < 500ms
- **Knowledge CRUD**: < 300ms

### Request Limits
- **Query length**: 1000 characters
- **Results per request**: 100 maximum
- **Bulk operations**: 50 items maximum
- **Request size**: 10MB maximum

## 🧪 Testing

### Using cURL
```bash
# Health check
curl http://localhost:8000/api/v1/health/

# Search example
curl -X POST http://localhost:8000/api/v1/search/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "server boot failure",
    "search_type": "hybrid",
    "max_results": 5
  }'

# Get case details
curl http://localhost:8000/api/v1/cases/case_123456
```

### Postman Collection
Import the API collection from `/data/postman_collection.json` for comprehensive testing.

### API Test Suite
```bash
# Run comprehensive API tests
python scripts/api_test_suite.py

# Test specific endpoints
python scripts/test_search.py
```

## 📈 Monitoring & Analytics

### Metrics Available
- Request volume and response times
- Search query analysis and success rates
- Cache hit rates and performance optimization
- Error rates and failure analysis
- User satisfaction and feedback trends

### Prometheus Metrics
Access metrics at `/api/v1/health/metrics` for Prometheus scraping.

### Custom Dashboards
- Grafana dashboards available for operations monitoring
- Business intelligence dashboards for search analytics
- Performance monitoring for capacity planning

## 🚀 Getting Started

1. **Start the API server**:
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access interactive docs**: http://localhost:8000/docs

3. **Test health endpoint**: http://localhost:8000/api/v1/health/

4. **Run your first search**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/search/ \
     -H "Content-Type: application/json" \
     -d '{"query": "test search", "max_results": 5}'
   ```

## 📞 Support

- **Documentation**: [Complete System Guide](ASYNC_PROCESSING_SYSTEM.md)
- **Architecture**: [System Flow Diagrams](SYSTEM_FLOW_DIAGRAM.md)
- **Repository**: [Structure Overview](REPOSITORY_STRUCTURE.md)
- **Issue Tracking**: GitHub Issues
- **Health Monitoring**: `/api/v1/health/detailed`

---

**KMS-V1 API**: Production-ready, AI-powered knowledge management with high-performance search capabilities and enterprise-grade monitoring.
