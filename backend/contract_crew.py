"""
CrewAI-based Contract Intelligence System
Implements the multi-agent architecture for contract analysis
"""

import os
import json

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
from objects import ContractObject, ClauseAnalysisResult
from utils import logger


def get_llm(temperature: float = 0.1):
    return LLM(
        base_url="https://openrouter.ai/api/v1",
        model= "openrouter/meta-llama/llama-3.2-3b-instruct",
        api_key= os.environ.get("OPENAI_API_KEY"),
        temperature=temperature
    )


# Define specialized agents based on your architecture

legal_agent = Agent(
    role='Legal Contract Analyst',
    goal='Analyze legal aspects of contracts including liability, IP, and compliance',
    backstory=(
        "You are an expert legal attorney with 15 years of experience in contract law."
        "You specialize in identifying legal risks, liability clauses, intellectual property issues"
        "and ensuring regulatory compliance in contracts."
    ),
    verbose=True,
    allow_delegation=False,
    llm=get_llm(0.1)
)

financial_agent = Agent(
    role='Financial Risk Analyst',
    goal='Analyze financial aspects including pricing, penalties, and payment terms',
    backstory="""You are a seasoned financial analyst with expertise in contract economics.
    You identify financial risks, pricing structures, payment terms, penalties, and cost implications
    in business contracts.""",
    verbose=True,
    allow_delegation=False,
    llm=get_llm(0.1)
)

operations_agent = Agent(
    role='Operations Analyst',
    goal='Analyze operational aspects including SLAs, delivery terms, and service requirements',
    backstory="""You are an operations expert with deep experience in service delivery and logistics.
    You analyze SLAs, delivery timelines, service requirements, and operational constraints in contracts.""",
    verbose=True,
    allow_delegation=False,
    llm=get_llm(0.1)
)

coordinator_agent = Agent(
    role='Contract Intelligence Coordinator',
    goal='Coordinate multi-agent analysis and generate comprehensive contract insights',
    backstory="""You are a senior contract intelligence coordinator who synthesizes insights from
    legal, financial, and operational analysis to provide holistic contract recommendations and risk assessments.""",
    verbose=True,
    allow_delegation=True,
    llm=get_llm(0.1)
)


def create_contract_crew(tasks: list[Task]) -> Crew:
    """Create and configure the contract analysis crew"""
    
    return Crew(
        agents=[legal_agent, financial_agent, operations_agent],
        tasks=tasks,
        manager_agent=coordinator_agent,
        process=Process.hierarchical,
        verbose=True
    )


def analyze_contract_clauses(text_content: str) -> any:
    """Analyze contract clauses using specialized agents"""
    
    # Legal analysis task
    legal_task = Task(
        description=f"""
        Analyze the legal aspects of this contract text:
        
        {text_content[:3000]}
        
        Focus on:
        - Liability clauses and limitations
        - Intellectual property provisions
        - Confidentiality requirements
        - Compliance and regulatory issues
        - Legal risks and obligations
        
        For each identified clause, provide:
        1. Clause type
        2. Content summary
        3. Risk score (0-100)
        4. Risk level (High/Medium/Low)
        5. Recommendations
        
        Return as a structured analysis of legal risks.
        """,
        agent=legal_agent,
        expected_output="Detailed legal risk analysis with identified clauses and recommendations",
        output_pydantic=ClauseAnalysisResult
    )
    
    # Financial analysis task
    financial_task = Task(
        description=f"""
        Analyze the financial aspects of this contract text:
        
        {text_content[:3000]}
        
        Focus on:
        - Payment terms and schedules
        - Pricing structures
        - Penalties and fees
        - Financial obligations
        - Cost-related risks
        
        For each identified clause, provide:
        1. Clause type
        2. Content summary
        3. Risk score (0-100)
        4. Risk level (High/Medium/Low)
        5. Recommendations
        
        Return as a structured analysis of financial risks.
        """,
        agent=financial_agent,
        expected_output="Detailed financial risk analysis with identified clauses and recommendations",
        output_pydantic=ClauseAnalysisResult
    )
    
    # Operations analysis task
    operations_task = Task(
        description=f"""
        Analyze the operational aspects of this contract text:
        
        {text_content[:3000]}
        
        Focus on:
        - Service Level Agreements (SLAs)
        - Delivery timelines
        - Performance requirements
        - Operational constraints
        - Service delivery risks
        
        For each identified clause, provide:
        1. Clause type
        2. Content summary
        3. Risk score (0-100)
        4. Risk level (High/Medium/Low)
        5. Recommendations
        
        Return as a structured analysis of operational risks.
        """,
        agent=operations_agent,
        expected_output="Detailed operational risk analysis with identified clauses and recommendations",
        output_pydantic=ClauseAnalysisResult
    )
    
    # Coordination task
    coordination_task = Task(
        description="""
        Synthesize the legal, financial, and operational analyses into a comprehensive contract assessment.
        
        Combine all identified clauses and:
        1. Calculate overall risk score
        2. Prioritize risks by severity
        3. Provide consolidated recommendations
        4. Generate executive summary
        
        Return a complete clause analysis with all identified risks and overall assessment.
        """,
        agent=coordinator_agent,
        expected_output="Comprehensive contract analysis with all clauses, risks, and overall risk score",
        output_pydantic=ContractObject
    )
    
    crew = create_contract_crew(tasks=[legal_task, financial_task, operations_task, coordination_task])
    result = crew.kickoff()

    if hasattr(result, 'raw'):
        result_dict = json.loads(result.raw)
    else:
        result_dict = result
    
    return result_dict


def read_contract_with_crewai(text_content: str) -> any:
    """
    Main contract ingestion function using CrewAI multi-agent system
    """
    try:
        clause_analysis = analyze_contract_clauses(text_content)
        logger.info(f"Successfully created contract object: {clause_analysis}")
        return clause_analysis
    except Exception as e:
        logger.error(f"Error in CrewAI contract ingestion: {str(e)}")
        raise e

