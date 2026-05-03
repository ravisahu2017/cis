#!/usr/bin/env python3
"""
FastAPI application for uploading images to S3 and integrating with existing MCP tools.
"""

import json
import os
import io
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
from typing import List
import mimetypes
from tools import file_util, image_util
import contract_crew
from tools.s3_util import upload_file_object
from utils import logger
from chat import chat_service
from chat.models import ChatRequest, ChatResponse




# Load environment variables
load_dotenv()

app = FastAPI(title="CIS API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def yield_output(streamingStatus, type, message = None, data = None):
    jsn = {"type": type, "streamingStatus": streamingStatus.lower()}
    if data:
        jsn['data'] = data
    if message:
        jsn['message'] = message
    return f"data: {json.dumps(jsn)}\n\n"



@app.post("/analyze-contracts")
async def upload(files: List[UploadFile] = File(...)):
    """
    Upload multiple files to S3 bucket using s3_util
    """
    try:
        logger.info(f"Starting upload of {len(files)} files")
        uploaded_files = []
        
        for file in files:
            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            s3_key = f"uploads/{unique_filename}"
            
            logger.info(f"Processing file: {file.filename} -> {s3_key}")
            
            # Get file content
            file_content = await file.read()
            
            # Create a file-like object from the content
            file_object = io.BytesIO(file_content)

            # Determine content type
            content_type, _ = mimetypes.guess_type(file.filename)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Upload using s3_util
            result_url = upload_file_object(file_object, s3_key, content_type)
            
            if "Error" in result_url or "not found" in result_url or "not available" in result_url:
                logger.error(f"Upload failed for {file.filename}: {result_url}")
                raise HTTPException(status_code=500, detail=f"Upload failed: {result_url}")
            
            uploaded_files.append({
                "original_filename": file.filename,
                "s3_key": s3_key,
                "url": result_url,
                "content_type": content_type,
                "size": len(file_content)
            })

            logger.info(f"Successfully uploaded {file.filename} to {result_url}")
            # Save to temp file for ingestion

            file_type = file.filename.split('.')[-1]
            temp_file_path = image_util.save_to_temp(file_content, "contract_ingestion", file_type)
            if(file_type == "pdf"):
                file_content = file_util.read_pdf(temp_file_path)
            elif(file_type == "docx"):
                file_content = file_util.read_docx(temp_file_path)
            elif(file_type == "txt"):
                file_content = file_util.read_txt(temp_file_path)
            elif(file_type == "jpg" or file_type == "jpeg" or file_type == "png"):
                file_content = file_util.read_image(temp_file_path)
            else:
                return {"success": False, "message": "Only PDF, DOCX, TXT, JPG, JPEG, and PNG files are supported for now"}
            
            contents = contract_crew.read_contract_with_crewai(file_content)
        return {
            "success": True,
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "data": contents
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint for general questions and contract-related inquiries
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

@app.get("/chat/capabilities")
async def chat_capabilities():
    """
    Get chat system capabilities and available features
    """
    try:
        return chat_service.get_capabilities()
    except Exception as e:
        logger.error(f"Chat capabilities error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get capabilities")

@app.get("/chat/agents")
async def chat_agents():
    """
    Get information about available chat agents
    """
    try:
        return chat_service.get_agent_info()
    except Exception as e:
        logger.error(f"Chat agents error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get agent info")

@app.get("/chat/sessions")
async def get_chat_sessions():
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

@app.get("/chat/analytics")
async def chat_analytics():
    """
    Get chat analytics and performance data
    """
    try:
        return chat_service.get_analytics()
    except Exception as e:
        logger.error(f"Chat analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@app.delete("/chat/sessions/{session_id}")
async def end_chat_session(session_id: str):
    """
    End a specific chat session
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

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI documentation
    """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="CIS API Documentation",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/openapi.json", include_in_schema=False)
async def openapi():
    """
    OpenAPI specification
    """
    return get_openapi(
        title="CIS - Contract Intelligence System API",
        version="1.0.0",
        description="""
        ## CIS API Documentation
        
        ### Contract Intelligence System
        
        This API provides contract analysis and intelligent chat capabilities using CrewAI agents.
        
        ### Main Features:
        - **Contract Analysis**: Upload and analyze contracts (PDF, DOCX, TXT, images)
        - **Intelligent Chat**: General questions and contract expertise
        - **Multi-Agent System**: Specialized AI agents for different domains
        
        ### Quick Start:
        1. Use `/chat` for general questions and contract inquiries
        2. Use `/analyze-contracts` for contract file analysis
        3. Check `/chat/capabilities` for available features
        
        ### Authentication:
        Currently no authentication required (configure as needed for production).
        
        ### Rate Limiting:
        Currently no rate limiting implemented (configure as needed for production).
        
        ### Support:
        For API support, contact ravi.sahu2017@gmail.com
        """,
        routes=app.routes,
        servers=[
            {"url": "http://localhost:8001", "description": "Development server"},
            {"url": "https://unhappy-edgy-challenge.ngrok-free.dev", "description": "Production server"},
        ],
        contact={
            "name": "Ravi Sahu",
            "email": "ravi.sahu2017@gmail.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
    )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "cis-api"}

if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
