# PhishGuard Testing Guide

Comprehensive testing documentation for PhishGuard.

## Testing Strategy

PhishGuard uses a multi-layered testing approach:
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API endpoint testing
3. **End-to-End Tests**: Full workflow testing
4. **Performance Tests**: Load and stress testing
5. **Security Tests**: Vulnerability scanning

## Backend Testing

### Setup Test Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Specific Tests

```bash
# Run specific file
pytest tests/test_feature_extractor.py

# Run specific test
pytest tests/test_feature_extractor.py::test_url_length

# Run by marker
pytest -m unit
pytest -m integration
pytest -m slow
```

### Test Structure

```
backend/tests/
├── conftest.py                 # Pytest fixtures
├── test_api/
│   ├── test_scan.py           # Scan endpoint tests
│   ├── test_reports.py        # Reports endpoint tests
│   ├── test_feedback.py       # Feedback endpoint tests
│   └── test_users.py          # Users endpoint tests
├── test_services/
│   ├── test_feature_extractor.py
│   ├── test_ml_inference.py
│   ├── test_threat_intel.py
│   └── test_llm_explainer.py
├── test_db/
│   └── test_models.py         # Database model tests
└── test_ml/
    └── test_training.py       # ML training tests
```

### Example Unit Test

```python
# tests/test_services/test_feature_extractor.py
import pytest
from app.services.feature_extractor import URLFeatureExtractor

@pytest.fixture
def extractor():
    return URLFeatureExtractor()

def test_url_length_feature(extractor):
    features = extractor.extract_features("https://example.com")
    assert features['url_length'] == 19

def test_has_https_feature(extractor):
    features = extractor.extract_features("https://example.com")
    assert features['has_https'] == 1
    
    features = extractor.extract_features("http://example.com")
    assert features['has_https'] == 0

def test_suspicious_keywords(extractor):
    features = extractor.extract_features("https://paypal-login-verify.com")
    assert features['has_suspicious_keywords'] == 1
```

### Example Integration Test

```python
# tests/test_api/test_scan.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_scan_url_success(client):
    response = client.post(
        "/api/v1/scan",
        json={"url": "https://google.com"},
        headers={"X-API-Key": "test-api-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert "is_phishing" in data
    assert "phishing_score" in data

def test_scan_url_invalid_key(client):
    response = client.post(
        "/api/v1/scan",
        json={"url": "https://google.com"},
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 401
```

### Mocking External APIs

```python
# tests/test_services/test_threat_intel.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.threat_intel import ThreatIntelService

@pytest.mark.asyncio
async def test_virustotal_check():
    service = ThreatIntelService()
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'data': {'id': 'test-id'}
        }
        
        result = await service._check_virustotal("https://example.com")
        assert result['available'] == True
```

## Frontend Testing

### Dashboard Tests

```bash
cd dashboard
npm install
npm test
```

### Run with Coverage

```bash
npm test -- --coverage
```

### Example Component Test

```typescript
// dashboard/__tests__/Dashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '@/app/dashboard/page';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

test('renders dashboard title', () => {
  render(
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
  
  expect(screen.getByText('PhishGuard Dashboard')).toBeInTheDocument();
});

test('displays user statistics', async () => {
  render(
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
  
  await waitFor(() => {
    expect(screen.getByText('Total Scans')).toBeInTheDocument();
  });
});
```

### Extension Tests

```bash
cd extension
npm install
npm test
```

## Performance Testing

### Load Testing with Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class PhishGuardUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def scan_url(self):
        self.client.post(
            "/api/v1/scan",
            json={"url": "https://example.com"},
            headers={"X-API-Key": "test-api-key"}
        )
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

### Benchmark ML Inference

```python
# tests/test_performance.py
import time
import pytest
from app.services.ml_inference import ml_service
from app.services.feature_extractor import URLFeatureExtractor

def test_inference_speed():
    extractor = URLFeatureExtractor()
    features = extractor.extract_features("https://example.com")
    
    start = time.time()
    for _ in range(100):
        ml_service.predict("https://example.com", features)
    duration = time.time() - start
    
    avg_time = duration / 100
    assert avg_time < 0.1  # Should be under 100ms
```

## Security Testing

### Dependency Scanning

```bash
# Python dependencies
pip install safety
safety check

# Node dependencies
npm audit
```

### Container Scanning

```bash
# Scan Docker images
docker scan phishguard-backend:latest
docker scan phishguard-dashboard:latest
```

### SAST (Static Analysis)

```bash
# Python
pip install bandit
bandit -r backend/app/

# TypeScript
npm install -g eslint-plugin-security
eslint --plugin security dashboard/
```

### API Security Testing

```bash
# Install OWASP ZAP
# Run automated scan
zap-cli quick-scan http://localhost:8000
```

## Database Testing

### Test Migrations

```bash
# Create test database
createdb phishguard_test

# Run migrations
DATABASE_URL=postgresql://localhost/phishguard_test alembic upgrade head

# Rollback
DATABASE_URL=postgresql://localhost/phishguard_test alembic downgrade -1
```

### Test Database Models

```python
# tests/test_db/test_models.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, ScanEvent

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_scan_event(db_session):
    scan = ScanEvent(
        id="test-id",
        url="https://example.com",
        domain="example.com",
        phishing_score=0.1,
        is_phishing=False,
        confidence=0.9,
        url_features={},
        ml_features={},
        scan_duration_ms=100
    )
    db_session.add(scan)
    db_session.commit()
    
    retrieved = db_session.query(ScanEvent).filter_by(id="test-id").first()
    assert retrieved.url == "https://example.com"
```

## ML Model Testing

### Test Feature Extraction

```python
# tests/test_ml/test_features.py
import pytest
from app.services.feature_extractor import URLFeatureExtractor

@pytest.fixture
def extractor():
    return URLFeatureExtractor()

def test_all_features_present(extractor):
    features = extractor.extract_features("https://example.com")
    expected_features = 47
    assert len(features) == expected_features

def test_feature_ranges(extractor):
    features = extractor.extract_features("https://example.com")
    
    # Binary features should be 0 or 1
    assert features['has_https'] in [0, 1]
    assert features['has_ip_address'] in [0, 1]
    
    # Ratio features should be 0-1
    assert 0 <= features['digit_ratio'] <= 1
    assert 0 <= features['letter_ratio'] <= 1
```

### Test Model Predictions

```python
# tests/test_ml/test_inference.py
import pytest
from app.services.ml_inference import ml_service
from app.services.feature_extractor import URLFeatureExtractor

def test_safe_url_prediction():
    extractor = URLFeatureExtractor()
    features = extractor.extract_features("https://google.com")
    
    score, is_phishing, confidence, ml_features = ml_service.predict(
        "https://google.com", features
    )
    
    assert 0 <= score <= 1
    assert isinstance(is_phishing, bool)
    assert 0 <= confidence <= 1

def test_phishing_url_prediction():
    extractor = URLFeatureExtractor()
    features = extractor.extract_features("http://192.168.1.1/paypal-login.php")
    
    score, is_phishing, confidence, ml_features = ml_service.predict(
        "http://192.168.1.1/paypal-login.php", features
    )
    
    # Should detect as phishing
    assert score > 0.5
    assert is_phishing == True
```

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Push to main/develop
- Pull requests
- Scheduled (daily)

View results:
```
https://github.com/yourusername/phishguard/actions
```

### Local CI Simulation

```bash
# Run all checks locally
make test
make lint
make type-check
make security-scan
```

## Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Backend API | 90%+ |
| Services | 85%+ |
| ML Models | 80%+ |
| Database | 85%+ |
| Frontend | 75%+ |
| Extension | 70%+ |

## Best Practices

1. **Write Tests First**: TDD approach
2. **Mock External APIs**: Don't hit real APIs in tests
3. **Use Fixtures**: Reusable test data
4. **Test Edge Cases**: Not just happy paths
5. **Keep Tests Fast**: Unit tests < 1s
6. **Isolate Tests**: No dependencies between tests
7. **Clear Assertions**: One concept per test
8. **Descriptive Names**: test_should_do_something_when_condition

## Debugging Tests

### Run with Verbose Output

```bash
pytest -v
pytest -vv  # Extra verbose
```

### Run with Print Statements

```bash
pytest -s
```

### Debug with PDB

```python
def test_something():
    import pdb; pdb.set_trace()
    # Test code
```

### Run Failed Tests Only

```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

## Test Data

### Sample URLs for Testing

```python
# tests/fixtures/urls.py
SAFE_URLS = [
    "https://google.com",
    "https://github.com",
    "https://stackoverflow.com"
]

PHISHING_URLS = [
    "http://192.168.1.1/login.php",
    "http://paypal-verify.tk/signin",
    "http://apple-id-locked.xyz/unlock"
]
```

## Reporting Issues

When tests fail:
1. Check test output for error messages
2. Review logs: `docker-compose logs backend`
3. Verify environment variables
4. Check database state
5. Open GitHub issue with:
   - Test name
   - Error message
   - Steps to reproduce
   - Environment details

## Support

- **GitHub Issues**: https://github.com/RamK2006/phishguard/issues


---

**Happy Testing! 🧪**
