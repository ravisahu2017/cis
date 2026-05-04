'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { backendApi } from '@/utils/api';
import contractController from '@/controllers/contract'
import { AlertTriangle, Clock, Users, Settings } from 'lucide-react';
import ErrorBoundary from '@/components/ErrorBoundary';
import ChatSection from '@/components/ChatSection';
import DashboardSection from '@/components/DashboardSection';
import { DashboardTile, ChatMessage, UploadedFile, AnalysisData, Contract, ContractsResponse, RecentAnalysis } from '@/models/models';
import { getDummyDashboardTiles } from '@/models/dummy';
import { getTilesFromAnalysis , getAnalysisChatMsg } from '@/models/dataFiller';
import AnalyseSection from '@/components/AnalyseSection';
import ContractListSection from '@/components/ContractListSection';
import ContractSection from '@/components/ContractSection';

export default function Home() {
  
  const [analysisResults, setAnalysisResults] = useState<AnalysisData | null>(null);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('');
  const [isLoadingContracts, setIsLoadingContracts] = useState(false);
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysis[]>([]);
  const [isLoadingAnalyses, setIsLoadingAnalyses] = useState(false);

  const [mainSection, setMainSection] = useState<'dashboard' | 'analyse' | 'contract' | 'contract-list' | 'default'>('dashboard');
  const [selectedContractId, setSelectedContractId] = useState<string | null>(null);

 

  // Fetch recent analyses from database
  const fetchRecentAnalysis = async () => {
    setIsLoadingAnalyses(true);
    contractController.fetchRecentAnalysis('default', 12, 3).then(items => {
      if (items) {
        setRecentAnalyses(items);
      }
    }).catch(error => {
      console.error('Failed to fetch recent analyses:', error);
    }).finally(() => {
      setIsLoadingAnalyses(false);
    });
  };

  // Load contracts and analyses on component mount
  useEffect(() => {
    fetchRecentAnalysis();
  }, []);

  const getRiskLevel = (score: number): string => {
    if (score >= 70) return 'High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
  };

  

  const handleDashboardAction = (cta: { action: string; data: any }) => {
    const section = cta.data.section;
    switch (section) {
      case 'contract_section':
        setMainSection('contract-list');
        break;
      case 'analyse_section':
        setMainSection('analyse');
        break;
      default:
        console.log('Unknown action:', cta.action);
    }
  };

  const handleContractSelect = (contractId: string) => {
    setSelectedContractId(contractId);
    setMainSection('contract');
  };

  const handleBackToContracts = () => {
    setSelectedContractId(null);
    setMainSection('contract-list');
  };

  const handleHome = () => {
    setMainSection('dashboard');
  };

  const handleBackToDashboard = () => {
    setMainSection('dashboard');
  };


  const mainContent = () => {
    switch (mainSection) {
      case 'analyse':
        return <AnalyseSection 
                onAnalysisComplete={(analysis) => {
                  setAnalysisResults(analysis);
                }}
                onBack={handleBackToDashboard}
                onHome={handleHome}
              />;
      case 'contract-list':
        return <ContractListSection 
                onContractSelect={handleContractSelect}
                onBack={handleBackToDashboard}
                onHome={handleHome}
              />;
      case 'contract':
        return selectedContractId ? (
          <ContractSection 
            contractId={selectedContractId} 
            onBack={handleBackToContracts}
            onHome={handleHome}
          />
        ) : null;
      default:
        return <DashboardSection
              // Contracts
              isLoadingContracts={isLoadingContracts}
              getRiskLevel={getRiskLevel}
              
              // Recent Analyses
              recentAnalyses={recentAnalyses}
              isLoadingAnalyses={isLoadingAnalyses}
              fetchRecentAnalysis={fetchRecentAnalysis}
              
              onAnalysisComplete={(analysis) => {
                console.log('Analysis complete:', analysis);
                setAnalysisResults(analysis);
              }}
              onDashboardAction={handleDashboardAction}
              onHome={handleHome}
            />;
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-[#F8F8F8] text-[#1A1A1A]">
        {/* Navigation */}
        <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-[#E5E5E5]">
          <div className="max-w-full px-6 py-4 flex justify-between items-center">
            <div className="text-2xl font-light tracking-wide">Contract Intelligence System</div>
            <div className="flex items-center space-x-4">
              <button className="px-4 py-2 text-[#1A1A1A] hover:bg-gray-100 rounded-lg text-sm font-medium transition-colors">
                Settings
              </button>
              <div className="w-8 h-8 bg-[#1A1A1A] rounded-full flex items-center justify-center text-white text-sm">
                U
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="pt-20 h-screen flex">
          <div className="flex-1 overflow-y-auto px-6 py-6">
            {mainContent()}
          </div>
          <div className="w-96 border-l border-gray-200 overflow-y-auto">
            <ChatSection 
              analysisResults={analysisResults}
            />
          </div>
        </main>
    </div>
    </ErrorBoundary>
  );
}
