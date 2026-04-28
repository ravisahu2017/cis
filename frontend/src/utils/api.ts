// Reusable API service methods for backend communication

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
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
   * Streaming request for real-time responses
   */
  async streamResponse<T = any>(
    endpoint: string, 
    formData: FormData,
    onProgress?: (data: any) => void,
    onChunk?: (chunk: string) => void,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      console.log(`Streaming request to: ${url}`);
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
      });

      clearTimeout(timeoutId);

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let result: any = null;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          
          // Call onChunk callback for each chunk received
          if (onChunk) {
            onChunk(chunk);
          }
          
          // Try to parse complete JSON objects from buffer
          const lines = buffer.split('\n');
          
          for (let i = 0; i < lines.length - 1; i++) {
            const line = lines[i].trim();
            if (line.startsWith('data: ')) {
              try {
                const jsonData = JSON.parse(line.slice(6));
                result = jsonData;
                
                // Call onProgress callback with parsed data
                if (onProgress) {
                  onProgress(jsonData);
                }
                
                console.log('Streaming data received:', jsonData);
              } catch (e) {
                console.warn('Failed to parse streaming data:', line);
              }
            } else if (line.startsWith('event: ')) {
              // Handle event stream messages
              try {
                const eventData = JSON.parse(line.slice(7));
                if (onProgress) {
                  onProgress(eventData);
                }
                console.log('Event stream data:', eventData);
              } catch (e) {
                console.warn('Failed to parse event stream data:', line);
              }
            }
          }
          
          // Keep the incomplete line for next iteration
          buffer = lines[lines.length - 1];
        }
      }

      // If no streaming, fall back to regular response
      if (!result) {
        const contentType = response.headers.get('content-type');
        
        if (contentType?.includes('application/json')) {
          result = await response.json();
        } else if (contentType?.includes('image/')) {
          const imageBuffer = await response.arrayBuffer();
          const base64Image = Buffer.from(imageBuffer).toString('base64');
          const mimeType = contentType.split(';')[0];
          result = { imageUrl: `data:${mimeType};base64,${base64Image}` };
        } else {
          const text = await response.text();
          try {
            result = JSON.parse(text);
          } catch {
            result = { success: false, error: 'Invalid response format', rawResponse: text };
          }
        }
      }

      return {
        success: true,
        data: result,
        ...result,
      };
    } catch (error) {
      console.error('Streaming request failed:', error);
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
export const backendApi = new ApiService('http://localhost:8001');

export default ApiService;
