"""
Text Processing Utilities
Functions for text processing, cleaning, and analysis
"""

import re
from typing import List, Dict, Optional, Tuple
from .contract_utils import preprocess_text, clean_text, normalize_text

# Re-export from contract_utils for backward compatibility
__all__ = [
    'preprocess_text',
    'clean_text', 
    'normalize_text',
    'extract_key_terms',
    'calculate_text_complexity',
    'tokenize_text',
    'remove_stopwords',
    'extract_sentences',
    'calculate_readability'
]

def tokenize_text(text: str, lowercase: bool = True) -> List[str]:
    """Tokenize text into words"""
    if not text:
        return []
    
    # Clean text first
    cleaned = clean_text(text)
    
    # Split into words
    words = re.findall(r'\b\w+\b', cleaned)
    
    if lowercase:
        words = [word.lower() for word in words]
    
    return words

def remove_stopwords(words: List[str], custom_stopwords: List[str] = None) -> List[str]:
    """Remove common stopwords from word list"""
    # Common English stopwords
    default_stopwords = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'i', 'you', 'your', 'we', 'our',
        'they', 'them', 'their', 'this', 'that', 'these', 'those'
    }
    
    if custom_stopwords:
        default_stopwords.update(custom_stopwords)
    
    return [word for word in words if word.lower() not in default_stopwords]

def extract_sentences(text: str) -> List[str]:
    """Extract sentences from text"""
    if not text:
        return []
    
    # Split by sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    
    # Clean and filter sentences
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 10:  # Keep meaningful sentences
            cleaned_sentences.append(sentence)
    
    return cleaned_sentences

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

# Re-export functions from contract_utils for convenience
from .contract_utils import extract_key_terms, calculate_text_complexity
