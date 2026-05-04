'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, FileText, TrendingUp, AlertTriangle, Settings, CheckCircle, 
  Clock, Loader2, Calendar, User, Tag, Shield, DollarSign, Building
} from 'lucide-react';
import { Contract, ContractVersion } from '@/models/models';
import contractController from '@/controllers/contract';
import SectionNavigation from './SectionNavigation';

interface ContractSectionProps {
  contractId: string;
  onBack: () => void;
  onHome?: () => void;
}

export default function ContractSection({ contractId, onBack, onHome }: ContractSectionProps) {
  const [contract, setContract] = useState<Contract | null>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchContract();
  }, [contractId]);

  const fetchContract = async () => {
    setIsLoading(true);
    try {
      const fetchedContract = await contractController.fetchContract('default', contractId);
      setContract(fetchedContract);
      setError(null);
    } catch (err) {
      setError('Failed to fetch contract details');
      setContract(null);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskLevel = (score: number) => {
    if (score >= 70) return 'High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
  };

  const handleViewVersion = (version: ContractVersion) => {
    console.log('Viewing version:', version);
    // TODO: Implement version viewing logic
    // This could open a modal, navigate to version details, or update the current view
  };

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'text-red-600 bg-red-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      </div>
    );
  }

  if (error || !contract) {
    return (
      <div className="flex-1 overflow-y-auto">
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">{error || 'Contract not found'}</p>
          <button
            onClick={onBack}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Back to Contracts
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1">
      <SectionNavigation
        title={contract.contract_name}
        subtitle="Contract Details"
        showBackButton={true}
        showHomeButton={!!onHome}
        onBack={onBack}
        onHome={onHome}
        extraActions={
          <span className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${getStatusColor(contract.analysis_status)}`}>
            {contract.analysis_status}
          </span>
        }
      />

      <div className="space-y-6">
        {/* Contract Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-xl shadow-sm border border-gray-100 p-6"
        >
          <h2 className="text-lg font-medium text-gray-900 mb-4">Contract Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Contract Type</p>
                <p className="font-medium text-gray-900">{contract.contract_type || 'Service Agreement'}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Calendar className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Created Date</p>
                <p className="font-medium text-gray-900">{new Date(contract.created_at).toLocaleDateString()}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <User className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">User ID</p>
                <p className="font-medium text-gray-900">{contract.user_id || 'default'}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Tag className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">File Size</p>
                <p className="font-medium text-gray-900">{(contract.file_size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Building className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Parties</p>
                <p className="font-medium text-gray-900">Tech Solutions Inc. & Client Corp</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <DollarSign className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Contract Value</p>
                <p className="font-medium text-gray-900">$250,000</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Clock className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Duration</p>
                <p className="font-medium text-gray-900">12 months</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Shield className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Renewal</p>
                <p className="font-medium text-gray-900">Auto-renewal</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Contract Details */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="bg-white rounded-xl shadow-sm border border-gray-100 p-6"
        >
          <h2 className="text-lg font-medium text-gray-900 mb-4">Contract Details</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Description</h3>
              <p className="text-sm text-gray-600">This Service Agreement governs the provision of technology consulting services between Tech Solutions Inc. and Client Corp for the development and maintenance of custom software solutions.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Start Date</h3>
                <p className="text-sm text-gray-600">January 1, 2024</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">End Date</h3>
                <p className="text-sm text-gray-600">December 31, 2024</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Payment Terms</h3>
                <p className="text-sm text-gray-600">Net 30 days</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Governing Law</h3>
                <p className="text-sm text-gray-600">State of California</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Version History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="bg-white rounded-xl shadow-sm border border-gray-100 p-6"
        >
          <h2 className="text-lg font-medium text-gray-900 mb-4">Version History</h2>
          <div className="space-y-3">
            {contract.versions?.map((version: ContractVersion, index: number) => {
              const isLatest = index === 0;
              const versionNumber = version.version || `v${contract.versions?.length - index}`;
              const isActive = version.status === 'active';
              
              return (
                <div 
                  key={version.id || index}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    isLatest 
                      ? 'bg-blue-50 border-blue-200' 
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 text-white rounded-full flex items-center justify-center text-sm font-medium ${
                      isLatest ? 'bg-blue-500' : 'bg-gray-400'
                    }`}>
                      {versionNumber}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        Version {versionNumber}
                      </p>
                      <p className="text-xs text-gray-500">
                        {isLatest && 'Current Version • '}
                        Updated {new Date(version.updated_at || version.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      isActive 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {isActive ? 'Active' : 'Archived'}
                    </span>
                    <button 
                      onClick={() => handleViewVersion(version)}
                      className="text-blue-600 hover:text-blue-700 text-sm"
                    >
                      View
                    </button>
                  </div>
                </div>
              );
            }) || (
              // Fallback if no versions data
              <>
                <div className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                      1
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Version 1.0</p>
                      <p className="text-xs text-gray-500">Current Version • Updated {new Date(contract.updated_at || contract.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Active</span>
                    <button className="text-blue-600 hover:text-blue-700 text-sm">View</button>
                  </div>
                </div>
              </>
            )}
          </div>
        </motion.div>

        {/* Risk Analysis */}
        {contract.analysis_data && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-6"
          >
            <h2 className="text-lg font-medium text-gray-900 mb-4">Risk Analysis</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className={`p-4 rounded-lg ${getRiskColor(contract.analysis_data.overall_risk_score)}`}>
                <div className="flex items-center justify-between mb-2">
                  <Shield className="w-5 h-5" />
                  <span className="text-2xl font-bold">{contract.analysis_data.overall_risk_score}</span>
                </div>
                <p className="text-sm font-medium">Overall Risk</p>
                <p className="text-xs opacity-75">{getRiskLevel(contract.analysis_data.overall_risk_score)}</p>
              </div>
              
              <div className={`p-4 rounded-lg ${getRiskColor(contract.analysis_data.legal_risk_score)}`}>
                <div className="flex items-center justify-between mb-2">
                  <FileText className="w-5 h-5" />
                  <span className="text-2xl font-bold">{contract.analysis_data.legal_risk_score}</span>
                </div>
                <p className="text-sm font-medium">Legal Risk</p>
                <p className="text-xs opacity-75">{getRiskLevel(contract.analysis_data.legal_risk_score)}</p>
              </div>
              
              <div className={`p-4 rounded-lg ${getRiskColor(contract.analysis_data.financial_risk_score)}`}>
                <div className="flex items-center justify-between mb-2">
                  <DollarSign className="w-5 h-5" />
                  <span className="text-2xl font-bold">{contract.analysis_data.financial_risk_score}</span>
                </div>
                <p className="text-sm font-medium">Financial Risk</p>
                <p className="text-xs opacity-75">{getRiskLevel(contract.analysis_data.financial_risk_score)}</p>
              </div>
              
              <div className={`p-4 rounded-lg ${getRiskColor(contract.analysis_data.operational_risk_score)}`}>
                <div className="flex items-center justify-between mb-2">
                  <Building className="w-5 h-5" />
                  <span className="text-2xl font-bold">{contract.analysis_data.operational_risk_score}</span>
                </div>
                <p className="text-sm font-medium">Operational Risk</p>
                <p className="text-xs opacity-75">{getRiskLevel(contract.analysis_data.operational_risk_score)}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Clauses */}
        {contract.analysis_data?.clauses && contract.analysis_data.clauses.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-6"
          >
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              Contract Clauses ({contract.analysis_data.clauses.length})
            </h2>
            <div className="space-y-3">
              {contract.analysis_data.clauses.map((clause, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 mb-2">{clause.title}</h3>
                      <p className="text-sm text-gray-600 mb-2">{clause.description}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className={`px-2 py-1 rounded-full ${getRiskColor(clause.risk_score)}`}>
                          Risk: {clause.risk_score}
                        </span>
                        <span>Category: {clause.category}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Analysis Metadata */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="bg-white rounded-xl shadow-sm border border-gray-100 p-6"
        >
          <h2 className="text-lg font-medium text-gray-900 mb-4">Analysis Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Analysis ID</p>
              <p className="font-mono text-sm text-gray-900">{contract.analysis_id || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Last Updated</p>
              <p className="text-sm text-gray-900">
                {contract.updated_at ? new Date(contract.updated_at).toLocaleString() : 'N/A'}
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
