"""
Contract Layer - Main Service
Orchestrates contract analysis functionality and provides API interface
"""

import uuid
import time
import asyncio
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .models import (
    ContractRequest, ContractResponse, ContractAnalysis, ContractCapabilities, 
    ContractAnalytics, AnalysisSession, AnalysisType, ContractType, AnalysisStatus
)
from .contract_utils import ContractUtils
from .crew import contract_crew_manager
from .agents import get_agent_capabilities
from utils import logger, read_pdf, read_docx, read_txt, read_image, HttpBaseResponse, QueuedResponse
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
        
        # Start background queue processor
        self.queue_processor_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.queue_processor_thread.start()
    
    def analyze_contract(self, request: ContractRequest) -> HttpBaseResponse:
        """
        Submit contract analysis request and return job ID immediately
        """
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            # Extract and validate content
            text_content = self._extract_text_content(request)
            if not text_content or len(text_content.strip()) < 100:
                raise ValueError("Insufficient text content (minimum 100 characters)")
            
            analysis_types = self._validate_analysis_types(request.analysis_types)
            
            # Create session (this is our job tracker)
            session = AnalysisSession(
                session_id=analysis_id,  # Use analysis_id as session_id
                user_id=request.user_id or "default",
                created_at=datetime.now(),
                last_activity=datetime.now(),
                analyses_completed=0,
                total_processing_time_ms=0,
                contract_types_analyzed=[],
                status=AnalysisStatus.QUEUED,
                current_analysis_id=analysis_id,
                progress=0,
                message="Analysis queued for processing"
            )
            
            # Add to queue
            queue_item = {
                'analysis_id': analysis_id,
                'request': request,
                'text_content': text_content,
                'analysis_types': analysis_types,
                'session': session
            }
            self.analysis_queue.append(queue_item)
            logger.info(f"Analysis {analysis_id} queued (position: {len(self.analysis_queue)})")

            # Start analysis
            self._run_analysis_async(
                analysis_id, 
                queue_item['text_content'], 
                queue_item['analysis_types'], 
                queue_item['request']
            )

            return HttpBaseResponse(
                success=True,
                message="Contract analysis submitted successfully",
                data=QueuedResponse(
                    analysis_id=analysis_id,
                    status=session.status,
                    message=session.message,
                    estimated_wait_time=len(self.analysis_queue) * 20
                ),
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Error submitting analysis: {str(e)}")
            return HttpBaseResponse(
                success=False,
                message="Failed to submit analysis",
                error=str(e),
                data={'analysis_id': analysis_id}
            )
    
    def get_analysis_status(self, analysis_id: str) -> HttpBaseResponse:
        """Get analysis status using active_sessions"""
        try:
            # Check if analysis is in queue
            queue_position = None
            for i, item in enumerate(self.analysis_queue):
                if item['analysis_id'] == analysis_id:
                    queue_position = i + 1
                    break
            
            if queue_position is not None:
                # Still in queue
                return HttpBaseResponse(
                    success=True,
                    message="Analysis status retrieved",
                    data={
                        'analysis_id': analysis_id,
                        'status': AnalysisStatus.QUEUED,
                        'progress': 0,
                        'message': 'Queued for processing',
                        'queue_position': queue_position
                    }
                )
            
            # Check if analysis is active or completed
            session = self.active_sessions.get(analysis_id)
            if not session:
                return HttpBaseResponse(
                    success=False,
                    message="Analysis not found",
                    error=f"Analysis ID {analysis_id} not found"
                )
            
            # Calculate progress
            progress = session.progress
            if session.status == AnalysisStatus.PROCESSING and session.current_analysis_id:
                # Estimate progress based on time
                elapsed = (datetime.now() - session.last_activity).total_seconds()
                progress = min(95, int((elapsed / 20) * 100))
            
            response_data = {
                'analysis_id': analysis_id,
                'status': session.status,
                'progress': progress,
                'message': session.message,
                'created_at': session.created_at.timestamp(),
                'queue_position': None
            }
            
            # Add result if completed
            if hasattr(session, 'result') and session.result:
                response_data['result'] = session.result
            
            return HttpBaseResponse(
                success=True,
                message="Analysis status retrieved",
                data=response_data
            )
            
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return HttpBaseResponse(
                success=False,
                message="Failed to get status",
                error=str(e)
            )
    
    def _run_analysis_async(self, analysis_id: str, text_content: str, analysis_types: List[AnalysisType], request: ContractRequest):
        """Run analysis in background thread"""
        def analysis_worker():
            session = self.active_sessions.get(analysis_id)
            if not session:
                return
            
            try:
                # Update status
                session.status = AnalysisStatus.PROCESSING
                session.message = "Processing analysis..."
                session.progress = 10
                session.last_activity = datetime.now()
                
                logger.info(f"Starting analysis {analysis_id}")
                
                # Perform analysis
                from contract.mock_data import get_mock_analysis
                analysis = get_mock_analysis(text_content, analysis_id, analysis_types)
                
                # Simulate processing time with progress updates
                for i in range(20):
                    time.sleep(1)
                    session.progress = min(90, 10 + i * 4)
                    session.last_activity = datetime.now()
                    if i == 10:
                        session.message = "Analyzing contract clauses..."
                    elif i == 15:
                        session.message = "Generating recommendations..."
                
                # Save result
                session.status = AnalysisStatus.COMPLETED
                session.message = "Analysis completed successfully"
                session.progress = 100
                session.result = analysis
                session.last_activity = datetime.now()
                
                logger.info(f"Analysis {analysis_id} completed")
                
            except Exception as e:
                logger.error(f"Analysis {analysis_id} failed: {str(e)}")
                session.status = AnalysisStatus.FAILED
                session.message = f"Analysis failed: {str(e)}"
                session.last_activity = datetime.now()
            
            finally:
                # Remove from active sessions after some time
                threading.Timer(300, lambda: self.active_sessions.pop(analysis_id, None)).start()
                
                # Process next item in queue
                self._process_queue()
        
        # Start worker thread
        thread = threading.Thread(target=analysis_worker, daemon=True)
        thread.start()
    
    def _process_queue(self):
        """Process next item in queue if slots available"""
        while (self.analysis_queue and 
               len(self.active_sessions) < self.max_concurrent_analyses):
            
            # Get next item
            queue_item = self.analysis_queue.pop(0)
            analysis_id = queue_item['analysis_id']
            
            # Move to active sessions
            session = queue_item['session']
            self.active_sessions[analysis_id] = session
            
            # Start analysis
            self._run_analysis_async(
                analysis_id, 
                queue_item['text_content'], 
                queue_item['analysis_types'], 
                queue_item['request']
            )
            
            logger.info(f"Started queued analysis {analysis_id}")
    
    def _save_analysis_result(self, job_info: Dict, analysis: ContractAnalysis) -> None:
        """Save analysis result to database"""
        try:
            # Create contract and version
            contract = self.contract_repo.create_contract(
                contract_name=analysis.contract_name,
                user_id=job_info['request'].user_id or "default",
                contract_type=analysis.metadata.contract_type.value if analysis.metadata.contract_type else None,
                parties=str(analysis.metadata.parties) if analysis.metadata.parties else None,
                description="Contract analyzed via API"
            )
            
            # Create version
            version = self.contract_repo.create_version(
                contract_id=contract.id,
                file_content=job_info['text_content'],
                version_name="v1.0",
                change_summary="Initial analysis"
            )
            
            # Save analyses
            agents_used = [agent_type.value for agent_type in job_info['analysis_types']]
            for analysis_type in job_info['analysis_types']:
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
            raise
    
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
