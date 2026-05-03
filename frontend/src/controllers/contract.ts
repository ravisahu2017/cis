import { backendApi } from '@/utils/api';
import { Contract } from '@/models/models';

export default class ContractController {
    static async fetch(userId: string = 'default', limit: number = 50, offset: number = 0): Promise<Contract[]> {
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
}
