"""
Chat Layer - Intent Classifier
Determines user intent and routes to appropriate agent
"""

import re
from typing import Dict, List
from utils import logger

class IntentClassifier:
    """Classifies user messages into different intent categories"""
    
    def __init__(self):
        # Contract-related keywords
        self.contract_keywords = [
            'contract', 'agreement', 'clause', 'legal', 'terms', 'liability',
            'payment', 'termination', 'confidentiality', 'nda', 'msa', 'sow',
            'party', 'signature', 'breach', 'obligation', 'warranty', 'indemnity',
            'governing law', 'jurisdiction', 'force majeure', 'severability',
            'assignment', 'amendment', 'renewal', 'expiration', 'effective date'
        ]
        
        # Business/financial keywords
        self.business_keywords = [
            'business', 'company', 'corporation', 'revenue', 'profit', 'cost',
            'investment', 'roi', 'budget', 'financial', 'economics', 'market',
            'strategy', 'planning', 'management', 'operations', 'sales'
        ]
        
        # General conversation indicators
        self.general_indicators = [
            'hello', 'hi', 'how are you', 'what is your name', 'help', 'explain',
            'tell me', 'can you', 'could you', 'what do you think', 'opinion',
            'weather', 'time', 'date', 'news', 'information'
        ]
    
    def classify_intent(self, message: str) -> Dict[str, any]:
        """
        Classify user message intent
        
        Args:
            message: User message string
            
        Returns:
            Dict with intent classification and confidence
        """
        try:
            message_lower = message.lower()
            
            # Calculate scores for each category
            contract_score = self._calculate_keyword_score(message_lower, self.contract_keywords)
            business_score = self._calculate_keyword_score(message_lower, self.business_keywords)
            general_score = self._calculate_keyword_score(message_lower, self.general_indicators)
            
            # Determine primary intent
            scores = {
                'contract': contract_score,
                'business': business_score,
                'general': general_score
            }
            
            primary_intent = max(scores, key=scores.get)
            confidence = scores[primary_intent] / max(1, sum(scores.values()))
            
            # Special handling for questions about contract analysis
            if any(word in message_lower for word in ['analyze', 'review', 'check', 'examine']) and contract_score > 0:
                primary_intent = 'contract_analysis'
            
            result = {
                'intent': primary_intent,
                'confidence': confidence,
                'scores': scores,
                'requires_file_upload': primary_intent in ['contract_analysis', 'contract']
            }
            
            logger.info(f"Intent classified: {primary_intent} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in intent classification: {str(e)}")
            return {
                'intent': 'general',
                'confidence': 0.0,
                'scores': {'contract': 0, 'business': 0, 'general': 0},
                'requires_file_upload': False
            }
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> int:
        """Calculate keyword matching score"""
        score = 0
        for keyword in keywords:
            if keyword in text:
                # Weight exact matches higher
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    score += 2
                else:
                    score += 1
        return score
    
    def should_route_to_contract_expert(self, message: str) -> bool:
        """Quick check if message should go to contract expert"""
        classification = self.classify_intent(message)
        return classification['intent'] in ['contract', 'contract_analysis']
    
    def get_conversation_type(self, messages: List[str]) -> str:
        """Determine overall conversation type from multiple messages"""
        if not messages:
            return 'general'
        
        intent_counts = {'contract': 0, 'business': 0, 'general': 0}
        
        for message in messages[-5:]:  # Look at last 5 messages
            classification = self.classify_intent(message)
            intent_counts[classification['intent']] += 1
        
        # Return the most common intent
        return max(intent_counts, key=intent_counts.get)

# Singleton instance
intent_classifier = IntentClassifier()
