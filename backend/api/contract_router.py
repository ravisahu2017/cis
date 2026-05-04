"""
Contract API Router
Provides contract analysis endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
import tempfile
import os
from contract import contract_service
from contract.models import (
    ContractRequest, ContractResponse, ContractAnalysis, ContractCapabilities, 
    ContractAnalytics, AnalysisSession, AnalysisType, ContractType
)
from contract.service import contract_service
from storage.repository import ContractRepository, AnalysisRepository
from storage.database import get_db_session
from utils import logger
from fastapi import HTTPException, status, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from utils.common_model import HttpBaseResponse, PaginationResponse

contract_router = APIRouter(
    prefix="/contract",
    tags=["Contract"],
    responses={404: {"description": "Not found"}},
)

@contract_router.post("/analyze", response_model=HttpBaseResponse)
async def analyze_contract(
    file: Optional[UploadFile] = File(None),
    file_content: Optional[str] = Form(None),
    analysis_types: Optional[List[str]] = Form(["comprehensive"]),
    contract_type_hint: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    priority: Optional[str] = Form("normal")
) -> HttpBaseResponse:
    """
    Analyze a contract using multi-agent AI system
    
    - **file**: Contract file (PDF, DOCX, TXT, or image)
    - **file_content**: Direct text content (alternative to file upload)
    - **analysis_types**: Types of analysis to perform (legal, financial, operations, comprehensive)
    - **contract_type_hint**: Hint about contract type (msa, nda, sow, etc.)
    - **user_id**: Optional user identifier
    - **priority**: Analysis priority (normal, high, urgent)
    
    Returns comprehensive contract analysis with risk assessment
    """
    try:
        # Validate inputs
        if not file and not file_content:
            raise HTTPException(
                status_code=400, 
                detail="Either file or file_content must be provided"
            )
        
        # Convert analysis types to enum
        analysis_type_enums = []
        for analysis_type in analysis_types:
            try:
                analysis_type_enums.append(AnalysisType(analysis_type))
            except ValueError:
                logger.warning(f"Invalid analysis type: {analysis_type}")
        
        if not analysis_type_enums:
            analysis_type_enums = [AnalysisType.COMPREHENSIVE]
        
        # Convert contract type hint
        contract_type_enum = None
        if contract_type_hint:
            try:
                contract_type_enum = ContractType(contract_type_hint)
            except ValueError:
                logger.warning(f"Invalid contract type hint: {contract_type_hint}")
        
        # Handle file upload
        file_path = None
        if file:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                content = await file.read()
                temp_file.write(content)
                file_path = temp_file.name
        
        try:
            # Create contract request
            request = ContractRequest(
                file_path=file_path,
                file_content=file_content,
                analysis_types=analysis_type_enums,
                contract_type_hint=contract_type_enum,
                user_id=user_id,
                priority=priority
            )
            
            logger.info(f"Starting contract analysis for {len(analysis_type_enums)} types")
            
            # Process analysis
            response = contract_service.analyze_contract(request)
            
            logger.info(f"Contract analysis completed: {response.success}")
            return response
            
        finally:
            # Clean up temporary file
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contract analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Contract analysis failed: {str(e)}")

@contract_router.post("/analyze-text", response_model=ContractResponse)
async def analyze_contract_text(request: ContractRequest) -> ContractResponse:
    """
    Analyze contract text directly (alternative to file upload)
    
    - **request**: ContractRequest with text content and analysis options
    
    Returns comprehensive contract analysis with risk assessment
    """
    try:
        logger.info(f"Starting text-based contract analysis")
        
        # Validate text content
        if not request.file_content or len(request.file_content.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Insufficient text content (minimum 100 characters required)"
            )
        
        # Process analysis
        response = contract_service.analyze_contract(request)
        
        logger.info(f"Text-based contract analysis completed: {response.success}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text contract analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Contract analysis failed: {str(e)}")

@contract_router.get("/capabilities")
async def contract_capabilities() -> Dict[str, Any]:
    """
    Get contract analysis system capabilities
    """
    try:
        capabilities = contract_service.get_capabilities()
        return capabilities.dict()  # Convert Pydantic to dict
    except Exception as e:
        logger.error(f"Contract capabilities error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get capabilities")

@contract_router.get("/analysis/{analysis_id}/status", response_model=HttpBaseResponse)
async def get_analysis_status(analysis_id: str) -> HttpBaseResponse:
    """
    Get the status and progress of an analysis job
    
    Args:
        analysis_id: The analysis job ID returned by analyze endpoints
        
    Returns:
        Current status, progress percentage, and queue position
    """
    try:
        response = contract_service.get_analysis_status(analysis_id)
        return response
    except Exception as e:
        logger.error(f"Analysis status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analysis status: {str(e)}")

@contract_router.get("/agents")
async def contract_agents() -> Dict[str, Any]:
    """
    Get information about available contract analysis agents
    """
    try:
        return contract_service.get_agent_info()
    except Exception as e:
        logger.error(f"Contract agents error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get agent info")

@contract_router.get("/analytics")
async def contract_analytics() -> Dict[str, Any]:
    """
    Get contract analysis analytics and performance data
    """
    try:
        analytics = contract_service.get_analytics()
        return analytics.dict()  # Convert Pydantic to dict
    except Exception as e:
        logger.error(f"Contract analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@contract_router.get("/sessions")
async def get_contract_sessions() -> Dict[str, Any]:
    """
    Get all active contract analysis sessions
    """
    try:
        sessions = contract_service.get_active_sessions()
        return {
            "active_sessions": len(sessions),
            "sessions": [
                {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "analyses_completed": session.analyses_completed,
                    "total_processing_time_ms": session.total_processing_time_ms,
                    "contract_types_analyzed": [ct.value for ct in session.contract_types_analyzed],
                    "created_at": session.created_at.isoformat(),
                    "status": session.status
                }
                for session in sessions
            ]
        }
    except Exception as e:
        logger.error(f"Contract sessions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")

@contract_router.get("/queue")
async def get_contract_queue() -> Dict[str, Any]:
    """
    Get current contract analysis queue status
    """
    try:
        return contract_service.get_queue_status()
    except Exception as e:
        logger.error(f"Contract queue error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get queue status")

@contract_router.delete("/sessions/{session_id}")
async def end_contract_session(session_id: str) -> Dict[str, str]:
    """
    End a contract analysis session
    
    - **session_id**: Session identifier to end
    """
    try:
        success = contract_service.end_session(session_id)
        if success:
            return {"message": f"Session {session_id} ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"End contract session error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end session")

@contract_router.get("/analysis-types")
async def get_analysis_types() -> Dict[str, Any]:
    """
    Get available contract analysis types
    """
    try:
        return {
            "analysis_types": [
                {
                    "value": at.value,
                    "description": at.name.replace("_", " ").title()
                }
                for at in AnalysisType
            ],
            "default": AnalysisType.COMPREHENSIVE.value
        }
    except Exception as e:
        logger.error(f"Analysis types error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analysis types")

@contract_router.get("/contract-types")
async def get_contract_types() -> Dict[str, Any]:
    """
    Get supported contract types
    """
    try:
        return {
            "contract_types": [ct.value for ct in ContractType],
            "descriptions": {
                "msa": "Master Service Agreement",
                "nda": "Non-Disclosure Agreement", 
                "sow": "Statement of Work",
                "service_agreement": "Service Agreement",
                "supplier_contract": "Supplier Contract",
                "employment_agreement": "Employment Agreement",
                "lease_agreement": "Lease Agreement",
                "other": "Other"
            }
        }
    except Exception as e:
        logger.error(f"Contract types error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contract types")

# Contract Retrieval Endpoints

def get_db_session_dep():
    """Dependency to get database session"""
    return get_db_session()

@contract_router.get("/contracts")
async def get_contracts(
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db_session_dep)
) -> HttpBaseResponse   :
    """
    Get all contracts with pagination and filtering
    """
    try:
        contract_repo = ContractRepository(db)
        
        if user_id:
            contracts = contract_repo.get_user_contracts(user_id, limit, offset)
        else:
            # Get all contracts (admin)
            contracts = contract_repo.search_contracts("", {}, limit, offset)
        
        response = HttpBaseResponse(
            success=True,
            message="Contracts retrieved successfully",
            data=PaginationResponse(
                total=len(contracts),
                limit=limit,
                offset=offset,
                has_more=len(contracts) > limit,
                items=[contract.to_dict() for contract in contracts]
            )
        )
        return response
        
    except Exception as e:
        logger.error(f"Get contracts error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contracts")

@contract_router.get("/contracts/{contract_id}")
async def get_contract(
    contract_id: str,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get specific contract by ID with all versions
    """
    try:
        contract_repo = ContractRepository(db)
        contract = contract_repo.get_contract(contract_id)
        
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Get all versions
        versions = contract_repo.get_contract_versions(contract_id)
        
        return {
            "contract": contract.to_dict(),
            "versions": [version.to_dict() for version in versions]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get contract error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contract")

@contract_router.get("/contracts/{contract_id}/versions/{version_number}")
async def get_contract_version(
    contract_id: str,
    version_number: int,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get specific version of a contract
    """
    try:
        contract_repo = ContractRepository(db)
        versions = contract_repo.get_contract_versions(contract_id)
        
        # Find specific version
        target_version = None
        for version in versions:
            if version.version_number == version_number:
                target_version = version
                break
        
        if not target_version:
            raise HTTPException(status_code=404, detail="Contract version not found")
        
        # Get analyses for this version
        analysis_repo = AnalysisRepository(db)
        analyses = analysis_repo.get_version_analyses(target_version.id)
        
        return {
            "contract_id": contract_id,
            "version": target_version.to_dict(),
            "analyses": [analysis.to_dict() for analysis in analyses]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get contract version error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contract version")

@contract_router.get("/contracts/search")
async def search_contracts(
    query: str = "",
    contract_type: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Search contracts with filters
    """
    try:
        contract_repo = ContractRepository(db)
        
        filters = {}
        if contract_type:
            filters["contract_type"] = contract_type
        
        contracts = contract_repo.search_contracts(user_id, query, filters, limit, offset)
        
        return {
            "contracts": [contract.to_dict() for contract in contracts],
            "query": query,
            "filters": filters,
            "total": len(contracts),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Search contracts error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search contracts")

@contract_router.get("/contracts/{contract_id}/current-version")
async def get_current_version(
    contract_id: str,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get current version of a contract
    """
    try:
        contract_repo = ContractRepository(db)
        current_version = contract_repo.get_current_version(contract_id)
        
        if not current_version:
            raise HTTPException(status_code=404, detail="Contract has no current version")
        
        # Get analyses for current version
        analysis_repo = AnalysisRepository(db)
        analyses = analysis_repo.get_version_analyses(current_version.id)
        
        return {
            "contract_id": contract_id,
            "current_version": current_version.to_dict(),
            "analyses": [analysis.to_dict() for analysis in analyses]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current version error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get current version")

# Analysis Retrieval Endpoints

@contract_router.get("/analyses")
async def get_analyses(
    user_id: Optional[str] = None,
    analysis_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get all analyses with pagination and filtering
    """
    try:
        analysis_repo = AnalysisRepository(db)
        
        if user_id:
            analyses = analysis_repo.get_user_analyses(user_id, limit, offset)
        else:
            # Get all analyses (admin)
            analyses = analysis_repo.search_analyses("", {}, limit, offset)
        
        return {
            "analyses": [analysis.to_dict() for analysis in analyses],
            "total": len(analyses),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Get analyses error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analyses")

@contract_router.get("/contracts/{contract_id}/versions/{version_number}/analyses")
async def get_version_analyses(
    contract_id: str,
    version_number: int,
    analysis_type: Optional[str] = None,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get all analyses for a specific contract version
    """
    try:
        contract_repo = ContractRepository(db)
        versions = contract_repo.get_contract_versions(contract_id)
        
        # Find specific version
        target_version = None
        for version in versions:
            if version.version_number == version_number:
                target_version = version
                break
        
        if not target_version:
            raise HTTPException(status_code=404, detail="Contract version not found")
        
        # Get analyses for this version
        analysis_repo = AnalysisRepository(db)
        analyses = analysis_repo.get_version_analyses(target_version.id)
        
        # Filter by analysis type if specified
        if analysis_type:
            analyses = [a for a in analyses if a.analysis_type == analysis_type]
        
        return {
            "contract_id": contract_id,
            "version_number": version_number,
            "version_id": target_version.id,
            "analyses": [analysis.to_dict() for analysis in analyses],
            "analysis_type_filter": analysis_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get version analyses error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get version analyses")

@contract_router.get("/contracts/{contract_id}/analyses")
async def get_contract_analyses(
    contract_id: str,
    analysis_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get all analyses for a contract (all versions)
    """
    try:
        contract_repo = ContractRepository(db)
        versions = contract_repo.get_contract_versions(contract_id)
        
        if not versions:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        # Get analyses for all versions
        analysis_repo = AnalysisRepository(db)
        all_analyses = []
        
        for version in versions:
            version_analyses = analysis_repo.get_version_analyses(version.id)
            for analysis in version_analyses:
                analysis_data = analysis.to_dict()
                analysis_data["version_number"] = version.version_number
                analysis_data["version_id"] = version.id
                all_analyses.append(analysis_data)
        
        # Filter by analysis type if specified
        if analysis_type:
            all_analyses = [a for a in all_analyses if a["analysis_type"] == analysis_type]
        
        # Apply pagination
        total = len(all_analyses)
        paginated_analyses = all_analyses[offset:offset + limit]
        
        return {
            "contract_id": contract_id,
            "analyses": paginated_analyses,
            "total": total,
            "limit": limit,
            "offset": offset,
            "analysis_type_filter": analysis_type
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get contract analyses error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contract analyses")

@contract_router.get("/analyses/search")
async def search_analyses(
    query: str = "",
    analysis_type: Optional[str] = None,
    user_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Search analyses with filters
    """
    try:
        analysis_repo = AnalysisRepository(db)
        
        filters = {}
        if analysis_type:
            filters["analysis_type"] = analysis_type
        if risk_level:
            filters["risk_level"] = risk_level
        
        analyses = analysis_repo.search_analyses(user_id, query, filters, limit, offset)
        
        return {
            "analyses": [analysis.to_dict() for analysis in analyses],
            "query": query,
            "filters": filters,
            "total": len(analyses),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Search analyses error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search analyses")

@contract_router.get("/analyses/types")
async def get_analysis_types() -> Dict[str, Any]:
    """
    Get available analysis types
    """
    try:
        return {
            "analysis_types": [at.value for at in AnalysisType],
            "descriptions": {
                "legal": "Legal risk analysis and compliance check",
                "financial": "Financial risk and cost analysis",
                "operations": "Operational risk and feasibility analysis",
                "comprehensive": "Complete analysis including all risk categories"
            }
        }
    except Exception as e:
        logger.error(f"Get analysis types error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analysis types")

@contract_router.get("/analyses/recent")
async def get_recent_analyses(
    user_id: Optional[str] = None,
    hours: int = 24,
    limit: int = 20,
    db: Session = Depends(get_db_session_dep)
) -> HttpBaseResponse:
    """
    Get recent analyses from last N hours
    """
    try:
        analysis_repo = AnalysisRepository(db)
        
        if user_id:
            analyses = analysis_repo.get_user_recent_analyses(user_id, hours, limit)
        else:
            analyses = analysis_repo.get_recent_analyses(hours, limit)
        
        return HttpBaseResponse(
            success=True,
            message="Recent analyses retrieved successfully",
            data= PaginationResponse(
                total=len(analyses),
                limit=limit,
                offset=0,
                has_more=False,
                items=[analysis.to_dict() for analysis in analyses]
            )
        )
    except Exception as e:
        logger.error(f"Get recent analyses error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recent analyses")

@contract_router.get("/analyses/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db_session_dep)
) -> Dict[str, Any]:
    """
    Get specific analysis by ID
    """
    try:
        analysis_repo = AnalysisRepository(db)
        analysis = analysis_repo.get_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "analysis": analysis.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analysis")
