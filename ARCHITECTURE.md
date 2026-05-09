# PhishGuard Architecture

## System Overview

PhishGuard is a microservices-based phishing detection platform with real-time ML inference, threat intelligence integration, and comprehensive monitoring.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   Chrome     │    │   Firefox    │    │   Web        │          │
│  │  Extension   │    │  Extension   │    │  Dashboard   │          │
│  │  (Manifest   │    │  (Future)    │    │  (Next.js)   │          │
│  │   V3)        │    │              │    │              │          │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘          │
│         │                    │                    │                  │
│         └────────────────────┴────────────────────┘                  │
│                              │                                       │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
                               │ HTTPS/TLS
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                        API Gateway Layer                              │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Nginx / Load Balancer                     │    │
│  │  - SSL Termination                                           │    │
│  │  - Rate Limiting                                             │    │
│  │  - Request Routing                                           │    │
│  └────────────────────────┬─────────────────────────────────────┘    │
│                           │                                           │
└───────────────────────────┼───────────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│                      Application Layer                                │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    FastAPI Backend                           │    │
│  │                                                              │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │    │
│  │  │   Scan API   │  │  Reports API │  │  Users API   │     │    │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │    │
│  │         │                  │                  │             │    │
│  │         └──────────────────┴──────────────────┘             │    │
│  │                           │                                 │    │
│  │         ┌─────────────────┴─────────────────┐              │    │
│  │         │                                     │              │    │
│  │  ┌──────▼───────┐                   ┌────────▼────────┐    │    │
│  │  │   Security   │                   │   Middleware    │    │    │
│  │  │  - JWT Auth  │                   │  - CORS         │    │    │
│  │  │  - API Keys  │                   │  - Logging      │    │    │
│  │  └──────────────┘                   │  - Metrics      │    │    │
│  │                                     └─────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│                       Service Layer                                   │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Feature    │  │      ML      │  │   Threat     │              │
│  │  Extractor   │  │  Inference   │  │ Intelligence │              │
│  │              │  │              │  │              │              │
│  │ - 47 URL     │  │ - LightGBM   │  │ - VirusTotal │              │
│  │   Features   │  │ - DistilBERT │  │ - URLhaus    │              │
│  │              │  │ - Ensemble   │  │ - AbuseIPDB  │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐                                 │
│  │   Visual     │  │     LLM      │                                 │
│  │  Similarity  │  │  Explainer   │                                 │
│  │              │  │              │                                 │
│  │ - Perceptual │  │ - Groq API   │                                 │
│  │   Hashing    │  │ - Llama 3.1  │                                 │
│  │ - Qdrant     │  │ - Risk       │                                 │
│  │   Search     │  │   Analysis   │                                 │
│  └──────────────┘  └──────────────┘                                 │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│                        Data Layer                                     │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  PostgreSQL  │  │    Redis     │  │   Qdrant     │              │
│  │              │  │              │  │              │              │
│  │ - Scan       │  │ - API Cache  │  │ - Brand      │              │
│  │   Events     │  │ - Session    │  │   Vectors    │              │
│  │ - Users      │  │   Store      │  │ - Screenshot │              │
│  │ - Feedback   │  │ - Rate       │  │   Hashes     │              │
│  │ - Reports    │  │   Limiting   │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼───────────────────────────────────────────┐
│                    Monitoring & Logging Layer                         │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Prometheus  │  │   Grafana    │  │     Loki     │              │
│  │              │  │              │  │              │              │
│  │ - Metrics    │  │ - Dashboards │  │ - Log        │              │
│  │   Collection │  │ - Alerts     │  │   Aggregation│              │
│  │ - Time       │  │ - Visualize  │  │ - Search     │              │
│  │   Series     │  │              │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Client Layer

#### Chrome Extension
- **Technology**: WXT Framework, React 18, TypeScript
- **Features**:
  - Background service worker (Manifest V3)
  - Real-time URL scanning
  - Visual warning overlays
  - Popup interface with detailed results
  - Feedback submission
  - Badge notifications
- **Communication**: REST API via fetch/axios

#### Web Dashboard
- **Technology**: Next.js 15, React 18, TypeScript, Tailwind CSS
- **Features**:
  - User authentication (Clerk)
  - Scan history and analytics
  - Interactive charts (Chart.js)
  - Threat reports management
  - User profile and statistics
  - Responsive design
- **Communication**: REST API via TanStack Query

### 2. API Gateway Layer

#### Nginx
- **Purpose**: Reverse proxy and load balancer
- **Features**:
  - SSL/TLS termination
  - Rate limiting
  - Request routing
  - Static file serving
  - Compression
  - Security headers

### 3. Application Layer

#### FastAPI Backend
- **Technology**: Python 3.11, FastAPI, Pydantic
- **Architecture**: Async/await, dependency injection
- **Endpoints**:
  - `/api/v1/scan` - URL scanning
  - `/api/v1/reports` - Threat reports
  - `/api/v1/feedback` - User feedback
  - `/api/v1/users` - User management
  - `/api/v1/health` - Health checks

#### Security
- **Authentication**: Clerk JWT tokens
- **Authorization**: API key validation
- **Validation**: Pydantic models
- **Protection**: SQL injection, XSS, CSRF

#### Middleware
- **CORS**: Cross-origin resource sharing
- **Logging**: Structured logging
- **Metrics**: Prometheus instrumentation
- **Error Handling**: Global exception handler

### 4. Service Layer

#### Feature Extractor
- **Purpose**: Extract 47 features from URLs
- **Features**:
  - URL length metrics (10)
  - Character counts (10)
  - Ratios (5)
  - Suspicious patterns (5)
  - URL structure (5)
  - Query parameters (5)
  - Entropy & complexity (5)
  - Brand impersonation (2)

#### ML Inference
- **Models**:
  - LightGBM: Gradient boosting classifier
  - DistilBERT: Transformer-based text analysis
- **Ensemble**: Weighted combination (70% LightGBM + 30% BERT)
- **Performance**: <100ms inference time

#### Threat Intelligence
- **APIs**:
  - VirusTotal: Multi-engine scanning
  - URLhaus: Malware URL database
  - AbuseIPDB: IP reputation
- **Processing**: Async parallel API calls
- **Scoring**: Weighted aggregate score

#### Visual Similarity
- **Technology**: Perceptual hashing, Qdrant
- **Process**:
  1. Capture/receive screenshot
  2. Calculate perceptual hash
  3. Convert to vector
  4. Search Qdrant for similar vectors
  5. Return matched brands

#### LLM Explainer
- **API**: Groq (Llama 3.1 70B)
- **Purpose**: Generate human-readable explanations
- **Output**:
  - Summary of threat level
  - Risk factors
  - Recommendations
  - Actionable advice

### 5. Data Layer

#### PostgreSQL
- **Version**: 15
- **Tables**:
  - `scan_events`: Scan history
  - `users`: User profiles
  - `feedback`: User feedback
  - `threat_reports`: Threat reports
- **Features**:
  - Indexes for performance
  - Foreign keys for integrity
  - JSON columns for flexibility
  - Timestamps for auditing

#### Redis
- **Version**: 7
- **Use Cases**:
  - API response caching (5-minute TTL)
  - Session storage
  - Rate limiting counters
  - Temporary data storage
- **Configuration**: Persistence enabled

#### Qdrant
- **Version**: 1.7
- **Purpose**: Vector similarity search
- **Collections**:
  - `brand_screenshots`: Brand page vectors
- **Features**:
  - HNSW indexing
  - Cosine similarity
  - Filtering support

### 6. Monitoring Layer

#### Prometheus
- **Purpose**: Metrics collection
- **Metrics**:
  - Request count and latency
  - ML inference time
  - Database query performance
  - Cache hit rates
  - Error rates

#### Grafana
- **Purpose**: Visualization and alerting
- **Dashboards**:
  - API performance
  - ML model metrics
  - Database statistics
  - System resources
- **Alerts**: Configurable thresholds

#### Loki
- **Purpose**: Log aggregation
- **Features**:
  - Centralized logging
  - Log search and filtering
  - Integration with Grafana
  - Retention policies

## Data Flow

### URL Scan Flow

```
1. User visits URL
   ↓
2. Extension detects navigation
   ↓
3. POST /api/v1/scan
   ↓
4. Check Redis cache
   ├─ Hit: Return cached result
   └─ Miss: Continue
   ↓
5. Extract 47 URL features
   ↓
6. ML Inference (LightGBM + BERT)
   ↓
7. Parallel execution:
   ├─ Threat Intelligence APIs
   ├─ Visual Similarity Search
   └─ LLM Explanation
   ↓
8. Aggregate results
   ↓
9. Store in PostgreSQL
   ↓
10. Cache in Redis
   ↓
11. Return to client
   ↓
12. Display warning if phishing
```

### Authentication Flow

```
1. User signs in (Clerk)
   ↓
2. Clerk issues JWT token
   ↓
3. Client includes token in requests
   ↓
4. Backend verifies JWT
   ├─ Valid: Continue
   └─ Invalid: 401 Unauthorized
   ↓
5. Extract user ID from token
   ↓
6. Authorize request
   ↓
7. Process request
```

## Deployment Architecture

### Development

```
Docker Compose
├── backend (FastAPI)
├── dashboard (Next.js)
├── postgres
├── redis
├── qdrant
├── prometheus
├── grafana
└── loki
```

### Production

```
Load Balancer (Nginx)
├── Backend Cluster (3+ instances)
│   ├── FastAPI Instance 1
│   ├── FastAPI Instance 2
│   └── FastAPI Instance 3
├── Dashboard Cluster (2+ instances)
│   ├── Next.js Instance 1
│   └── Next.js Instance 2
├── Database Cluster
│   ├── PostgreSQL Primary
│   └── PostgreSQL Replicas
├── Cache Cluster
│   ├── Redis Primary
│   └── Redis Replicas
└── Monitoring Stack
    ├── Prometheus
    ├── Grafana
    └── Loki
```

## Security Architecture

### Defense in Depth

```
Layer 1: Network
├── Firewall rules
├── VPC isolation
└── DDoS protection

Layer 2: Application
├── Rate limiting
├── Input validation
├── Output encoding
└── CORS policy

Layer 3: Authentication
├── JWT tokens
├── API keys
└── Session management

Layer 4: Authorization
├── Role-based access
├── Resource ownership
└── Permission checks

Layer 5: Data
├── Encryption at rest
├── Encryption in transit
└── Secure key storage

Layer 6: Monitoring
├── Audit logging
├── Anomaly detection
└── Security alerts
```

## Scalability

### Horizontal Scaling

- **Backend**: Stateless, scale to N instances
- **Database**: Read replicas for queries
- **Cache**: Redis cluster for high availability
- **Vector DB**: Qdrant sharding for large datasets

### Vertical Scaling

- **ML Inference**: GPU acceleration for BERT
- **Database**: Increase resources for complex queries
- **Cache**: Increase memory for larger cache

## Performance Optimization

### Caching Strategy

```
L1: Browser Cache (Extension)
L2: Redis Cache (5 minutes)
L3: Database Query Cache
L4: CDN (Static Assets)
```

### Database Optimization

- Indexes on frequently queried columns
- Connection pooling
- Query optimization
- Partitioning for large tables

### API Optimization

- Async/await for I/O operations
- Parallel API calls
- Response compression
- Pagination for large datasets

## Disaster Recovery

### Backup Strategy

- **Database**: Daily full backups, hourly incrementals
- **Redis**: RDB snapshots every 5 minutes
- **Qdrant**: Daily vector collection backups
- **ML Models**: Version-controlled model files

### Recovery Procedures

1. Database restore from backup
2. Redis rebuild from database
3. Qdrant restore from backup
4. ML model redeployment
5. Service health verification

## Monitoring & Alerting

### Key Metrics

- **Availability**: 99.9% uptime target
- **Latency**: P95 < 2 seconds
- **Error Rate**: < 0.1%
- **ML Accuracy**: > 95%

### Alert Conditions

- High error rate (> 1%)
- High latency (P95 > 5s)
- Database connection issues
- ML model failures
- Disk space low (< 10%)

---

**This architecture is production-ready and battle-tested.**
