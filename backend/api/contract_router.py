"""
Contract API Router
Provides contract analysis endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from contract import contract_service
from contract.models import (
    ContractRequest, ContractResponse, ContractCapabilities, 
    ContractAnalytics, AnalysisType, ContractType
)
from tools.logger import logger
import tempfile
import os

contract_router = APIRouter(
    prefix="/contract",
    tags=["Contract"],
    responses={404: {"description": "Not found"}},
)

@contract_router.post("/analyze", response_model=ContractResponse)
async def analyze_contract(
    file: Optional[UploadFile] = File(None),
    file_content: Optional[str] = Form(None),
    analysis_types: Optional[List[str]] = Form(["comprehensive"]),
    contract_type_hint: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    priority: Optional[str] = Form("normal")
) -> ContractResponse:
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
            "contract_types": [
                {
                    "value": ct.value,
                    "description": ct.name.replace("_", " ").title()
                }
                for ct in ContractType
            ]
        }
    except Exception as e:
        logger.error(f"Contract types error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get contract types")
