from app import db
from datetime import datetime
import json

class PolicyCard(db.Model):
    __tablename__ = 'policy_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    ministry = db.Column(db.String(200), nullable=False)
    notification_number = db.Column(db.String(100), unique=True)
    publication_date = db.Column(db.DateTime, nullable=False)
    effective_date = db.Column(db.DateTime)
    
    # Policy content
    original_text = db.Column(db.Text)
    summary_english = db.Column(db.Text)
    summary_nepali = db.Column(db.Text)
    
    # Structured data
    what_changed = db.Column(db.Text)
    who_affected = db.Column(db.Text)
    what_to_do = db.Column(db.Text)
    
    # Source and metadata
    source_url = db.Column(db.String(500))
    gazette_type = db.Column(db.String(100))  # Ordinary, Extraordinary
    status = db.Column(db.String(50), default='New')  # New, Updated, Action Required
    
    # Missing information flags
    missing_dates = db.Column(db.Boolean, default=False)
    missing_officer_info = db.Column(db.Boolean, default=False)
    missing_urls = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert policy card to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'ministry': self.ministry,
            'notification_number': self.notification_number,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'effective_date': self.effective_date.isoformat() if self.effective_date else None,
            'summary': {
                'english': self.summary_english,
                'nepali': self.summary_nepali
            },
            'details': {
                'what_changed': self.what_changed,
                'who_affected': self.who_affected,
                'what_to_do': self.what_to_do
            },
            'source_url': self.source_url,
            'gazette_type': self.gazette_type,
            'status': self.status,
            'operational_gaps': {
                'missing_dates': self.missing_dates,
                'missing_officer_info': self.missing_officer_info,
                'missing_urls': self.missing_urls
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<PolicyCard {self.notification_number}: {self.title[:50]}...>'
