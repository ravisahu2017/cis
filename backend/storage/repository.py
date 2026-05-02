"""
Storage Layer - Repository Classes
Provides data access methods for contract storage
"""

import uuid
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from tools.logger import logger
from .models import ContractRecord, ContractVersion, AnalysisRecord, AnalysisQueue
from .database import get_db_session

class ContractRepository:
    """Repository for contract and version operations"""
    
    def __init__(self, session: Session = None):
        self.session = session or get_db_session()
    
    def create_contract(self, contract_name: str, user_id: str, **kwargs) -> ContractRecord:
        """Create a new contract record"""
        try:
            contract = ContractRecord(
                id=str(uuid.uuid4()),
                contract_name=contract_name,
                user_id=user_id,
                **kwargs
            )
            
            self.session.add(contract)
            self.session.commit()
            
            logger.info(f"Created contract: {contract.id}")
            return contract
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create contract: {str(e)}")
            raise
    
    def get_contract(self, contract_id: str) -> Optional[ContractRecord]:
        """Get contract by ID"""
        try:
            return self.session.query(ContractRecord).filter(
                ContractRecord.id == contract_id,
                ContractRecord.status != "deleted"
            ).first()
        except Exception as e:
            logger.error(f"Failed to get contract {contract_id}: {str(e)}")
            return None
    
    def get_user_contracts(self, user_id: str, limit: int = 50, offset: int = 0) -> List[ContractRecord]:
        """Get all contracts for a user"""
        try:
            return self.session.query(ContractRecord).filter(
                ContractRecord.user_id == user_id,
                ContractRecord.status != "deleted"
            ).order_by(desc(ContractRecord.last_modified_date)).offset(offset).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get user contracts: {str(e)}")
            return []
    
    def search_contracts(self, user_id: str, query: str = "", filters: Dict = None, 
                        limit: int = 50, offset: int = 0) -> List[ContractRecord]:
        """Search contracts with filters"""
        try:
            query_obj = self.session.query(ContractRecord).filter(
                ContractRecord.user_id == user_id,
                ContractRecord.status != "deleted"
            )
            
            # Text search
            if query:
                query_obj = query_obj.filter(
                    or_(
                        ContractRecord.contract_name.contains(query),
                        ContractRecord.description.contains(query),
                        ContractRecord.parties.contains(query)
                    )
                )
            
            # Apply filters
            if filters:
                if filters.get("contract_type"):
                    query_obj = query_obj.filter(ContractRecord.contract_type == filters["contract_type"])
                
                if filters.get("status"):
                    query_obj = query_obj.filter(ContractRecord.status == filters["status"])
                
                if filters.get("date_from"):
                    query_obj = query_obj.filter(ContractRecord.last_modified_date >= filters["date_from"])
                
                if filters.get("date_to"):
                    query_obj = query_obj.filter(ContractRecord.last_modified_date <= filters["date_to"])
            
            return query_obj.order_by(desc(ContractRecord.last_modified_date)).offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Failed to search contracts: {str(e)}")
            return []
    
    def create_version(self, contract_id: str, filename: str, file_path: str, 
                      file_content: str, **kwargs) -> ContractVersion:
        """Create a new version of a contract"""
        try:
            # Generate file hash
            file_hash = hashlib.sha256(file_content.encode()).hexdigest()
            
            # Get next version number
            latest_version = self.session.query(ContractVersion).filter(
                ContractVersion.contract_id == contract_id
            ).order_by(desc(ContractVersion.version_number)).first()
            
            version_number = (latest_version.version_number + 1) if latest_version else 1
            
            # Mark previous versions as not current
            if latest_version:
                latest_version.is_current = False
            
            version = ContractVersion(
                id=str(uuid.uuid4()),
                contract_id=contract_id,
                version_number=version_number,
                filename=filename,
                file_path=file_path,
                file_hash=file_hash,
                file_size=len(file_content),
                content_text=file_content,
                **kwargs
            )
            
            self.session.add(version)
            
            # Update contract's current version
            contract = self.get_contract(contract_id)
            if contract:
                contract.current_version_id = version.id
                contract.last_modified_date = datetime.utcnow()
            
            self.session.commit()
            
            logger.info(f"Created version {version_number} for contract {contract_id}")
            return version
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create version: {str(e)}")
            raise
    
    def get_contract_versions(self, contract_id: str) -> List[ContractVersion]:
        """Get all versions of a contract"""
        try:
            return self.session.query(ContractVersion).filter(
                ContractVersion.contract_id == contract_id
            ).order_by(desc(ContractVersion.version_number)).all()
        except Exception as e:
            logger.error(f"Failed to get contract versions: {str(e)}")
            return []
    
    def get_version(self, version_id: str) -> Optional[ContractVersion]:
        """Get specific version by ID"""
        try:
            return self.session.query(ContractVersion).filter(
                ContractVersion.id == version_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to get version {version_id}: {str(e)}")
            return None
    
    def get_current_version(self, contract_id: str) -> Optional[ContractVersion]:
        """Get current version of a contract"""
        try:
            return self.session.query(ContractVersion).filter(
                ContractVersion.contract_id == contract_id,
                ContractVersion.is_current == True
            ).first()
        except Exception as e:
            logger.error(f"Failed to get current version: {str(e)}")
            return None
    
    def find_similar_contracts(self, file_hash: str, user_id: str, threshold: float = 0.9) -> List[ContractRecord]:
        """Find contracts with similar content (for version detection)"""
        try:
            return self.session.query(ContractRecord).join(ContractVersion).filter(
                ContractRecord.user_id == user_id,
                ContractVersion.file_hash == file_hash,
                ContractRecord.status != "deleted"
            ).all()
        except Exception as e:
            logger.error(f"Failed to find similar contracts: {str(e)}")
            return []
    
    def get_expiring_contracts(self, days: int = 30, user_id: str = None) -> List[ContractRecord]:
        """Get contracts expiring within specified days"""
        try:
            cutoff_date = datetime.utcnow() + timedelta(days=days)
            query = self.session.query(ContractRecord).join(ContractVersion).filter(
                ContractVersion.expiry_date <= cutoff_date,
                ContractVersion.expiry_date >= datetime.utcnow(),
                ContractRecord.status != "deleted"
            )
            
            if user_id:
                query = query.filter(ContractRecord.user_id == user_id)
            
            return query.order_by(ContractVersion.expiry_date).all()
        except Exception as e:
            logger.error(f"Failed to get expiring contracts: {str(e)}")
            return []
    
    def get_high_risk_contracts(self, risk_threshold: int = 70, user_id: str = None) -> List[ContractRecord]:
        """Get contracts with high risk scores"""
        try:
            query = self.session.query(ContractRecord).join(ContractVersion).join(AnalysisRecord).filter(
                AnalysisRecord.overall_risk_score >= risk_threshold,
                ContractRecord.status != "deleted"
            )
            
            if user_id:
                query = query.filter(ContractRecord.user_id == user_id)
            
            return query.order_by(desc(AnalysisRecord.overall_risk_score)).all()
        except Exception as e:
            logger.error(f"Failed to get high risk contracts: {str(e)}")
            return []

class AnalysisRepository:
    """Repository for analysis operations"""
    
    def __init__(self, session: Session = None):
        self.session = session or get_db_session()
    
    def create_analysis(self, version_id: str, analysis_type: str, 
                       analysis_result: Dict, **kwargs) -> AnalysisRecord:
        """Create a new analysis record"""
        try:
            analysis = AnalysisRecord(
                id=str(uuid.uuid4()),
                version_id=version_id,
                analysis_type=analysis_type,
                **kwargs
            )
            
            # Set analysis data from result
            if hasattr(analysis_result, 'overall_risk_score'):
                analysis.overall_risk_score = analysis_result.overall_risk_score
                analysis.risk_level = analysis_result.risk_level.value
                analysis.legal_risk_score = analysis_result.legal_risk_score
                analysis.financial_risk_score = analysis_result.financial_risk_score
                analysis.operational_risk_score = analysis_result.operational_risk_score
                analysis.analysis_json = analysis_result.dict()
                analysis.clauses_json = str([clause.dict() for clause in analysis_result.clauses])
                analysis.executive_summary = analysis_result.executive_summary
                analysis.key_recommendations = str(analysis_result.key_recommendations)
            
            self.session.add(analysis)
            self.session.commit()
            
            logger.info(f"Created analysis: {analysis.id} for version {version_id}")
            return analysis
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create analysis: {str(e)}")
            raise
    
    def get_analysis(self, analysis_id: str) -> Optional[AnalysisRecord]:
        """Get analysis by ID"""
        try:
            return self.session.query(AnalysisRecord).filter(
                AnalysisRecord.id == analysis_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to get analysis {analysis_id}: {str(e)}")
            return None
    
    def get_version_analyses(self, version_id: str) -> List[AnalysisRecord]:
        """Get all analyses for a version"""
        try:
            return self.session.query(AnalysisRecord).filter(
                AnalysisRecord.version_id == version_id
            ).order_by(desc(AnalysisRecord.analysis_date)).all()
        except Exception as e:
            logger.error(f"Failed to get version analyses: {str(e)}")
            return []
    
    def get_contract_analyses(self, contract_id: str) -> List[AnalysisRecord]:
        """Get all analyses for a contract (all versions)"""
        try:
            return self.session.query(AnalysisRecord).join(ContractVersion).filter(
                ContractVersion.contract_id == contract_id
            ).order_by(desc(AnalysisRecord.analysis_date)).all()
        except Exception as e:
            logger.error(f"Failed to get contract analyses: {str(e)}")
            return []
    
    def queue_analysis(self, contract_id: str, version_id: str, analysis_types: List[str], 
                      user_id: str, priority: str = "normal") -> AnalysisQueue:
        """Queue analysis for background processing"""
        try:
            queue_item = AnalysisQueue(
                id=str(uuid.uuid4()),
                contract_id=contract_id,
                version_id=version_id,
                analysis_types=str(analysis_types),
                user_id=user_id,
                priority=priority
            )
            
            self.session.add(queue_item)
            self.session.commit()
            
            logger.info(f"Queued analysis: {queue_item.id}")
            return queue_item
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to queue analysis: {str(e)}")
            raise
    
    def get_queue_item(self, queue_id: str) -> Optional[AnalysisQueue]:
        """Get queue item by ID"""
        try:
            return self.session.query(AnalysisQueue).filter(
                AnalysisQueue.id == queue_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to get queue item {queue_id}: {str(e)}")
            return None
    
    def get_pending_analyses(self, limit: int = 10) -> List[AnalysisQueue]:
        """Get pending analyses for processing"""
        try:
            return self.session.query(AnalysisQueue).filter(
                AnalysisQueue.status == "pending"
            ).order_by(
                desc(AnalysisQueue.priority),  # Higher priority first
                asc(AnalysisQueue.created_date)  # Earlier first
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get pending analyses: {str(e)}")
            return []
    
    def update_queue_status(self, queue_id: str, status: str, **kwargs):
        """Update queue item status"""
        try:
            queue_item = self.get_queue_item(queue_id)
            if queue_item:
                queue_item.status = status
                
                if status == "processing":
                    queue_item.started_date = datetime.utcnow()
                elif status in ["completed", "failed"]:
                    queue_item.completed_date = datetime.utcnow()
                
                # Update additional fields
                for key, value in kwargs.items():
                    if hasattr(queue_item, key):
                        setattr(queue_item, key, value)
                
                self.session.commit()
                logger.info(f"Updated queue {queue_id} status to {status}")
                
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update queue status: {str(e)}")
            raise
