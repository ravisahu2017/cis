"""
Contract Layer - Package Initialization
Provides easy access to contract analysis functionality
"""

from .service import contract_service
from .models import ContractRequest, ContractResponse, ContractMetadata
from .agents import get_agent_by_type, get_all_contract_agents
from .crew import contract_crew_manager
from .contract_utils import ContractUtils
from .mock_data import get_mock_analysis

__all__ = [
    'contract_service',
    'ContractRequest',
    'ContractResponse', 
    'ContractMetadata',
    'get_agent_by_type',
    'get_all_contract_agents',
    'contract_crew_manager',
    'ContractUtils',
    'get_mock_analysis'
]

# Version info
__version__ = '1.0.0'
__description__ = 'CrewAI-powered contract analysis service for contract intelligence system'
__author__ = 'Ravi Sahu'
__email__ = 'ravi.sahu2017@gmail.com'
