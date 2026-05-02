"""
Common Utilities - Package Initialization
Shared utility functions for contract processing and analysis
"""

from .contract_utils import (
    extract_parties, extract_dates, extract_monetary_amounts,
    infer_contract_type, generate_file_hash, calculate_similarity,
    detect_changes, generate_contract_name, validate_contract_content
)
from .text_utils import (
    preprocess_text, extract_key_terms, calculate_text_complexity,
    clean_text, normalize_text
)

__all__ = [
    # Contract utilities
    'extract_parties',
    'extract_dates', 
    'extract_monetary_amounts',
    'infer_contract_type',
    'generate_file_hash',
    'calculate_similarity',
    'detect_changes',
    'generate_contract_name',
    'validate_contract_content',
    
    # Text utilities
    'preprocess_text',
    'extract_key_terms',
    'calculate_text_complexity',
    'clean_text',
    'normalize_text'
]

# Version info
__version__ = '1.0.0'
__description__ = 'Common utilities for CIS contract analysis system'
__author__ = 'Ravi Sahu'
__email__ = 'ravi.sahu2017@gmail.com'
