from datetime import datetime
from app import db

class UserComplaint(db.Model):
    __tablename__ = 'user_complaints'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1000), nullable=False)
    complaint_text = db.Column(db.Text, nullable=False)
    is_valid_government_url = db.Column(db.Boolean, default=False)
    validation_status = db.Column(db.String(50), default='pending')  # pending, valid, invalid
    validation_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    rti_request = db.relationship('RTIRequest', backref='complaint', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'complaint_text': self.complaint_text,
            'is_valid_government_url': self.is_valid_government_url,
            'validation_status': self.validation_status,
            'validation_reason': self.validation_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class RTIRequest(db.Model):
    __tablename__ = 'rti_requests'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('user_complaints.id'), nullable=False, unique=True)

    rti_text = db.Column(db.Text, nullable=False)
    compliance_score = db.Column(db.Integer, default=0)
    pdf_path = db.Column(db.String(1000))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'rti_text': self.rti_text,
            'compliance_score': self.compliance_score,
            'pdf_path': self.pdf_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
