"""
Storage Layer - Database Manager
Handles database connections and operations
"""

import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from tools.logger import logger
from .models import Base, ContractRecord, ContractVersion, AnalysisRecord, AnalysisQueue
import uuid
from datetime import datetime

class DatabaseManager:
    """Manages SQLite database for contract storage"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            db_path = "data/contracts.db"
        
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            # Create SQLite engine with connection pooling
            self.engine = create_engine(
                f"sqlite:///{self.db_path}",
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 20  # 20 second timeout
                },
                echo=False  # Set to True for SQL debugging
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session"""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized")
        
        return self.SessionLocal()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
    
    def health_check(self) -> dict:
        """Check database health"""
        try:
            with self.get_session() as session:
                # Test basic query
                result = session.execute(text("SELECT 1")).fetchone()
                
                # Get table counts
                contract_count = session.query(ContractRecord).count()
                version_count = session.query(ContractVersion).count()
                analysis_count = session.query(AnalysisRecord).count()
                
                return {
                    "status": "healthy",
                    "database_path": self.db_path,
                    "tables": {
                        "contracts": contract_count,
                        "contract_versions": version_count,
                        "analyses": analysis_count
                    }
                }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def cleanup_old_records(self, days: int = 90):
        """Clean up old records (for maintenance)"""
        try:
            with self.get_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # Delete old analysis queue records
                deleted_queue = session.query(AnalysisQueue).filter(
                    AnalysisQueue.created_date < cutoff_date,
                    AnalysisQueue.status.in_(["completed", "failed"])
                ).delete()
                
                session.commit()
                logger.info(f"Cleaned up {deleted_queue} old queue records")
                
                return {"deleted_queue_records": deleted_queue}
                
        except Exception as e:
            logger.error(f"Database cleanup failed: {str(e)}")
            raise

# Global database instance
_database_manager = None

def get_database() -> DatabaseManager:
    """Get global database manager instance"""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager

def get_db_session() -> Session:
    """Get database session (for dependency injection)"""
    return get_database().get_session()

# Database initialization function
def init_database(db_path: str = None):
    """Initialize the database (call this on app startup)"""
    return DatabaseManager(db_path)
