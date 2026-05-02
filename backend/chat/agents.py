"""
Chat Layer - CrewAI Agents
Defines specialized agents for chat functionality
"""

import os
from crewai import Agent
from crewai.llm import LLM
from tools.logger import logger

def get_chat_llm(temperature: float = 0.7):
    """Get LLM configured for chat conversations"""
    return LLM(
        base_url="https://openrouter.ai/api/v1",
        model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=temperature  # Higher temperature for more creative/conversational responses
    )

# General Assistant Agent
general_assistant = Agent(
    role='AI Assistant',
    goal='Provide helpful, accurate, and engaging responses to general user questions',
    backstory=(
        "You are a friendly and knowledgeable AI assistant with broad expertise across many topics. "
        "You excel at explaining complex concepts simply, providing helpful recommendations, "
        "and engaging in natural conversation. You're curious, patient, and always strive to be useful. "
        "You can discuss science, technology, business, arts, current events, and everyday topics. "
        "When you don't know something, you admit it honestly and suggest where the user might find reliable information."
    ),
    verbose=True,
    allow_delegation=False,
    llm=get_chat_llm(0.7)
)

# Contract Expert Agent  
contract_expert = Agent(
    role='Contract & Legal Expert',
    goal='Provide expert insights about contracts, legal terms, and business agreements',
    backstory=(
        "You are an experienced legal professional with deep expertise in contract law and business agreements. "
        "You can explain complex legal concepts in simple terms, analyze contract clauses, identify potential risks, "
        "and provide practical business advice. You understand various types of agreements (NDAs, MSAs, SOWs, etc.) "
        "and can explain their purposes and key provisions. "
        "IMPORTANT: You provide general information and education, not legal advice. "
        "Always include a disclaimer that users should consult qualified legal professionals for specific situations."
    ),
    verbose=True,
    allow_delegation=False,
    llm=get_chat_llm(0.3)  # Lower temperature for more precise legal information
)

# Business Analyst Agent
business_analyst = Agent(
    role='Business Strategy Analyst',
    goal='Provide insights on business operations, strategy, and financial matters',
    backstory=(
        "You are a seasoned business analyst with expertise in strategy, operations, and financial analysis. "
        "You help users understand business concepts, analyze market trends, evaluate opportunities, "
        "and make informed business decisions. You're skilled at breaking down complex business topics "
        "into actionable insights and practical advice. You can discuss topics like business models, "
        "competitive analysis, financial metrics, and strategic planning."
    ),
    verbose=True,
    allow_delegation=False,
    llm=get_chat_llm(0.5)
)

# Coordinator Agent (for complex multi-agent conversations)
coordinator = Agent(
    role='Conversation Coordinator',
    goal='Coordinate between specialized agents to provide comprehensive responses',
    backstory=(
        "You are an expert conversation coordinator who knows when to involve different specialists. "
        "You can identify when a question requires expertise from multiple domains and orchestrate "
        "collaborative responses. You ensure users get comprehensive, well-rounded answers by "
        "leveraging the right combination of agents when needed."
    ),
    verbose=True,
    allow_delegation=True,
    llm=get_chat_llm(0.6)
)

def get_agent_by_intent(intent: str):
    """Get appropriate agent based on classified intent"""
    agent_map = {
        'general': general_assistant,
        'contract': contract_expert,
        'business': business_analyst,
        'contract_analysis': contract_expert,
        'coordination': coordinator
    }
    
    agent = agent_map.get(intent, general_assistant)
    logger.info(f"Selected agent: {agent.role} for intent: {intent}")
    return agent

def get_all_agents():
    """Return all available chat agents"""
    return {
        'general_assistant': general_assistant,
        'contract_expert': contract_expert,
        'business_analyst': business_analyst,
        'coordinator': coordinator
    }

def get_agent_capabilities():
    """Return capabilities of each agent"""
    return {
        'general_assistant': {
            'specialties': ['General knowledge', 'Explanation', 'Conversation', 'Research'],
            'best_for': ['General questions', 'Learning', 'Casual conversation', 'Research help']
        },
        'contract_expert': {
            'specialties': ['Contract analysis', 'Legal terminology', 'Risk assessment', 'Compliance'],
            'best_for': ['Contract questions', 'Legal terms', 'Agreement review', 'Compliance guidance']
        },
        'business_analyst': {
            'specialties': ['Business strategy', 'Financial analysis', 'Market research', 'Operations'],
            'best_for': ['Business advice', 'Strategic planning', 'Financial questions', 'Market analysis']
        },
        'coordinator': {
            'specialties': ['Multi-domain coordination', 'Complex problem solving', 'Synthesis'],
            'best_for': ['Complex questions', 'Multi-faceted issues', 'Comprehensive analysis']
        }
    }
