from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ...db import get_db
from ...services import ml_service
import time

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        'status': 'healthy',
        'timestamp': time.time()
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with service status"""
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {}
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status['services']['database'] = {'status': 'healthy'}
    except Exception as e:
        health_status['services']['database'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'degraded'
    
    # Check ML models
    try:
        if ml_service.lgb_model:
            health_status['services']['lightgbm'] = {'status': 'healthy'}
        else:
            health_status['services']['lightgbm'] = {'status': 'not_loaded'}
            health_status['status'] = 'degraded'
        
        if ml_service.bert_model:
            health_status['services']['bert'] = {'status': 'healthy'}
        else:
            health_status['services']['bert'] = {'status': 'not_loaded'}
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['services']['ml'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'degraded'
    
    return health_status


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        db.execute(text("SELECT 1"))
        return {'ready': True}
    except Exception:
        return {'ready': False}


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {'alive': True}
