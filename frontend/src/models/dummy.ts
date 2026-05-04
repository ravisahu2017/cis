import { DashboardTile } from './models';

/**
 * Returns dummy dashboard tiles for testing and development
 */
export function getDummyDashboardTiles(): DashboardTile[] {
  return [
    {
      id: '1',
      title: 'Total Contracts',
      value: 45,
      subtitle: 'Moderate Risk',
      icon: '📊',
      color: 'bg-yellow-50 text-yellow-600',
      trend: 'Calculated',
      onClick: 'contract_section'
    },{
      id: '12',
      title: 'Upload Contracts',
      value: 45,
      subtitle: 'Moderate Risk',
      icon: '📊',
      color: 'bg-yellow-50 text-yellow-600',
      trend: 'Calculated',
      onClick: 'analyse_section'
    },
    {
      id: '2',
      title: 'Legal Risk Score',
      value: 38,
      subtitle: 'Low Risk',
      icon: '⚖️',
      color: 'bg-green-50 text-green-600',
      trend: 'Legal assessment',
      onClick: 'legal_section'
    },
    {
      id: '3',
      title: 'Financial Risk Score',
      value: 62,
      subtitle: 'High Risk',
      icon: '💰',
      color: 'bg-red-50 text-red-600',
      trend: 'Financial exposure',
      onClick: 'financial_section'
    },
    {
      id: '4',
      title: 'Operational Risk Score',
      value: 29,
      subtitle: 'Low Risk',
      icon: '⚙️',
      color: 'bg-green-50 text-green-600',
      trend: 'Operations impact',
      onClick: 'operational_section'
    },
    {
      id: '5',
      title: 'Contract Type',
      value: 'Service Agreement',
      subtitle: 'Agreement category',
      icon: '📄',
      color: 'bg-blue-50 text-blue-600',
      trend: 'Contract type',
      onClick: 'contract_type_section'
    },
    {
      id: '6',
      title: 'Total Clauses',
      value: 24,
      subtitle: 'Number of clauses',
      icon: '📋',
      color: 'bg-purple-50 text-purple-600',
      trend: 'Clause count',
      onClick: 'clause_section'
    }
  ];
}


