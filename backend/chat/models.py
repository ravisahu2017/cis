"""
Chat Layer - Pydantic Models
Defines data structures for chat functionality
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(description="Message role: 'user' or 'assistant'")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(description="Message timestamp")
    agent_used: Optional[str] = Field(default=None, description="Which agent handled this message")

class ChatRequest(BaseModel):
    """Incoming chat request"""
    message: str = Field(description="User's question or message")
    session_id: Optional[str] = Field(default=None, description="Chat session identifier")
    context: Optional[List[ChatMessage]] = Field(default=None, description="Previous chat history")
    user_id: Optional[str] = Field(default=None, description="User identifier")

class ChatResponse(BaseModel):
    """Chat response to user"""
    response: str = Field(description="AI response to user message")
    session_id: str = Field(description="Chat session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    agent_used: str = Field(description="Which agent handled the request")
    intent: str = Field(description="Classified intent (general/contract)")
    response_time_ms: Optional[int] = Field(default=None, description="Response time in milliseconds")

class ChatSession(BaseModel):
    """Chat session information"""
    session_id: str = Field(description="Unique session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    message_count: int = Field(default=0)
    context: List[ChatMessage] = Field(default_factory=list)

class ChatCapabilities(BaseModel):
    """Chat system capabilities"""
    supported_intents: List[str] = Field(description="Supported conversation intents")
    agent_types: List[str] = Field(description="Available agent types")
    features: List[str] = Field(description="Available features")
    limitations: List[str] = Field(description="System limitations")

class ChatAnalytics(BaseModel):
    """Chat analytics data"""
    total_sessions: int = Field(default=0)
    total_messages: int = Field(default=0)
    avg_response_time: float = Field(default=0.0)
    intent_distribution: Dict[str, int] = Field(default_factory=dict)
    agent_usage: Dict[str, int] = Field(default_factory=dict)
