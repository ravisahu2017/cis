'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { backendApi } from '@/utils/api';
import { FileText, TrendingUp, AlertTriangle, Clock, Users, Settings, Send, Bot, User, Upload, X, File, Loader2 } from 'lucide-react';
import ErrorBoundary from '@/components/ErrorBoundary';
import { DashboardTile, ChatMessage, UploadedFile, AnalysisData } from '@/models/models';
import { getDummyDashboardTiles } from '@/models/dummy';
import { getTilesFromAnalysis , getAnalysisChatMsg } from '@/models/dataFiller';


export default function Home() {
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'bot',
      message: 'Hello! I\'m your contract intelligence assistant. How can I help you analyze contracts today?',
      timestamp: '9:50 PM'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisData | null>(null);
  const [isSummaryCollapsed, setIsSummaryCollapsed] = useState(false);
  const [isClausesCollapsed, setIsClausesCollapsed] = useState(true);
  const [collapsedCategories, setCollapsedCategories] = useState<Set<string>>(new Set());
  const [isChatStreaming, setIsChatStreaming] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('');

  // Generate dynamic dashboard tiles based on analysis results
  const getDashboardTiles = (): DashboardTile[] => {
    if (analysisResults) {
      return getTilesFromAnalysis(analysisResults);
    }
    
    return getDummyDashboardTiles();
  };

  const getRiskColor = (score: number): string => {
    if (score >= 70) return 'bg-red-50 text-red-600';
    if (score >= 40) return 'bg-orange-50 text-orange-600';
    return 'bg-green-50 text-green-600';
  };

  const getRiskLevel = (score: number): string => {
    if (score >= 70) return 'High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
  };

  const toggleCategory = (category: string) => {
    setCollapsedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isChatStreaming) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      message: inputMessage,
      timestamp: new Date().toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsChatStreaming(true);
    setCurrentStreamingMessage('');
    
    // Create a placeholder for streaming response
    const botMessageId = (Date.now() + 1).toString();
    const botMessagePlaceholder: ChatMessage = {
      id: botMessageId,
      type: 'bot',
      message: '',
      timestamp: new Date().toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      })
    };
    
    setChatMessages(prev => [...prev, botMessagePlaceholder]);
    
    try {
      // Prepare context from analysis results if available
      const context = analysisResults ? {
        contract_name: analysisResults.contract_name,
        overall_risk_score: analysisResults.overall_risk_score,
        clauses: analysisResults.clauses.map(c => ({
          type: c.clause_type,
          risk_score: c.risk_score,
          risk_tag: c.risk_tag,
          content: c.content.substring(0, 200) + '...'
        }))
      } : null;
      
      // Use regular HTTP API for chat
      const requestData = {
        message: inputMessage,
        context: context,
        session_id: null,
        user_id: null
      };

      const response = await backendApi.post('/chat', requestData);
      
      if (response.success && response.data) {
        const botResponse: ChatMessage = {
          id: botMessageId,
          type: 'bot',
          message: response.data.message || response.data.response || 'I received your message but couldn\'t generate a response.',
          timestamp: new Date().toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
          })
        };
        setChatMessages(prev => prev.map(msg => 
          msg.id === botMessageId ? botResponse : msg
        ));
      } else {
        throw new Error(response.error || 'Chat request failed');
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage: ChatMessage = {
        id: botMessageId,
        type: 'bot',
        message: `Sorry, I'm having trouble connecting right now. Please try again.`,
        timestamp: new Date().toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
      };
      
      setChatMessages(prev => prev.map(msg => 
        msg.id === botMessageId ? errorMessage : msg
      ));
    } finally {
      setIsChatStreaming(false);
      setCurrentStreamingMessage('');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFiles(files);
    }
  };

  const handleFiles = (files: File[]) => {
    const newFiles: UploadedFile[] = files.map(file => ({
      id: Date.now().toString() + Math.random().toString(),
      name: file.name,
      size: file.size,
      type: file.type,
      uploadedAt: new Date().toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      }),
      file: file // Store actual File object
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const analyzeContracts = async () => {
    if (uploadedFiles.length === 0) return;
    
    setIsAnalyzing(true);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      
      // Add files to FormData - backend expects 'files' field with actual File objects
      uploadedFiles.forEach((uploadedFile) => {
        formData.append('file', uploadedFile.file);
      });
      
      // Add analysis_types key with ["legal"] as value
      formData.append('analysis_types', ["legal"]);
      
      // Call backend API
      const response = await backendApi.postFormData('/contract/analyze', formData, { timeout: 15 * 60 * 1000});
      
      if (response.success) {
        console.log(response.data);
        setAnalysisResults(response.data.analysis);
        
        // Update chat with analysis results
        const analysisMessage: ChatMessage = getAnalysisChatMsg(response.data.analysis, uploadedFiles);
        
        setChatMessages(prev => [...prev, analysisMessage]);
      } else {
        throw new Error(response.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Contract analysis error:', error);
      
      // Update chat with error message
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'bot',
        message: `Sorry, I encountered an error while analyzing the contracts: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
        timestamp: new Date().toLocaleTimeString('en-US', { 
          hour: 'numeric', 
          minute: '2-digit',
          hour12: true 
        })
      };
      
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const clearAllFiles = () => {
    setUploadedFiles([]);
    setAnalysisResults(null);
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
        {/* Dashboard Section - Left */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-6xl">
            <div className="mb-8">
              <h1 className="text-3xl font-light mb-2">Dashboard Overview</h1>
              <p className="text-gray-600">Monitor your contract intelligence metrics</p>
            </div>

            {/* Upload Contract Section */}
            <div className="mt-8 mb-8">
              <h2 className="text-xl font-light mb-4">Upload Contracts</h2>
              <div className="bg-white rounded-xl shadow-sm border border-gray-100">
                {/* Upload Area */}
                <div
                  className={`p-8 border-2 border-dashed rounded-xl transition-colors ${
                    isDragging 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  <div className="text-center">
                    <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <h3 className="text-lg font-medium mb-2">
                      {isDragging ? 'Drop files here' : 'Upload Contract Documents'}
                    </h3>
                    <p className="text-gray-500 mb-4">
                      Drag and drop files here, or click to browse
                    </p>
                    <input
                      type="file"
                      multiple
                      onChange={handleFileInput}
                      accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.tiff,.bmp"
                      className="hidden"
                      id="file-input"
                    />
                    <label
                      htmlFor="file-input"
                      className="inline-flex items-center px-6 py-3 bg-[#1A1A1A] text-white rounded-xl cursor-pointer hover:bg-[#2A2A2A] transition-colors"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Choose Files
                    </label>
                    <p className="text-xs text-gray-400 mt-4">
                      Supported formats: PDF, DOC, DOCX, TXT, JPG, PNG, TIFF, BMP (Max 10MB)
                    </p>
                  </div>
                </div>

                {/* Uploaded Files List */}
                {uploadedFiles.length > 0 && (
                  <div className="p-6 border-t border-gray-200">
                    <h4 className="font-medium mb-4">Uploaded Files ({uploadedFiles.length})</h4>
                    <div className="space-y-3">
                      {uploadedFiles.map((file) => (
                        <motion.div
                          key={file.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                              <File className="w-4 h-4 text-blue-600" />
                            </div>
                            <div>
                              <p className="text-sm font-medium">{file.name}</p>
                              <p className="text-xs text-gray-500">
                                {formatFileSize(file.size)} • {file.uploadedAt}
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => removeFile(file.id)}
                            className="p-1 hover:bg-gray-200 rounded transition-colors"
                          >
                            <X className="w-4 h-4 text-gray-500" />
                          </button>
                        </motion.div>
                      ))}
                    </div>
                    {uploadedFiles.length > 0 && (
                      <div className="mt-4 flex space-x-3">
                        <button
                          onClick={analyzeContracts}
                          disabled={isAnalyzing}
                          className="flex-1 px-4 py-2 bg-[#1A1A1A] text-white rounded-lg hover:bg-[#2A2A2A] transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                        >
                          {isAnalyzing ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Analyzing...
                            </>
                          ) : (
                            'Analyze Contracts'
                          )}
                        </button>
                        <button
                          onClick={clearAllFiles}
                          disabled={isAnalyzing}
                          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Clear All
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Dashboard Tiles Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {getDashboardTiles().map((tile, index) => (
                <motion.div
                  key={tile.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-lg ${tile.color}`}>
                      {tile.icon}
                    </div>
                    <span className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded">
                      {tile.trend}
                    </span>
                  </div>
                  <div className="mb-1">
                    <h3 className="text-2xl font-semibold">{tile.value}</h3>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">{tile.title}</h4>
                    <p className="text-xs text-gray-500">{tile.subtitle}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Contract Summary Section */}
            {analysisResults && (
              <div className="mt-8">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-light">Contract Summary</h2>
                  <button
                    onClick={() => setIsSummaryCollapsed(!isSummaryCollapsed)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <motion.div
                      animate={{ rotate: isSummaryCollapsed ? 0 : 180 }}
                      transition={{ duration: 0.2 }}
                    >
                      <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </motion.div>
                  </button>
                </div>
                <motion.div
                  initial={false}
                  animate={{ 
                    height: isSummaryCollapsed ? 0 : 'auto',
                    opacity: isSummaryCollapsed ? 0 : 1
                  }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Contract Name</h4>
                        <p className="text-base font-medium">{analysisResults.contract_name}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Execution Date</h4>
                        <p className="text-base">{analysisResults.execution_date}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Expiry Date</h4>
                        <p className="text-base">{analysisResults.expiry_date}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Governing Law</h4>
                        <p className="text-base">{analysisResults.governing_law}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Parties</h4>
                        <p className="text-base">{analysisResults.parties?.join(', ')}</p>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-500 mb-1">Contract Type</h4>
                        <p className="text-base">{analysisResults.contract_type}</p>
                      </div>
                    </div>
                    {analysisResults.summary && (
                      <div className="mt-6 pt-6 border-t border-gray-200">
                        <h4 className="text-sm font-medium text-gray-500 mb-2">Summary</h4>
                        <p className="text-sm text-gray-700">{analysisResults.summary}</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              </div>
            )}

            {/* Clauses Section */}
            {analysisResults && analysisResults.clauses && analysisResults.clauses.length > 0 && (
              <div className="mt-8">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-light">Contract Clauses</h2>
                  <button
                    onClick={() => setIsClausesCollapsed(!isClausesCollapsed)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <motion.div
                      animate={{ rotate: isClausesCollapsed ? 0 : 180 }}
                      transition={{ duration: 0.2 }}
                    >
                      <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </motion.div>
                  </button>
                </div>
                <motion.div
                  initial={false}
                  animate={{ 
                    height: isClausesCollapsed ? 0 : 'auto',
                    opacity: isClausesCollapsed ? 0 : 1
                  }}
                  transition={{ duration: 0.3 }}
                  className="overflow-hidden"
                >
                  <div className="bg-white rounded-xl shadow-sm border border-gray-100">
                    <div className="p-6">
                      {(() => {
                        // Group clauses by risk_category
                        const groupedClauses = analysisResults.clauses.reduce((acc, clause) => {
                          const category = clause.risk_category || 'Uncategorized';
                          if (!acc[category]) {
                            acc[category] = [];
                          }
                          acc[category].push(clause);
                          return acc;
                        }, {} as Record<string, Clause[]>);

                        return Object.entries(groupedClauses).map(([category, clauses], categoryIndex) => {
                          const isCategoryCollapsed = collapsedCategories.has(category);
                          
                          return (
                            <div key={category} className="mb-8 last:mb-0">
                              <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center">
                                  <h3 className="text-lg font-semibold text-gray-900">{category}</h3>
                                  <span className="ml-3 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                                    {clauses.length} clause{clauses.length !== 1 ? 's' : ''}
                                  </span>
                                </div>
                                <button
                                  onClick={() => toggleCategory(category)}
                                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                  <motion.div
                                    animate={{ rotate: isCategoryCollapsed ? 0 : 180 }}
                                    transition={{ duration: 0.2 }}
                                  >
                                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                  </motion.div>
                                </button>
                              </div>
                              <motion.div
                                initial={false}
                                animate={{ 
                                  height: isCategoryCollapsed ? 0 : 'auto',
                                  opacity: isCategoryCollapsed ? 0 : 1
                                }}
                                transition={{ duration: 0.3 }}
                                className="overflow-hidden"
                              >
                                <div className="space-y-4">
                                  {clauses.map((clause, index) => (
                                    <motion.div
                                      key={index}
                                      initial={{ opacity: 0, x: -20 }}
                                      animate={{ opacity: 1, x: 0 }}
                                      transition={{ duration: 0.3, delay: (categoryIndex * 0.1) + (index * 0.05) }}
                                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                                    >
                                      <div className="flex items-start justify-between mb-3">
                                        <div className="flex-1">
                                          <h4 className="text-base font-medium text-gray-900 mb-1">
                                            {clause.clause_type}
                                          </h4>
                                          <div className="flex items-center space-x-3">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                              clause.risk_tag === 'High' ? 'bg-red-100 text-red-800' :
                                              clause.risk_tag === 'Medium' ? 'bg-orange-100 text-orange-800' :
                                              'bg-green-100 text-green-800'
                                            }`}>
                                              {clause.risk_tag} Risk
                                            </span>
                                            <span className="text-sm text-gray-500">
                                              Risk Score: {clause.risk_score}
                                            </span>
                                          </div>
                                        </div>
                                        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                                          clause.risk_score >= 70 ? 'bg-red-100' :
                                          clause.risk_score >= 40 ? 'bg-orange-100' :
                                          'bg-green-100'
                                        }`}>
                                          <span className={`text-lg font-bold ${
                                            clause.risk_score >= 70 ? 'text-red-600' :
                                            clause.risk_score >= 40 ? 'text-orange-600' :
                                            'text-green-600'
                                          }`}>
                                            {clause.risk_score}
                                          </span>
                                        </div>
                                      </div>
                                      <div className="mb-3">
                                        <h5 className="text-sm font-medium text-gray-700 mb-1">Content</h5>
                                        <p className="text-sm text-gray-600">{clause.content}</p>
                                      </div>
                                      {clause.recommendation && (
                                        <div>
                                          <h5 className="text-sm font-medium text-gray-700 mb-1">Recommendation</h5>
                                          <p className="text-sm text-blue-600">{clause.recommendation}</p>
                                        </div>
                                      )}
                                    </motion.div>
                                  ))}
                                </div>
                              </motion.div>
                            </div>
                          );
                        });
                      })()}
                    </div>
                  </div>
                </motion.div>
              </div>
            )}

            {/* Recent Activity Section */}
            <div className="mt-8">
              <h2 className="text-xl font-light mb-4">Recent Activity</h2>
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Contract #1234 reviewed</p>
                      <p className="text-xs text-gray-500">2 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">High-risk contract flagged</p>
                      <p className="text-xs text-gray-500">4 hours ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Compliance check completed</p>
                      <p className="text-xs text-gray-500">6 hours ago</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Section - Right */}
        <div className="w-[500px] bg-white border-l border-gray-200 flex flex-col">
          {/* Chat Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="font-medium">AI Assistant</h3>
                <p className="text-xs text-gray-500">Always here to help</p>
              </div>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.type === 'user'
                      ? 'bg-[#1A1A1A] text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.type === 'bot' && (
                      <Bot className="w-4 h-4 mt-0.5 text-gray-600" />
                    )}
                    <div>
                      <p className="text-sm whitespace-pre-wrap">{message.message}</p>
                      <p className={`text-xs mt-1 ${
                        message.type === 'user' ? 'text-gray-300' : 'text-gray-500'
                      }`}>
                        {message.timestamp}
                      </p>
                    </div>
                    {message.type === 'user' && (
                      <User className="w-4 h-4 mt-0.5 text-gray-300" />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Chat Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                placeholder={isChatStreaming ? "AI is responding..." : "Ask about contracts, compliance, or analysis..."}
                disabled={isChatStreaming}
                className="flex-1 px-4 py-3 bg-gray-100 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <button
                onClick={handleSendMessage}
                disabled={isChatStreaming || !inputMessage.trim()}
                className="px-4 py-3 bg-[#1A1A1A] text-white rounded-xl hover:bg-[#2A2A2A] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isChatStreaming ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
            {analysisResults && (
              <div className="mt-2 text-xs text-gray-500">
                💡 I can help you analyze uploaded contract. Ask me about risks, clauses, or recommendations.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
    </ErrorBoundary>
  );
}
