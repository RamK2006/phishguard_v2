from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import Optional
import time
import uuid
import tldextract

from ...db import get_db, ScanEvent, User
from ...core.security import verify_extension_key, get_current_user
from ...services import (
    URLFeatureExtractor,
    ml_service,
    threat_intel_service,
    visual_similarity_service,
    llm_explainer_service
)

router = APIRouter()


class ScanRequest(BaseModel):
    url: HttpUrl
    user_agent: Optional[str] = None
    screenshot_url: Optional[str] = None


class ScanResponse(BaseModel):
    scan_id: str
    url: str
    is_phishing: bool
    phishing_score: float
    confidence: float
    explanation: Optional[str] = None
    risk_factors: Optional[list] = None
    recommendation: Optional[str] = None
    scan_duration_ms: int
    threat_intel_summary: dict
    visual_similarity_summary: dict


@router.post("/scan", response_model=ScanResponse)
async def scan_url(
    request: ScanRequest,
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_extension_key),
    x_forwarded_for: Optional[str] = Header(None)
):
    """Scan URL for phishing"""
    start_time = time.time()
    
    url = str(request.url)
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    
    # Extract URL features
    feature_extractor = URLFeatureExtractor()
    url_features = feature_extractor.extract_features(url)
    
    # ML prediction
    phishing_score, is_phishing, confidence, ml_features = ml_service.predict(url, url_features)
    
    # Threat intelligence check (async)
    threat_intel = await threat_intel_service.check_url(url, domain)
    
    # Visual similarity check (async)
    visual_similarity = await visual_similarity_service.check_visual_similarity(
        url, request.screenshot_url
    )
    
    # LLM explanation (async)
    llm_result = await llm_explainer_service.generate_explanation(
        url, phishing_score, is_phishing, url_features, threat_intel, visual_similarity
    )
    
    # Calculate scan duration
    scan_duration_ms = int((time.time() - start_time) * 1000)
    
    # Create scan event
    scan_id = str(uuid.uuid4())
    scan_event = ScanEvent(
        id=scan_id,
        user_id=None,  # Extension scans are anonymous
        url=url,
        domain=domain,
        phishing_score=phishing_score,
        is_phishing=is_phishing,
        confidence=confidence,
        url_features=url_features,
        ml_features=ml_features,
        threat_intel=threat_intel,
        virustotal_score=threat_intel.get('virustotal', {}).get('score'),
        urlhaus_listed=threat_intel.get('urlhaus', {}).get('listed'),
        abuseipdb_score=threat_intel.get('abuseipdb', {}).get('abuse_score'),
        visual_similarity=visual_similarity,
        matched_brand=visual_similarity.get('matched_brand'),
        similarity_score=visual_similarity.get('similarity_score'),
        explanation=llm_result.get('explanation'),
        risk_factors=llm_result.get('risk_factors'),
        scan_duration_ms=scan_duration_ms,
        user_agent=request.user_agent,
        ip_address=x_forwarded_for
    )
    
    db.add(scan_event)
    db.commit()
    
    # Prepare response
    threat_intel_summary = {
        'aggregate_score': threat_intel.get('aggregate_score', 0),
        'virustotal_flagged': threat_intel.get('virustotal', {}).get('is_malicious', False),
        'urlhaus_listed': threat_intel.get('urlhaus', {}).get('listed', False),
        'abuseipdb_flagged': threat_intel.get('abuseipdb', {}).get('is_malicious', False)
    }
    
    visual_similarity_summary = {
        'has_match': visual_similarity.get('has_match', False),
        'matched_brand': visual_similarity.get('matched_brand'),
        'similarity_score': visual_similarity.get('similarity_score', 0)
    }
    
    return ScanResponse(
        scan_id=scan_id,
        url=url,
        is_phishing=is_phishing,
        phishing_score=phishing_score,
        confidence=confidence,
        explanation=llm_result.get('explanation'),
        risk_factors=llm_result.get('risk_factors'),
        recommendation=llm_result.get('recommendation'),
        scan_duration_ms=scan_duration_ms,
        threat_intel_summary=threat_intel_summary,
        visual_similarity_summary=visual_similarity_summary
    )


@router.get("/scan/{scan_id}")
async def get_scan_result(
    scan_id: str,
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_extension_key)
):
    """Get scan result by ID"""
    scan = db.query(ScanEvent).filter(ScanEvent.id == scan_id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {
        'scan_id': scan.id,
        'url': scan.url,
        'is_phishing': scan.is_phishing,
        'phishing_score': scan.phishing_score,
        'confidence': scan.confidence,
        'explanation': scan.explanation,
        'risk_factors': scan.risk_factors,
        'threat_intel': scan.threat_intel,
        'visual_similarity': scan.visual_similarity,
        'created_at': scan.created_at.isoformat()
    }
