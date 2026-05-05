"""
Chat API Router
Provides chat-related endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from chat import chat_service
from chat.models import ChatRequest, ChatResponse
from utils import logger

from utils.auth import verify_api_key

chat_router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    dependencies=[Depends(verify_api_key)],
    responses={404: {"description": "Not found"}},
)

@chat_router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for general questions and contract-related inquiries
    
    - **message**: User's question or message
    - **session_id**: Optional chat session identifier
    - **user_id**: Optional user identifier
    - **context**: Optional chat history
    
    Returns AI response with metadata about which agent handled the request
    """
    try:
        logger.info(f"Chat request received: {request.message[:100]}...")
        
        # Process message through chat service
        response = chat_service.process_message(request)
        
        logger.info(f"Chat response sent via {response.agent_used}")
        return response
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@chat_router.get("/capabilities")
async def chat_capabilities() -> Dict[str, Any]:
    """
    Get chat system capabilities and available features
    """
    try:
        capabilities = chat_service.get_capabilities()
        return capabilities.dict()  # Convert Pydantic to dict
    except Exception as e:
        logger.error(f"Chat capabilities error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get capabilities")

@chat_router.get("/agents")
async def chat_agents() -> Dict[str, Any]:
    """
    Get information about available chat agents
    """
    try:
        return chat_service.get_agent_info()
    except Exception as e:
        logger.error(f"Chat agents error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get agent info")

@chat_router.get("/sessions")
async def get_chat_sessions() -> Dict[str, Any]:
    """
    Get all active chat sessions
    """
    try:
        sessions = chat_service.get_active_sessions()
        return {
            "active_sessions": len(sessions),
            "sessions": [
                {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "message_count": session.message_count,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat()
                }
                for session in sessions
            ]
        }
    except Exception as e:
        logger.error(f"Chat sessions error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")

@chat_router.get("/analytics")
async def chat_analytics() -> Dict[str, Any]:
    """
    Get chat analytics and performance data
    """
    try:
        return chat_service.get_analytics()
    except Exception as e:
        logger.error(f"Chat analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@chat_router.delete("/sessions/{session_id}")
async def end_chat_session(session_id: str) -> Dict[str, str]:
    """
    End a specific chat session
    
    - **session_id**: Session identifier to end
    """
    try:
        success = chat_service.end_session(session_id)
        if success:
            return {"message": f"Session {session_id} ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"End session error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end session")
