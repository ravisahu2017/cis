"""
Chat Layer - Crew Configuration
Defines and manages chat crews for different conversation types
"""

import time
from typing import Dict, List, Optional
from crewai import Task, Crew, Process
from crewai.llm import LLM
from .agents import get_agent_by_intent, get_all_agents, coordinator
from .intent_classifier import intent_classifier
from .models import ChatResponse
from tools.logger import logger

class ChatCrewManager:
    """Manages chat crews for different conversation types"""
    
    def __init__(self):
        self.active_crews: Dict[str, Crew] = {}
        self.crew_stats: Dict[str, Dict] = {}
    
    def create_single_agent_crew(self, intent: str, message: str) -> Crew:
        """Create a crew with a single specialized agent"""
        agent = get_agent_by_intent(intent)
        
        task = Task(
            description=f"""
            You are responding to a user message in a chat conversation.
            
            User message: "{message}"
            
            Guidelines:
            - Be helpful, accurate, and engaging
            - Keep responses conversational but informative
            - If you don't know something, admit it honestly
            - For legal/financial topics, include appropriate disclaimers
            - Adapt your tone to be friendly and approachable
            - Provide specific, actionable information when possible
            
            Provide a natural, helpful response that directly addresses the user's question.
            """,
            agent=agent,
            expected_output="A helpful, conversational response to the user's message"
        )
        
        return Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
    
    def create_multi_agent_crew(self, intent: str, message: str) -> Crew:
        """Create a crew with multiple agents for complex queries"""
        
        # Determine which agents to include based on intent
        agents_to_use = []
        
        if intent in ['contract', 'contract_analysis']:
            agents_to_use.append(get_agent_by_intent('contract'))
        
        if intent == 'business':
            agents_to_use.append(get_agent_by_intent('business'))
        
        # Always include general assistant for conversational support
        if len(agents_to_use) > 1:
            agents_to_use.append(get_agent_by_intent('general'))
        
        # Use coordinator for multi-agent scenarios
        if len(agents_to_use) > 1:
            agents_to_use.append(coordinator)
        
        # Create tasks for each agent
        tasks = []
        for i, agent in enumerate(agents_to_use):
            task_description = f"""
            You are contributing to a comprehensive response for this user message:
            
            "{message}"
            
            Your role: {agent.role}
            
            Provide your expert perspective on this message. Focus on your area of expertise
            while being conversational and helpful. If you're not the primary agent for this
            type of question, provide supporting insights that complement the main response.
            """
            
            task = Task(
                description=task_description,
                agent=agent,
                expected_output=f"Expert perspective from {agent.role}"
            )
            tasks.append(task)
        
        # Final coordination task if using multiple agents
        if len(agents_to_use) > 1:
            coordination_task = Task(
                description=f"""
                Synthesize the insights from all agents into a comprehensive, cohesive response
                to the user's message: "{message}"
                
                Create a natural, flowing response that incorporates the best insights from
                all perspectives while being conversational and directly addressing the user's question.
                Avoid mentioning that multiple agents were involved - present as a single, helpful response.
                """,
                agent=coordinator,
                expected_output="A comprehensive, synthesized response to the user"
            )
            tasks.append(coordination_task)
        
        return Crew(
            agents=agents_to_use,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )
    
    def process_message(self, message: str, session_id: str = None) -> ChatResponse:
        """Process a chat message and return response"""
        start_time = time.time()
        
        try:
            # Classify intent
            classification = intent_classifier.classify_intent(message)
            intent = classification['intent']
            confidence = classification['confidence']
            
            logger.info(f"Processing message with intent: {intent} (confidence: {confidence:.2f})")
            
            # Determine crew complexity
            use_multi_agent = (
                confidence < 0.7 or  # Low confidence, need multiple perspectives
                len(message.split()) > 50 or  # Long, complex message
                '?' in message.split()[-1]  # Question ending
            )
            
            # Create appropriate crew
            if use_multi_agent and intent in ['contract', 'business']:
                crew = self.create_multi_agent_crew(intent, message)
                agent_used = "Multi-Agent Team"
            else:
                crew = self.create_single_agent_crew(intent, message)
                agent_used = get_agent_by_intent(intent).role
            
            # Execute crew
            result = crew.kickoff()
            
            # Extract response
            if hasattr(result, 'result'):
                response_text = result.result
            elif hasattr(result, 'raw'):
                response_text = result.raw
            else:
                response_text = str(result)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Update stats
            self._update_crew_stats(intent, response_time_ms, True)
            
            # Create response
            chat_response = ChatResponse(
                response=response_text.strip(),
                session_id=session_id or "default",
                agent_used=agent_used,
                intent=intent,
                response_time_ms=response_time_ms
            )
            
            logger.info(f"Chat response generated in {response_time_ms}ms using {agent_used}")
            return chat_response
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            self._update_crew_stats(intent, int((time.time() - start_time) * 1000), False)
            
            # Fallback response
            return ChatResponse(
                response="I apologize, but I'm having trouble processing your message right now. Please try again later.",
                session_id=session_id or "error",
                agent_used="Error Handler",
                intent="error",
                response_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _update_crew_stats(self, intent: str, response_time: int, success: bool):
        """Update performance statistics"""
        if intent not in self.crew_stats:
            self.crew_stats[intent] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_response_time': 0,
                'avg_response_time': 0
            }
        
        stats = self.crew_stats[intent]
        stats['total_requests'] += 1
        
        if success:
            stats['successful_requests'] += 1
        
        stats['total_response_time'] += response_time
        stats['avg_response_time'] = stats['total_response_time'] / stats['total_requests']
    
    def get_performance_stats(self) -> Dict:
        """Return crew performance statistics"""
        return self.crew_stats

# Singleton instance
chat_crew_manager = ChatCrewManager()
