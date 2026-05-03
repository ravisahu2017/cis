// Reusable API service methods for backend communication

interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  timestamp: any;
  response_time_ms: number;
}

interface RequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
  retries?: number;
}

class ApiService {
  private baseUrl: string;
  private defaultTimeout: number = 100000;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  /**
   * Generic GET request
   */
  async get<T = any>(
    endpoint: string, 
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      console.log(`GET request to: ${url}`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), options.timeout || this.defaultTimeout);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
        mode: 'cors',
        credentials: 'omit',
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('GET response:', data);
      
      return {
        success: true,
        data,
        ...data,
      };
    } catch (error) {
      console.error('GET request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * Generic POST request with JSON data
   */
  async post<T = any>(
    endpoint: string, 
    data: any, 
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      console.log(`POST request to: ${url}`);
      console.log('POST data:', data);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), options.timeout || this.defaultTimeout);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        body: JSON.stringify(data),
        signal: controller.signal,
        mode: 'cors',
        credentials: 'omit',
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log('POST response:', result);
      
      return {
        success: true,
        data: result,
        ...result,
      };
    } catch (error) {
      console.error('POST request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * POST request with FormData (for file uploads)
   */
  async postFormData<T = any>(
    endpoint: string, 
    formData: FormData, 
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      console.log(`POST FormData request to: ${url}`);
      console.log('FormData contents:', {
        files: formData.getAll('files').length,
        ...Object.fromEntries(
          Array.from(formData.entries())
            .filter(([key]) => key !== 'files')
        )
      });

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), options.timeout || this.defaultTimeout);

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
        mode: 'cors',
        credentials: 'omit',
        // Don't set Content-Type header for FormData - browser sets it with boundary
      });

      clearTimeout(timeoutId);

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const contentType = response.headers.get('content-type');
      let result: any;

      if (contentType?.includes('application/json')) {
        result = await response.json();
        console.log('JSON response:', result);
      } else if (contentType?.includes('image/')) {
        const imageBuffer = await response.arrayBuffer();
        const base64Image = Buffer.from(imageBuffer).toString('base64');
        const mimeType = contentType.split(';')[0];
        const dataUrl = `data:${mimeType};base64,${base64Image}`;
        console.log('Image response received, size:', imageBuffer.byteLength);
        result = { imageUrl: dataUrl, success: true };
      } else {
        const text = await response.text();
        console.log('Text response:', text);
        try {
          result = JSON.parse(text);
        } catch {
          result = { success: false, error: 'Invalid response format', rawResponse: text };
        }
      }

      return {
        success: true,
        data: result,
        ...result,
      };
    } catch (error) {
      console.error('POST FormData request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * PUT request
   */
  async put<T = any>(
    endpoint: string, 
    data: any, 
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      console.log(`PUT request to: ${url}`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), options.timeout || this.defaultTimeout);

      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        body: JSON.stringify(data),
        signal: controller.signal,
        mode: 'cors',
        credentials: 'omit',
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log('PUT response:', result);
      
      return {
        success: true,
        data: result,
        ...result,
      };
    } catch (error) {
      console.error('PUT request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  /**
   * DELETE request
   */
  async delete<T = any>(
    endpoint: string, 
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      console.log(`DELETE request to: ${url}`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), options.timeout || this.defaultTimeout);

      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
        mode: 'cors',
        credentials: 'omit',
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log('DELETE response:', result);
      
      return {
        success: true,
        data: result,
        ...result,
      };
    } catch (error) {
      console.error('DELETE request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }
}


// For specific backend servers
const backendUrl = 'http://localhost:8001';
export const backendApi = new ApiService(backendUrl);


export default ApiService;
