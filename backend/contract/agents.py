"""
Contract Layer - CrewAI Agents
Defines specialized agents for contract analysis functionality
"""

import os
from crewai import Agent
from crewai.llm import LLM
from utils import logger

def get_contract_llm(temperature: float = 0.1):
    """Get LLM configured for contract analysis"""
    return LLM(
        base_url="https://openrouter.ai/api/v1",
        model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=temperature  # Lower temperature for precise analysis
    )

# Legal Contract Analyst Agent
legal_agent = Agent(
    role='Legal Contract Analyst',
    goal='Analyze legal aspects of contracts including liability, IP, and compliance',
    backstory=(
        "You are an expert legal attorney with 15 years of experience in contract law. "
        "You specialize in identifying legal risks, liability clauses, intellectual property issues "
        "and ensuring regulatory compliance in contracts. You have deep knowledge of various "
        "contract types including MSAs, NDAs, SOWs, and service agreements. Your analysis is "
        "thorough, precise, and always considers legal implications and compliance requirements."
    ),
    verbose=True,
    allow_delegation=False,
    llm=get_contract_llm(0.1)
)

# Financial Risk Analyst Agent
financial_agent = Agent(
    role='Financial Risk Analyst',
    goal='Analyze financial aspects including pricing, penalties, and payment terms',
    backstory=(
        "You are a seasoned financial analyst with expertise in contract economics and risk management. "
        "You identify financial risks, pricing structures, payment terms, penalties, and cost implications "
        "in business contracts. You have extensive experience with financial modeling, risk assessment, "
        "and contract valuation. Your analysis focuses on financial exposure, payment security, and "
        "economic impact of contract terms."
    ),
    verbose=True,
    allow_delegation=False,
    llm=get_contract_llm(0.1)
)

# Operations Analyst Agent
operations_agent = Agent(
    role='Operations Analyst',
    goal='Analyze operational aspects including SLAs, delivery terms, and service requirements',
    backstory=(
        "You are an operations expert with deep experience in service delivery, logistics, and "
        "operational management. You analyze SLAs, delivery timelines, service requirements, and "
        "operational constraints in contracts. You understand the practical implications of "
        "operational clauses and can identify potential bottlenecks, resource requirements, and "
        "execution risks in contract commitments."
    ),
    verbose=True,
    allow_delegation=False,
    llm=get_contract_llm(0.1)
)

# Contract Intelligence Coordinator Agent
coordinator_agent = Agent(
    role='Contract Intelligence Coordinator',
    goal='Coordinate multi-agent analysis and generate comprehensive contract insights',
    backstory=(
        "You are a senior contract intelligence coordinator with 20+ years of experience in "
        "contract management and risk assessment. You excel at synthesizing insights from legal, "
        "financial, and operational analysis to provide holistic contract recommendations and "
        "risk assessments. You understand how different aspects of contracts interact and can "
        "prioritize risks effectively. Your coordination ensures comprehensive, actionable "
        "contract intelligence."
    ),
    verbose=True,
    allow_delegation=True,
    llm=get_contract_llm(0.2)
)

# Compliance Analyst Agent (Specialized)
compliance_agent = Agent(
    role='Compliance Analyst',
    goal='Ensure regulatory compliance and identify compliance risks',
    backstory=(
        "You are a compliance specialist with expertise in regulatory requirements across "
        "multiple industries and jurisdictions. You identify compliance risks, regulatory violations, "
        "and ensure contracts meet legal and regulatory standards. You have deep knowledge of "
        "GDPR, SOX, HIPAA, and other major compliance frameworks."
    ),
    verbose=True,
    allow_delegation=False,
    llm=get_contract_llm(0.1)
)

# Risk Assessment Agent (Specialized)
risk_assessment_agent = Agent(
    role='Risk Assessment Specialist',
    goal='Quantify and prioritize contract risks across all dimensions',
    backstory=(
        "You are a risk assessment expert who specializes in quantifying and prioritizing "
        "contract risks. You have developed sophisticated risk models and can assign accurate "
        "risk scores to different contract elements. Your analysis helps organizations make "
        "informed decisions about contract acceptance and negotiation strategies."
    ),
    verbose=True,
    allow_delegation=False,
    llm=get_contract_llm(0.1)
)

def get_agent_by_type(agent_type: str):
    """Get appropriate agent by type"""
    agent_map = {
        'legal': legal_agent,
        'financial': financial_agent,
        'operations': operations_agent,
        'coordinator': coordinator_agent,
        'compliance': compliance_agent,
        'risk_assessment': risk_assessment_agent
    }
    
    agent = agent_map.get(agent_type, legal_agent)
    logger.info(f"Selected agent: {agent.role} for type: {agent_type}")
    return agent

def get_all_contract_agents():
    """Return all available contract agents"""
    return {
        'legal_agent': legal_agent,
        'financial_agent': financial_agent,
        'operations_agent': operations_agent,
        'coordinator_agent': coordinator_agent,
        'compliance_agent': compliance_agent,
        'risk_assessment_agent': risk_assessment_agent
    }

def get_agent_capabilities():
    """Return capabilities of each agent"""
    return {
        'legal_agent': {
            'specialties': [
                'Legal risk identification',
                'Liability clause analysis',
                'IP rights assessment',
                'Regulatory compliance',
                'Contract validity',
                'Jurisdiction analysis'
            ],
            'best_for': [
                'Legal risk assessment',
                'Compliance checking',
                'Contract validity',
                'Regulatory review'
            ],
            'temperature': 0.1
        },
        'financial_agent': {
            'specialties': [
                'Financial risk analysis',
                'Payment terms review',
                'Pricing structure analysis',
                'Penalty assessment',
                'Cost implications',
                'Financial exposure'
            ],
            'best_for': [
                'Financial risk assessment',
                'Payment term analysis',
                'Cost-benefit analysis',
                'Financial due diligence'
            ],
            'temperature': 0.1
        },
        'operations_agent': {
            'specialties': [
                'SLA analysis',
                'Operational feasibility',
                'Delivery risk assessment',
                'Resource requirements',
                'Service level analysis',
                'Operational constraints'
            ],
            'best_for': [
                'Operational risk assessment',
                'SLA review',
                'Service delivery analysis',
                'Operational planning'
            ],
            'temperature': 0.1
        },
        'coordinator_agent': {
            'specialties': [
                'Multi-agent coordination',
                'Risk prioritization',
                'Executive summary generation',
                'Comprehensive assessment',
                'Strategic recommendations',
                'Holistic analysis'
            ],
            'best_for': [
                'Comprehensive contract review',
                'Executive summaries',
                'Risk prioritization',
                'Strategic recommendations'
            ],
            'temperature': 0.2
        },
        'compliance_agent': {
            'specialties': [
                'Regulatory compliance',
                'GDPR compliance',
                'Industry regulations',
                'Compliance risk assessment',
                'Audit requirements',
                'Legal compliance'
            ],
            'best_for': [
                'Compliance checking',
                'Regulatory review',
                'Audit preparation',
                'Compliance risk assessment'
            ],
            'temperature': 0.1
        },
        'risk_assessment_agent': {
            'specialties': [
                'Risk quantification',
                'Risk scoring',
                'Risk prioritization',
                'Risk modeling',
                'Exposure assessment',
                'Risk mitigation'
            ],
            'best_for': [
                'Risk scoring',
                'Risk quantification',
                'Risk prioritization',
                'Exposure analysis'
            ],
            'temperature': 0.1
        }
    }

def get_primary_analysis_agents(analysis_types: list):
    """Get primary agents based on analysis types"""
    agent_mapping = {
        'legal': [legal_agent],
        'financial': [financial_agent],
        'operations': [operations_agent],
        'compliance': [compliance_agent],
        'comprehensive': [legal_agent, financial_agent, operations_agent]
    }
    
    agents = []
    for analysis_type in analysis_types:
        if analysis_type in agent_mapping:
            agents.extend(agent_mapping[analysis_type])
    
    # Remove duplicates while preserving order
    unique_agents = []
    seen = set()
    for agent in agents:
        if agent.role not in seen:
            unique_agents.append(agent)
            seen.add(agent.role)
    
    return unique_agents
