"""
Storage Layer - Package Initialization
Provides database and storage functionality for contract analysis results
"""

from .database import DatabaseManager
from .models import ContractRecord, ContractVersion, AnalysisRecord, TestRecord
from .repository import AnalysisRepository, ContractRepository, TestRepository

__all__ = [
    'DatabaseManager',
    'ContractRecord',
    'ContractVersion', 
    'AnalysisRecord',
    'TestRecord',
    'AnalysisRepository',
    'ContractRepository',
    'TestRepository'
]

# Version info
__version__ = '1.0.0'
__description__ = 'Storage layer for CIS contract analysis system'
__author__ = 'Ravi Sahu'
__email__ = 'ravi.sahu2017@gmail.com'
