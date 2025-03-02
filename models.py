from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Job(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    url = db.Column(db.String(512), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    target = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)
    message = db.Column(db.String(512))
    result = db.Column(db.Text)
    result_url = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Job {self.id}>'