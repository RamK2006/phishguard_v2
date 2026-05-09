# PhishGuard API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

### Extension API Key
For Chrome extension requests:
```
X-API-Key: your-extension-api-key
```

### User Authentication (Clerk JWT)
For dashboard/authenticated requests:
```
Authorization: Bearer <clerk-jwt-token>
```

## Endpoints

### 1. Scan URL

Scan a URL for phishing indicators.

**Endpoint:** `POST /scan`

**Headers:**
- `Content-Type: application/json`
- `X-API-Key: <extension-api-key>`

**Request Body:**
```json
{
  "url": "https://example.com",
  "user_agent": "Mozilla/5.0...",
  "screenshot_url": "https://..." // optional
}
```

**Response:** `200 OK`
```json
{
  "scan_id": "uuid",
  "url": "https://example.com",
  "is_phishing": false,
  "phishing_score": 0.15,
  "confidence": 0.85,
  "explanation": "This URL appears safe based on multiple factors...",
  "risk_factors": [
    {
      "category": "URL Structure",
      "risk": "Long URL",
      "severity": "low",
      "description": "URL is longer than average"
    }
  ],
  "recommendation": "✅ SAFE - This URL appears to be legitimate.",
  "scan_duration_ms": 1250,
  "threat_intel_summary": {
    "aggregate_score": 5.2,
    "virustotal_flagged": false,
    "urlhaus_listed": false,
    "abuseipdb_flagged": false
  },
  "visual_similarity_summary": {
    "has_match": false,
    "matched_brand": null,
    "similarity_score": 0
  }
}
```

### 2. Get Scan Result

Retrieve a previous scan result by ID.

**Endpoint:** `GET /scan/{scan_id}`

**Headers:**
- `X-API-Key: <extension-api-key>`

**Response:** `200 OK`
```json
{
  "scan_id": "uuid",
  "url": "https://example.com",
  "is_phishing": false,
  "phishing_score": 0.15,
  "confidence": 0.85,
  "explanation": "...",
  "risk_factors": [...],
  "threat_intel": {...},
  "visual_similarity": {...},
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 3. Submit Feedback

Submit feedback on a scan result.

**Endpoint:** `POST /feedback`

**Headers:**
- `Content-Type: application/json`
- `X-API-Key: <extension-api-key>`

**Request Body:**
```json
{
  "scan_id": "uuid",
  "is_correct": true,
  "actual_label": "safe",
  "comment": "This was correctly identified",
  "reported_issues": {}
}
```

**Response:** `200 OK`
```json
{
  "feedback_id": "uuid",
  "scan_id": "uuid",
  "is_correct": true,
  "message": "Thank you for your feedback!"
}
```

### 4. Create Threat Report

Report a phishing/malware URL (authenticated).

**Endpoint:** `POST /reports`

**Headers:**
- `Content-Type: application/json`
- `Authorization: Bearer <clerk-jwt>`

**Request Body:**
```json
{
  "url": "https://phishing-site.com",
  "report_type": "phishing",
  "description": "Impersonating PayPal login page",
  "evidence": {
    "screenshot": "...",
    "additional_info": "..."
  }
}
```

**Response:** `200 OK`
```json
{
  "report_id": "uuid",
  "url": "https://phishing-site.com",
  "domain": "phishing-site.com",
  "report_type": "phishing",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 5. List Reports

Get user's threat reports (authenticated).

**Endpoint:** `GET /reports`

**Headers:**
- `Authorization: Bearer <clerk-jwt>`

**Query Parameters:**
- `status` (optional): Filter by status (pending, verified, false_positive)
- `report_type` (optional): Filter by type (phishing, malware, scam)
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
[
  {
    "report_id": "uuid",
    "url": "https://phishing-site.com",
    "domain": "phishing-site.com",
    "report_type": "phishing",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### 6. Get User Profile

Get current user profile (authenticated).

**Endpoint:** `GET /users/me`

**Headers:**
- `Authorization: Bearer <clerk-jwt>`

**Response:** `200 OK`
```json
{
  "user_id": "clerk-user-id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "total_scans": 150,
  "phishing_detected": 12,
  "safe_sites": 138,
  "created_at": "2024-01-01T00:00:00Z",
  "last_scan_at": "2024-01-15T12:00:00Z"
}
```

### 7. Get User Statistics

Get detailed user statistics (authenticated).

**Endpoint:** `GET /users/me/stats`

**Headers:**
- `Authorization: Bearer <clerk-jwt>`

**Response:** `200 OK`
```json
{
  "total_scans": 150,
  "phishing_detected": 12,
  "safe_sites": 138,
  "scans_last_7_days": 25,
  "scans_last_30_days": 89,
  "top_domains": [
    {
      "domain": "google.com",
      "count": 45
    }
  ],
  "scan_history": [
    {
      "date": "2024-01-15",
      "total_scans": 8,
      "phishing_detected": 1
    }
  ]
}
```

### 8. Health Check

Check API health status.

**Endpoint:** `GET /health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": 1704067200.0
}
```

### 9. Detailed Health Check

Get detailed service health status.

**Endpoint:** `GET /health/detailed`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": 1704067200.0,
  "services": {
    "database": {
      "status": "healthy"
    },
    "lightgbm": {
      "status": "healthy"
    },
    "bert": {
      "status": "healthy"
    }
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- Extension API: 100 requests per minute per API key
- User API: 1000 requests per hour per user

## Webhooks

Coming soon: Real-time notifications for threat reports and scan results.
