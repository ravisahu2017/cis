"""
API Layer - Package Initialization
Provides organized API endpoints for different features
"""

from .chat_router import chat_router
from .contract_router import contract_router
from .file_router import file_router
from .health_router import health_router

__all__ = [
    'chat_router',
    'contract_router', 
    'file_router',
    'health_router'
]

# Version info
__version__ = '1.0.0'
__description__ = 'Organized API layer for CIS backend'
__author__ = 'Ravi Sahu'
__email__ = 'ravi.sahu2017@gmail.com'
