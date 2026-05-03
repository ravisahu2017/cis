"""
Contract Layer - Utilities and Helpers
Provides utility functions for contract analysis and processing
"""

import re
import hashlib
from .models import ContractType
from typing import List, Dict, Optional
from .models import RiskLevel, ContractType
from utils import extract_sentences, tokenize_text

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
    def generate_file_hash(content: str) -> str:
        """Generate SHA-256 hash of file content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def detect_changes(old_text: str, new_text: str) -> Dict:
        """Detect changes between two contract versions"""
        similarity = ContractUtils.calculate_similarity(old_text, new_text)
        
        # Extract key information from both versions
        old_parties = ContractUtils.extract_parties(old_text)
        new_parties = ContractUtils.extract_parties(new_text)
        
        old_dates = ContractUtils.extract_dates(old_text)
        new_dates = ContractUtils.extract_dates(new_text)
        
        old_amounts = ContractUtils.extract_monetary_amounts(old_text)
        new_amounts = ContractUtils.extract_monetary_amounts(new_text)
        
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

    @staticmethod
    def generate_contract_name(text: str, parties: List[str] = None) -> str:
        """Generate a descriptive contract name"""
        parties = parties or ContractUtils.extract_parties(text)
        
        if parties:
            if len(parties) == 1:
                return f"{parties[0]} Agreement"
            elif len(parties) == 2:
                return f"{parties[0]} - {parties[1]} Agreement"
            else:
                return f"{parties[0]} et al. Agreement"
        
        # Fallback to contract type
        contract_type = ContractUtils.infer_contract_type(text)
        if contract_type:
            return f"{contract_type.value.replace('_', ' ').title()} Contract"
        
        return "Generic Contract"

    @staticmethod
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
            'has_parties': len(ContractUtils.extract_parties(text)) > 0,
            'has_dates': len(ContractUtils.extract_dates(text)) > 0,
            'has_amounts': len(ContractUtils.extract_monetary_amounts(text)) > 0,
            'contract_type': ContractUtils.infer_contract_type(text),
            'quality_score': min(100, int(
                (len(words) / 100) * 20 +  # Word count contribution
                (len(ContractUtils.extract_parties(text)) * 10) +  # Parties contribution
                (len(ContractUtils.extract_dates(text)) * 10) +  # Dates contribution
                (len(ContractUtils.extract_monetary_amounts(text)) * 10)  # Amounts contribution
            ))
        }
        
        return metrics

    # Additional utility functions for contract processing
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def calculate_readability(text: str) -> Dict:
        """Calculate readability metrics for text"""
        if not text:
            return {'readability_score': 0, 'metrics': {}}
        
        sentences = extract_sentences(text)
        words = tokenize_text(text, lowercase=False)
        
        if not sentences or not words:
            return {'readability_score': 0, 'metrics': {}}
        
        # Calculate metrics
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Count complex words (more than 6 characters)
        complex_words = [word for word in words if len(word) > 6]
        complex_word_ratio = len(complex_words) / len(words)
        
        # Simple readability score (lower is easier to read)
        readability_score = int(
            (avg_sentence_length * 2) +  # Sentence length factor
            (avg_word_length * 3) +      # Word length factor
            (complex_word_ratio * 20)     # Complex words factor
        )
        
        return {
            'readability_score': readability_score,
            'metrics': {
                'sentence_count': len(sentences),
                'word_count': len(words),
                'avg_sentence_length': avg_sentence_length,
                'avg_word_length': avg_word_length,
                'complex_word_ratio': complex_word_ratio,
                'complex_word_count': len(complex_words)
            },
            'interpretation': {
                'level': 'Complex' if readability_score > 30 else 'Moderate' if readability_score > 15 else 'Simple',
                'description': get_readability_description(readability_score)
            }
        }

    @staticmethod
    def get_readability_description(score: int) -> str:
        """Get description for readability score"""
        if score < 10:
            return "Very easy to read"
        elif score < 15:
            return "Easy to read"
        elif score < 25:
            return "Fairly easy to read"
        elif score < 35:
            return "Standard readability"
        elif score < 45:
            return "Fairly difficult to read"
        else:
            return "Difficult to read"