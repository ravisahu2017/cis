"""
Contract Layer - Task Definitions
Defines and creates tasks for different types of contract analysis
"""

from typing import List
from crewai import Task
from .agents import get_agent_by_type, coordinator_agent
from .models import AnalysisType, ContractAnalysis, ContractMetadata, ClauseAnalysisResult
from tools.logger import logger

def create_legal_analysis_task(text_content: str) -> Task:
    """Create legal analysis task"""
    legal_agent = get_agent_by_type('legal')
    
    return Task(
        description=f"""
        Analyze the legal aspects of this contract text:
        
        {text_content[:3000]}
        
        Focus on identifying and analyzing:
        - Liability clauses and limitations
        - Intellectual property provisions and rights
        - Confidentiality requirements and data protection
        - Compliance and regulatory issues
        - Legal risks and obligations
        - Termination clauses and conditions
        - Dispute resolution mechanisms
        - Governing law and jurisdiction
        
        For each identified clause, provide:
        1. Clause type (e.g., 'Liability', 'IP Rights', 'Confidentiality')
        2. Content summary (brief description)
        3. Risk score (0-100, where 100 is highest risk)
        4. Risk level (High/Medium/Low)
        5. Specific recommendations for risk mitigation
        
        Pay special attention to:
        - Unusual liability limitations
        - IP ownership clauses
        - Data protection requirements
        - Regulatory compliance issues
        - Ambiguous legal language
        
        Return a detailed legal risk analysis with all identified clauses and recommendations.
        """,
        agent=legal_agent,
        expected_output="Detailed legal risk analysis with identified clauses, risk scores, and recommendations",
        output_pydantic=ClauseAnalysisResult
    )

def create_financial_analysis_task(text_content: str) -> Task:
    """Create financial analysis task"""
    financial_agent = get_agent_by_type('financial')
    
    return Task(
        description=f"""
        Analyze the financial aspects of this contract text:
        
        {text_content[:3000]}
        
        Focus on identifying and analyzing:
        - Payment terms and schedules
        - Pricing structures and fee arrangements
        - Penalties, fines, and liquidated damages
        - Financial obligations and commitments
        - Cost-related risks and exposures
        - Payment security mechanisms
        - Currency and exchange rate considerations
        - Financial performance requirements
        
        For each identified clause, provide:
        1. Clause type (e.g., 'Payment Terms', 'Penalties', 'Pricing')
        2. Content summary (brief description)
        3. Risk score (0-100, where 100 is highest risk)
        4. Risk level (High/Medium/Low)
        5. Specific financial recommendations
        
        Pay special attention to:
        - Unfavorable payment terms
        - Excessive penalties or liquidated damages
        - Unclear pricing structures
        - Currency exchange risks
        - Payment security issues
        
        Return a detailed financial risk analysis with all identified clauses and recommendations.
        """,
        agent=financial_agent,
        expected_output="Detailed financial risk analysis with identified clauses, risk scores, and recommendations",
        output_pydantic=ClauseAnalysisResult
    )

def create_operations_analysis_task(text_content: str) -> Task:
    """Create operations analysis task"""
    operations_agent = get_agent_by_type('operations')
    
    return Task(
        description=f"""
        Analyze the operational aspects of this contract text:
        
        {text_content[:3000]}
        
        Focus on identifying and analyzing:
        - Service Level Agreements (SLAs) and performance metrics
        - Delivery timelines and milestones
        - Performance requirements and quality standards
        - Operational constraints and limitations
        - Service delivery risks and dependencies
        - Resource requirements and availability
        - Change management procedures
        - Operational responsibilities
        
        For each identified clause, provide:
        1. Clause type (e.g., 'SLA', 'Delivery', 'Performance')
        2. Content summary (brief description)
        3. Risk score (0-100, where 100 is highest risk)
        4. Risk level (High/Medium/Low)
        5. Specific operational recommendations
        
        Pay special attention to:
        - Unrealistic SLA requirements
        - Aggressive delivery timelines
        - Unclear performance metrics
        - Resource constraints
        - Operational dependencies
        
        Return a detailed operational risk analysis with all identified clauses and recommendations.
        """,
        agent=operations_agent,
        expected_output="Detailed operational risk analysis with identified clauses, risk scores, and recommendations",
        output_pydantic=ClauseAnalysisResult
    )

def create_compliance_analysis_task(text_content: str) -> Task:
    """Create compliance analysis task"""
    compliance_agent = get_agent_by_type('compliance')
    
    return Task(
        description=f"""
        Analyze the compliance aspects of this contract text:
        
        {text_content[:3000]}
        
        Focus on identifying and analyzing:
        - Regulatory compliance requirements
        - Industry-specific regulations
        - Data protection and privacy compliance
        - Anti-corruption and bribery provisions
        - Export control and trade compliance
        - Environmental compliance requirements
        - Labor law compliance
        - Audit and reporting requirements
        
        For each identified clause, provide:
        1. Clause type (e.g., 'Compliance', 'Data Protection', 'Regulatory')
        2. Content summary (brief description)
        3. Risk score (0-100, where 100 is highest risk)
        4. Risk level (High/Medium/Low)
        5. Specific compliance recommendations
        
        Pay special attention to:
        - Missing compliance provisions
        - Outdated regulatory references
        - Inadequate data protection
        - Non-compliance risks
        - Audit requirement gaps
        
        Return a detailed compliance risk analysis with all identified clauses and recommendations.
        """,
        agent=compliance_agent,
        expected_output="Detailed compliance risk analysis with identified clauses, risk scores, and recommendations",
        output_pydantic=ClauseAnalysisResult
    )

def create_metadata_extraction_task(text_content: str) -> Task:
    """Create metadata extraction task"""
    legal_agent = get_agent_by_type('legal')
    
    return Task(
        description=f"""
        Extract structured metadata from this contract text:
        
        {text_content[:3000]}
        
        Extract and identify:
        - Contract type (MSA, NDA, SOW, Service Agreement, etc.)
        - Effective date and expiration date
        - All parties involved in the contract
        - Governing law and jurisdiction
        - Total contract value (if specified)
        - Currency used for financial terms
        - Renewal terms and conditions
        - Termination notice periods
        - Key dates and milestones
        
        Look for:
        - Contract titles and headings
        - Date formats and references
        - Party names and addresses
        - Governing law clauses
        - Financial amounts and currencies
        - Renewal and termination provisions
        
        Return structured contract metadata with all identified information.
        """,
        agent=legal_agent,
        expected_output="Structured contract metadata with extracted information",
        output_pydantic=ContractMetadata
    )

def create_coordination_task(text_content: str, analysis_results: dict) -> Task:
    """Create coordination task to synthesize all analyses"""
    
    return Task(
        description=f"""
        Synthesize all contract analysis results into a comprehensive assessment.
        
        Original contract text:
        {text_content[:1000]}
        
        Analysis Results Available:
        {chr(10).join([f"{k}: {len(v) if isinstance(v, list) else 'Present'}" for k, v in analysis_results.items()])}
        
        Your coordination responsibilities:
        
        1. **Consolidate All Clauses**: Combine all identified clauses from legal, financial, operations, and compliance analyses
        2. **Calculate Overall Risk Score**: Compute weighted average of all risk scores
        3. **Prioritize Risks**: Rank clauses by overall business impact
        4. **Generate Executive Summary**: Create concise summary for business stakeholders
        5. **Provide Key Recommendations**: Top 5-7 actionable recommendations
        6. **Assess Contract Viability**: Overall assessment of contract acceptability
        
        Risk Scoring Guidelines:
        - Critical (80-100): Immediate attention required, may be deal-breaker
        - High (60-79): Significant concerns, requires negotiation
        - Medium (40-59): Moderate concerns, monitor closely
        - Low (0-39): Minor issues, standard contract language
        
        Executive Summary should include:
        - Overall contract risk level
        - Number and type of major risks identified
        - Key deal-breakers or negotiation points
        - Recommended next steps
        
        Return a complete contract analysis with:
        - Overall risk assessment
        - Consolidated clause list
        - Executive summary
        - Key recommendations
        - Processing statistics
        """,
        agent=coordinator_agent,
        expected_output="Comprehensive contract analysis with all risks, overall assessment, and recommendations",
        output_pydantic=ContractAnalysis
    )

def create_analysis_tasks(text_content: str, analysis_types: List[AnalysisType]) -> List[Task]:
    """Create appropriate tasks based on analysis types"""
    tasks = []
    
    # Always extract metadata first
    tasks.append(create_metadata_extraction_task(text_content))
    
    # Add analysis tasks based on requested types
    for analysis_type in analysis_types:
        if analysis_type == AnalysisType.LEGAL:
            tasks.append(create_legal_analysis_task(text_content))
        elif analysis_type == AnalysisType.FINANCIAL:
            tasks.append(create_financial_analysis_task(text_content))
        elif analysis_type == AnalysisType.OPERATIONS:
            tasks.append(create_operations_analysis_task(text_content))
        elif analysis_type == AnalysisType.COMPREHENSIVE:
            tasks.extend([
                create_legal_analysis_task(text_content),
                create_financial_analysis_task(text_content),
                create_operations_analysis_task(text_content)
            ])
    
    # Always add coordination task at the end
    tasks.append(create_coordination_task(text_content, {}))
    
    logger.info(f"Created {len(tasks)} tasks for analysis types: {[t.value for t in analysis_types]}")
    return tasks

def get_task_templates():
    """Return task templates for different analysis types"""
    return {
        'legal_analysis': {
            'focus_areas': [
                'Liability clauses', 'IP rights', 'Confidentiality', 
                'Compliance', 'Legal risks', 'Termination'
            ],
            'output_format': 'List[ClauseRisk]',
            'risk_factors': ['legal_exposure', 'compliance_risk', 'liability_limitation']
        },
        'financial_analysis': {
            'focus_areas': [
                'Payment terms', 'Pricing', 'Penalties', 
                'Financial obligations', 'Cost risks'
            ],
            'output_format': 'List[ClauseRisk]',
            'risk_factors': ['financial_exposure', 'payment_risk', 'cost_impact']
        },
        'operations_analysis': {
            'focus_areas': [
                'SLAs', 'Delivery', 'Performance', 
                'Operational constraints', 'Service risks'
            ],
            'output_format': 'List[ClauseRisk]',
            'risk_factors': ['operational_risk', 'delivery_risk', 'performance_risk']
        },
        'metadata_extraction': {
            'focus_areas': [
                'Contract type', 'Dates', 'Parties', 
                'Governing law', 'Financial values'
            ],
            'output_format': 'ContractMetadata',
            'risk_factors': []
        },
        'coordination': {
            'focus_areas': [
                'Risk consolidation', 'Executive summary', 
                'Recommendations', 'Overall assessment'
            ],
            'output_format': 'ContractAnalysis',
            'risk_factors': ['overall_risk', 'business_impact', 'strategic_risk']
        }
    }
