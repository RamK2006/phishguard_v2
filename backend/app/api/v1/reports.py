from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import tldextract

from ...db import get_db, ThreatReport
from ...core.security import verify_token, get_current_user

router = APIRouter()


class ReportRequest(BaseModel):
    url: HttpUrl
    report_type: str  # 'phishing', 'malware', 'scam'
    description: Optional[str] = None
    evidence: Optional[dict] = None


class ReportResponse(BaseModel):
    report_id: str
    url: str
    domain: str
    report_type: str
    status: str
    created_at: datetime


@router.post("/reports", response_model=ReportResponse)
async def create_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """Create a new threat report"""
    url = str(request.url)
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    
    # Validate report type
    valid_types = ['phishing', 'malware', 'scam']
    if request.report_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Create report
    report_id = str(uuid.uuid4())
    report = ThreatReport(
        id=report_id,
        url=url,
        domain=domain,
        reported_by=user_id,
        report_type=request.report_type,
        description=request.description,
        evidence=request.evidence,
        status='pending'
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return ReportResponse(
        report_id=report.id,
        url=report.url,
        domain=report.domain,
        report_type=report.report_type,
        status=report.status,
        created_at=report.created_at
    )


@router.get("/reports", response_model=List[ReportResponse])
async def list_reports(
    status: Optional[str] = Query(None, description="Filter by status"),
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """List threat reports"""
    query = db.query(ThreatReport).filter(ThreatReport.reported_by == user_id)
    
    if status:
        query = query.filter(ThreatReport.status == status)
    
    if report_type:
        query = query.filter(ThreatReport.report_type == report_type)
    
    reports = query.order_by(desc(ThreatReport.created_at)).offset(offset).limit(limit).all()
    
    return [
        ReportResponse(
            report_id=r.id,
            url=r.url,
            domain=r.domain,
            report_type=r.report_type,
            status=r.status,
            created_at=r.created_at
        )
        for r in reports
    ]


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """Get report details"""
    report = db.query(ThreatReport).filter(
        ThreatReport.id == report_id,
        ThreatReport.reported_by == user_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        'report_id': report.id,
        'url': report.url,
        'domain': report.domain,
        'report_type': report.report_type,
        'description': report.description,
        'evidence': report.evidence,
        'status': report.status,
        'threat_score': report.threat_score,
        'threat_tags': report.threat_tags,
        'created_at': report.created_at.isoformat(),
        'updated_at': report.updated_at.isoformat() if report.updated_at else None,
        'verified_at': report.verified_at.isoformat() if report.verified_at else None
    }


@router.get("/reports/domain/{domain}")
async def get_domain_reports(
    domain: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """Get all reports for a specific domain"""
    reports = db.query(ThreatReport).filter(
        ThreatReport.domain == domain
    ).order_by(desc(ThreatReport.created_at)).all()
    
    return {
        'domain': domain,
        'total_reports': len(reports),
        'reports': [
            {
                'report_id': r.id,
                'url': r.url,
                'report_type': r.report_type,
                'status': r.status,
                'created_at': r.created_at.isoformat()
            }
            for r in reports
        ]
    }
