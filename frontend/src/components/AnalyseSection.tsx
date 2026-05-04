
import { motion } from 'framer-motion';
import { useState, useEffect } from "react";
import { 
  Upload, X, File, Loader2, FileText, TrendingUp, CheckCircle, AlertCircle, Clock 
} from 'lucide-react';
import { backendApi } from '@/utils/api';
import contractController from '@/controllers/contract'
import UploadedFileSection from './UploadedFileSection';



export default function AnalyseSection({ onAnalysisComplete }: { 
    onAnalysisComplete: (analysis: any) => void 
}) {
    const [isDragging, setIsDragging] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isSummaryCollapsed, setIsSummaryCollapsed] = useState(false);
    const [isClausesCollapsed, setIsClausesCollapsed] = useState(true);
    const [collapsedCategories, setCollapsedCategories] = useState<Set<string>>(new Set());
    const [isChatStreaming, setIsChatStreaming] = useState(false);
    const [analysisResults, setAnalysisResults] = useState<AnalysisData | null>(null);

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
        file: file, // Store actual File object
        uploadStatus: 'pending',
        uploadProgress: 0
        }));

        setUploadedFiles(prev => [...prev, ...newFiles]);
    };

    const uploadFile = async (file: UploadedFile) => {
        // Update status to uploading
        setUploadedFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, uploadStatus: 'uploading', uploadProgress: 0 } : f
        ));

        try {
            // Simulate upload progress
            const progressInterval = setInterval(() => {
                setUploadedFiles(prev => prev.map(f => {
                    if (f.id === file.id && f.uploadStatus === 'uploading') {
                        const newProgress = Math.min((f.uploadProgress || 0) + 10, 90);
                        return { ...f, uploadProgress: newProgress };
                    }
                    return f;
                }));
            }, 200);

            // send file for analysis
            const response = await contractController.analyse(["legal"], file.file);

            clearInterval(progressInterval);

            if (response.success && response.data?.analysis_id) {
                // Update status to uploaded and start processing
                setUploadedFiles(prev => prev.map(f => 
                    f.id === file.id ? { 
                        ...f, 
                        uploadStatus: 'uploaded', 
                        uploadProgress: 100,
                        analysisId: response.data.analysis_id
                    } : f
                ));

                // Start polling for analysis status
                pollAnalysisStatus(file.id, response.data.analysis_id);
            } else {
                throw new Error(response.error || 'Upload failed');
            }
        } catch (error) {
            clearInterval(progressInterval);
            setUploadedFiles(prev => prev.map(f => 
                f.id === file.id ? { 
                    ...f, 
                    uploadStatus: 'failed',
                    errorMessage: error instanceof Error ? error.message : 'Upload failed'
                } : f
            ));
        }
    };

  



    const removeFile = (fileId: string) => {
        setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
    };

    const analyzeContracts = async () => {
        // This function is now handled automatically by uploadFile
        // Files are uploaded and analyzed as soon as they are added
        console.log('Files are automatically uploaded and analyzed upon selection');
    };

    const clearAllFiles = () => {
        setUploadedFiles([]);
        setAnalysisResults(null);
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

    const uploadedFile = (file: any) => {
        return <UploadedFileSection fileToUpload={file} onAnalysisComplete={(analysis) => {
            setAnalysisResults(analysis);
        }} />;
    }
 
    return (
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
                    <div key={file.id} className="flex items-center justify-between">
                        <div className="flex-1">
                            {uploadedFile(file)}
                        </div>
                        {file.uploadStatus !== 'processing' && file.uploadStatus !== 'uploading' && (
                            <button
                                onClick={() => removeFile(file.id)}
                                className="p-1 hover:bg-gray-200 rounded transition-colors"
                            >
                                <X className="w-4 h-4 text-gray-500" />
                            </button>
                        )}
                    </div>
                  ))}
                </div>
                {uploadedFiles.length > 0 && (
                  <div className="mt-4 flex space-x-3">
                    <div className="flex-1 text-center">
                      <p className="text-xs text-gray-500">
                        Files are automatically uploaded and analyzed
                      </p>
                    </div>
                    <button
                      onClick={clearAllFiles}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm"
                    >
                      Clear All
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          <div>
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
          </div>
        </div>
    )
}