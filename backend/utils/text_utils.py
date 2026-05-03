"""
Text Processing Utilities
Functions for text processing, cleaning, and analysis
"""

import re
from typing import List, Dict


# Re-export from contract_utils for backward compatibility
__all__ = [
    'preprocess_text',
    'clean_text', 
    'normalize_text',
    'calculate_text_complexity',
    'tokenize_text',
    'remove_stopwords',
    'extract_sentences'
]

# Wrapper functions for ContractUtils methods
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
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    return text.strip()

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