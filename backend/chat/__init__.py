"""
Chat Layer - Package Initialization
Provides easy access to chat functionality
"""

from .service import chat_service
from .models import ChatRequest, ChatResponse, ChatSession
from .agents import get_agent_by_intent
from .intent_classifier import intent_classifier

__all__ = [
    'chat_service',
    'ChatRequest', 
    'ChatResponse',
    'ChatSession',
    'get_agent_by_intent',
    'intent_classifier'
]

# Version info
__version__ = '1.0.0'
__description__ = 'CrewAI-powered chat service for contract intelligence system'
__author__ = 'Ravi Sahu'
__email__ = 'ravi.sahu2017@gmail.com'

