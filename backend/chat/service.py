"""
Chat Layer - Main Service
Orchestrates chat functionality and provides API interface
"""

import uuid
from typing import Optional, List, Dict
from datetime import datetime
from .models import ChatRequest, ChatResponse, ChatSession, ChatCapabilities
from .crew import chat_crew_manager
from .intent_classifier import intent_classifier
from .agents import get_agent_capabilities
from utils import logger

class ChatService:
    """Main chat service orchestrating all chat functionality"""
    
    def __init__(self):
        self.active_sessions: Dict[str, ChatSession] = {}
        self.session_timeout_minutes = 30
    
    def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat message and return response
        
        Args:
            request: ChatRequest with message and optional session info
            
        Returns:
            ChatResponse with AI response
        """
        try:
            # Get or create session
            session = self._get_or_create_session(request.session_id, request.user_id)
            
            # Add user message to session context
            user_message = {
                'role': 'user',
                'content': request.message,
                'timestamp': datetime.now().isoformat()
            }
            session.context.append(user_message)
            session.message_count += 1
            session.last_activity = datetime.now()
            
            # Process message through crew manager
            chat_response = chat_crew_manager.process_message(
                request.message, 
                session.session_id
            )
            
            # Add assistant response to session context
            assistant_message = {
                'role': 'assistant',
                'content': chat_response.response,
                'timestamp': chat_response.timestamp.isoformat(),
                'agent_used': chat_response.agent_used
            }
            session.context.append(assistant_message)
            
            # Update session
            self.active_sessions[session.session_id] = session
            
            logger.info(f"Processed message in session {session.session_id}")
            return chat_response
            
        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            raise e
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve chat session by ID"""
        return self.active_sessions.get(session_id)
    
    def get_active_sessions(self) -> List[ChatSession]:
        """Get all active sessions"""
        return list(self.active_sessions.values())
    
    def cleanup_sessions(self):
        """Remove inactive sessions"""
        current_time = datetime.now()
        inactive_sessions = []
        
        for session_id, session in self.active_sessions.items():
            time_diff = current_time - session.last_activity
            if time_diff.total_seconds() > (self.session_timeout_minutes * 60):
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleaned up inactive session: {session_id}")
        
        return len(inactive_sessions)
    
    def get_capabilities(self) -> ChatCapabilities:
        """Return chat system capabilities"""
        return ChatCapabilities(
            supported_intents=['general', 'contract', 'business', 'contract_analysis'],
            agent_types=['general_assistant', 'contract_expert', 'business_analyst', 'coordinator'],
            features=[
                'Intent classification',
                'Multi-agent coordination',
                'Session management',
                'Context awareness',
                'Performance analytics'
            ],
            limitations=[
                'Not legal advice',
                'General information only',
                'No file analysis in chat',
                'Session timeout after 30 minutes'
            ]
        )
    
    def get_agent_info(self) -> Dict:
        """Return information about available agents"""
        return get_agent_capabilities()
    
    def get_analytics(self) -> Dict:
        """Return chat analytics and performance data"""
        crew_stats = chat_crew_manager.get_performance_stats()
        
        # Calculate additional analytics
        total_sessions = len(self.active_sessions)
        total_messages = sum(session.message_count for session in self.active_sessions.values())
        
        # Intent distribution from recent sessions
        intent_counts = {'general': 0, 'contract': 0, 'business': 0, 'contract_analysis': 0}
        for session in self.active_sessions.values():
            for message in session.context[-10:]:  # Look at last 10 messages per session
                if message['role'] == 'user':
                    classification = intent_classifier.classify_intent(message['content'])
                    intent_counts[classification['intent']] += 1
        
        return {
            'active_sessions': total_sessions,
            'total_messages': total_messages,
            'crew_performance': crew_stats,
            'intent_distribution': intent_counts,
            'session_timeout_minutes': self.session_timeout_minutes
        }
    
    def _get_or_create_session(self, session_id: Optional[str], user_id: Optional[str]) -> ChatSession:
        """Get existing session or create new one"""
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.last_activity = datetime.now()
            return session
        
        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        session = ChatSession(
            session_id=new_session_id,
            user_id=user_id
        )
        
        self.active_sessions[new_session_id] = session
        logger.info(f"Created new chat session: {new_session_id}")
        return session
    
    def end_session(self, session_id: str) -> bool:
        """End a chat session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Ended chat session: {session_id}")
            return True
        return False

# Singleton instance
chat_service = ChatService()
