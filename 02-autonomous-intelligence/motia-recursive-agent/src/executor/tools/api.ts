import { Tool, ToolInfo } from './registry.js';
import { RunContext } from '../../core/runContext.js';

/**
 * API Tool - handles HTTP API calls
 */
export class ApiTool implements Tool {
  private readonly context: RunContext;

  constructor(context: RunContext) {
    this.context = context;
  }

  async execute(operation: string, params: Record<string, any>): Promise<any> {
    if (operation !== 'call_api') {
      throw new Error(`Unknown API operation: ${operation}`);
    }

    return this.callApi(params);
  }

  async validate(operation: string, params: Record<string, any>): Promise<void> {
    if (!params.url) {
      throw new Error('Missing required parameter: url');
    }

    if (!params.method) {
      throw new Error('Missing required parameter: method');
    }

    // Validate URL
    try {
      new URL(params.url);
    } catch {
      throw new Error(`Invalid URL: ${params.url}`);
    }

    // Validate method
    const validMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'];
    if (!validMethods.includes(params.method.toUpperCase())) {
      throw new Error(`Invalid HTTP method: ${params.method}`);
    }

    // Safety checks
    if (this.context.config.safeMode) {
      await this.validateApiSafety(params);
    }
  }

  getInfo(): ToolInfo {
    return {
      name: 'API',
      description: 'HTTP API calls',
      operations: ['call_api'],
      requiredParams: {
        'call_api': ['url', 'method']
      },
      optionalParams: {
        'call_api': ['headers', 'body', 'timeout', 'auth']
      }
    };
  }

  /**
   * Make HTTP API call
   */
  private async callApi(params: Record<string, any>): Promise<any> {
    const {
      url,
      method,
      headers = {},
      body,
      timeout = 30000,
      auth
    } = params;

    const startTime = Date.now();
    
    this.context.log('debug', `Making API call: ${method} ${url}`);

    try {
      // Prepare headers
      const requestHeaders = {
        'Content-Type': 'application/json',
        'User-Agent': 'Motia-Agent/1.0',
        ...headers
      };

      // Add authentication if provided
      if (auth) {
        if (auth.type === 'bearer') {
          requestHeaders['Authorization'] = `Bearer ${auth.token}`;
        } else if (auth.type === 'basic') {
          const credentials = Buffer.from(`${auth.username}:${auth.password}`).toString('base64');
          requestHeaders['Authorization'] = `Basic ${credentials}`;
        }
      }

      // Prepare request options
      const requestOptions: RequestInit = {
        method: method.toUpperCase(),
        headers: requestHeaders,
        signal: AbortSignal.timeout(timeout)
      };

      // Add body for non-GET requests
      if (body && method.toUpperCase() !== 'GET') {
        requestOptions.body = typeof body === 'string' ? body : JSON.stringify(body);
      }

      // Make the request
      const response = await fetch(url, requestOptions);
      const duration = Date.now() - startTime;

      // Parse response
      let responseData;
      const contentType = response.headers.get('content-type') || '';
      
      if (contentType.includes('application/json')) {
        responseData = await response.json();
      } else if (contentType.includes('text/')) {
        responseData = await response.text();
      } else {
        responseData = await response.arrayBuffer();
      }

      const result = {
        url,
        method: method.toUpperCase(),
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        data: responseData,
        duration,
        success: response.ok
      };

      this.context.log('debug', `API call completed`, {
        url,
        status: response.status,
        duration
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }

      return result;

    } catch (error) {
      const duration = Date.now() - startTime;
      
      this.context.log('error', `API call failed: ${url}`, {
        error: error.message,
        duration
      });

      if (error.name === 'AbortError') {
        throw new Error(`API call timeout after ${timeout}ms: ${url}`);
      }

      throw new Error(`API call failed: ${error.message}`);
    }
  }

  /**
   * Validate API call safety
   */
  private async validateApiSafety(params: Record<string, any>): Promise<void> {
    const { url, method } = params;
    const parsedUrl = new URL(url);

    // Block localhost/internal network calls in safe mode
    const hostname = parsedUrl.hostname.toLowerCase();
    const dangerousHosts = [
      'localhost',
      '127.0.0.1',
      '0.0.0.0',
      '::1'
    ];

    if (dangerousHosts.includes(hostname)) {
      throw new Error(`API calls to localhost/internal networks are blocked in safe mode: ${hostname}`);
    }

    // Block private IP ranges
    if (this.isPrivateIP(hostname)) {
      throw new Error(`API calls to private IP addresses are blocked in safe mode: ${hostname}`);
    }

    // Block non-HTTPS in production
    if (parsedUrl.protocol !== 'https:' && !hostname.includes('localhost')) {
      this.context.log('warn', `Non-HTTPS API call detected: ${url}`);
    }

    // Warn about destructive methods
    const destructiveMethods = ['DELETE', 'PUT', 'PATCH'];
    if (destructiveMethods.includes(method.toUpperCase())) {
      this.context.log('warn', `Potentially destructive API method: ${method}`, { url });
    }
  }

  /**
   * Check if hostname is a private IP address
   */
  private isPrivateIP(hostname: string): boolean {
    // Simple check for common private IP ranges
    const privateRanges = [
      /^10\./,
      /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
      /^192\.168\./,
      /^169\.254\./  // Link-local
    ];

    return privateRanges.some(range => range.test(hostname));
  }

  /**
   * Get common API endpoints for testing
   */
  public getTestEndpoints(): Record<string, string> {
    return {
      'httpbin-get': 'https://httpbin.org/get',
      'httpbin-post': 'https://httpbin.org/post',
      'jsonplaceholder': 'https://jsonplaceholder.typicode.com/posts/1',
      'github-api': 'https://api.github.com/user'
    };
  }
}