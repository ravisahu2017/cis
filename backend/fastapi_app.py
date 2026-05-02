#!/usr/bin/env python3
"""
CIS - Contract Intelligence System
Restructured FastAPI application with modular architecture
"""

import os
from dotenv import load_dotenv
from tools.logger import logger
from app_config import create_app, register_routers, setup_middleware, setup_exception_handlers

# Load environment variables
load_dotenv()

def main():
    """Main application entry point"""
    
    logger.info("Starting CIS FastAPI Application...")
    
    # Initialize database
    try:
        from storage.database import init_database
        db = init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        # Continue without database for now
    
    # Create FastAPI app
    app = create_app()
    
    # Setup components
    setup_middleware(app)
    setup_exception_handlers(app)
    register_routers(app)
    
    logger.info("CIS FastAPI Application configured successfully")
    return app

# Create app instance
app = main()

if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI server
    uvicorn.run(
        "fastapi_app:app",  # Use import string for reload
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=True  # Enable auto-reload for development
    )
