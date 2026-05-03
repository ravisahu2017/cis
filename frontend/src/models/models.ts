interface DashboardTile {
  id: string;
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  trend?: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  message: string;
  timestamp: string;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: string;
  file: File; // Store actual File object for API upload
}

interface Clause {
  clause_type: string;
  content: string;
  recommendation: string;
  risk_score: number;
  risk_tag: string;
  risk_category: string;
}

interface ContractMetadata {
  contract_type: string;
  effective_date: string;
  effective_date: string;
  currency: string;
  governing_law: string;
  parties: string[];
  renewal_term: string;
  termination_notice: string;
  total_value: string;
}

interface Contract {
  id: string;
  contract_name: string;
  contract_type: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  file_path: string;
  file_size: number;
  analysis_status: 'pending' | 'processing' | 'completed' | 'failed';
  analysis_data?: AnalysisData;
}

interface ContractsResponse {
  contracts: Contract[];
  total_count: number;
  limit: number;
  offset: number;
}

interface AnalysisData {
  contract_name: string;
  metadata: ContractMetadata;

  risk_level: string;
  financial_risk_score: number;
  legal_risk_score: number;
  operational_risk_score: number;
  overall_risk_score: number;

  key_recommendations: string[];
  clauses: Clause[];

  analysis_timestamp: string;
  executive_summary: string;
  processing_time_ms: number;
}