import { backendApi } from '@/utils/api';
import { Contract, RecentAnalysis, PaginatedResponse } from '@/models/models';

export default class ContractController {
    static async fetch(userId: string = 'default', limit: number = 5, offset: number = 0): Promise<Contract[]> {
        try {
            const params = new URLSearchParams({
                user_id: userId,
                limit: limit.toString(),
                offset: offset.toString()
            });
            const response = await backendApi.get(`/contract/contracts?${params.toString()}`, {});
            if (response.success && response.data) {
                return response.data.items || [];
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch contracts:', error);
            return [];
        }
    }

    static async fetchContract(userId: string = 'default', contract_id: string): Promise<Contract> {
        try {
            const response = await backendApi.get(`/contract/contracts/${contract_id}`);
            if (response.success && response.data) {
                return response.data;
            }
            return null;
        } catch (error) {
            console.error('Failed to fetch contracts:', error);
            return null;
        }
    }

    static async analyse(analysis_types: string[], file: File): Promise<any> {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('analysis_types', JSON.stringify(analysis_types));
            const response = await backendApi.postFormData('/contract/analyze', formData);
            return response;
        } catch (error) {
            console.error('Failed to analyse contract:', error);
            return null;
        }
    }

    static async fetchAnalysisStatus(userId: string = 'default', analysisId: string): Promise<any> {
        try {
            const response = await backendApi.get(`/contract/analysis/${analysisId}/status`);
            if (response.success && response.data) {
                return response.data;
            }
            return null;
        } catch (error) {
            console.error('Failed to fetch contracts:', error);
            return null;
        }
    }

    static async fetchRecentAnalysis(userId: string = 'default', hours: number = 12, limit: number = 2): Promise<RecentAnalysis[]> {
        try {
            const params = new URLSearchParams({
                user_id: userId,
                hours: hours.toString(),
                limit: limit.toString()
            });
            const response = await backendApi.get(`/contract/analyses/recent?${params.toString()}`, {});
            if (response.success && response.data) {
                return response.data.items || [];
            }
            return [];
        } catch (error) {
            console.error('Failed to fetch recent analyses:', error);
            return [];
        }
    }
}
