"""
Common Utilities - Package Initialization
Shared utility functions for contract processing and analysis
"""

# Note: contract_utils moved to contract package to avoid circular imports
from .text_utils import (
    preprocess_text, calculate_text_complexity,
    clean_text, normalize_text, tokenize_text, remove_stopwords, extract_sentences
)
from .json_utils import (
    safe_json_serialize, safe_json_dumps, safe_json_loads, safe_parse_json_field
)
from .logger import logger
from .file_util import read_pdf, read_docx, read_txt, read_image


__all__ = [
    # Text utilities
    'preprocess_text',
    'clean_text', 
    'normalize_text',
    'calculate_text_complexity',
    'tokenize_text',
    'remove_stopwords',
    'extract_sentences'

    # JSON utilities
    'safe_json_serialize',
    'safe_json_dumps',
    'safe_json_loads',
    'safe_parse_json_field',

    # File utilities
    'read_pdf',
    'read_docx',
    'read_txt',
    'read_image',

    # Logger
    'logger'
]

# Version info
__version__ = '1.0.0'
__description__ = 'Common utilities for CIS contract analysis system'
__author__ = 'Ravi Sahu'
__email__ = 'ravi.sahu2017@gmail.com'
