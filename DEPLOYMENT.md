# PhishGuard Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Qdrant 1.7+

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/phishguard.git
cd phishguard
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
```env
# Database
DATABASE_URL=postgresql://phishguard:phishguard@postgres:5432/phishguard

# Redis
REDIS_URL=redis://redis:6379/0

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Clerk Authentication
CLERK_SECRET_KEY=sk_test_xxxxx
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx

# Extension API Key
EXTENSION_API_KEY=your-secure-api-key-here

# Threat Intelligence APIs (Optional)
VIRUSTOTAL_API_KEY=your-virustotal-key
ABUSEIPDB_API_KEY=your-abuseipdb-key

# LLM API (Optional)
GROQ_API_KEY=your-groq-api-key

# Application
DEBUG=false
CORS_ORIGINS=["http://localhost:3000"]
ML_MODEL_PATH=/app/app/ml/models
```

## Development Deployment

### Using Docker Compose

1. **Start all services:**
```bash
make dev
```

This starts:
- Backend API (port 8000)
- Dashboard (port 3000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Qdrant (port 6333)
- Prometheus (port 9090)
- Grafana (port 3001)
- Loki (port 3100)

2. **Run database migrations:**
```bash
make migrate
```

3. **Train ML model:**
```bash
make train
```

4. **Access services:**
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:3000
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090

### Manual Setup (Without Docker)

#### Backend

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run migrations:**
```bash
alembic upgrade head
```

4. **Train model:**
```bash
python app/ml/train.py
```

5. **Start server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Dashboard

1. **Install dependencies:**
```bash
cd dashboard
npm install
```

2. **Start development server:**
```bash
npm run dev
```

#### Extension

1. **Install dependencies:**
```bash
cd extension
npm install
```

2. **Build extension:**
```bash
npm run build
```

3. **Load in Chrome:**
- Open `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked"
- Select `extension/.output/chrome-mv3` directory

## Production Deployment

### Docker Compose Production

1. **Build production images:**
```bash
make build
```

2. **Start production stack:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Run migrations:**
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

4. **Train model:**
```bash
docker-compose -f docker-compose.prod.yml exec backend python app/ml/train.py
```

### Kubernetes Deployment

Coming soon: Kubernetes manifests and Helm charts.

### Cloud Platforms

#### AWS Deployment

1. **ECS/Fargate:**
- Use provided Dockerfile
- Configure RDS for PostgreSQL
- Use ElastiCache for Redis
- Deploy Qdrant on EC2 or ECS

2. **Environment:**
- Store secrets in AWS Secrets Manager
- Use Application Load Balancer
- Configure CloudWatch for monitoring

#### Google Cloud Platform

1. **Cloud Run:**
```bash
gcloud run deploy phishguard-backend \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

2. **Cloud SQL:**
- Create PostgreSQL instance
- Configure connection via Cloud SQL Proxy

#### Azure Deployment

1. **Container Instances:**
- Deploy using Azure Container Registry
- Use Azure Database for PostgreSQL
- Configure Azure Cache for Redis

## Database Migrations

### Create New Migration
```bash
cd backend
alembic revision --autogenerate -m "description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

## ML Model Updates

### Retrain Model
```bash
python backend/app/ml/train.py
```

### Deploy New Model
1. Train model locally or in CI/CD
2. Copy `lightgbm_model.txt` to production
3. Restart backend service

## Monitoring

### Prometheus Metrics

Available at `/metrics`:
- Request count and latency
- ML inference time
- Database query performance
- Cache hit rates

### Grafana Dashboards

Import provided dashboards:
- API Performance
- ML Model Metrics
- Database Statistics
- System Resources

### Loki Logs

Query logs in Grafana:
```logql
{job="phishguard-backend"} |= "error"
```

## Backup & Recovery

### Database Backup
```bash
docker-compose exec postgres pg_dump -U phishguard phishguard > backup.sql
```

### Database Restore
```bash
docker-compose exec -T postgres psql -U phishguard phishguard < backup.sql
```

### Qdrant Backup
```bash
docker-compose exec qdrant tar -czf /qdrant/storage/backup.tar.gz /qdrant/storage
```

## Security Checklist

- [ ] Change default passwords
- [ ] Configure HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Rotate API keys regularly
- [ ] Enable audit logging
- [ ] Set up intrusion detection
- [ ] Configure backup encryption
- [ ] Implement secrets management

## Performance Tuning

### Backend
- Adjust worker count: `--workers 4`
- Configure connection pooling
- Enable Redis caching
- Optimize database indexes

### Database
- Tune PostgreSQL settings
- Set up read replicas
- Configure connection pooling
- Enable query caching

### Qdrant
- Adjust vector dimensions
- Configure HNSW parameters
- Set up sharding for scale

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Verify database connection
docker-compose exec backend python -c "from app.db import engine; engine.connect()"
```

### ML model not loading
```bash
# Check model file exists
ls -la backend/app/ml/models/

# Retrain model
make train
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U phishguard -d phishguard -c "SELECT 1"
```

## Scaling

### Horizontal Scaling
- Deploy multiple backend instances behind load balancer
- Use Redis for session storage
- Configure database read replicas
- Shard Qdrant collections

### Vertical Scaling
- Increase container resources
- Optimize ML model size
- Use GPU for BERT inference
- Tune database parameters

## CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push
        run: |
          docker build -t phishguard:latest .
          docker push phishguard:latest
      - name: Deploy
        run: |
          kubectl apply -f k8s/
```

## Support

For deployment issues:
- Check logs: `docker-compose logs -f`
- Review documentation
- Open GitHub issue
- Contact support team
