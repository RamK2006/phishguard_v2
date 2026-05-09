from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from ...db import get_db, Feedback, ScanEvent, User
from ...core.security import verify_extension_key, get_current_user, verify_token

router = APIRouter()


class FeedbackRequest(BaseModel):
    scan_id: str
    is_correct: bool
    actual_label: str  # 'phishing' or 'safe'
    comment: Optional[str] = None
    reported_issues: Optional[dict] = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    scan_id: str
    is_correct: bool
    message: str


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    api_key_valid: bool = Depends(verify_extension_key)
):
    """Submit feedback on scan result (anonymous from extension)"""
    # Validate scan exists
    scan = db.query(ScanEvent).filter(ScanEvent.id == request.scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Validate actual_label
    if request.actual_label not in ['phishing', 'safe']:
        raise HTTPException(
            status_code=400,
            detail="actual_label must be 'phishing' or 'safe'"
        )
    
    # Create feedback
    feedback_id = str(uuid.uuid4())
    predicted_label = 'phishing' if scan.is_phishing else 'safe'
    
    feedback = Feedback(
        id=feedback_id,
        scan_id=request.scan_id,
        user_id=None,  # Anonymous from extension
        is_correct=request.is_correct,
        actual_label=request.actual_label,
        predicted_label=predicted_label,
        comment=request.comment,
        reported_issues=request.reported_issues
    )
    
    db.add(feedback)
    db.commit()
    
    return FeedbackResponse(
        feedback_id=feedback_id,
        scan_id=request.scan_id,
        is_correct=request.is_correct,
        message="Thank you for your feedback! This helps improve our detection accuracy."
    )


@router.post("/feedback/authenticated", response_model=FeedbackResponse)
async def submit_authenticated_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """Submit feedback on scan result (authenticated user)"""
    # Validate scan exists
    scan = db.query(ScanEvent).filter(ScanEvent.id == request.scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Validate actual_label
    if request.actual_label not in ['phishing', 'safe']:
        raise HTTPException(
            status_code=400,
            detail="actual_label must be 'phishing' or 'safe'"
        )
    
    # Create feedback
    feedback_id = str(uuid.uuid4())
    predicted_label = 'phishing' if scan.is_phishing else 'safe'
    
    feedback = Feedback(
        id=feedback_id,
        scan_id=request.scan_id,
        user_id=user_id,
        is_correct=request.is_correct,
        actual_label=request.actual_label,
        predicted_label=predicted_label,
        comment=request.comment,
        reported_issues=request.reported_issues
    )
    
    db.add(feedback)
    db.commit()
    
    return FeedbackResponse(
        feedback_id=feedback_id,
        scan_id=request.scan_id,
        is_correct=request.is_correct,
        message="Thank you for your feedback! This helps improve our detection accuracy."
    )


@router.get("/feedback/stats")
async def get_feedback_stats(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    """Get feedback statistics"""
    total_feedback = db.query(Feedback).count()
    correct_predictions = db.query(Feedback).filter(Feedback.is_correct == True).count()
    incorrect_predictions = db.query(Feedback).filter(Feedback.is_correct == False).count()
    
    # False positives (predicted phishing, actually safe)
    false_positives = db.query(Feedback).filter(
        Feedback.predicted_label == 'phishing',
        Feedback.actual_label == 'safe'
    ).count()
    
    # False negatives (predicted safe, actually phishing)
    false_negatives = db.query(Feedback).filter(
        Feedback.predicted_label == 'safe',
        Feedback.actual_label == 'phishing'
    ).count()
    
    accuracy = (correct_predictions / total_feedback * 100) if total_feedback > 0 else 0
    
    return {
        'total_feedback': total_feedback,
        'correct_predictions': correct_predictions,
        'incorrect_predictions': incorrect_predictions,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'accuracy_percentage': round(accuracy, 2)
    }
