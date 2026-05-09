from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class ScanEvent(Base):
    __tablename__ = "scan_events"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True, index=True)
    url = Column(Text, nullable=False)
    domain = Column(String, nullable=False, index=True)
    
    # ML Predictions
    phishing_score = Column(Float, nullable=False)
    is_phishing = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Feature Scores
    url_features = Column(JSON, nullable=False)
    ml_features = Column(JSON, nullable=False)
    
    # Threat Intelligence
    threat_intel = Column(JSON, nullable=True)
    virustotal_score = Column(Integer, nullable=True)
    urlhaus_listed = Column(Boolean, nullable=True)
    abuseipdb_score = Column(Integer, nullable=True)
    
    # Visual Similarity
    visual_similarity = Column(JSON, nullable=True)
    matched_brand = Column(String, nullable=True)
    similarity_score = Column(Float, nullable=True)
    
    # LLM Explanation
    explanation = Column(Text, nullable=True)
    risk_factors = Column(JSON, nullable=True)
    
    # Metadata
    scan_duration_ms = Column(Integer, nullable=False)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_scan_events_created_at', 'created_at'),
        Index('idx_scan_events_is_phishing', 'is_phishing'),
        Index('idx_scan_events_user_created', 'user_id', 'created_at'),
    )


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # Clerk user ID
    email = Column(String, nullable=False, unique=True, index=True)
    full_name = Column(String, nullable=True)
    
    # Statistics
    total_scans = Column(Integer, default=0, nullable=False)
    phishing_detected = Column(Integer, default=0, nullable=False)
    safe_sites = Column(Integer, default=0, nullable=False)
    
    # Preferences
    preferences = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_scan_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_users_email', 'email'),
    )


class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(String, primary_key=True)
    scan_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    
    # Feedback
    is_correct = Column(Boolean, nullable=False)
    actual_label = Column(String, nullable=False)  # 'phishing' or 'safe'
    predicted_label = Column(String, nullable=False)
    
    # Additional Info
    comment = Column(Text, nullable=True)
    reported_issues = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_feedback_scan_id', 'scan_id'),
        Index('idx_feedback_created_at', 'created_at'),
    )


class ThreatReport(Base):
    __tablename__ = "threat_reports"
    
    id = Column(String, primary_key=True)
    url = Column(Text, nullable=False)
    domain = Column(String, nullable=False, index=True)
    
    # Report Details
    reported_by = Column(String, nullable=True)
    report_type = Column(String, nullable=False)  # 'phishing', 'malware', 'scam'
    description = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=True)
    
    # Status
    status = Column(String, default='pending', nullable=False)  # 'pending', 'verified', 'false_positive'
    verified_by = Column(String, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Threat Intelligence
    threat_score = Column(Float, nullable=True)
    threat_tags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    __table_args__ = (
        Index('idx_threat_reports_domain', 'domain'),
        Index('idx_threat_reports_status', 'status'),
        Index('idx_threat_reports_created_at', 'created_at'),
    )
