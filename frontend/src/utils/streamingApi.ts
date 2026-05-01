// Streaming API utilities for real-time responses

export interface StreamProgress {
  status: 'status' | 'message' | 'error' | 'data';
  message: string;
  error: string | null;
  data: any;
  helpers: string[];
  timestamp: Date;
  typeofData: string;
}

export interface StreamCallback {
  (progressData: StreamProgress): void;
}

export class StreamingApi {
  private baseUrl: string;
  private defaultTimeout: number = 100000;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }



  /**
   * Chat with contract analysis using streaming responses
   */
  async chatWithContract(
    message: string,
    context: any = null,
    onProgress: StreamCallback
  ): Promise<void> {
    const requestData = {
      message,
      context,
      session_id: null,
      user_id: null
    };

    await this.streamJsonResponse('/chat', requestData, onProgress);
  }

  /**
   * Generic streaming response handler for JSON requests
   */
  private async streamJsonResponse(
    endpoint: string, 
    requestData: any, 
    onProgress: StreamCallback
  ): Promise<void> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      console.log(`Streaming JSON request to: ${url}`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.defaultTimeout);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
        signal: controller.signal,
        mode: 'cors',
        credentials: 'omit',
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.trim()) {
              try {
                // Handle different streaming formats
                let progressData: StreamProgress;

                if (line.startsWith('data: ')) {
                  // Server-Sent Events format
                  const jsonStr = line.substring(6);
                  progressData = JSON.parse(jsonStr);
                } else if (line.startsWith('{') && line.endsWith('}')) {
                  // Direct JSON format
                  progressData = JSON.parse(line);
                } else {
                  // Plain text message
                  progressData = {
                    status: 'message' as const,
                    message: line,
                    error: null,
                    data: null,
                    helpers: [],
                    timestamp: new Date(),
                    typeofData: 'string'
                  };
                }

                // Ensure all required properties are present
                if (!progressData.helpers) progressData.helpers = [];
                if (!progressData.timestamp) progressData.timestamp = new Date();
                if (!progressData.typeofData) progressData.typeofData = typeof progressData.data;

                // Call progress callback
                onProgress(progressData);

              } catch (parseError) {
                console.warn('Failed to parse streaming data:', line, parseError);
                
                // Send as plain message if parsing fails
                onProgress({
                  status: 'message' as const,
                  message: line,
                  error: null,
                  data: null,
                  helpers: [],
                  timestamp: new Date(),
                  typeofData: 'string'
                });
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

    } catch (error) {
      console.error('Streaming JSON request failed:', error);
      throw error;
    }
  }

  /**
   * Create a context message for chat
   */
  createContextMessage(message: string, data: any = null): StreamProgress {
    return {
      status: 'message',
      message,
      helpers: [],
      data,
      error: null,
      timestamp: new Date(),
      typeofData: typeof data
    };
  }

  /**
   * Create an error message for chat
   */
  createErrorMessage(error: Error | string): StreamProgress {
    const errorMessage = error instanceof Error ? error.message : error;
    
    return {
      status: 'error',
      message: `Error: ${errorMessage}`,
      helpers: [],
      data: null,
      error: errorMessage,
      timestamp: new Date(),
      typeofData: 'string'
    };
  }
}

// Export singleton instance
export const streamingApi = new StreamingApi(process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001');
