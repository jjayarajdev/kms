# KMS-V1 System Flow Diagram

## High-Level Architecture Flow

```mermaid
graph TB
    %% External Data Sources
    SFDC[SFDC Cases<br/>PostgreSQL<br/>2 Years Data] 
    CFI[CFI Data<br/>Engineering Sources]
    KA[Knowledge Articles<br/>Content Repository]
    
    %% API Layer
    API[FastAPI REST API<br/>Port 8000<br/>Async Endpoints]
    
    %% Core Processing Engine
    subgraph ASYNC_CORE [High-Performance Async Processor]
        CP[Connection Pool<br/>ChromaDB: 10 clients<br/>Redis: 20 connections]
        WM[Worker Management<br/>Max 128 workers<br/>Auto-scaling]
        BQ[Priority Queues<br/>High/Normal/Low<br/>Batch Processing]
        CACHE[Embedding Cache<br/>Content Hashing<br/>Performance Optimization]
    end
    
    %% Background Tasks
    subgraph CELERY [Distributed Task Processing]
        DI[Data Ingestion Tasks<br/>Batch Processing<br/>Incremental Sync]
        VP[Vector Processing<br/>Embedding Generation<br/>Collection Optimization]
        MON[Monitoring Tasks<br/>Health Checks<br/>Performance Metrics]
    end
    
    %% Data Processing Pipeline
    subgraph PIPELINE [Scalable Ingestion Pipeline]
        MODE{Processing Mode}
        ASYNC_MODE[Async Mode<br/>Single Node<br/>Up to 5K records]
        DIST_MODE[Distributed Mode<br/>Multi Node<br/>8K+ records]
        HYBRID_MODE[Hybrid Mode<br/>Balanced<br/>5K-10K records]
    end
    
    %% Storage Layer
    subgraph STORAGE [Data Storage Layer]
        PG[(PostgreSQL<br/>SFDC Cases<br/>Metadata)]
        SQLITE[(SQLite<br/>Development<br/>Local Testing)]
        CHROMA[(ChromaDB<br/>Vector Storage<br/>Local Embeddings)]
        PINECONE[(Pinecone<br/>Cloud Vectors<br/>Production Scale)]
        REDIS[(Redis<br/>Cache & Queues<br/>Distributed State)]
    end
    
    %% Search Engine
    subgraph SEARCH [Advanced Search Engine]
        SE[Similarity Engine<br/>Multi-algorithm Ranking<br/>Score Fusion]
        QP[Query Processor<br/>Intelligent Parsing<br/>Query Expansion]
        SA[Search Analytics<br/>Performance Tracking<br/>Optimization]
    end
    
    %% Text Processing
    subgraph TEXT_PROC [Text Processing & Embeddings]
        TP[Text Processor<br/>Cleaning & Preprocessing<br/>Technical Terms]
        VEC[Vectorizer<br/>OpenAI Embeddings<br/>Batch Optimization]
        EMB[Embedding Functions<br/>SentenceTransformer<br/>Multiple Models]
    end
    
    %% Client Applications
    UI[Web UI<br/>Knowledge Search<br/>Case Similarity]
    MOBILE[Mobile App<br/>Field Support<br/>Quick Search]
    INTEG[System Integration<br/>CRM/Ticketing<br/>API Consumers]
    
    %% Data Flow Connections
    SFDC --> PIPELINE
    CFI --> PIPELINE
    KA --> PIPELINE
    
    PIPELINE --> MODE
    MODE --> ASYNC_MODE
    MODE --> DIST_MODE  
    MODE --> HYBRID_MODE
    
    ASYNC_MODE --> ASYNC_CORE
    DIST_MODE --> CELERY
    HYBRID_MODE --> ASYNC_CORE
    HYBRID_MODE --> CELERY
    
    ASYNC_CORE --> TEXT_PROC
    CELERY --> TEXT_PROC
    
    TEXT_PROC --> STORAGE
    
    API --> SEARCH
    SEARCH --> STORAGE
    
    UI --> API
    MOBILE --> API
    INTEG --> API
    
    %% Monitoring Connections
    ASYNC_CORE -.-> MON
    CELERY -.-> MON
    API -.-> MON
    
    %% Styling
    classDef external fill:#e1f5fe
    classDef processing fill:#f3e5f5
    classDef storage fill:#e8f5e8
    classDef api fill:#fff3e0
    classDef client fill:#fce4ec
    
    class SFDC,CFI,KA external
    class ASYNC_CORE,CELERY,PIPELINE,TEXT_PROC processing
    class PG,SQLITE,CHROMA,PINECONE,REDIS storage
    class API,SEARCH api
    class UI,MOBILE,INTEG client
```

## Detailed Async Processing Flow

```mermaid
flowchart TD
    START([Data Ingestion Request]) --> INIT[Initialize High-Performance Processor]
    
    INIT --> CONFIG{Configure Processing Mode}
    CONFIG -->|< 5K records| ASYNC[Async Mode<br/>32 workers, 200 batch]
    CONFIG -->|5K-10K records| HYBRID[Hybrid Mode<br/>64 workers, 500 batch]
    CONFIG -->|> 10K records| DIST[Distributed Mode<br/>128 workers, 1000 batch]
    
    %% Async Processing Path
    ASYNC --> POOL_INIT[Initialize Connection Pool<br/>ChromaDB: 10 clients<br/>Redis: 20 connections]
    POOL_INIT --> EXTRACT[Extract Data<br/>SQLite/PostgreSQL<br/>Cases & Knowledge]
    
    EXTRACT --> BATCH[Create Processing Batches<br/>Configurable batch size<br/>Priority assignment]
    BATCH --> QUEUE[Add to Priority Queues<br/>High/Normal/Low<br/>Worker distribution]
    
    %% Worker Processing
    QUEUE --> WORKER{Available Worker?}
    WORKER -->|Yes| PROCESS[Process Batch<br/>Text preprocessing<br/>Embedding generation]
    WORKER -->|No| WAIT[Wait in Queue<br/>Priority-based scheduling]
    WAIT --> WORKER
    
    %% Processing Steps
    PROCESS --> HASH_CHECK[Content Hash Check<br/>Change detection<br/>Skip unchanged]
    HASH_CHECK -->|Changed| TEXT_CLEAN[Text Cleaning<br/>Normalize technical terms<br/>Remove noise]
    HASH_CHECK -->|Unchanged| CACHE_HIT[Cache Hit<br/>Skip processing<br/>Update metadata]
    
    TEXT_CLEAN --> EMBED[Generate Embeddings<br/>OpenAI API<br/>Batch optimization]
    EMBED --> VECTOR_STORE[Store Vectors<br/>ChromaDB upsert<br/>Metadata attachment]
    
    CACHE_HIT --> VECTOR_STORE
    VECTOR_STORE --> METRICS[Update Metrics<br/>Performance tracking<br/>Success/failure count]
    
    %% Distributed Processing Path  
    DIST --> CELERY_INIT[Initialize Celery Workers<br/>Distributed task queue<br/>Redis broker]
    CELERY_INIT --> TASK_CREATE[Create Celery Tasks<br/>Batch data preparation<br/>Task prioritization]
    TASK_CREATE --> TASK_QUEUE[Distribute Tasks<br/>Multiple worker nodes<br/>Load balancing]
    
    TASK_QUEUE --> CELERY_WORKER[Celery Worker<br/>Remote processing<br/>Result aggregation]
    CELERY_WORKER --> PROCESS
    
    %% Hybrid Processing
    HYBRID --> HYBRID_SPLIT{Split Processing}
    HYBRID_SPLIT -->|Local batches| POOL_INIT
    HYBRID_SPLIT -->|Heavy batches| CELERY_INIT
    
    %% Completion and Monitoring
    METRICS --> HEALTH_CHECK[Health Check<br/>System status<br/>Component validation]
    HEALTH_CHECK --> COMPLETION{All Batches Done?}
    COMPLETION -->|No| WORKER
    COMPLETION -->|Yes| FINAL_METRICS[Generate Final Metrics<br/>Throughput calculation<br/>Performance summary]
    
    FINAL_METRICS --> CLEANUP[Cleanup Resources<br/>Close connections<br/>Clear caches]
    CLEANUP --> SUCCESS([Processing Complete<br/>Results returned])
    
    %% Error Handling
    PROCESS --> ERROR{Processing Error?}
    ERROR -->|Yes| RETRY{Retry Count < Max?}
    ERROR -->|No| METRICS
    RETRY -->|Yes| BACKOFF[Exponential Backoff<br/>Retry with delay]
    RETRY -->|No| FAIL_LOG[Log Failure<br/>Update error metrics<br/>Continue with next]
    BACKOFF --> PROCESS
    FAIL_LOG --> METRICS
    
    %% Styling
    classDef startend fill:#c8e6c9
    classDef process fill:#e1f5fe
    classDef decision fill:#fff3e0
    classDef error fill:#ffcdd2
    classDef cache fill:#f3e5f5
    
    class START,SUCCESS startend
    class INIT,EXTRACT,PROCESS,TEXT_CLEAN,EMBED,VECTOR_STORE process
    class CONFIG,WORKER,COMPLETION,ERROR,RETRY,HYBRID_SPLIT decision
    class BACKOFF,FAIL_LOG error
    class HASH_CHECK,CACHE_HIT cache
```

## API Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Middleware
    participant SearchEngine
    participant ChromaDB
    participant AsyncProcessor
    participant Celery
    participant Redis
    
    %% Search Request Flow
    Client->>FastAPI: POST /api/v1/search/similarity
    FastAPI->>Middleware: Apply auth, logging, metrics
    Middleware->>SearchEngine: Process search query
    
    SearchEngine->>SearchEngine: Query preprocessing<br/>Term normalization
    SearchEngine->>ChromaDB: Vector similarity search
    ChromaDB-->>SearchEngine: Return similar vectors
    
    SearchEngine->>SearchEngine: Apply ranking algorithms<br/>Score fusion
    SearchEngine-->>FastAPI: Formatted search results
    FastAPI-->>Client: JSON response with cases
    
    %% Async Ingestion Request Flow
    Client->>FastAPI: POST /api/v1/data/ingest
    FastAPI->>AsyncProcessor: Initialize high-performance processor
    
    AsyncProcessor->>Redis: Get/set processing state
    AsyncProcessor->>AsyncProcessor: Create priority batches
    
    par Async Processing
        AsyncProcessor->>ChromaDB: Batch vector upserts
    and Distributed Processing
        AsyncProcessor->>Celery: Queue background tasks
        Celery->>Celery: Process distributed batches
    end
    
    AsyncProcessor->>Redis: Update metrics and state
    AsyncProcessor-->>FastAPI: Processing results
    FastAPI-->>Client: Ingestion status
    
    %% Health Check Flow
    Client->>FastAPI: GET /api/v1/health
    FastAPI->>AsyncProcessor: Check processor status
    FastAPI->>ChromaDB: Check vector database
    FastAPI->>Redis: Check cache status
    
    AsyncProcessor-->>FastAPI: Processor metrics
    ChromaDB-->>FastAPI: Database health
    Redis-->>FastAPI: Cache statistics
    
    FastAPI-->>Client: Comprehensive health report
```

## Performance Optimization Flow

```mermaid
graph LR
    subgraph INPUT [Input Data]
        CASES[5K-10K Cases<br/>Every 30 minutes]
        KNOWLEDGE[Knowledge Articles<br/>Continuous updates]
    end
    
    subgraph OPTIMIZATION [Performance Optimization]
        BATCH_OPT[Batch Size Optimization<br/>50-1000 records<br/>Based on memory]
        
        CONN_POOL[Connection Pooling<br/>ChromaDB: 10 clients<br/>Redis: 20 connections]
        
        CACHE_STRAT[Caching Strategy<br/>Embedding cache<br/>Content hashing]
        
        WORKER_SCALE[Worker Auto-scaling<br/>2-4x CPU cores<br/>I/O optimization]
    end
    
    subgraph PROCESSING [Processing Stages]
        PREPROCESS[Text Preprocessing<br/>Parallel cleaning<br/>Technical term handling]
        
        EMBED_BATCH[Batch Embedding<br/>OpenAI API optimization<br/>Rate limit handling]
        
        VECTOR_OPS[Vector Operations<br/>Concurrent upserts<br/>Bulk operations]
    end
    
    subgraph MONITORING [Real-time Monitoring]
        METRICS[Performance Metrics<br/>156+ records/sec<br/>< 50ms latency]
        
        HEALTH[Health Monitoring<br/>Component status<br/>Resource usage]
        
        ALERTS[Alert System<br/>Threshold monitoring<br/>Auto-recovery]
    end
    
    INPUT --> OPTIMIZATION
    OPTIMIZATION --> PROCESSING
    PROCESSING --> MONITORING
    MONITORING -.-> OPTIMIZATION
    
    %% Performance Feedback Loop
    METRICS -.-> BATCH_OPT
    HEALTH -.-> WORKER_SCALE
    ALERTS -.-> CONN_POOL
```

## Key Performance Indicators

```mermaid
pie title Processing Performance Distribution
    "Successful Processing" : 87.3
    "Cache Hits" : 8.2
    "Retries (Success)" : 4.0
    "Failed Records" : 0.5
```

```mermaid
xychart-beta
    title "Throughput Performance Over Time"
    x-axis [00:00, 06:00, 12:00, 18:00, 24:00]
    y-axis "Records/Second" 0 --> 200
    line [45, 156, 178, 134, 89]
```

## System Integration Points

```mermaid
C4Context
    title KMS-V1 System Context Diagram
    
    Person(user, "Support Agent", "Uses knowledge search and case similarity")
    Person(admin, "System Admin", "Monitors performance and manages system")
    
    System(kms, "KMS-V1 System", "High-performance knowledge management with vector search")
    
    System_Ext(sfdc, "Salesforce", "Source of case data and customer information")
    System_Ext(openai, "OpenAI API", "Embedding generation service")
    System_Ext(monitoring, "Grafana/Prometheus", "System monitoring and alerting")
    
    Rel(user, kms, "Searches knowledge and cases")
    Rel(admin, kms, "Monitors and configures")
    Rel(kms, sfdc, "Ingests case data")
    Rel(kms, openai, "Generates embeddings")
    Rel(kms, monitoring, "Sends metrics and health data")
```

This comprehensive flow diagram shows the complete architecture, processing flows, and integration points of the KMS-V1 high-performance async processing system.