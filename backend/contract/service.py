"""
Contract Layer - Main Service
Orchestrates contract analysis functionality and provides API interface
"""

import uuid
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import (
    ContractRequest, ContractResponse, ContractAnalysis, ContractCapabilities, 
    ContractAnalytics, AnalysisSession, AnalysisType, ContractType
)
from .contract_utils import ContractUtils

from .crew import contract_crew_manager
from .agents import get_agent_capabilities
from utils import logger, read_pdf, read_docx, read_txt, read_image, HttpBaseResponse
from storage.repository import ContractRepository, AnalysisRepository
from storage.database import get_database

class ContractService:
    """Main contract service orchestrating all contract analysis functionality"""
    
    def __init__(self):
        self.active_sessions: Dict[str, AnalysisSession] = {}
        self.session_timeout_hours = 24
        self.analysis_queue: List[Dict] = []
        self.max_concurrent_analyses = 5
        
        # Initialize storage
        self.db = get_database()
        self.contract_repo = ContractRepository()
        self.analysis_repo = AnalysisRepository()
    
    def analyze_contract(self, request: ContractRequest) -> ContractResponse:
        """
        Analyze a contract and return comprehensive results
        
        Args:
            request: ContractRequest with file path/content and analysis options
            
        Returns:
            ContractResponse with analysis results
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            # Get or create session
            session = self._get_or_create_session(None, request.user_id)
            
            # Extract text content
            text_content = self._extract_text_content(request)
            
            if not text_content or len(text_content.strip()) < 100:
                raise ValueError("Insufficient text content for analysis (minimum 100 characters required)")
            
            # Validate analysis types
            analysis_types = self._validate_analysis_types(request.analysis_types)
            
            # Check concurrent analysis limit
            if len(self.analysis_queue) >= self.max_concurrent_analyses:
                raise Exception("Analysis queue is full. Please try again later.")
            
            # Add to queue
            queue_item = {
                'analysis_id': analysis_id,
                'request': request,
                'text_content': text_content,
                'session_id': session.session_id,
                'started_at': time.time()
            }
            self.analysis_queue.append(queue_item)
            
            logger.info(f"Starting contract analysis {analysis_id} for session {session.session_id}")
            
            # Process analysis
            # Use mock data for testing (remove LLM calls)
            from contract.mock_data import get_mock_analysis
            
            analysis = get_mock_analysis(text_content, analysis_id, analysis_types)
            
            # Uncomment this line to enable real LLM calls:
            # analysis = contract_crew_manager.analyze_contract(text_content, analysis_types, analysis_id)
            
            # Extract agents used from analysis types
            agents_used = [agent_type.value for agent_type in analysis_types]
            
            # Save analysis results to database
            try:
                # Create or get contract record
                contract = self._get_or_create_contract(request, text_content)
                
                # Create version record
                version = self.contract_repo.create_version(
                    contract_id=contract.id,
                    filename=request.file_path.split('/')[-1] if request.file_path else "text_input",
                    file_path=request.file_path or "",
                    file_content=text_content,
                    effective_date=analysis.metadata.effective_date if analysis.metadata else None,
                    expiry_date=analysis.metadata.expiration_date if analysis.metadata else None,
                    governing_law=analysis.metadata.governing_law if analysis.metadata else None,
                    total_value=analysis.metadata.total_value if analysis.metadata else None,
                    currency=analysis.metadata.currency if analysis.metadata else None,
                    metadata_json=analysis.metadata.dict() if analysis.metadata else {}
                )
                
                # Save analysis results
                for analysis_type in analysis_types:
                    self.analysis_repo.create_analysis(
                        version_id=version.id,
                        analysis_type=analysis_type.value,
                        analysis_result=analysis,
                        processing_time_ms=analysis.processing_time_ms,
                        agents_used=agents_used
                    )
                
                logger.info(f"Saved analysis to database: contract={contract.id}, version={version.id}")
                
            except Exception as e:
                logger.error(f"Failed to save analysis to database: {str(e)}")
                # Continue with response even if storage fails
            
            # Update session
            session.analyses_completed += 1
            session.total_processing_time_ms += analysis.processing_time_ms or 0
            if request.contract_type_hint:
                if request.contract_type_hint not in session.contract_types_analyzed:
                    session.contract_types_analyzed.append(request.contract_type_hint)
            session.last_activity = datetime.now()
            
            # Remove from queue
            self.analysis_queue = [item for item in self.analysis_queue if item['analysis_id'] != analysis_id]
            
            # Calculate total processing time
            total_processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Determine agents used
            agents_used = self._get_agents_used(analysis_types)
            
            # Create response
            response = HttpBaseResponse(
                success=True,
                message="Contract analysis completed successfully",
                data=ContractResponse(
                    analysis=analysis,
                    analysis_id=analysis_id,
                    agents_used=agents_used
                ),
                response_time_ms=total_processing_time_ms,
            )

            logger.info(f"Contract analysis {analysis_id} completed successfully")
            return response
            
        except Exception as e:
            # Remove from queue if error
            self.analysis_queue = [item for item in self.analysis_queue if item['analysis_id'] != analysis_id]
            
            logger.error(f"Error in contract analysis: {str(e)}")
            
            # Calculate processing time even for errors
            total_processing_time_ms = int((time.time() - start_time) * 1000)
            
            return HttpBaseResponse(
                success=False,
                message="Contract analysis failed",
                error=str(e),
                data=ContractResponse(
                    success=False,
                    analysis_id=analysis_id,
                    agents_used=[]
                ),
                response_time_ms=total_processing_time_ms,
            )
    
    def _extract_text_content(self, request: ContractRequest) -> str:
        """Extract text content from file path or direct content"""
        
        if request.file_content:
            return request.file_content.strip()
        
        elif request.file_path:
            # Extract text based on file extension
            if request.file_path.lower().endswith('.pdf'):
                return read_pdf(request.file_path)
            elif request.file_path.lower().endswith('.docx'):
                return read_docx(request.file_path)
            elif request.file_path.lower().endswith('.txt'):
                return read_txt(request.file_path)
            elif request.file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                return read_image(request.file_path)
            else:
                raise ValueError(f"Unsupported file type: {request.file_path}")
        
        else:
            raise ValueError("Either file_path or file_content must be provided")
    
    def _validate_analysis_types(self, analysis_types: List[AnalysisType]) -> List[AnalysisType]:
        """Validate and normalize analysis types"""
        
        if not analysis_types:
            return [AnalysisType.COMPREHENSIVE]
        
        # Remove duplicates
        unique_types = list(set(analysis_types))
        
        # Validate each type
        valid_types = []
        for analysis_type in unique_types:
            if isinstance(analysis_type, str):
                try:
                    valid_types.append(AnalysisType(analysis_type))
                except ValueError:
                    logger.warning(f"Invalid analysis type: {analysis_type}")
            elif isinstance(analysis_type, AnalysisType):
                valid_types.append(analysis_type)
        
        if not valid_types:
            valid_types = [AnalysisType.COMPREHENSIVE]
        
        return valid_types
    
    def _get_agents_used(self, analysis_types: List[AnalysisType]) -> List[str]:
        """Determine which agents were used based on analysis types"""
        agents = []
        
        for analysis_type in analysis_types:
            if analysis_type == AnalysisType.LEGAL:
                agents.append('Legal Contract Analyst')
            elif analysis_type == AnalysisType.FINANCIAL:
                agents.append('Financial Risk Analyst')
            elif analysis_type == AnalysisType.OPERATIONS:
                agents.append('Operations Analyst')
            elif analysis_type == AnalysisType.COMPREHENSIVE:
                agents.extend([
                    'Legal Contract Analyst',
                    'Financial Risk Analyst', 
                    'Operations Analyst',
                    'Contract Intelligence Coordinator'
                ])
        
        # Remove duplicates while preserving order
        unique_agents = []
        seen = set()
        for agent in agents:
            if agent not in seen:
                unique_agents.append(agent)
                seen.add(agent)
        
        return unique_agents
    
    def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """Retrieve analysis session by ID"""
        return self.active_sessions.get(session_id)
    
    def get_active_sessions(self) -> List[AnalysisSession]:
        """Get all active sessions"""
        return list(self.active_sessions.values())
    
    def cleanup_sessions(self):
        """Remove inactive sessions"""
        current_time = datetime.now()
        inactive_sessions = []
        
        for session_id, session in self.active_sessions.items():
            time_diff = current_time - session.last_activity
            if time_diff.total_seconds() > (self.session_timeout_hours * 3600):
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleaned up inactive contract analysis session: {session_id}")
        
        return len(inactive_sessions)
    
    def get_capabilities(self) -> ContractCapabilities:
        """Return contract analysis system capabilities"""
        return ContractCapabilities(
            supported_file_types=['pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'bmp', 'tiff'],
            supported_contract_types=list(ContractType),
            analysis_types=list(AnalysisType),
            agent_types=['Legal Contract Analyst', 'Financial Risk Analyst', 'Operations Analyst', 
                        'Contract Intelligence Coordinator', 'Compliance Analyst', 'Risk Assessment Specialist'],
            features=[
                'Multi-agent contract analysis',
                'Legal risk assessment',
                'Financial risk analysis', 
                'Operational risk assessment',
                'Compliance checking',
                'Metadata extraction',
                'Risk scoring and prioritization',
                'Executive summary generation',
                'Session management',
                'Performance analytics'
            ],
            limitations=[
                'Minimum 100 characters of text required',
                'Analysis accuracy depends on text quality',
                'Not legal advice - requires professional review',
                'Processing time varies with complexity',
                'Maximum 5 concurrent analyses'
            ]
        )
    
    def get_agent_info(self) -> Dict:
        """Return information about available agents"""
        return get_agent_capabilities()
    
    def get_analytics(self) -> ContractAnalytics:
        """Return contract analysis analytics and performance data"""
        crew_stats = contract_crew_manager.get_performance_stats()
        analysis_history = contract_crew_manager.get_analysis_history()
        
        # Calculate additional analytics
        total_analyses = len(analysis_history)
        successful_analyses = sum(1 for record in analysis_history if record['success'])
        
        # Average processing time
        if analysis_history:
            avg_processing_time = sum(record['processing_time_ms'] for record in analysis_history) / len(analysis_history)
        else:
            avg_processing_time = 0.0
        
        # Contract type distribution (from sessions)
        contract_type_counts = {}
        for session in self.active_sessions.values():
            for contract_type in session.contract_types_analyzed:
                contract_type_counts[contract_type.value] = contract_type_counts.get(contract_type.value, 0) + 1
        
        # Risk level distribution (from recent analyses)
        risk_level_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        # This would need to be tracked from actual analysis results
        
        # Agent usage (from crew stats)
        agent_usage = {}
        for analysis_type, stats in crew_stats.items():
            agent_usage[analysis_type] = stats['total_requests']
        
        return ContractAnalytics(
            total_analyses=total_analyses,
            successful_analyses=successful_analyses,
            avg_processing_time=avg_processing_time,
            contract_type_distribution=contract_type_counts,
            risk_level_distribution=risk_level_counts,
            agent_usage=agent_usage,
            common_clause_types={}  # Would need to be tracked from actual analyses
        )
    
    def get_queue_status(self) -> Dict:
        """Return current analysis queue status"""
        return {
            'queue_length': len(self.analysis_queue),
            'max_concurrent': self.max_concurrent_analyses,
            'active_analyses': [
                {
                    'analysis_id': item['analysis_id'],
                    'started_at': item['started_at'],
                    'session_id': item['session_id']
                }
                for item in self.analysis_queue
            ]
        }
    
    def _get_or_create_contract(self, request: ContractRequest, text_content: str):
        """Get existing contract or create new one"""
        try:
            # Generate file hash for similarity detection
            import hashlib
            file_hash = hashlib.sha256(text_content.encode()).hexdigest()
            
            # Check for similar existing contracts
            similar_contracts = self.contract_repo.find_similar_contracts(
                file_hash=file_hash, 
                user_id=request.user_id or "default"
            )
            
            if similar_contracts:
                # Use existing contract (new version)
                contract = similar_contracts[0]
                logger.info(f"Found existing contract: {contract.id}")
                return contract
            else:
                # Create new contract
                contract_type = ContractUtils.infer_contract_type(text_content) or request.contract_type_hint
                parties = ContractUtils.extract_parties(text_content)
                
                contract = self.contract_repo.create_contract(
                    contract_name=analysis.contract_name if 'analysis' in locals() else f"Contract {len(similar_contracts) + 1}",
                    user_id=request.user_id or "default",
                    contract_type=contract_type.value if contract_type else None,
                    parties=str(parties),
                    description="Contract uploaded for analysis"
                )
                logger.info(f"Created new contract: {contract.id}")
                return contract
                
        except Exception as e:
            logger.error(f"Error in _get_or_create_contract: {str(e)}")
            # Fallback: create minimal contract
            return self.contract_repo.create_contract(
                contract_name="Unknown Contract",
                user_id=request.user_id or "default",
                description="Contract created due to error in processing"
            )
    
    def _get_or_create_session(self, session_id: Optional[str], user_id: Optional[str]) -> AnalysisSession:
        """Get existing session or create new one"""
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.last_activity = datetime.now()
            return session
        
        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        session = AnalysisSession(
            session_id=new_session_id,
            user_id=user_id
        )
        
        self.active_sessions[new_session_id] = session
        logger.info(f"Created new contract analysis session: {new_session_id}")
        return session
    
    def end_session(self, session_id: str) -> bool:
        """End a contract analysis session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Ended contract analysis session: {session_id}")
            return True
        return False

# Singleton instance
contract_service = ContractService()
