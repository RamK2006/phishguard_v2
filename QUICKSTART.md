# PhishGuard Quick Start Guide

Get PhishGuard up and running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- 8GB RAM minimum
- 10GB free disk space

## Quick Start (Docker)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/phishguard.git
cd phishguard
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
# Required
CLERK_SECRET_KEY=sk_test_your_key_here
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
EXTENSION_API_KEY=your-secure-random-key

# Optional (for full functionality)
VIRUSTOTAL_API_KEY=your_virustotal_key
ABUSEIPDB_API_KEY=your_abuseipdb_key
GROQ_API_KEY=your_groq_key
```

### 3. Start Services
```bash
make dev
```

This starts all 8 services:
- ✅ Backend API (http://localhost:8000)
- ✅ Dashboard (http://localhost:3000)
- ✅ PostgreSQL
- ✅ Redis
- ✅ Qdrant
- ✅ Prometheus
- ✅ Grafana
- ✅ Loki

### 4. Initialize Database
```bash
make migrate
```

### 5. Train ML Model
```bash
make train
```

This downloads datasets and trains the model (~5-10 minutes).

### 6. Access Services

- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

## Test the API

### Scan a URL
```bash
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-extension-api-key" \
  -d '{
    "url": "https://google.com"
  }'
```

Expected response:
```json
{
  "scan_id": "uuid",
  "url": "https://google.com",
  "is_phishing": false,
  "phishing_score": 0.05,
  "confidence": 0.95,
  "recommendation": "✅ SAFE - This URL appears to be legitimate."
}
```

## Install Chrome Extension

### 1. Build Extension
```bash
cd extension
npm install
npm run build
```

### 2. Load in Chrome
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select `extension/.output/chrome-mv3` directory

### 3. Configure Extension
1. Click the PhishGuard icon
2. Extension will automatically scan pages you visit

## Access Dashboard

### 1. Sign Up
1. Go to http://localhost:3000
2. Click "Sign In"
3. Create account with Clerk

### 2. View Analytics
- Total scans
- Phishing detected
- Scan history charts
- Top domains

## Common Commands

```bash
# Start services
make dev

# Stop services
make stop

# View logs
make logs

# Run migrations
make migrate

# Train model
make train

# Run tests
make test

# Clean up
make clean
```

## Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs backend
```

### Database connection error
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check connection
docker-compose exec postgres psql -U phishguard -d phishguard -c "SELECT 1"
```

### ML model not loading
```bash
# Check model file exists
ls -la backend/app/ml/models/

# Retrain model
make train
```

### Port already in use
```bash
# Change ports in docker-compose.yml
# Or stop conflicting services
lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
```

## Next Steps

1. **Read Documentation**
   - [README.md](README.md) - Full documentation
   - [API.md](API.md) - API reference
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

2. **Customize Configuration**
   - Adjust ML model parameters
   - Configure threat intelligence APIs
   - Set up monitoring alerts

3. **Deploy to Production**
   - Use `docker-compose.prod.yml`
   - Configure HTTPS/TLS
   - Set up backups

4. **Contribute**
   - See [CONTRIBUTING.md](CONTRIBUTING.md)
   - Report issues on GitHub
   - Submit pull requests

## Getting API Keys

### Clerk (Required)
1. Go to https://clerk.com
2. Create account
3. Create new application
4. Copy API keys from dashboard

### VirusTotal (Optional)
1. Go to https://www.virustotal.com
2. Sign up for free account
3. Get API key from profile

### AbuseIPDB (Optional)
1. Go to https://www.abuseipdb.com
2. Create account
3. Get API key from account settings

### Groq (Optional)
1. Go to https://groq.com
2. Sign up for API access
3. Get API key from console

## Support

- **GitHub Issues**: https://github.com/RamK2006/phishguard/issues


## Quick Reference

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Dashboard | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Qdrant | 6333 | http://localhost:6333 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3001 | http://localhost:3001 |
| Loki | 3100 | http://localhost:3100 |

---

**You're all set! Start protecting yourself from phishing attacks! 🛡️**
