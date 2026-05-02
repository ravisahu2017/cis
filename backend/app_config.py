"""
Application Configuration
Centralized configuration for FastAPI app
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from tools.logger import logger

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Create FastAPI app
    app = FastAPI(
        title="CIS - Contract Intelligence System",
        description="AI-powered contract analysis and intelligent chat system",
        version="1.0.0",
        docs_url=None,  # We'll create custom docs
        redoc_url=None,
        openapi_url="/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify your frontend domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom OpenAPI docs
    setup_custom_docs(app)
    
    return app

def setup_custom_docs(app: FastAPI):
    """Setup custom OpenAPI documentation"""
    
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
        from fastapi.openapi.utils import get_openapi
        
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
            - **File Management**: Secure file upload and S3 integration
            - **Real-time Analytics**: Performance monitoring and insights
            
            ### Quick Start:
            1. Use `/chat` for general questions and contract inquiries
            2. Use `/contract/analyze` for contract file analysis
            3. Use `/files/upload` for file management
            4. Check `/health` for system status
            
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

def register_routers(app: FastAPI):
    """Register all API routers"""
    
    # Import routers
    from api.chat_router import chat_router
    from api.contract_router import contract_router
    from api.file_router import file_router
    from api.health_router import health_router
    from api.test_router import test_router
    
    # Register routers
    app.include_router(chat_router)
    app.include_router(contract_router)
    app.include_router(file_router)
    app.include_router(health_router)
    app.include_router(test_router)
    
    logger.info("All API routers registered successfully")

def setup_middleware(app: FastAPI):
    """Setup middleware for the application"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Logging middleware
    @app.middleware("http")
    async def log_requests(request, call_next):
        """Log all requests"""
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    
    # Concurrency middleware
    @app.middleware("http")
    async def add_concurrency_headers(request, call_next):
        """Add headers to handle concurrent requests"""
        response = await call_next(request)
        response.headers["X-Content-Type"] = "application/json"
        response.headers["Keep-Alive"] = "timeout=5, max=100"
        return response
    
    # Security headers middleware
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        """Add security headers"""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        logger.warning(f"404 Not Found: {request.url}")
        return {"error": "Resource not found", "path": str(request.url)}
    
    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        logger.error(f"500 Internal Error: {request.url} - {str(exc)}")
        return {"error": "Internal server error", "path": str(request.url)}
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled Exception: {request.url} - {str(exc)}")
        return {"error": "An unexpected error occurred", "path": str(request.url)}
