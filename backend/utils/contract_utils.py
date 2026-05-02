"""
Common Contract Utilities
Shared functions for contract processing and analysis used across the system
"""

import re
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from contract.models import ContractType

def generate_file_hash(content: str) -> str:
    """Generate SHA-256 hash of file content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def extract_parties(text: str) -> List[str]:
    """Extract party names from contract text"""
    party_patterns = [
        r'between\s+([^,\n]+(?:\s+Inc\.?|\s+LLC\.?|\s+Ltd\.?|\s+Corp\.?|\s+Corporation)?)',
        r'by\s+and\s+between\s+([^,\n]+(?:\s+Inc\.?|\s+LLC\.?|\s+Ltd\.?|\s+Corp\.?)?)',
        r'party.*?([^,\n]+(?:\s+Inc\.?|\s+LLC\.?|\s+Ltd\.?|\s+Corp\.?)?)',
        r'agreement.*?([^,\n]+(?:\s+Inc\.?|\s+LLC\.?|\s+Ltd\.?|\s+Corp\.?)?)',
    ]
    
    parties = []
    for pattern in party_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            party = match.group(1).strip()
            if len(party) > 3 and party.lower() not in [p.lower() for p in parties]:
                parties.append(party)
    
    # Limit to reasonable number of parties
    return parties[:10]

def extract_dates(text: str) -> List[Dict]:
    """Extract dates from contract text"""
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',      # YYYY/MM/DD or YYYY-MM-DD
        r'\b\w+\s+\d{1,2},?\s+\d{4}\b',         # January 1, 2024
        r'\b\d{1,2}\s+\w+\s+\d{4}\b',            # 1 January 2024
    ]
    
    dates = []
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            dates.append({
                'text': match.group(),
                'position': match.start(),
                'pattern': pattern
            })
    
    return dates

def infer_contract_type(text: str) -> Optional[ContractType]:
    """Infer contract type from text content"""
    text_lower = text.lower()
    
    contract_type_patterns = {
        ContractType.MSA: [
            r'master.*service.*agreement', r'msa', r'master.*agreement',
            r'framework.*agreement', r'umbrella.*agreement'
        ],
        ContractType.NDA: [
            r'non.*disclosure', r'confidentiality.*agreement', r'nda',
            r'secrecy.*agreement', r'confidential.*disclosure'
        ],
        ContractType.SOW: [
            r'statement.*work', r'sow', r'work.*statement',
            r'scope.*work', r'deliverable.*statement'
        ],
        ContractType.SERVICE_AGREEMENT: [
            r'service.*agreement', r'service.*contract', r'sla',
            r'service.*level', r'professional.*service'
        ],
        ContractType.SUPPLIER_CONTRACT: [
            r'supplier.*agreement', r'vendor.*contract', r'procurement',
            r'supply.*agreement', r'supplier.*relationship'
        ],
        ContractType.EMPLOYMENT_AGREEMENT: [
            r'employment.*agreement', r'employment.*contract', r'work.*agreement',
            r'employee.*contract', r'employment.*terms'
        ],
        ContractType.LEASE_AGREEMENT: [
            r'lease.*agreement', r'rental.*agreement', r'lease.*contract',
            r'property.*lease', r'rental.*contract'
        ]
    }
    
    scores = {}
    for contract_type, patterns in contract_type_patterns.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            score += len(matches)
        scores[contract_type] = score
    
    # Return contract type with highest score
    if scores and max(scores.values()) > 0:
        return max(scores, key=scores.get)
    
    return ContractType.OTHER

def extract_monetary_amounts(text: str) -> List[Dict]:
    """Extract monetary amounts from contract text"""
    money_patterns = [
        r'\$\s*[\d,]+(?:\.\d{2})?',  # $1,234.56
        r'[\d,]+(?:\.\d{2})?\s*USD',  # 1,234.56 USD
        r'[\d,]+(?:\.\d{2})?\s*dollars?',  # 1,234.56 dollars
        r'USD\s*[\d,]+(?:\.\d{2})?',  # USD 1,234.56
    ]
    
    amounts = []
    for pattern in money_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Extract numeric value
            numeric_match = re.search(r'[\d,]+(?:\.\d{2})?', match.group())
            if numeric_match:
                amount_str = numeric_match.group().replace(',', '')
                try:
                    amount = float(amount_str)
                    amounts.append({
                        'text': match.group(),
                        'amount': amount,
                        'position': match.start(),
                        'currency': 'USD'
                    })
                except ValueError:
                    continue
    
    return amounts

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity score between two texts (0-1)"""
    if not text1 or not text2:
        return 0.0
    
    # Simple similarity based on common words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def detect_changes(old_text: str, new_text: str) -> Dict:
    """Detect changes between two contract versions"""
    similarity = calculate_similarity(old_text, new_text)
    
    # Extract key information from both versions
    old_parties = extract_parties(old_text)
    new_parties = extract_parties(new_text)
    
    old_dates = extract_dates(old_text)
    new_dates = extract_dates(new_text)
    
    old_amounts = extract_monetary_amounts(old_text)
    new_amounts = extract_monetary_amounts(new_text)
    
    changes = {
        'similarity_score': similarity,
        'parties_changed': old_parties != new_parties,
        'dates_changed': old_dates != new_dates,
        'amounts_changed': old_amounts != new_amounts,
        'party_changes': {
            'added': list(set(new_parties) - set(old_parties)),
            'removed': list(set(old_parties) - set(new_parties))
        },
        'date_changes': {
            'added': new_dates,
            'removed': old_dates
        },
        'amount_changes': {
            'added': new_amounts,
            'removed': old_amounts
        }
    }
    
    return changes

def generate_contract_name(text: str, parties: List[str] = None) -> str:
    """Generate a descriptive contract name"""
    parties = parties or extract_parties(text)
    
    if parties:
        if len(parties) == 1:
            return f"{parties[0]} Agreement"
        elif len(parties) == 2:
            return f"{parties[0]} - {parties[1]} Agreement"
        else:
            return f"{parties[0]} et al. Agreement"
    
    # Fallback to contract type
    contract_type = infer_contract_type(text)
    if contract_type:
        return f"{contract_type.value.replace('_', ' ').title()} Contract"
    
    return "Generic Contract"

def validate_contract_content(text: str) -> Dict:
    """Validate contract content and return quality metrics"""
    if not text or len(text.strip()) < 100:
        return {
            'valid': False,
            'error': 'Insufficient text content (minimum 100 characters required)',
            'word_count': len(text.split()) if text else 0,
            'character_count': len(text) if text else 0
        }
    
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Quality metrics
    metrics = {
        'valid': True,
        'word_count': len(words),
        'character_count': len(text),
        'sentence_count': len(sentences),
        'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
        'has_parties': len(extract_parties(text)) > 0,
        'has_dates': len(extract_dates(text)) > 0,
        'has_amounts': len(extract_monetary_amounts(text)) > 0,
        'contract_type': infer_contract_type(text),
        'quality_score': min(100, int(
            (len(words) / 100) * 20 +  # Word count contribution
            (len(extract_parties(text)) * 10) +  # Parties contribution
            (len(extract_dates(text)) * 10) +  # Dates contribution
            (len(extract_monetary_amounts(text)) * 10)  # Amounts contribution
        ))
    }
    
    return metrics

# Additional utility functions for contract processing

def extract_key_terms(text: str, min_length: int = 3, max_terms: int = 20) -> List[str]:
    """Extract key terms from contract text"""
    # Common contract terms to look for
    contract_terms = [
        'liability', 'indemnification', 'termination', 'confidentiality',
        'governing law', 'jurisdiction', 'force majeure', 'arbitration',
        'payment terms', 'delivery', 'warranty', 'intellectual property',
        'assignment', 'non-compete', 'non-solicitation', 'compliance'
    ]
    
    found_terms = []
    text_lower = text.lower()
    
    for term in contract_terms:
        if term in text_lower:
            found_terms.append(term)
    
    # Add other important words (capitalized words, legal terms)
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    for word in words:
        if len(word) >= min_length and word.lower() not in [t.lower() for t in found_terms]:
            found_terms.append(word)
    
    return found_terms[:max_terms]

def preprocess_text(text: str) -> str:
    """Preprocess contract text for analysis"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep important ones
    text = re.sub(r'[^\w\s\.\,\;\:\-\$\/\(\)]', ' ', text)
    
    # Normalize line breaks
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()

def clean_text(text: str) -> str:
    """Clean contract text for storage"""
    if not text:
        return ""
    
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def calculate_text_complexity(text: str) -> Dict:
    """Calculate text complexity metrics"""
    if not text:
        return {'complexity_score': 0, 'metrics': {}}
    
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Calculate metrics
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    avg_sentence_length = len(words) / len(sentences) if sentences else 0
    
    # Count complex words (more than 6 characters)
    complex_words = [word for word in words if len(word) > 6]
    complex_word_ratio = len(complex_words) / len(words) if words else 0
    
    # Count legal/technical terms
    legal_terms = ['whereas', 'hereinafter', 'notwithstanding', 'pursuant', 'heretofore']
    legal_term_count = sum(1 for term in legal_terms if term in text.lower())
    
    # Calculate complexity score (0-100)
    complexity_score = min(100, int(
        (avg_word_length * 10) +  # Word length contribution
        (avg_sentence_length * 5) +  # Sentence length contribution
        (complex_word_ratio * 30) +  # Complex words contribution
        (legal_term_count * 5)  # Legal terms contribution
    ))
    
    return {
        'complexity_score': complexity_score,
        'metrics': {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'complex_word_ratio': complex_word_ratio,
            'legal_term_count': legal_term_count
        }
    }
