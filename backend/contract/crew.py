"""
Contract Layer - Crew Configuration
Defines and manages contract analysis crews for different analysis types
"""

import time
import uuid
from typing import Dict, List, Optional, Any
from crewai import Task, Crew, Process
from crewai.llm import LLM
from .agents import get_all_contract_agents, get_primary_analysis_agents, coordinator_agent
from .tasks import create_analysis_tasks
from .models import ContractAnalysis, ClauseRisk, ContractMetadata, AnalysisType, RiskLevel
from utils import logger

class ContractCrewManager:
    """Manages contract analysis crews for different analysis types"""
    
    def __init__(self):
        self.active_crews: Dict[str, Crew] = {}
        self.crew_stats: Dict[str, Dict] = {}
        self.analysis_history: List[Dict] = []
    
    def create_contract_crew(self, tasks: List[Task], analysis_types: List[AnalysisType]) -> Crew:
        """Create and configure the contract analysis crew"""
        
        # Get primary agents based on analysis types
        primary_agents = get_primary_analysis_agents([t.value for t in analysis_types])
        
        # Always include coordinator for complex analyses
        use_coordinator = len(analysis_types) > 1 or AnalysisType.COMPREHENSIVE in analysis_types
        
        if use_coordinator:
            agents = primary_agents
            process = Process.hierarchical
            manager_agent = coordinator_agent
        else:
            agents = primary_agents
            process = Process.sequential
            manager_agent = None
        
        crew = Crew(
            agents=agents,
            tasks=tasks,
            manager_agent=manager_agent,
            process=process,
            verbose=True,
            memory=True,
            cache=True
        )
        
        logger.info(f"Created crew with {len(agents)} agents for {len(analysis_types)} analysis types")
        return crew
    
    def analyze_contract(self, text_content: str, analysis_types: List[AnalysisType], 
                        analysis_id: str = None) -> ContractAnalysis:
        """Main contract analysis method"""
        start_time = time.time()
        
        try:
            # Generate analysis ID if not provided
            if not analysis_id:
                analysis_id = str(uuid.uuid4())
            
            logger.info(f"Starting contract analysis {analysis_id} with types: {[t.value for t in analysis_types]}")
            
            # Create analysis tasks
            tasks = create_analysis_tasks(text_content, analysis_types)
            
            # Create crew
            crew = self.create_contract_crew(tasks, analysis_types)
            
            # Execute analysis
            result = crew.kickoff()
            
            # Process results
            analysis = self._process_crew_result(result, analysis_id, text_content, analysis_types)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            analysis.processing_time_ms = processing_time_ms
            
            # Update statistics
            self._update_crew_stats(analysis_types, processing_time_ms, True)
            self._record_analysis(analysis_id, analysis_types, processing_time_ms, True)
            
            logger.info(f"Contract analysis {analysis_id} completed in {processing_time_ms}ms")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in contract analysis: {str(e)}")
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Update error statistics
            self._update_crew_stats(analysis_types, processing_time_ms, False)
            self._record_analysis(analysis_id, analysis_types, processing_time_ms, False)
            
            # Re-raise exception
            raise e
    
    def _process_crew_result(self, result: Any, analysis_id: str, text_content: str, 
                           analysis_types: List[AnalysisType]) -> ContractAnalysis:
        """Process crew result into ContractAnalysis object"""
        
        try:
            # Extract result data
            if hasattr(result, 'raw'):
                result_dict = result.raw
            elif hasattr(result, 'result'):
                result_dict = result.result
            else:
                result_dict = result
            
            # Parse result based on its type
            if isinstance(result_dict, dict):
                return self._parse_dict_result(result_dict, analysis_id, text_content, analysis_types)
            elif isinstance(result_dict, str):
                return self._parse_string_result(result_dict, analysis_id, text_content, analysis_types)
            else:
                # Fallback: create basic analysis
                return self._create_fallback_analysis(analysis_id, text_content, analysis_types)
                
        except Exception as e:
            logger.error(f"Error processing crew result: {str(e)}")
            return self._create_fallback_analysis(analysis_id, text_content, analysis_types)
    
    def _parse_dict_result(self, result_dict: Dict, analysis_id: str, text_content: str, 
                          analysis_types: List[AnalysisType]) -> ContractAnalysis:
        """Parse dictionary result into ContractAnalysis"""
        
        # Extract clauses from different analysis types
        all_clauses = []
        legal_risks = result_dict.get('legal_analysis', [])
        financial_risks = result_dict.get('financial_analysis', [])
        operational_risks = result_dict.get('operations_analysis', [])
        compliance_risks = result_dict.get('compliance_analysis', [])
        
        # Convert to ClauseRisk objects
        for risk_list in [legal_risks, financial_risks, operational_risks, compliance_risks]:
            if isinstance(risk_list, list):
                for risk in risk_list:
                    if isinstance(risk, dict):
                        clause = ClauseRisk(
                            clause_type=risk.get('clause_type', 'Unknown'),
                            content_summary=risk.get('content_summary', ''),
                            risk_score=risk.get('risk_score', 50),
                            risk_level=risk.get('risk_level') or 'medium',
                            recommendations=risk.get('recommendations', []),
                            location=risk.get('location'),
                            severity=risk.get('severity')
                        )
                        all_clauses.append(clause)
        
        # Extract metadata
        metadata_dict = result_dict.get('metadata', {})
        metadata = ContractMetadata(
            contract_type=metadata_dict.get('contract_type'),
            effective_date=metadata_dict.get('effective_date'),
            expiration_date=metadata_dict.get('expiration_date'),
            parties=metadata_dict.get('parties', []),
            governing_law=metadata_dict.get('governing_law'),
            total_value=metadata_dict.get('total_value'),
            currency=metadata_dict.get('currency'),
            renewal_terms=metadata_dict.get('renewal_terms'),
            termination_notice=metadata_dict.get('termination_notice')
        )
        
        # Calculate risk scores
        legal_score = self._calculate_risk_score(legal_risks)
        financial_score = self._calculate_risk_score(financial_risks)
        operational_score = self._calculate_risk_score(operational_risks)
        overall_score = int((legal_score + financial_score + operational_score) / 3)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Generate contract name
        contract_name = f"Contract Analysis {analysis_id[:8]}"
        if metadata.parties:
            contract_name = f"{metadata.parties[0]} Agreement"
        
        # Create analysis
        analysis = ContractAnalysis(
            contract_name=contract_name,
            overall_risk_score=overall_score,
            risk_level=risk_level,
            legal_risk_score=legal_score,
            financial_risk_score=financial_score,
            operational_risk_score=operational_score,
            clauses=all_clauses,
            metadata=metadata,
            executive_summary=result_dict.get('executive_summary', 'Contract analysis completed.'),
            key_recommendations=result_dict.get('key_recommendations', ['Review contract terms carefully']),
            analysis_id=analysis_id
        )
        
        return analysis
    
    def _parse_string_result(self, result_string: str, analysis_id: str, text_content: str, 
                           analysis_types: List[AnalysisType]) -> ContractAnalysis:
        """Parse string result into ContractAnalysis"""
        
        # For string results, create a basic analysis
        return self._create_fallback_analysis(analysis_id, text_content, analysis_types, result_string)
    
    def _create_fallback_analysis(self, analysis_id: str, text_content: str, 
                                 analysis_types: List[AnalysisType], summary: str = None) -> ContractAnalysis:
        """Create fallback analysis when result parsing fails"""
        
        metadata = ContractMetadata(
            contract_type=None,
            effective_date=None,
            expiration_date=None,
            parties=[],
            governing_law=None
        )
        
        analysis = ContractAnalysis(
            contract_name=f"Contract Analysis {analysis_id[:8]}",
            overall_risk_score=50,
            risk_level=RiskLevel.MEDIUM,
            legal_risk_score=50,
            financial_risk_score=50,
            operational_risk_score=50,
            clauses=[],
            metadata=metadata,
            executive_summary=summary or "Contract analysis completed with basic assessment.",
            key_recommendations=["Review contract terms carefully", "Seek legal advice if needed"],
            analysis_id=analysis_id
        )
        
        return analysis
    
    def _calculate_risk_score(self, risks: List) -> int:
        """Calculate average risk score from a list of risks"""
        if not risks:
            return 50
        
        scores = []
        for risk in risks:
            if isinstance(risk, dict):
                score = risk.get('risk_score', 50)
            elif hasattr(risk, 'risk_score'):
                score = risk.risk_score
            else:
                score = 50
            scores.append(score)
        
        return int(sum(scores) / len(scores)) if scores else 50
    
    def _determine_risk_level(self, score: int) -> RiskLevel:
        """Determine risk level from score"""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _update_crew_stats(self, analysis_types: List[AnalysisType], processing_time: int, success: bool):
        """Update performance statistics"""
        analysis_key = '_'.join([t.value for t in sorted(analysis_types)])
        
        if analysis_key not in self.crew_stats:
            self.crew_stats[analysis_key] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_processing_time': 0,
                'avg_processing_time': 0
            }
        
        stats = self.crew_stats[analysis_key]
        stats['total_requests'] += 1
        
        if success:
            stats['successful_requests'] += 1
        
        stats['total_processing_time'] += processing_time
        stats['avg_processing_time'] = stats['total_processing_time'] / stats['total_requests']
    
    def _record_analysis(self, analysis_id: str, analysis_types: List[AnalysisType], 
                        processing_time: int, success: bool):
        """Record analysis in history"""
        record = {
            'analysis_id': analysis_id,
            'analysis_types': [t.value for t in analysis_types],
            'processing_time_ms': processing_time,
            'success': success,
            'timestamp': time.time()
        }
        self.analysis_history.append(record)
        
        # Keep only last 1000 records
        if len(self.analysis_history) > 1000:
            self.analysis_history = self.analysis_history[-1000:]
    
    def get_performance_stats(self) -> Dict:
        """Return crew performance statistics"""
        return self.crew_stats
    
    def get_analysis_history(self, limit: int = 100) -> List[Dict]:
        """Return recent analysis history"""
        return self.analysis_history[-limit:]
    
    def get_active_crews(self) -> Dict[str, Crew]:
        """Return currently active crews"""
        return self.active_crews

# Singleton instance
contract_crew_manager = ContractCrewManager()
