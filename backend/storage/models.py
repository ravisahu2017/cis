"""
Storage Layer - Database Models
Defines database models for contract storage and versioning
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any
import json
import uuid

Base = declarative_base()

class ContractRecord(Base):
    """Master contract record - tracks versions of the same contract"""
    __tablename__ = "contracts"
    
    id = Column(String, primary_key=True)  # UUID
    contract_name = Column(String, nullable=False)
    description = Column(Text)
    contract_type = Column(String)  # MSA, NDA, SOW, etc.
    parties = Column(Text)  # JSON array of parties
    user_id = Column(String, nullable=False)
    original_upload_date = Column(DateTime, default=datetime.utcnow)
    last_modified_date = Column(DateTime, default=datetime.utcnow)
    current_version_id = Column(String, ForeignKey("contract_versions.id"), nullable=True)
    status = Column(String, default="active")  # active, archived, deleted
    metadata_json = Column(Text)  # Additional metadata as JSON
    
    # Access current version manually:
    def current_version(self):
        if self.current_version_id:
            return self.session.query(ContractVersion).filter(
                ContractVersion.id == self.current_version_id
            ).first()
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "contract_name": self.contract_name,
            "description": self.description,
            "contract_type": self.contract_type,
            "parties": json.loads(self.parties) if self.parties else [],
            "user_id": self.user_id,
            "original_upload_date": self.original_upload_date.isoformat() if self.original_upload_date else None,
            "last_modified_date": self.last_modified_date.isoformat() if self.last_modified_date else None,
            "current_version_id": self.current_version_id,
            "status": self.status,
            "metadata": json.loads(self.metadata_json) if self.metadata_json else {}
        }

class ContractVersion(Base):
    """Individual version of a contract"""
    __tablename__ = "contract_versions"
    
    id = Column(String, primary_key=True)  # UUID
    contract_id = Column(String, ForeignKey("contracts.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)  # SHA-256 hash
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.utcnow)
    upload_reason = Column(Text)  # Why this version was created
    change_summary = Column(Text)  # Summary of changes from previous version
    
    # Contract metadata
    effective_date = Column(DateTime)
    expiry_date = Column(DateTime)
    governing_law = Column(String)
    total_value = Column(Float)
    currency = Column(String)
    
    # Content analysis
    content_text = Column(Text)  # Extracted text content
    metadata_json = Column(Text)  # Extracted metadata as JSON
    
    # Version tracking
    similarity_score = Column(Float)  # Similarity with previous version
    is_current = Column(Boolean, default=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "contract_id": self.contract_id,
            "version_number": self.version_number,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "upload_reason": self.upload_reason,
            "change_summary": self.change_summary,
            "effective_date": self.effective_date.isoformat() if self.effective_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "governing_law": self.governing_law,
            "total_value": self.total_value,
            "currency": self.currency,
            "metadata": json.loads(self.metadata_json) if self.metadata_json else {},
            "similarity_score": self.similarity_score,
            "is_current": self.is_current
        }

class AnalysisRecord(Base):
    """Analysis results for a specific contract version"""
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True)  # UUID
    version_id = Column(String, ForeignKey("contract_versions.id"), nullable=False)
    analysis_type = Column(String, nullable=False)  # legal, financial, operations, comprehensive
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Analysis results
    overall_risk_score = Column(Integer)
    risk_level = Column(String)  # low, medium, high, critical
    legal_risk_score = Column(Integer)
    financial_risk_score = Column(Integer)
    operational_risk_score = Column(Integer)
    
    # Processing info
    processing_time_ms = Column(Integer)
    agents_used = Column(Text)  # JSON array of agent names
    analysis_status = Column(String, default="completed")  # pending, processing, completed, failed
    
    # Results storage
    analysis_json = Column(Text)  # Full analysis results as JSON
    clauses_json = Column(Text)  # Clause analysis as JSON
    executive_summary = Column(Text)
    key_recommendations = Column(Text)  # JSON array
    
    # Version comparison
    comparison_with_previous = Column(Text)  # Comparison with previous version
    changes_detected = Column(Text)  # JSON array of detected changes
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version_id": self.version_id,
            "analysis_type": self.analysis_type,
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "overall_risk_score": self.overall_risk_score,
            "risk_level": self.risk_level,
            "legal_risk_score": self.legal_risk_score,
            "financial_risk_score": self.financial_risk_score,
            "operational_risk_score": self.operational_risk_score,
            "processing_time_ms": self.processing_time_ms,
            "agents_used": json.loads(self.agents_used) if self.agents_used else [],
            "analysis_status": self.analysis_status,
            "analysis": json.loads(self.analysis_json) if self.analysis_json else {},
            "clauses": json.loads(self.clauses_json) if self.clauses_json else [],
            "executive_summary": self.executive_summary,
            "key_recommendations": json.loads(self.key_recommendations) if self.key_recommendations else [],
            "comparison_with_previous": json.loads(self.comparison_with_previous) if self.comparison_with_previous else {},
            "changes_detected": json.loads(self.changes_detected) if self.changes_detected else []
        }

class AnalysisQueue(Base):
    """Queue for tracking analysis jobs"""
    __tablename__ = 'analysis_queue'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String, ForeignKey('contracts.id'), nullable=False)
    version_id = Column(String, ForeignKey('contract_versions.id'), nullable=False)
    analysis_type = Column(String, nullable=False)
    status = Column(String, nullable=False)  # pending, processing, completed, failed
    priority = Column(String, nullable=False)  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'version_id': self.version_id,
            'analysis_type': self.analysis_type,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }

class TestRecord(Base):
    """Test table for API testing"""
    __tablename__ = 'test_records'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    value = Column(Integer, nullable=True)
    tags = Column(String, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'value': self.value,
            'tags': json.loads(self.tags) if self.tags else [],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
