import { motion } from 'framer-motion';
import { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import contractController from '@/controllers/contract'
import { 
  Upload, X, File, Loader2, CheckCircle, AlertCircle, Clock 
} from 'lucide-react';
import { UploadedFile } from '@/types/contract';

export interface UploadedFileSectionRef {
    analyzeFile: () => void;
}

export default forwardRef<UploadedFileSectionRef, { 
    onAnalysisComplete: (analysis: any) => void 
    onStatusChange: (file: UploadedFile) => void
    fileToUpload: UploadedFile
}>(({ onAnalysisComplete, onStatusChange, fileToUpload }, ref) => {
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

    const getStatusIcon = () => {
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

    const getStatusColor = () => {
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

    const getStatusText = () => {
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
                        setFile(prevFile => {
                            const updatedFile = {...prevFile, uploadStatus: 'queued', processingProgress: (prevFile.processingProgress || 0) + 1};
                            onStatusChange(updatedFile); // Send updated file to parent
                            return updatedFile;
                        });
                        attempts++;
                        if (attempts < maxAttempts) {
                            setTimeout(poll, 10000); // Poll every 5 seconds
                        }
                    } else if (status.status === 'processing') {
                        setFile(prevFile => {
                            const updatedFile = {...prevFile, uploadStatus: 'processing', processingProgress: (prevFile.processingProgress || 0) + 2};
                            onStatusChange(updatedFile); // Send updated file to parent
                            return updatedFile;
                        });
                        
                        attempts++;
                        if (attempts < maxAttempts) {
                            setTimeout(poll, 4000); // Poll every 5 seconds
                        }
                    } else if (status.status === 'completed') {
                        setFile(prevFile => {
                            const updatedFile = {...prevFile, uploadStatus: 'completed', processingProgress: 100};
                            onStatusChange(updatedFile); // Send updated file to parent
                            // Notify parent component
                            if (status.analysis) {
                                onAnalysisComplete(status.analysis);
                            }
                            return updatedFile;
                        });
                    } else if (status.status === 'failed') {
                        setFile(prevFile => {
                            const updatedFile = {...prevFile, uploadStatus: 'failed', errorMessage: status.error || 'Analysis failed', processingProgress: 0};
                            onStatusChange(updatedFile); // Send updated file to parent
                            return updatedFile;
                        });
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

    const analyzeFile = async () => {
        // Update status to uploading
        setFile(prevFile => {
            const updatedFile = { ...prevFile, uploadStatus: 'uploading', uploadProgress: 0 };
            onStatusChange(updatedFile); // Send updated file to parent
            return updatedFile;
        });
        
        // Simulate border animation progress
        const progressInterval = setInterval(() => {
            setFile(prev => {
                if (prev.uploadStatus === 'uploading') {
                    const newProgress = Math.min((prev.uploadProgress || 0) + 10, 90);
                    const updatedFile = { ...prev, uploadProgress: newProgress, processingProgress: newProgress };
                    onStatusChange(updatedFile); // Send updated file to parent
                    return updatedFile;
                }
                return prev;
            });
        }, 200);
        try {
            const response = await contractController.analyse(["legal"], file.file);

            clearInterval(progressInterval);

            if (response.success && response.data?.analysis_id) {
                setFile(prevFile => {
                    const updatedFile = { ...prevFile, uploadStatus: 'uploaded', uploadProgress: 100, analysisId: response.data.analysis_id };
                    onStatusChange(updatedFile); // Send updated file to parent
                    return updatedFile;
                });
                // Start polling for analysis status
                pollAnalysisStatus(file.id, response.data.analysis_id);
            } else {
                throw new Error(response.error || 'Upload failed');
            }
        } catch (error) {
            clearInterval(progressInterval);
            setFile(prevFile => {
                const updatedFile = { ...prevFile, uploadStatus: 'failed', uploadProgress: 0, errorMessage: error instanceof Error ? error.message : 'Upload failed' };
                onStatusChange(updatedFile); // Send updated file to parent
                return updatedFile;
            });
        }
    };

    const uploadFile = () => {
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
                                    onClick={() => analyzeFile()}
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
        uploadFile()
    );
});