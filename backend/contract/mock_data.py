"""
Mock data for contract analysis testing
Provides realistic test data without LLM calls
"""

from contract.models import ContractAnalysis, ClauseRisk, RiskLevel, ContractMetadata
from datetime import datetime
import random
import hashlib


def get_mock_analysis(text_content: str, analysis_id: str, analysis_types: list) -> ContractAnalysis:
    """Generate mock contract analysis for testing"""
    
    # Create variable processing time based on content
    content_hash = hashlib.md5(text_content.encode()).hexdigest()
    processing_time = 1000 + int(content_hash[:8], 16) % 4000
    
    # Generate realistic clauses based on content
    mock_clauses = generate_mock_clauses(text_content, analysis_types)
    
    # Calculate risk scores
    risk_scores = calculate_risk_scores(mock_clauses)
    
    # Create contract metadata
    metadata = ContractMetadata(
        effective_date=datetime.now(),
        expiration_date=datetime.now(),
        parties=["Test Party", "Counterparty Inc."],
        governing_law="English Law",
        total_value=100000,
        currency="INR"
    )
    
    # Create analysis
    analysis = ContractAnalysis(
        analysis_timestamp=datetime.now(),
        contract_name=random.choice(["Test Contract 1", "Test Contract 2", "Test Contract 3", "Test Contract 4", "Test Contract 5", "Test Contract 6", "Test Contract 7", "Test Contract 8", "Test Contract 9", "Test Contract 10"]),
        overall_risk_score=risk_scores['overall'],
        risk_level=risk_scores['level'],
        legal_risk_score=risk_scores['legal'],
        financial_risk_score=risk_scores['financial'],
        operational_risk_score=risk_scores['operational'],
        clauses=mock_clauses,
        executive_summary=generate_executive_summary(mock_clauses, risk_scores),
        key_recommendations=generate_recommendations(mock_clauses, risk_scores),
        metadata=metadata,
        processing_time_ms=processing_time
    )
    
    return analysis


def generate_mock_clauses(text_content: str, analysis_types: list) -> list:
    """Generate realistic mock clauses based on content"""
    
    # Base clause templates
    clause_templates = [
        {
            "type": "Liability",
            "category": "Legal",
            "template": "The parties agree to limit liability under applicable law.",
            "risk_range": (30, 70)
        },
        {
            "type": "Payment Terms",
            "category": "Financial", 
            "template": "Payment shall be made within 30 days of invoice.",
            "risk_range": (20, 50)
        },
        {
            "type": "Termination",
            "category": "Legal",
            "template": "Either party may terminate with 30 days notice.",
            "risk_range": (40, 60)
        },
        {
            "type": "Confidentiality",
            "category": "Legal",
            "template": "Both parties shall maintain confidentiality of shared information.",
            "risk_range": (25, 45)
        },
        {
            "type": "Delivery",
            "category": "Operational",
            "template": "Goods shall be delivered within specified timeframe.",
            "risk_range": (15, 40)
        },
        {
            "type": "Indemnification",
            "category": "Legal",
            "template": "Each party shall indemnify the other against claims.",
            "risk_range": (50, 80)
        }
    ]
    
    # Select clauses based on analysis types and content
    selected_clauses = []
    
    # Always include 2-4 clauses
    num_clauses = min(4, max(2, len(analysis_types) + 1))
    
    for i in range(num_clauses):
        template = clause_templates[i % len(clause_templates)]
        
        # Generate risk score within range
        risk_score = random.randint(template["risk_range"][0], template["risk_range"][1])
        
        # Determine risk tag
        if risk_score < 30:
            risk_tag = "Low"
        elif risk_score < 60:
            risk_tag = "Medium"
        else:
            risk_tag = "High"
        
        clause = ClauseRisk(
            clause_type=template["type"],
            content=f"{template['template']} (Analysis ID: {hash(text_content) % 10000})",
            risk_category=template["category"],
            risk_score=risk_score,
            risk_tag=risk_tag,
            recommendation=generate_recommendation(template["type"], risk_score)
        )
        
        selected_clauses.append(clause)
    
    return selected_clauses


def calculate_risk_scores(clauses: list) -> dict:
    """Calculate overall risk scores from clauses"""
    
    if not clauses:
        return {
            'overall': random.randint(0, 100),
            'level': random.choice([RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]),
            'legal': random.randint(0, 100),
            'financial': random.randint(0, 100),
            'operational': random.randint(0, 100)
        }
    
    # Calculate category scores
    legal_scores = [c.risk_score for c in clauses if c.risk_category == "Legal"]
    financial_scores = [c.risk_score for c in clauses if c.risk_category == "Financial"]
    operational_scores = [c.risk_score for c in clauses if c.risk_category == "Operational"]
    
    legal_avg = sum(legal_scores) / len(legal_scores) if legal_scores else 0
    financial_avg = sum(financial_scores) / len(financial_scores) if financial_scores else 0
    operational_avg = sum(operational_scores) / len(operational_scores) if operational_scores else 0
    
    # Calculate overall score
    all_scores = [c.risk_score for c in clauses]
    overall_avg = sum(all_scores) / len(all_scores)
    
    # Determine risk level
    if overall_avg < 30:
        risk_level = RiskLevel.LOW
    elif overall_avg < 60:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.HIGH
    
    return {
        'overall': int(overall_avg),
        'level': risk_level,
        'legal': int(legal_avg),
        'financial': int(financial_avg),
        'operational': int(operational_avg)
    }


def generate_executive_summary(clauses: list, risk_scores: dict) -> str:
    """Generate realistic executive summary"""
    
    num_clauses = len(clauses)
    high_risk_count = len([c for c in clauses if c.risk_score > 60])
    
    summary = f"This contract contains {num_clauses} key clauses for analysis. "
    
    if risk_scores['level'] == RiskLevel.HIGH:
        summary += "The overall risk level is HIGH due to several concerning clauses. "
    elif risk_scores['level'] == RiskLevel.MEDIUM:
        summary += "The overall risk level is MEDIUM with some areas requiring attention. "
    else:
        summary += "The overall risk level is LOW with generally favorable terms. "
    
    if high_risk_count > 0:
        summary += f"Immediate attention required for {high_risk_count} high-risk clauses. "
    
    summary += "Legal review recommended before execution."
    
    return summary


def generate_recommendations(clauses: list, risk_scores: dict) -> list:
    """Generate realistic recommendations"""
    
    recommendations = []
    
    # Add recommendations based on high-risk clauses
    high_risk_clauses = [c for c in clauses if c.risk_score > 60]
    for clause in high_risk_clauses:
        recommendations.append(f"Review and negotiate {clause.clause_type} terms")
    
    # Add general recommendations
    if risk_scores['legal'] > 50:
        recommendations.append("Seek comprehensive legal review")
    
    if risk_scores['financial'] > 50:
        recommendations.append("Evaluate financial implications and cash flow impact")
    
    if risk_scores['operational'] > 50:
        recommendations.append("Assess operational feasibility and resource requirements")
    
    # Add default recommendations if none
    if not recommendations:
        recommendations = [
            "Review all terms carefully before signing",
            "Ensure compliance with applicable regulations",
            "Consider future business impact"
        ]
    
    return recommendations[:5]  # Limit to 5 recommendations


def generate_recommendation(clause_type: str, risk_score: int) -> str:
    """Generate specific recommendation for a clause"""
    
    recommendations = {
        "Liability": f"Liability limitations should be reviewed (Risk: {risk_score})",
        "Payment Terms": f"Payment schedule appears acceptable (Risk: {risk_score})",
        "Termination": f"Termination clauses need careful review (Risk: {risk_score})",
        "Confidentiality": f"Confidentiality terms are standard (Risk: {risk_score})",
        "Delivery": f"Delivery terms should be verified (Risk: {risk_score})",
        "Indemnification": f"Indemnification clauses require legal attention (Risk: {risk_score})"
    }
    
    return recommendations.get(clause_type, f"Review {clause_type} clause carefully (Risk: {risk_score})")


# Mock analysis types configuration
MOCK_ANALYSIS_CONFIGS = {
    "comprehensive": {
        "clauses_count": 4,
        "include_all_types": True
    },
    "legal": {
        "clauses_count": 3,
        "include_all_types": False,
        "focus_categories": ["Legal"]
    },
    "financial": {
        "clauses_count": 2,
        "include_all_types": False,
        "focus_categories": ["Financial"]
    },
    "operational": {
        "clauses_count": 2,
        "include_all_types": False,
        "focus_categories": ["Operational"]
    }
}


def get_mock_config(analysis_type: str) -> dict:
    """Get mock configuration for analysis type"""
    return MOCK_ANALYSIS_CONFIGS.get(analysis_type, MOCK_ANALYSIS_CONFIGS["comprehensive"])
