import { DashboardTile } from './models';
import { AlertTriangle, FileText, TrendingUp, Settings } from 'lucide-react';

/**
 * Helper function to get risk level text
 */
function getRiskLevel(score: number): string {
  if (score >= 70) return 'High Risk';
  if (score >= 40) return 'Moderate Risk';
  return 'Low Risk';
}

/**
 * Helper function to get risk color classes
 */
function getRiskColor(score: number): string {
  if (score >= 70) return 'bg-red-50 text-red-600';
  if (score >= 40) return 'bg-orange-50 text-orange-600';
  return 'bg-green-50 text-green-600';
}

/**
 * Returns dashboard tiles based on analysis results
 */
export function getTilesFromAnalysis(analysisResults: AnalysisData): DashboardTile[] {
  return [
        {
          id: '1',
          title: 'Overall Risk Score',
          value: analysisResults.overall_risk_score,
          subtitle: getRiskLevel(analysisResults.overall_risk_score),
          icon: <AlertTriangle className="w-6 h-6" />,
          color: getRiskColor(analysisResults.overall_risk_score),
          trend: 'Calculated'
        },
        {
          id: '2',
          title: 'Legal Risk Score',
          value: analysisResults.legal_risk_score,
          subtitle: getRiskLevel(analysisResults.legal_risk_score),
          icon: <FileText className="w-6 h-6" />,
          color: getRiskColor(analysisResults.legal_risk_score),
          trend: 'Legal assessment'
        },
        {
          id: '3',
          title: 'Financial Risk Score',
          value: analysisResults.financial_risk_score,
          subtitle: getRiskLevel(analysisResults.financial_risk_score),
          icon: <TrendingUp className="w-6 h-6" />,
          color: getRiskColor(analysisResults.financial_risk_score),
          trend: 'Financial exposure'
        },
        {
          id: '4',
          title: 'Operational Risk Score',
          value: analysisResults.operational_risk_score,
          subtitle: getRiskLevel(analysisResults.operational_risk_score),
          icon: <Settings className="w-6 h-6" />,
          color: getRiskColor(analysisResults.operational_risk_score),
          trend: 'Operations impact'
        },
        {
          id: '5',
          title: 'Contract Type',
          value: analysisResults.contract_type,
          subtitle: 'Agreement category',
          icon: <FileText className="w-6 h-6" />,
          color: 'bg-blue-50 text-blue-600',
          trend: analysisResults.governing_law
        },
        {
          id: '6',
          title: 'Total Clauses',
          value: analysisResults.clauses?.length || 0,
          subtitle: 'Identified provisions',
          icon: <FileText className="w-6 h-6" />,
          color: 'bg-purple-50 text-purple-600',
          trend: `${analysisResults.clauses?.filter(c => c.risk_tag === 'High').length || 0} high risk`
        }
    ];
}

export function getAnalysisChatMsg(analysis: AnalysisData, fileCount: number): ChatMessage {
  const analysisMessage: ChatMessage = {
    id: Date.now().toString(),
    type: 'bot',
    message: `Analysis complete! I've analyzed ${fileCount} contract(s). Key findings:\n\n• Overall Risk Score: ${analysis.overall_risk_score || 'N/A'}\n• Legal Risk Score: ${analysis.legal_risk_score || 'N/A'}\n• Financial Risk Score: ${analysis.financial_risk_score || 'N/A'}\n• Operational Risk Score: ${analysis.operational_risk_score || 'N/A'}\n• Total Clauses: ${analysis.clauses?.length || 0}\n• High Risk Clauses: ${analysis.clauses?.filter((c: Clause) => c.risk_tag === 'High').length || 0}`,
    timestamp: new Date().toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    })
  };
  return analysisMessage;
}

