'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Loader2, FileText, Search, Filter, RefreshCw
} from 'lucide-react';
import { Contract } from '@/models/models';
import contractController from '@/controllers/contract';
import SectionNavigation from './SectionNavigation';

interface ContractListSectionProps {
  onContractSelect?: (contractId: string) => void;
  onBack?: () => void;
  onHome?: () => void;
}

export default function ContractListSection({ onContractSelect, onBack, onHome }: ContractListSectionProps) {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [isLoadingContracts, setIsLoadingContracts] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('created_at');
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  // Fetch contracts on component mount and when pagination changes
  useEffect(() => {
    fetchContracts();
  }, [currentPage, pageSize]);

  const fetchContracts = async () => {
    setIsLoadingContracts(true);
    try {
      const offset = (currentPage - 1) * pageSize;
      const paginatedResponse = await contractController.fetchWithPagination('default', pageSize, offset);
      
      setContracts(paginatedResponse.items);
      setTotalCount(paginatedResponse.totalCount);
      setHasMore(paginatedResponse.hasMore);
    } catch (error) {
      console.error('Failed to fetch contracts:', error);
      setContracts([]);
      setTotalCount(0);
      setHasMore(false);
    } finally {
      setIsLoadingContracts(false);
    }
  };

  const getRiskLevel = (score: number) => {
    if (score >= 70) return 'High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
  };

  // Filter and sort contracts
  const filteredAndSortedContracts = contracts
    .filter(contract => {
      const matchesSearch = contract.contract_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           contract.contract_type?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesFilter = filterStatus === 'all' || contract.analysis_status === filterStatus;
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return (a.contract_name || '').localeCompare(b.contract_name || '');
        case 'risk_score':
          return (b.analysis_data?.overall_risk_score || 0) - (a.analysis_data?.overall_risk_score || 0);
        case 'status':
          return (a.analysis_status || '').localeCompare(b.analysis_status || '');
        case 'created_at':
        default:
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
    });

  const handleContractClick = (contract: Contract) => {
    if (onContractSelect && contract.id) {
      onContractSelect(contract.id);
    }
  };

  // Pagination handlers
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    setCurrentPage(1); // Reset to first page when changing page size
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (hasMore) {
      setCurrentPage(currentPage + 1);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <SectionNavigation
        title="All Contracts"
        subtitle="Browse and manage your contract portfolio"
        showBackButton={!!onBack}
        showHomeButton={!!onHome}
        onBack={onBack}
        onHome={onHome}
        extraActions={
          <button
            onClick={() => {
              setCurrentPage(1);
              fetchContracts();
            }}
            disabled={isLoadingContracts}
            className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isLoadingContracts ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Loading...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </>
            )}
          </button>
        }
      />
      
      <div className="px-6 py-6">

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search contracts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="sm:w-48">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          {/* Sort */}
          <div className="sm:w-48">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="created_at">Latest First</option>
              <option value="name">Name (A-Z)</option>
              <option value="risk_score">Risk Score (High-Low)</option>
              <option value="status">Status</option>
            </select>
          </div>
        </div>
      </div>

      {/* Contracts Table */}
      {isLoadingContracts ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
        </div>
      ) : filteredAndSortedContracts.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">
            {contracts.length === 0 ? 'No contracts found in database' : 'No contracts match your filters'}
          </p>
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="mt-2 text-blue-600 hover:text-blue-700 text-sm"
            >
              Clear search
            </button>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contract Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Score</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAndSortedContracts.map((contract) => (
                  <motion.tr
                    key={contract.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className={`hover:bg-gray-50 cursor-pointer ${onContractSelect ? 'hover:bg-blue-50' : ''}`}
                    onClick={() => handleContractClick(contract)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <FileText className="w-4 h-4 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">{contract.contract_name}</div>
                          <div className="text-xs text-gray-500">{(contract.file_size / 1024 / 1024).toFixed(2)} MB</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {contract.contract_type || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        contract.analysis_status === 'completed' ? 'bg-green-100 text-green-800' :
                        contract.analysis_status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        contract.analysis_status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {contract.analysis_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(contract.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {contract.analysis_data?.overall_risk_score ? (
                        <div className="flex items-center">
                          <span className={`text-sm font-medium ${
                            contract.analysis_data.overall_risk_score >= 70 ? 'text-red-600' :
                            contract.analysis_data.overall_risk_score >= 40 ? 'text-yellow-600' :
                            'text-green-600'
                          }`}>
                            {contract.analysis_data.overall_risk_score}
                          </span>
                          <span className="ml-2 text-xs text-gray-500">
                            {getRiskLevel(contract.analysis_data.overall_risk_score)}
                          </span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">—</span>
                      )}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Results count */}
          <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 text-xs text-gray-500 flex items-center justify-between">
            <span>
              Showing {filteredAndSortedContracts.length} of {contracts.length} contracts
              {totalCount > 0 && ` (Page ${currentPage})`}
            </span>
            
            {/* Page Size Selector */}
            <div className="flex items-center space-x-2">
              <span className="text-gray-500">Show:</span>
              <select
                value={pageSize}
                onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                className="text-xs border border-gray-300 rounded px-2 py-1 focus:ring-1 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>
          </div>
          
          {/* Pagination Controls */}
          {contracts.length > 0 && (
            <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Page {currentPage}
                {totalCount > 0 && ` of ${Math.ceil(totalCount / pageSize)}`}
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={handlePreviousPage}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                
                {/* Page Numbers */}
                <div className="flex items-center space-x-1">
                  {Array.from({ length: Math.min(5, Math.ceil(totalCount / pageSize)) }, (_, i) => {
                    const pageNum = i + 1;
                    const isActive = pageNum === currentPage;
                    return (
                      <button
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        className={`w-8 h-8 text-sm border rounded transition-colors ${
                          isActive
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'border-gray-300 hover:bg-gray-100'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  onClick={handleNextPage}
                  disabled={!hasMore}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}
        </div>
    </div>
  );
}
