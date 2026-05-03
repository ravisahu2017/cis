"""
Test API Router
Provides test endpoints for API testing and development
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from storage.repository import TestRepository
from storage.database import get_db_session
from utils import logger
from sqlalchemy.orm import Session

test_router = APIRouter(
    prefix="/test",
    tags=["Test"],
    responses={404: {"description": "Not found"}},
)

def get_db_session_dep():
    """Dependency to get database session"""
    return get_db_session()

@test_router.post("/", response_model=Dict[str, Any])
async def create_test_record(
    name: str,
    description: Optional[str] = None,
    value: Optional[int] = None,
    tags: Optional[List[str]] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Create a new test record
    """
    try:
        test_repo = TestRepository(db)
        test_record = test_repo.create_test_record(
            name=name,
            description=description,
            value=value,
            tags=tags or [],
            is_active=is_active
        )
        
        return {
            "success": True,
            "test_record": test_record.to_dict(),
            "message": "Test record created successfully"
        }
    except Exception as e:
        logger.error(f"Create test record error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create test record")

@test_router.get("/", response_model=Dict[str, Any])
async def get_test_records(
    limit: int = 50,
    offset: int = 0,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get all test records with pagination and filtering
    """
    try:
        test_repo = TestRepository(db)
        test_records = test_repo.get_all_test_records(limit, offset, is_active)
        
        return {
            "test_records": [record.to_dict() for record in test_records],
            "total": len(test_records),
            "limit": limit,
            "offset": offset,
            "is_active_filter": is_active
        }
    except Exception as e:
        logger.error(f"Get test records error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get test records")

@test_router.get("/{record_id}", response_model=Dict[str, Any])
async def get_test_record(
    record_id: str,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get specific test record by ID
    """
    try:
        test_repo = TestRepository(db)
        test_record = test_repo.get_test_record(record_id)
        
        if not test_record:
            raise HTTPException(status_code=404, detail="Test record not found")
        
        return {
            "success": True,
            "test_record": test_record.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get test record error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get test record")

@test_router.put("/{record_id}", response_model=Dict[str, Any])
async def update_test_record(
    record_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    value: Optional[int] = None,
    tags: Optional[List[str]] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Update existing test record
    """
    try:
        test_repo = TestRepository(db)
        test_record = test_repo.update_test_record(
            record_id=record_id,
            name=name,
            description=description,
            value=value,
            tags=tags,
            is_active=is_active
        )
        
        if not test_record:
            raise HTTPException(status_code=404, detail="Test record not found")
        
        return {
            "success": True,
            "test_record": test_record.to_dict(),
            "message": "Test record updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update test record error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update test record")

@test_router.delete("/{record_id}", response_model=Dict[str, Any])
async def delete_test_record(
    record_id: str,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Delete test record
    """
    try:
        test_repo = TestRepository(db)
        success = test_repo.delete_test_record(record_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Test record not found")
        
        return {
            "success": True,
            "record_id": record_id,
            "message": "Test record deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete test record error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete test record")

@test_router.get("/search", response_model=Dict[str, Any])
async def search_test_records(
    query: str = "",
    tags: Optional[List[str]] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Search test records with filters
    """
    try:
        test_repo = TestRepository(db)
        test_records = test_repo.search_test_records(query, tags, limit, offset)
        
        return {
            "test_records": [record.to_dict() for record in test_records],
            "query": query,
            "tags": tags,
            "total": len(test_records),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Search test records error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search test records")

@test_router.get("/by-value", response_model=Dict[str, Any])
async def get_test_records_by_value_range(
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get test records by value range
    """
    try:
        test_repo = TestRepository(db)
        test_records = test_repo.get_test_records_by_value_range(
            min_value, max_value, limit, offset
        )
        
        return {
            "test_records": [record.to_dict() for record in test_records],
            "min_value": min_value,
            "max_value": max_value,
            "total": len(test_records),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Get test records by value range error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get test records by value range")

@test_router.get("/health", response_model=Dict[str, Any])
async def test_health_check(
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Test endpoint for health checks
    """
    try:
        test_repo = TestRepository(db)
        # Test database connection
        test_records = test_repo.get_all_test_records(limit=1)
        
        return {
            "status": "healthy",
            "database": "connected",
            "test_table_exists": True,
            "total_test_records": len(test_records),
            "timestamp": "2024-05-02T15:30:00Z"
        }
    except Exception as e:
        logger.error(f"Test health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": "2024-05-02T15:30:00Z"
        }
