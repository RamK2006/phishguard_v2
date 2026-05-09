"""initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create scan_events table
    op.create_table(
        'scan_events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('phishing_score', sa.Float(), nullable=False),
        sa.Column('is_phishing', sa.Boolean(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('url_features', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('ml_features', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('threat_intel', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('virustotal_score', sa.Integer(), nullable=True),
        sa.Column('urlhaus_listed', sa.Boolean(), nullable=True),
        sa.Column('abuseipdb_score', sa.Integer(), nullable=True),
        sa.Column('visual_similarity', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('matched_brand', sa.String(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('risk_factors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('scan_duration_ms', sa.Integer(), nullable=False),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scan_events_created_at', 'scan_events', ['created_at'])
    op.create_index('idx_scan_events_domain', 'scan_events', ['domain'])
    op.create_index('idx_scan_events_is_phishing', 'scan_events', ['is_phishing'])
    op.create_index('idx_scan_events_user_created', 'scan_events', ['user_id', 'created_at'])
    op.create_index('idx_scan_events_user_id', 'scan_events', ['user_id'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('total_scans', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('phishing_detected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('safe_sites', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_scan_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('scan_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('actual_label', sa.String(), nullable=False),
        sa.Column('predicted_label', sa.String(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('reported_issues', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_feedback_created_at', 'feedback', ['created_at'])
    op.create_index('idx_feedback_scan_id', 'feedback', ['scan_id'])
    op.create_index('idx_feedback_user_id', 'feedback', ['user_id'])

    # Create threat_reports table
    op.create_table(
        'threat_reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(), nullable=False),
        sa.Column('reported_by', sa.String(), nullable=True),
        sa.Column('report_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('evidence', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('verified_by', sa.String(), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('threat_score', sa.Float(), nullable=True),
        sa.Column('threat_tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_threat_reports_created_at', 'threat_reports', ['created_at'])
    op.create_index('idx_threat_reports_domain', 'threat_reports', ['domain'])
    op.create_index('idx_threat_reports_status', 'threat_reports', ['status'])


def downgrade() -> None:
    op.drop_index('idx_threat_reports_status', table_name='threat_reports')
    op.drop_index('idx_threat_reports_domain', table_name='threat_reports')
    op.drop_index('idx_threat_reports_created_at', table_name='threat_reports')
    op.drop_table('threat_reports')
    
    op.drop_index('idx_feedback_user_id', table_name='feedback')
    op.drop_index('idx_feedback_scan_id', table_name='feedback')
    op.drop_index('idx_feedback_created_at', table_name='feedback')
    op.drop_table('feedback')
    
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
    
    op.drop_index('idx_scan_events_user_id', table_name='scan_events')
    op.drop_index('idx_scan_events_user_created', table_name='scan_events')
    op.drop_index('idx_scan_events_is_phishing', table_name='scan_events')
    op.drop_index('idx_scan_events_domain', table_name='scan_events')
    op.drop_index('idx_scan_events_created_at', table_name='scan_events')
    op.drop_table('scan_events')
