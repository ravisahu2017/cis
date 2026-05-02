"""
File Upload API Router
Provides file upload and S3 integration endpoints
"""

import json
import io
import uuid
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import mimetypes
from tools import file_util, image_util
from tools.s3_util import upload_file_object
from tools.logger import logger

file_router = APIRouter(
    prefix="/files",
    tags=["File Upload"],
    responses={404: {"description": "Not found"}},
)

def yield_output(streaming_status: str, type: str, message: Optional[str] = None, data: Optional[Dict] = None) -> str:
    """Helper function for streaming responses"""
    jsn = {"type": type, "streamingStatus": streaming_status.lower()}
    if data:
        jsn['data'] = data
    if message:
        jsn['message'] = message
    return f"data: {json.dumps(jsn)}\n\n"

@file_router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    analyze_contracts: Optional[bool] = Form(False),
    user_id: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Upload multiple files to S3 bucket with optional contract analysis
    
    - **files**: List of files to upload
    - **analyze_contracts**: Whether to perform contract analysis on uploaded files
    - **user_id**: Optional user identifier
    
    Returns upload results and optional contract analysis
    """
    try:
        logger.info(f"Starting upload of {len(files)} files")
        uploaded_files = []
        contract_analyses = []
        
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
            
            # Optional contract analysis
            if analyze_contracts and file_extension.lower() in ['pdf', 'docx', 'txt']:
                try:
                    # Save to temp file for analysis
                    temp_file_path = image_util.save_to_temp(file_content, "contract_ingestion", file_extension)
                    
                    # Perform contract analysis
                    from contract import contract_service
                    from contract.models import ContractRequest, AnalysisType
                    
                    # Extract text content
                    if file_extension.lower() == 'pdf':
                        text_content = file_util.read_pdf(temp_file_path)
                    elif file_extension.lower() == 'docx':
                        text_content = file_util.read_docx(temp_file_path)
                    elif file_extension.lower() == 'txt':
                        text_content = file_util.read_txt(temp_file_path)
                    else:
                        text_content = ""
                    
                    if text_content and len(text_content.strip()) >= 100:
                        contract_request = ContractRequest(
                            file_content=text_content,
                            analysis_types=[AnalysisType.COMPREHENSIVE],
                            user_id=user_id
                        )
                        
                        contract_response = contract_service.analyze_contract(contract_request)
                        
                        contract_analyses.append({
                            "filename": file.filename,
                            "analysis_id": contract_response.analysis_id,
                            "success": contract_response.success,
                            "overall_risk_score": contract_response.analysis.overall_risk_score if contract_response.analysis else None,
                            "risk_level": contract_response.analysis.risk_level if contract_response.analysis else None,
                            "processing_time_ms": contract_response.processing_time_ms
                        })
                    else:
                        logger.warning(f"Insufficient text content for contract analysis: {file.filename}")
                        
                except Exception as e:
                    logger.error(f"Contract analysis failed for {file.filename}: {str(e)}")
                    contract_analyses.append({
                        "filename": file.filename,
                        "analysis_id": None,
                        "success": False,
                        "error": str(e)
                    })
            
            logger.info(f"Successfully uploaded {file.filename} to {result_url}")
        
        response_data = {
            "success": True,
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files": uploaded_files
        }
        
        if contract_analyses:
            response_data["contract_analyses"] = contract_analyses
        
        logger.info(f"Upload completed successfully. {len(uploaded_files)} files processed.")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@file_router.post("/upload-stream")
async def upload_files_stream(
    files: List[UploadFile] = File(...),
    analyze_contracts: Optional[bool] = Form(False),
    user_id: Optional[str] = Form(None)
) -> StreamingResponse:
    """
    Upload files with streaming response for real-time progress updates
    
    - **files**: List of files to upload
    - **analyze_contracts**: Whether to perform contract analysis
    - **user_id**: Optional user identifier
    
    Returns streaming response with progress updates
    """
    async def generate():
        try:
            # Send initial status
            yield yield_output("Started", "status", f"Starting upload of {len(files)} files")
            
            uploaded_files = []
            
            for i, file in enumerate(files):
                # Send file start status
                yield yield_output("Processing", "status", f"Processing file {i+1}/{len(files)}: {file.filename}")
                
                try:
                    # Generate unique filename
                    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
                    unique_filename = f"{uuid.uuid4()}.{file_extension}"
                    s3_key = f"uploads/{unique_filename}"
                    
                    # Get file content
                    file_content = await file.read()
                    
                    # Create file-like object
                    file_object = io.BytesIO(file_content)
                    
                    # Determine content type
                    content_type, _ = mimetypes.guess_type(file.filename)
                    if content_type is None:
                        content_type = 'application/octet-stream'
                    
                    # Upload to S3
                    result_url = upload_file_object(file_object, s3_key, content_type)
                    
                    if "Error" in result_url or "not found" in result_url:
                        yield yield_output("Error", "error", f"Upload failed for {file.filename}: {result_url}")
                        continue
                    
                    uploaded_files.append({
                        "original_filename": file.filename,
                        "s3_key": s3_key,
                        "url": result_url,
                        "content_type": content_type,
                        "size": len(file_content)
                    })
                    
                    # Send file completion status
                    yield yield_output("Completed", "status", f"Successfully uploaded {file.filename}")
                    
                except Exception as e:
                    yield yield_output("Error", "error", f"Failed to process {file.filename}: {str(e)}")
                    continue
            
            # Send final status
            yield yield_output("Completed", "status", f"Upload completed. {len(uploaded_files)} files uploaded successfully.")
            yield yield_output("Completed", "data", None, {"files": uploaded_files})
            
        except Exception as e:
            yield yield_output("Error", "error", f"Upload failed: {str(e)}")
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@file_router.get("/supported-types")
async def get_supported_file_types() -> Dict[str, Any]:
    """
    Get supported file types for upload and analysis
    """
    try:
        return {
            "upload_types": [
                {"extension": "pdf", "mime_type": "application/pdf", "description": "PDF documents"},
                {"extension": "docx", "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "description": "Word documents"},
                {"extension": "txt", "mime_type": "text/plain", "description": "Text files"},
                {"extension": "jpg", "mime_type": "image/jpeg", "description": "JPEG images"},
                {"extension": "jpeg", "mime_type": "image/jpeg", "description": "JPEG images"},
                {"extension": "png", "mime_type": "image/png", "description": "PNG images"},
                {"extension": "bmp", "mime_type": "image/bmp", "description": "Bitmap images"},
                {"extension": "tiff", "mime_type": "image/tiff", "description": "TIFF images"}
            ],
            "contract_analysis_types": ["pdf", "docx", "txt"],
            "max_file_size": "50MB",
            "max_files_per_request": 10
        }
    except Exception as e:
        logger.error(f"Supported types error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get supported types")

@file_router.get("/upload-stats")
async def get_upload_stats() -> Dict[str, Any]:
    """
    Get upload statistics and S3 bucket information
    """
    try:
        # This would typically query your database or S3 for statistics
        # For now, return placeholder data
        return {
            "total_uploads": 0,
            "total_size_mb": 0,
            "file_type_distribution": {
                "pdf": 0,
                "docx": 0,
                "txt": 0,
                "images": 0
            },
            "recent_uploads": [],
            "s3_bucket_status": "healthy"
        }
    except Exception as e:
        logger.error(f"Upload stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get upload stats")
