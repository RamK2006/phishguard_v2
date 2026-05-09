from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from ...db import get_db, User, ScanEvent
from ...core.security import get_current_user

router = APIRouter()


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str]
    total_scans: int
    phishing_detected: int
    safe_sites: int
    created_at: datetime
    last_scan_at: Optional[datetime]


class UserStatsResponse(BaseModel):
    total_scans: int
    phishing_detected: int
    safe_sites: int
    scans_last_7_days: int
    scans_last_30_days: int
    top_domains: List[dict]
    scan_history: List[dict]


@router.get("/users/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """Get current user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        total_scans=user.total_scans,
        phishing_detected=user.phishing_detected,
        safe_sites=user.safe_sites,
        created_at=user.created_at,
        last_scan_at=user.last_scan_at
    )


@router.get("/users/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """Get user statistics"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate time-based stats
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    
    scans_last_7_days = db.query(ScanEvent).filter(
        ScanEvent.user_id == user_id,
        ScanEvent.created_at >= seven_days_ago
    ).count()
    
    scans_last_30_days = db.query(ScanEvent).filter(
        ScanEvent.user_id == user_id,
        ScanEvent.created_at >= thirty_days_ago
    ).count()
    
    # Top domains
    top_domains_query = db.query(
        ScanEvent.domain,
        func.count(ScanEvent.id).label('count')
    ).filter(
        ScanEvent.user_id == user_id
    ).group_by(
        ScanEvent.domain
    ).order_by(
        desc('count')
    ).limit(10).all()
    
    top_domains = [
        {'domain': domain, 'count': count}
        for domain, count in top_domains_query
    ]
    
    # Scan history (last 30 days, grouped by day)
    scan_history_query = db.query(
        func.date(ScanEvent.created_at).label('date'),
        func.count(ScanEvent.id).label('count'),
        func.sum(func.cast(ScanEvent.is_phishing, db.Integer)).label('phishing_count')
    ).filter(
        ScanEvent.user_id == user_id,
        ScanEvent.created_at >= thirty_days_ago
    ).group_by(
        func.date(ScanEvent.created_at)
    ).order_by(
        'date'
    ).all()
    
    scan_history = [
        {
            'date': date.isoformat(),
            'total_scans': count,
            'phishing_detected': phishing_count or 0
        }
        for date, count, phishing_count in scan_history_query
    ]
    
    return UserStatsResponse(
        total_scans=user.total_scans,
        phishing_detected=user.phishing_detected,
        safe_sites=user.safe_sites,
        scans_last_7_days=scans_last_7_days,
        scans_last_30_days=scans_last_30_days,
        top_domains=top_domains,
        scan_history=scan_history
    )


@router.get("/users/me/scans")
async def get_user_scans(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """Get user's scan history"""
    scans = db.query(ScanEvent).filter(
        ScanEvent.user_id == user_id
    ).order_by(
        desc(ScanEvent.created_at)
    ).offset(offset).limit(limit).all()
    
    return {
        'total': db.query(ScanEvent).filter(ScanEvent.user_id == user_id).count(),
        'scans': [
            {
                'scan_id': scan.id,
                'url': scan.url,
                'domain': scan.domain,
                'is_phishing': scan.is_phishing,
                'phishing_score': scan.phishing_score,
                'confidence': scan.confidence,
                'created_at': scan.created_at.isoformat()
            }
            for scan in scans
        ]
    }


@router.put("/users/me/preferences")
async def update_user_preferences(
    preferences: dict,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """Update user preferences"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.preferences = preferences
    db.commit()
    
    return {'message': 'Preferences updated successfully', 'preferences': preferences}
