"""
Contract Layer - Pydantic Models
Defines data structures for contract analysis functionality
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ContractType(str, Enum):
    """Supported contract types"""
    MSA = "msa"
    NDA = "nda"
    SOW = "sow"
    SERVICE_AGREEMENT = "service_agreement"
    SUPPLIER_CONTRACT = "supplier_contract"
    EMPLOYMENT_AGREEMENT = "employment_agreement"
    LEASE_AGREEMENT = "lease_agreement"
    OTHER = "other"

class RiskLevel(str, Enum):
    """Risk level classifications"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AnalysisType(str, Enum):
    """Analysis types available"""
    LEGAL = "legal"
    FINANCIAL = "financial"
    OPERATIONS = "operations"
    COMPREHENSIVE = "comprehensive"

class ClauseRisk(BaseModel):
    """Individual clause risk assessment"""
    clause_type: str = Field(description="Type of clause (e.g., 'Liability', 'Payment')")
    content_summary: str = Field(description="Brief summary of clause content")
    risk_score: int = Field(ge=0, le=100, description="Risk score from 0-100")
    risk_level: RiskLevel = Field(description="Risk level classification")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for this clause")
    location: Optional[str] = Field(default=None, description="Section/page location in contract")
    severity: Optional[str] = Field(default=None, description="Additional severity information")

class ContractMetadata(BaseModel):
    """Contract metadata extracted from analysis"""
    contract_type: Optional[ContractType] = Field(default=None, description="Type of contract")
    effective_date: Optional[datetime] = Field(default=None, description="Contract effective date")
    expiration_date: Optional[datetime] = Field(default=None, description="Contract expiration date")
    parties: List[str] = Field(default_factory=list, description="Parties involved in contract")
    governing_law: Optional[str] = Field(default=None, description="Governing law/jurisdiction")
    total_value: Optional[float] = Field(default=None, description="Total contract value")
    currency: Optional[str] = Field(default=None, description="Currency for financial values")
    renewal_terms: Optional[str] = Field(default=None, description="Renewal terms and conditions")
    termination_notice: Optional[str] = Field(default=None, description="Termination notice period")

class ContractAnalysis(BaseModel):
    """Complete contract analysis results"""
    contract_name: str = Field(description="Name/identifier of the contract")
    overall_risk_score: int = Field(ge=0, le=100, description="Overall contract risk score")
    risk_level: RiskLevel = Field(description="Overall risk level")
    legal_risk_score: int = Field(ge=0, le=100, description="Legal risk score")
    financial_risk_score: int = Field(ge=0, le=100, description="Financial risk score")
    operational_risk_score: int = Field(ge=0, le=100, description="Operational risk score")
    clauses: List[ClauseRisk] = Field(description="List of identified risky clauses")
    metadata: ContractMetadata = Field(description="Extracted contract metadata")
    executive_summary: str = Field(description="Executive summary of contract analysis")
    key_recommendations: List[str] = Field(description="Key recommendations for the contract")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="When analysis was performed")
    processing_time_ms: Optional[int] = Field(default=None, description="Processing time in milliseconds")

class ContractRequest(BaseModel):
    """Incoming contract analysis request"""
    file_path: Optional[str] = Field(default=None, description="Path to contract file")
    file_content: Optional[str] = Field(default=None, description="Raw text content of contract")
    analysis_types: List[AnalysisType] = Field(default=[AnalysisType.COMPREHENSIVE], description="Types of analysis to perform")
    contract_type_hint: Optional[ContractType] = Field(default=None, description="Hint about contract type")
    user_id: Optional[str] = Field(default=None, description="User requesting analysis")
    priority: Optional[str] = Field(default="normal", description="Analysis priority")

class ContractResponse(BaseModel):
    """Contract analysis response"""
    success: bool = Field(description="Whether analysis was successful")
    analysis: Optional[ContractAnalysis] = Field(default=None, description="Analysis results if successful")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    processing_time_ms: int = Field(description="Total processing time in milliseconds")
    analysis_id: str = Field(description="Unique identifier for this analysis")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    agents_used: List[str] = Field(description="List of agents used in analysis")

class ContractCapabilities(BaseModel):
    """Contract analysis system capabilities"""
    supported_file_types: List[str] = Field(description="Supported file formats")
    supported_contract_types: List[ContractType] = Field(description="Supported contract types")
    analysis_types: List[AnalysisType] = Field(description="Available analysis types")
    agent_types: List[str] = Field(description="Available agent types")
    features: List[str] = Field(description="System features")
    limitations: List[str] = Field(description="System limitations")

class ContractAnalytics(BaseModel):
    """Contract analysis analytics data"""
    total_analyses: int = Field(default=0)
    successful_analyses: int = Field(default=0)
    avg_processing_time: float = Field(default=0.0)
    contract_type_distribution: Dict[str, int] = Field(default_factory=dict)
    risk_level_distribution: Dict[str, int] = Field(default_factory=dict)
    agent_usage: Dict[str, int] = Field(default_factory=dict)
    common_clause_types: Dict[str, int] = Field(default_factory=dict)

class AnalysisSession(BaseModel):
    """Contract analysis session information"""
    session_id: str = Field(description="Unique session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    analyses_completed: int = Field(default=0)
    total_processing_time_ms: int = Field(default=0)
    contract_types_analyzed: List[ContractType] = Field(default_factory=list)
    status: str = Field(default="active", description="Session status")
