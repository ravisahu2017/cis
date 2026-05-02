"""
Contract Layer - Utilities and Helpers
Provides utility functions for contract analysis and processing
"""

import re
import uuid
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from .models import ClauseRisk, RiskLevel, ContractType, AnalysisType
from utils.contract_utils import (
    extract_parties, extract_dates, extract_monetary_amounts,
    infer_contract_type, generate_file_hash, calculate_similarity,
    detect_changes, generate_contract_name, validate_contract_content
)

class ContractUtils:
    """Utility functions for contract analysis"""
    
    # Common contract clause patterns
    CLAUSE_PATTERNS = {
        'liability': [
            r'liability', r'limitation.*liability', r'damages', r'indemnif',
            r'hold harmless', r'liable', r'responsibility'
        ],
        'confidentiality': [
            r'confidential', r'non-disclosure', r'nda', r'proprietary',
            r'trade secret', r'secrecy', r'non-disclosure'
        ],
        'payment': [
            r'payment', r'fee', r'cost', r'price', r'invoice',
            r'billing', r'remuneration', r'compensation'
        ],
        'termination': [
            r'terminat', r'end.*agreement', r'discontinu', r'cancel',
            r'expire', r'cessation', r'dissolution'
        ],
        'intellectual_property': [
            r'intellectual.*property', r'ip', r'copyright', r'trademark',
            r'patent', r'proprietary.*rights', r'ownership'
        ],
        'governing_law': [
            r'governing.*law', r'jurisdiction', r'applicable.*law',
            r'choice.*law', r'legal.*jurisdiction'
        ],
        'force_majeure': [
            r'force.*majeure', r'act.*god', r'unforeseeable',
            r'beyond.*control', r'uncontrollable'
        ],
        'dispute_resolution': [
            r'dispute.*resolution', r'arbitration', r'mediation',
            r'litigation', r'legal.*proceeding'
        ]
    }
    
    # Risk scoring weights
    RISK_WEIGHTS = {
        'critical': 0.9,
        'high': 0.7,
        'medium': 0.5,
        'low': 0.3
    }
    
    # Contract type indicators
    CONTRACT_TYPE_INDICATORS = {
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
    
    # Note: extract_dates, extract_parties, and extract_monetary_amounts 
# are now imported from utils.contract_utils to avoid duplication
    
    @staticmethod
    def identify_clause_type(text: str) -> Optional[str]:
        """Identify the type of contract clause"""
        text_lower = text.lower()
        
        scores = {}
        for clause_type, patterns in ContractUtils.CLAUSE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            scores[clause_type] = score
        
        # Return clause type with highest score
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return None
    
    @staticmethod
    def calculate_risk_score(clause_text: str, clause_type: str, context: str = "") -> int:
        """Calculate risk score for a contract clause"""
        risk_indicators = {
            'critical': [
                r'unlimited.*liability', r'no.*limitation', r'irrevocable',
                r'perpetual', r'permanent.*injunction', r'punitive.*damages'
            ],
            'high': [
                r'liquidated.*damages', r'penalty.*clause', r'strict.*liability',
                r'exclusive.*jurisdiction', r'no.*appeal', r'binding.*arbitration'
            ],
            'medium': [
                r'reasonable.*efforts', r'best.*efforts', r'time.*is.*of.*essence',
                r'material.*breach', r'notice.*period'
            ],
            'low': [
                r'commercial.*reasonable', r'good.*faith', r'mutual.*agreement',
                r'standard.*terms', r'customary.*practice'
            ]
        }
        
        text_lower = clause_text.lower()
        score = 50  # Base score
        
        # Adjust based on risk indicators
        for risk_level, patterns in risk_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if risk_level == 'critical':
                        score = max(score, 85)
                    elif risk_level == 'high':
                        score = max(score, 70)
                    elif risk_level == 'medium':
                        score = max(score, 55)
                    elif risk_level == 'low':
                        score = min(score, 45)
        
        # Adjust based on clause type
        clause_type_risks = {
            'liability': 10,
            'termination': 8,
            'payment': 6,
            'intellectual_property': 7,
            'confidentiality': 5,
            'dispute_resolution': 4,
            'governing_law': 3,
            'force_majeure': 2
        }
        
        type_adjustment = clause_type_risks.get(clause_type, 0)
        score = min(100, max(0, score + type_adjustment))
        
        return int(score)
    
    @staticmethod
    def determine_risk_level(score: int) -> RiskLevel:
        """Determine risk level from score"""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    @staticmethod
    def infer_contract_type(text: str) -> Optional[ContractType]:
        """Infer contract type from text content"""
        text_lower = text.lower()
        
        scores = {}
        for contract_type, patterns in ContractUtils.CONTRACT_TYPE_INDICATORS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches)
            scores[contract_type] = score
        
        # Return contract type with highest score
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return ContractType.OTHER
    
    @staticmethod
    def generate_recommendations(clause_text: str, clause_type: str, risk_score: int) -> List[str]:
        """Generate recommendations for a contract clause"""
        recommendations = []
        
        if risk_score >= 80:
            recommendations.append("URGENT: Seek immediate legal review before signing")
            recommendations.append("Consider negotiating significant modifications")
        elif risk_score >= 60:
            recommendations.append("Strongly recommend legal review")
            recommendations.append("Negotiate more favorable terms if possible")
        elif risk_score >= 40:
            recommendations.append("Consider legal consultation")
            recommendations.append("Review carefully and understand implications")
        else:
            recommendations.append("Standard clause - review for context")
        
        # Add clause-specific recommendations
        clause_recommendations = {
            'liability': [
                "Consider adding liability limitations",
                "Review indemnification clauses carefully"
            ],
            'payment': [
                "Verify payment terms are clear and achievable",
                "Consider adding payment security provisions"
            ],
            'termination': [
                "Ensure termination clauses are balanced",
                "Review notice periods and termination conditions"
            ],
            'intellectual_property': [
                "Clarify IP ownership rights",
                "Consider IP protection mechanisms"
            ],
            'confidentiality': [
                "Ensure confidentiality obligations are reasonable",
                "Review duration and scope of confidentiality"
            ]
        }
        
        if clause_type in clause_recommendations:
            recommendations.extend(clause_recommendations[clause_type])
        
        # Remove duplicates and limit
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:5]
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """Preprocess contract text for analysis"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common artifacts
        text = re.sub(r'\f', ' ', text)  # Form feeds
        text = re.sub(r'\x0c', ' ', text)  # Form feed characters
        
        # Normalize line endings
        text = re.sub(r'\r\n|\r|\n', ' ', text)
        
        # Remove page numbers and headers/footers patterns
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', ' ', text)
        text = re.sub(r'\d+\s+/\s+\d+', ' ', text)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_key_terms(text: str) -> List[str]:
        """Extract key terms from contract text"""
        # Common legal and business terms
        term_patterns = [
            r'\b[a-zA-Z]+\s+Agreement\b',
            r'\b[a-zA-Z]+\s+Contract\b',
            r'\b[a-zA-Z]+\s+Terms\b',
            r'\b[a-zA-Z]+\s+Conditions\b',
            r'\b[a-zA-Z]+\s+Policy\b',
            r'\b[a-zA-Z]+\s+Protocol\b'
        ]
        
        terms = []
        for pattern in term_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.extend(matches)
        
        # Remove duplicates and limit
        unique_terms = list(dict.fromkeys([term.title() for term in terms]))
        return unique_terms[:20]
    
    @staticmethod
    def calculate_text_complexity(text: str) -> Dict[str, Any]:
        """Calculate complexity metrics for contract text"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Average sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Complex words (more than 6 characters)
        complex_words = [word for word in words if len(word) > 6]
        complex_word_ratio = len(complex_words) / len(words) if words else 0
        
        # Legal jargon indicators
        legal_terms = [
            'hereinafter', 'whereas', 'notwithstanding', 'heretofore',
            'forthwith', 'henceforth', 'witnesseth', 'aforementioned'
        ]
        legal_jargon_count = sum(1 for term in legal_terms if term.lower() in text.lower())
        
        return {
            'total_words': len(words),
            'total_sentences': len(sentences),
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'complex_word_ratio': complex_word_ratio,
            'legal_jargon_count': legal_jargon_count,
            'complexity_score': min(100, int(
                (avg_sentence_length * 2) + 
                (complex_word_ratio * 100) + 
                (legal_jargon_count * 5)
            ))
        }

# Utility functions for direct access
def extract_dates(text: str) -> List[Dict[str, Any]]:
    return ContractUtils.extract_dates(text)

def extract_parties(text: str) -> List[str]:
    return ContractUtils.extract_parties(text)

def calculate_risk_score(clause_text: str, clause_type: str, context: str = "") -> int:
    return ContractUtils.calculate_risk_score(clause_text, clause_type, context)

def infer_contract_type(text: str) -> Optional[ContractType]:
    return ContractUtils.infer_contract_type(text)

def preprocess_text(text: str) -> str:
    return ContractUtils.preprocess_text(text)
