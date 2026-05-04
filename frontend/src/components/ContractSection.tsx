'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, FileText, TrendingUp, AlertTriangle, Settings, CheckCircle, 
  Clock, Loader2, Calendar, User, Tag, Shield, DollarSign, Building
} from 'lucide-react';
import { Contract } from '@/models/models';
import contractController from '@/controllers/contract';
import SectionNavigation from './SectionNavigation';

interface ContractSectionProps {
  contractId: string;
  onBack: () => void;
  onHome?: () => void;
}

export default function ContractSection({ contractId, onBack, onHome }: ContractSectionProps) {
  const [contract, setContract] = useState<Contract | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchContract();
  }, [contractId]);

  const fetchContract = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const fetchedContract = await contractController.fetchContract('default', contractId);
      if (fetchedContract) {
        setContract(fetchedContract);
      } else {
        setError('Contract not found');
      }
    } catch (err) {
      console.error('Failed to fetch contract:', err);
      setError('Failed to load contract');
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskLevel = (score: number) => {
    if (score >= 70) return 'High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
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
    <div className="flex-1 overflow-y-auto">
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

      <div className="px-6 py-6 space-y-6">
        {/* Contract Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-white rounded-xl shadow-sm border border-gray-100 p-6"
        >
          <h2 className="text-lg font-medium text-gray-900 mb-4">Contract Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Contract Type</p>
                <p className="font-medium text-gray-900">{contract.contract_type || 'Unknown'}</p>
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
