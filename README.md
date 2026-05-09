# 🛡️ PhishGuard

**Real-time phishing detection powered by Machine Learning, Threat Intelligence, and Visual Similarity Analysis**

PhishGuard is a comprehensive phishing detection platform that combines multiple detection techniques to protect users from phishing attacks in real-time.

## 🌟 Features

### Core Detection Engine
- **Machine Learning**: LightGBM + DistilBERT ensemble model with 47 URL features
- **Threat Intelligence**: Integration with VirusTotal, URLhaus, and AbuseIPDB
- **Visual Similarity**: Perceptual hashing with Qdrant vector database for brand impersonation detection
- **LLM Explanations**: Human-readable explanations powered by Groq API (Llama 3.1)

### Components
- **Backend API**: FastAPI-based REST API with async processing
- **Chrome Extension**: Real-time URL scanning with Manifest V3
- **Dashboard**: Next.js 15 analytics dashboard with Clerk authentication
- **ML Pipeline**: Automated training on PhishTank + Tranco datasets

### Infrastructure
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for API response caching
- **Vector DB**: Qdrant for visual similarity search
- **Monitoring**: Prometheus + Grafana + Loki stack
- **Deployment**: Docker Compose with production-ready configuration

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+ (for dashboard/extension)
- API Keys:
  - Clerk (authentication)
  - VirusTotal (optional)
  - AbuseIPDB (optional)
  - Groq API (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/phishguard.git
cd phishguard
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start services with Docker Compose**
```bash
make dev
```

This will start:
- Backend API (http://localhost:8000)
- Dashboard (http://localhost:3000)
- PostgreSQL (localhost:5432)
- Redis (localhost:6379)
- Qdrant (localhost:6333)
- Prometheus (localhost:9090)
- Grafana (localhost:3001)
- Loki (localhost:3100)

4. **Run database migrations**
```bash
make migrate
```

5. **Train ML model**
```bash
make train
```

## 📖 Documentation

### API Endpoints

#### Scan URL
```bash
POST /api/v1/scan
Content-Type: application/json
X-API-Key: your-extension-api-key

{
  "url": "https://example.com",
  "user_agent": "Mozilla/5.0...",
  "screenshot_url": "https://..."
}
```

Response:
```json
{
  "scan_id": "uuid",
  "url": "https://example.com",
  "is_phishing": false,
  "phishing_score": 0.15,
  "confidence": 0.85,
  "explanation": "This URL appears safe...",
  "risk_factors": [...],
  "recommendation": "✅ SAFE - This URL appears to be legitimate.",
  "scan_duration_ms": 1250,
  "threat_intel_summary": {...},
  "visual_similarity_summary": {...}
}
```

#### Submit Feedback
```bash
POST /api/v1/feedback
X-API-Key: your-extension-api-key

{
  "scan_id": "uuid",
  "is_correct": true,
  "actual_label": "safe",
  "comment": "This was correctly identified"
}
```

#### Create Threat Report
```bash
POST /api/v1/reports
Authorization: Bearer <clerk-jwt>

{
  "url": "https://phishing-site.com",
  "report_type": "phishing",
  "description": "Impersonating PayPal",
  "evidence": {...}
}
```

### ML Model Training

The model is trained on:
- **PhishTank**: 10,000+ confirmed phishing URLs
- **Tranco**: Top 10,000 legitimate websites

Features extracted (47 total):
- URL structure (length, entropy, character ratios)
- Domain analysis (TLD, subdomains, IP detection)
- Suspicious patterns (keywords, brand names, shorteners)
- Query parameters analysis
- Visual and textual entropy

Training command:
```bash
python backend/app/ml/train.py
```

Model performance:
- Accuracy: ~95%
- Precision: ~93%
- Recall: ~96%
- F1 Score: ~94%
- AUC-ROC: ~98%

### Chrome Extension

Build and load:
```bash
cd extension
npm install
npm run build
# Load dist/ folder in Chrome as unpacked extension
```

Features:
- Real-time URL scanning on page load
- Visual warning overlays for phishing sites
- One-click feedback submission
- Scan history and statistics

### Dashboard

Access at http://localhost:3000

Features:
- Scan history and analytics
- Threat reports management
- User statistics and trends
- Real-time monitoring
- Feedback submission

## 🏗️ Architecture

```
┌─────────────────┐
│ Chrome Extension│
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│   FastAPI       │────▶│  PostgreSQL  │
│   Backend       │     └──────────────┘
└────────┬────────┘
         │
         ├──────▶ Redis (Cache)
         │
         ├──────▶ Qdrant (Vectors)
         │
         ├──────▶ VirusTotal API
         │
         ├──────▶ URLhaus API
         │
         ├──────▶ AbuseIPDB API
         │
         └──────▶ Groq API (LLM)

┌─────────────────┐
│  Next.js        │
│  Dashboard      │
└─────────────────┘
```

## 🛠️ Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run Tests
```bash
make test
```

### Lint Code
```bash
make lint
```

### Build for Production
```bash
make build
```

## 📊 Monitoring

Access monitoring dashboards:
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API Docs**: http://localhost:8000/docs

Metrics tracked:
- Request latency and throughput
- ML inference time
- Threat intelligence API response times
- Database query performance
- Error rates and types

## 🔒 Security

- API authentication via Clerk JWT tokens
- Extension API key validation
- Rate limiting on all endpoints
- SQL injection prevention via SQLAlchemy ORM
- XSS protection in dashboard
- CORS configuration
- Secure password hashing (if applicable)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PhishTank for phishing URL dataset
- Tranco for legitimate URL rankings
- VirusTotal, URLhaus, AbuseIPDB for threat intelligence
- Groq for LLM API access
- Clerk for authentication

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for a safer internet**
