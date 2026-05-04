import { motion } from 'framer-motion';
import { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import contractController from '@/controllers/contract'
import { 
  Upload, X, File, Loader2, FileText, TrendingUp, CheckCircle, AlertCircle, Clock 
} from 'lucide-react';
import { UploadedFile } from '@/types/contract';

export interface UploadedFileSectionRef {
    analyzeFile: () => void;
}

export default forwardRef<UploadedFileSectionRef, { 
    onAnalysisComplete: (analysis: any) => void 
    fileToUpload: UploadedFile
}>(({ onAnalysisComplete, fileToUpload }, ref) => {
    const [file, setFile] = useState<UploadedFile>(fileToUpload);

    // Expose analyzeFile function to parent via ref
    useImperativeHandle(ref, () => ({
        analyzeFile: () => analyzeFile(file)
    }));

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const getStatusIcon = (file: UploadedFile) => {
        if(!file) {
            return <File className="w-4 h-4 text-blue-600" />;
        }
        switch (file.uploadStatus) {
            case 'pending':
                return <Clock className="w-4 h-4 text-gray-400" />;
            case 'uploading':
                return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
            case 'uploaded':
                return <CheckCircle className="w-4 h-4 text-blue-500" />;
            case 'processing':
                return <Loader2 className="w-4 h-4 text-orange-500 animate-spin" />;
            case 'completed':
                return <CheckCircle className="w-4 h-4 text-green-500" />;
            case 'failed':
                return <AlertCircle className="w-4 h-4 text-red-500" />;
            default:
                return <File className="w-4 h-4 text-blue-600" />;
        }
    };

    const getStatusColor = (file: UploadedFile) => {
        if(!file) {
            return 'bg-blue-100';
        }
        switch (file.uploadStatus) {
            case 'pending':
                return 'bg-gray-100';
            case 'uploading':
                return 'bg-blue-100';
            case 'uploaded':
                return 'bg-blue-100';
            case 'processing':
                return 'bg-orange-100';
            case 'completed':
                return 'bg-green-100';
            case 'failed':
                return 'bg-red-100';
            default:
                return 'bg-blue-100';
        }
    };

    const getStatusText = (file: UploadedFile) => {
        if(!file) {
            return 'Ready';
        }


        switch (file.uploadStatus) {
            case 'pending':
                return 'Ready to analyze';
            case 'uploading':
                return `Sending to server... ${file.uploadProgress || 0}%`;
            case 'uploaded':
                return 'File sent, starting analysis...';
            case 'processing':
                return 'Analyzing contract...';
            case 'completed':
                return 'Analysis complete';
            case 'failed':
                return file.errorMessage || 'Upload failed';
            default:
                return 'Ready';
        }
    };

    const pollAnalysisStatus = async (fileId: string, analysisId: string) => {
        const maxAttempts = 75; // Poll for up to 50 seconds (every 5 seconds)
        let attempts = 0;

        const poll = async () => {
            try {
                const status = await contractController.fetchAnalysisStatus('default', analysisId);
                
                if (status && status.status) {
                    if (status.status === 'queued') {
                        setFile(prevFile => ({...prevFile, uploadStatus: 'queued', processingProgress: (prevFile.processingProgress || 0) + 1}));
                        attempts++;
                        if (attempts < maxAttempts) {
                            setTimeout(poll, 10000); // Poll every 5 seconds
                        }
                    } else if (status.status === 'processing') {
                        setFile(prevFile => ({...prevFile, uploadStatus: 'processing', processingProgress: (prevFile.processingProgress || 0) + 2}));
                        attempts++;
                        if (attempts < maxAttempts) {
                            setTimeout(poll, 4000); // Poll every 5 seconds
                        }
                    } else if (status.status === 'completed') {
                        setFile(prevFile => ({...prevFile, uploadStatus: 'completed', processingProgress: 100}));
                        // Notify parent component
                        if (status.analysis) {
                            onAnalysisComplete(status.analysis);
                        }
                    } else if (status.status === 'failed') {
                        setFile(prevFile => ({...prevFile, uploadStatus: 'failed', errorMessage: status.error || 'Analysis failed', processingProgress: 0}));
                    }
                } else {
                    // Status not available yet, continue polling
                    attempts++;
                    if (attempts < maxAttempts) {
                        setTimeout(poll, 5000);
                    }
                }
            } catch (error) {
                console.error('Error polling status:', error);
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(poll, 5000);
                }
            }
        };

        // Start polling after a short delay
        setTimeout(poll, 2000);
    };

    const analyzeFile = async (file: UploadedFile) => {
        // Update status to uploading
        setFile({ ...file, uploadStatus: 'uploading', uploadProgress: 0 });
        // Simulate border animation progress
        const progressInterval = setInterval(() => {
            setFile(prev => {
                if (prev.uploadStatus === 'uploading') {
                    const newProgress = Math.min((prev.uploadProgress || 0) + 10, 90);
                    return { ...prev, uploadProgress: newProgress, processingProgress: newProgress };
                }
                return prev;
            });
        }, 200);
        try {
            const response = await contractController.analyse(["legal"], file.file);

            clearInterval(progressInterval);

            if (response.success && response.data?.analysis_id) {
                setFile({ ...file, uploadStatus: 'uploaded', uploadProgress: 100, analysisId: response.data.analysis_id });
                // Start polling for analysis status
                pollAnalysisStatus(file.id, response.data.analysis_id);
            } else {
                throw new Error(response.error || 'Upload failed');
            }
        } catch (error) {
            clearInterval(progressInterval);
            setFile({ ...file, uploadStatus: 'failed', uploadProgress: 0, errorMessage: error instanceof Error ? error.message : 'Upload failed' });
        }
    };

    const progressBorder = () => {
        return (<>
            <motion.div
                className="absolute top-0 left-0 h-0.5 bg-blue-500"
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ duration: 0.5, delay: 0 }}
            />
            <motion.div
                className="absolute top-0 right-0 w-0.5 h-full bg-blue-500"
                initial={{ height: 0 }}
                animate={{ height: "100%" }}
                transition={{ duration: 0.5, delay: 0.5 }}
            />
            <motion.div
                className="absolute bottom-0 right-0 h-0.5 bg-blue-500"
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ duration: 0.5, delay: 1 }}
            />
            <motion.div
                className="absolute bottom-0 left-0 w-0.5 h-full bg-blue-500"
                initial={{ height: 0 }}
                animate={{ height: "100%" }}
                transition={{ duration: 0.5, delay: 1.5 }}
            />
        </>)
    }

    const fileUploadProgressBar = () => {
        
        return (<>
            <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-700">
                    {getStatusText()}
                </span>
                {file.processingProgress !== undefined && file.processingProgress > 0 && (
                    <span className="text-xs text-gray-500">
                        {file.processingProgress}%
                    </span>
                )}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5" title={`${file.processingProgress || 0}%`}>
                <div 
                    className="h-1.5 rounded-full transition-all duration-300 bg-blue-500"
                    style={{ width: `${file.processingProgress || 0}%` }}
                ></div>
            </div>
        </>)
    }



    const uploadedFile = (file) => {
        if(!file) return null;
        return (
            <motion.div
                key={file.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`relative border rounded-lg p-3 overflow-hidden ${
                    file.uploadStatus === 'failed' ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-gray-50'
                }`}
            >
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${getStatusColor()}`}>
                            {getStatusIcon()}
                        </div>
                        <div className="flex-1">
                            <p className="text-sm font-medium text-gray-900">{file.name}</p>
                            <p className="text-xs text-gray-500">
                                {formatFileSize(file.size)} • {file.uploadedAt}
                            </p>
                        </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex items-center space-x-2">
                        {file.uploadStatus === 'pending' && (
                            <button
                                onClick={() => analyzeFile(file)}
                                className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors flex items-center"
                            >
                                <Upload className="w-3 h-3 mr-1" />
                                Analyze
                            </button>
                        )}
                    </div>
                </div>
                
                {fileUploadProgressBar()}
                
                {/* Status and Progress */}
                <div className="mt-2">
                    {/* Error Message */}
                    {file.uploadStatus === 'failed' && file.errorMessage && (
                        <p className="text-xs text-red-600 mt-1">
                            {file.errorMessage}
                        </p>
                    )}
                </div>
            </motion.div>
        );
    }


    const uploadFileV2 = (file) => {
        if(!file) return null;
        return (
            <div className="w-full bg-gray-50 rounded-lg overflow-hidden relative" title={`${file.processingProgress || 0}%`}>
                {/* Progress Background */}
                <div 
                    className="absolute inset-0 bg-blue-100 transition-all duration-3000"
                    style={{ width: `${file.processingProgress || 0}%` }}
                />
                
                {/* Content */}
                <div className="relative z-10 p-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${getStatusColor()}`}>
                                {getStatusIcon()}
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900">{file.name}</p>
                                <p className="text-xs text-gray-500">
                                    {formatFileSize(file.size)} • {file.uploadedAt}
                                </p>
                            </div>
                        </div>
                    
                        {/* Action Buttons */}
                        <div className="flex items-center space-x-2">
                            {file.uploadStatus === 'pending' && (
                                <button
                                    onClick={() => analyzeFile(file)}
                                    className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 transition-colors flex items-center"
                                >
                                    <Upload className="w-3 h-3 mr-1" />
                                    Analyze
                                </button>
                            )}
                        </div>

                        {file.uploadStatus != "pending" && (
                            <div className="text-xs text-gray-500 capitalize">
                                {file.uploadStatus}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    return (
        uploadFileV2(file)
    );
});