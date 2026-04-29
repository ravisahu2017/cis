"""
CrewAI-based Contract Intelligence System
Implements the multi-agent architecture for contract analysis
"""

from cgi import test
import os
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from crewai.llm import LLM
from pydantic import BaseModel, Field
from typing import List, Optional, Type
from objects import ContractObject, ClauseRisk
from datetime import date
import re
import fitz  # PyMuPDF
from tools.logger import logger

@tool("pdf_extraction_tool")
def pdf_extraction_tool(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        doc = fitz.open(file_path)
        text_content = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text()
        doc.close()
        logger.info(f"Extracted {len(text_content)} characters from PDF")
        return text_content
    except Exception as e:
        logger.error(f"Error extracting PDF: {str(e)}")
        raise e

def get_llm(temperature: float = 0.1):
    return LLM(
        base_url="https://openrouter.ai/api/v1",
        model= "openrouter/nvidia/nemotron-nano-9b-v2:free",# or any OpenRouter model
        api_key= os.environ["OPENAI_API_KEY"],
        temperature=temperature
    )

class ContractMetadata(BaseModel):
    contract_type: str = Field(description="e.g., MSA, NDA, SOW")
    effective_date: Optional[str] = Field(description="Date the contract becomes effective")
    expiration_date: Optional[str] = Field(description="Date the contract expires")
    parties: List[str] = Field(description="List of all entities involved in the contract")
    governing_law: Optional[str] = Field(description="Jurisdiction or governing law")


class ClauseAnalysisResult(BaseModel):
    clauses: List[ClauseRisk] = Field(description="List of analyzed clauses with risk scores")
    overall_risk_score: int = Field(description="Overall contract risk score (0-100)")


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
    tools=[pdf_extraction_tool],
    llm=get_llm(0.1)
)

# test_agent = Agent(
#     role="Trend Analyst (Cultural Curator)",
#     goal="Define the target audience, brand voice, and Identify high-velocity Gen Z aesthetics (Y2K, Gorpcore, etc.)",
#     backstory=(
#         "You are a seasoned data-driven marketing guru. You understand genz psychology and "
#         "how to position a product to make it irresistible to early adopters. "
#         "You always base your strategies rigidly on the historical data provided to you."
#     ),
#     verbose=True,
#     llm= get_llm(0.1),
#     tools=[search_tool],
#     allow_delegation=False
# )

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


def create_contract_crew() -> Crew:
    """Create and configure the contract analysis crew"""
    
    return Crew(
        agents=[legal_agent, financial_agent, operations_agent, coordinator_agent],
        process=Process.sequential,
        verbose=True,
        memory=True
    )


def extract_contract_metadata(text_content: str) -> ContractMetadata:
    """Extract basic contract metadata using coordinator agent"""
    
    task = Task(
        description=f"""
        Extract structured metadata from the following contract text:
        
        {text_content[:2000]}  # Limit to first 2000 chars for context
        
        Focus on identifying:
        1. Contract type (MSA, NDA, SOW, etc.)
        2. Effective date
        3. Expiration date
        4. All parties involved
        5. Governing law/jurisdiction
        
        Return the information in a structured format.
        """,
        agent=coordinator_agent,
        output_pydantic=ContractMetadata,
    )
    
    crew = create_contract_crew()
    result = crew.kickoff(tasks=[task])
    
    
    return result


def analyze_contract_clauses(text_content: str) -> ClauseAnalysisResult:
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
        expected_output="Detailed legal risk analysis with identified clauses and recommendations"
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
        expected_output="Detailed financial risk analysis with identified clauses and recommendations"
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
        expected_output="Detailed operational risk analysis with identified clauses and recommendations"
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
        expected_output="Comprehensive contract analysis with all clauses, risks, and overall risk score"
    )
    
    crew = create_contract_crew()
    result = crew.kickoff(tasks=[legal_task, financial_task, operations_task, coordination_task])
    
    # Parse result to create ClauseAnalysisResult
    # This is simplified - enhance based on actual CrewAI output format
    clauses = []
    overall_risk_score = 50  # Default medium risk
    
    # Add parsing logic for CrewAI output
    # You'll need to customize this based on how CrewAI returns results
    
    return ClauseAnalysisResult(clauses=clauses, overall_risk_score=overall_risk_score)


def read_contract_with_crewai(file_path: str) -> ContractObject:
    """
    Main contract ingestion function using CrewAI multi-agent system
    """
    try:
        # 1. Extract text from PDF
        text_content = ""
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text()
        doc.close()
        
        logger.info(f"Extracted {len(text_content)} characters from {file_path}")
        
        # 2. Extract metadata using coordinator agent
        metadata = extract_contract_metadata(text_content)
        logger.info(f"Extracted metadata: {metadata}")
        
        # 3. Analyze clauses using multi-agent crew
        clause_analysis = analyze_contract_clauses(text_content)
        logger.info(f"Analyzed {len(clause_analysis.clauses)} clauses")
        
        # 4. Create contract object
        contract_data = ContractObject(
            contract_name=metadata.parties[0] if metadata.parties and len(metadata.parties) > 0 else "Unknown Contract",
            counterparty=metadata.parties[1] if metadata.parties and len(metadata.parties) > 1 else "Unknown Party",
            execution_date=date.today(),  # Would use metadata.effective_date if properly parsed
            expiry_date=date.today(),    # Would use metadata.expiration_date if properly parsed
            summary=f"{metadata.contract_type} contract between {', '.join(metadata.parties) if metadata.parties else 'Unknown parties'}",
            clauses=clause_analysis.clauses,
            overall_risk_score=clause_analysis.overall_risk_score,
            legal_risk_score=0,  # Would calculate from legal clauses
            financial_risk_score=0,  # Would calculate from financial clauses
            operational_risk_score=0,  # Would calculate from operational clauses
        )
        
        logger.info(f"Successfully created contract object: {contract_data.contract_name}")
        return contract_data
        
    except Exception as e:
        logger.error(f"Error in CrewAI contract ingestion: {str(e)}")
        raise e
