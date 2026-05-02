"""
Database Test Router
Direct database structure testing endpoints (no LLM calls)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from storage.database import get_db_session
from storage.repository import ContractRepository, AnalysisRepository, TestRepository
from storage.models import ContractRecord, ContractVersion, AnalysisRecord, TestRecord
from tools.logger import logger

db_test_router = APIRouter(prefix="/db-test", tags=["database-testing"])

@db_test_router.get("/contracts", response_model=Dict[str, Any])
def test_contracts_table():
    """Test contracts table structure and data"""
    try:
        session = get_db_session()
        repo = ContractRepository(session)
        
        # Get all contracts
        contracts = session.query(ContractRecord).all()
        
        return {
            "success": True,
            "table": "contracts",
            "total_records": len(contracts),
            "records": [
                {
                    "id": c.id,
                    "contract_name": c.contract_name,
                    "user_id": c.user_id,
                    "current_version_id": c.current_version_id,
                    "status": c.status,
                    "created_at": c.original_upload_date.isoformat() if c.original_upload_date else None
                }
                for c in contracts
            ],
            "columns": [
                "id", "contract_name", "description", "contract_type", "parties",
                "user_id", "original_upload_date", "last_modified_date", 
                "current_version_id", "status", "metadata_json"
            ]
        }
    except Exception as e:
        logger.error(f"DB test contracts error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")
    finally:
        session.close()

@db_test_router.get("/versions", response_model=Dict[str, Any])
def test_versions_table():
    """Test contract_versions table structure and data"""
    try:
        session = get_db_session()
        
        # Get all versions
        versions = session.query(ContractVersion).all()
        
        return {
            "success": True,
            "table": "contract_versions",
            "total_records": len(versions),
            "records": [
                {
                    "id": v.id,
                    "contract_id": v.contract_id,
                    "version_number": v.version_number,
                    "filename": v.filename,
                    "file_size": v.file_size,
                    "is_current": v.is_current,
                    "created_at": v.upload_date.isoformat() if v.upload_date else None
                }
                for v in versions
            ],
            "columns": [
                "id", "contract_id", "version_number", "filename", "file_path",
                "file_hash", "file_size", "upload_date", "upload_reason", 
                "change_summary", "effective_date", "expiry_date", "governing_law",
                "total_value", "currency", "content_text", "metadata_json",
                "similarity_score", "is_current"
            ]
        }
    except Exception as e:
        logger.error(f"DB test versions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")
    finally:
        session.close()

@db_test_router.get("/analyses", response_model=Dict[str, Any])
def test_analyses_table():
    """Test analyses table structure and data"""
    try:
        session = get_db_session()
        
        # Get all analyses
        analyses = session.query(AnalysisRecord).all()
        
        return {
            "success": True,
            "table": "analyses",
            "total_records": len(analyses),
            "records": [
                {
                    "id": a.id,
                    "version_id": a.version_id,
                    "analysis_type": a.analysis_type,
                    "risk_score": a.overall_risk_score,
                    "risk_level": a.risk_level,
                    "created_at": a.analysis_date.isoformat() if a.analysis_date else None
                }
                for a in analyses
            ],
            "columns": [
                "id", "version_id", "analysis_type", "analysis_date", 
                "overall_risk_score", "risk_level", "legal_risk_score",
                "financial_risk_score", "operational_risk_score",
                "analysis_json", "clauses_json", "executive_summary",
                "key_recommendations", "comparison_with_previous", "changes_detected"
            ]
        }
    except Exception as e:
        logger.error(f"DB test analyses error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")
    finally:
        session.close()

@db_test_router.get("/test-records", response_model=Dict[str, Any])
def test_test_records_table():
    """Test test_records table structure and data"""
    try:
        session = get_db_session()
        repo = TestRepository(session)
        
        # Get all test records
        test_records = session.query(TestRecord).all()
        
        return {
            "success": True,
            "table": "test_records",
            "total_records": len(test_records),
            "records": [
                {
                    "id": t.id,
                    "name": t.name,
                    "value": t.value,
                    "is_active": t.is_active,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in test_records
            ],
            "columns": [
                "id", "name", "description", "value", "tags", 
                "is_active", "created_at", "updated_at"
            ]
        }
    except Exception as e:
        logger.error(f"DB test test_records error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")
    finally:
        session.close()

@db_test_router.post("/create-test-contract", response_model=Dict[str, Any])
def create_test_contract():
    """Create a test contract without LLM calls"""
    try:
        session = get_db_session()
        repo = ContractRepository(session)
        
        # Create contract
        contract = ContractRecord(
            id="test-contract-001",
            contract_name="Test Contract for DB Validation",
            description="This is a test contract to validate database structure",
            contract_type="test",
            parties='["Test Party A", "Test Party B"]',
            user_id="test-user",
            status="active",
            metadata_json='{"test": true, "purpose": "db_validation"}'
        )
        
        session.add(contract)
        session.commit()
        
        # Create version
        version = ContractVersion(
            id="test-version-001",
            contract_id=contract.id,
            version_number=1,
            filename="test_contract.txt",
            file_path="/tmp/test_contract.txt",
            file_hash="abc123hash",
            file_size=1024,
            content_text="This is test contract content for database validation purposes.",
            metadata_json='{"extracted": "test"}',
            is_current=True
        )
        
        session.add(version)
        session.commit()
        
        # Update contract's current version
        contract.current_version_id = version.id
        session.commit()
        
        return {
            "success": True,
            "message": "Test contract created successfully",
            "contract_id": contract.id,
            "version_id": version.id,
            "current_version_id": contract.current_version_id
        }
        
    except Exception as e:
        logger.error(f"Create test contract error: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create test contract: {str(e)}")
    finally:
        session.close()

@db_test_router.post("/create-test-analysis", response_model=Dict[str, Any])
def create_test_analysis():
    """Create a test analysis without LLM calls"""
    try:
        session = get_db_session()
        
        # Find a version to attach analysis to
        version = session.query(ContractVersion).first()
        if not version:
            raise HTTPException(status_code=404, detail="No contract version found. Create test contract first.")
        
        # Create analysis
        analysis = AnalysisRecord(
            id="test-analysis-001",
            version_id=version.id,
            analysis_type="comprehensive",
            overall_risk_score=75,
            risk_level="high",
            legal_risk_score=80,
            financial_risk_score=70,
            operational_risk_score=75,
            analysis_json='{"test": "analysis", "score": 75}',
            clauses_json='[{"clause_type": "test", "risk_score": 75}]',
            executive_summary="Test analysis summary for database validation",
            key_recommendations='["Test recommendation 1", "Test recommendation 2"]'
        )
        
        session.add(analysis)
        session.commit()
        
        return {
            "success": True,
            "message": "Test analysis created successfully",
            "analysis_id": analysis.id,
            "version_id": version.id,
            "contract_id": version.contract_id
        }
        
    except Exception as e:
        logger.error(f"Create test analysis error: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create test analysis: {str(e)}")
    finally:
        session.close()

@db_test_router.get("/relationships", response_model=Dict[str, Any])
def test_relationships():
    """Test foreign key relationships manually"""
    try:
        session = get_db_session()
        
        # Test contract -> version relationship
        contracts = session.query(ContractRecord).all()
        relationship_tests = []
        
        for contract in contracts:
            if contract.current_version_id:
                version = session.query(ContractVersion).filter(
                    ContractVersion.id == contract.current_version_id
                ).first()
                
                relationship_tests.append({
                    "type": "contract -> current_version",
                    "contract_id": contract.id,
                    "version_id": contract.current_version_id,
                    "version_found": version is not None,
                    "version_contract_id": version.contract_id if version else None,
                    "relationship_valid": version and version.contract_id == contract.id
                })
        
        # Test version -> contract relationship
        versions = session.query(ContractVersion).all()
        for version in versions:
            contract = session.query(ContractRecord).filter(
                ContractRecord.id == version.contract_id
            ).first()
            
            relationship_tests.append({
                "type": "version -> contract",
                "version_id": version.id,
                "contract_id": version.contract_id,
                "contract_found": contract is not None,
                "relationship_valid": contract is not None
            })
        
        # Test version -> analysis relationship
        analyses = session.query(AnalysisRecord).all()
        for analysis in analyses:
            version = session.query(ContractVersion).filter(
                ContractVersion.id == analysis.version_id
            ).first()
            
            relationship_tests.append({
                "type": "analysis -> version",
                "analysis_id": analysis.id,
                "version_id": analysis.version_id,
                "version_found": version is not None,
                "relationship_valid": version is not None
            })
        
        return {
            "success": True,
            "total_relationship_tests": len(relationship_tests),
            "valid_relationships": len([r for r in relationship_tests if r["relationship_valid"]]),
            "invalid_relationships": len([r for r in relationship_tests if not r["relationship_valid"]]),
            "tests": relationship_tests
        }
        
    except Exception as e:
        logger.error(f"Test relationships error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Relationship test failed: {str(e)}")
    finally:
        session.close()

@db_test_router.delete("/cleanup", response_model=Dict[str, Any])
def cleanup_test_data():
    """Clean up test data"""
    try:
        session = get_db_session()
        
        # Delete test records (identify by test prefix)
        test_contracts = session.query(ContractRecord).filter(
            ContractRecord.id.like("test-%")
        ).all()
        
        test_versions = session.query(ContractVersion).filter(
            ContractVersion.id.like("test-%")
        ).all()
        
        test_analyses = session.query(AnalysisRecord).filter(
            AnalysisRecord.id.like("test-%")
        ).all()
        
        # Delete in correct order (child to parent)
        for analysis in test_analyses:
            session.delete(analysis)
        
        for version in test_versions:
            session.delete(version)
        
        for contract in test_contracts:
            session.delete(contract)
        
        session.commit()
        
        return {
            "success": True,
            "message": "Test data cleaned up successfully",
            "deleted_contracts": len(test_contracts),
            "deleted_versions": len(test_versions),
            "deleted_analyses": len(test_analyses)
        }
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
    finally:
        session.close()

@db_test_router.get("/health", response_model=Dict[str, Any])
def db_health_check():
    """Comprehensive database health check"""
    try:
        session = get_db_session()
        
        # Check table counts
        contract_count = session.query(ContractRecord).count()
        version_count = session.query(ContractVersion).count()
        analysis_count = session.query(AnalysisRecord).count()
        test_count = session.query(TestRecord).count()
        
        # Check for data integrity issues
        issues = []
        
        # Check contracts without current version
        contracts_no_current = session.query(ContractRecord).filter(
            ContractRecord.current_version_id.is_(None)
        ).count()
        if contracts_no_current > 0:
            issues.append(f"{contracts_no_current} contracts have no current version")
        
        # Check versions without contract
        versions_no_contract = session.query(ContractVersion).filter(
            ~ContractVersion.contract_id.in_(
                session.query(ContractRecord.id)
            )
        ).count()
        if versions_no_contract > 0:
            issues.append(f"{versions_no_contract} versions reference non-existent contracts")
        
        # Check analyses without version
        analyses_no_version = session.query(AnalysisRecord).filter(
            ~AnalysisRecord.version_id.in_(
                session.query(ContractVersion.id)
            )
        ).count()
        if analyses_no_version > 0:
            issues.append(f"{analyses_no_version} analyses reference non-existent versions")
        
        return {
            "success": True,
            "database_status": "healthy" if len(issues) == 0 else "issues_found",
            "table_counts": {
                "contracts": contract_count,
                "versions": version_count,
                "analyses": analysis_count,
                "test_records": test_count
            },
            "integrity_issues": issues,
            "total_issues": len(issues)
        }
        
    except Exception as e:
        logger.error(f"DB health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
    finally:
        session.close()
