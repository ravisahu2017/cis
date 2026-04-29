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
from dotenv import load_dotenv
from typing import List
import mimetypes
from tools import image_util
import contract_crew
from tools.s3_util import upload_file_object
from tools.logger import logger




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
            temp_file_path = image_util.save_to_temp(file_content, "contract_ingestion", "pdf")
            contents = contract_crew.read_contract_with_crewai(temp_file_path)
            logger.info(f"Contract ingested: {contents}")
            

        
        logger.info(f"Upload completed successfully. {len(uploaded_files)} files processed.")
        
        return {
            "success": True,
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files": uploaded_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

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
