/**
 * REST API Gateway - Exposes RESTful endpoints for external system integration
 * Part of MOIE-OS Sovereign Upgrade - Phase 4.2
 */

import { EventEmitter } from 'events';
import * as http from 'http';
import * as url from 'url';
import { expertRegistry } from '../core/expert-registry';
import { gatingEngine } from '../core/gating-engine';
import { expertCoordinator } from '../core/expert-coordinator';

/**
 * API Configuration
 */
interface APIConfig {
  port: number;
  host: string;
  enableAuth: boolean;
  enableRateLimit: boolean;
  enableCORS: boolean;
  maxRequestSize: number; // bytes
  requestTimeout: number; // milliseconds
  rateLimit: {
    windowMs: number;
    maxRequests: number;
  };
}

/**
 * API Request
 */
interface APIRequest {
  method: string;
  path: string;
  query: Record<string, string>;
  headers: Record<string, string>;
  body?: any;
  ip: string;
  timestamp: Date;
}

/**
 * API Response
 */
interface APIResponse {
  statusCode: number;
  headers: Record<string, string>;
  body: any;
}

/**
 * Rate limit entry
 */
interface RateLimitEntry {
  count: number;
  resetTime: number;
}

/**
 * Authentication token
 */
interface AuthToken {
  token: string;
  userId: string;
  permissions: string[];
  expiresAt: Date;
}

/**
 * REST API Gateway
 * Provides RESTful endpoints for external system integration
 */
export class APIGateway extends EventEmitter {
  private config: APIConfig;
  private server?: http.Server;
  private running: boolean = false;
  private rateLimitMap: Map<string, RateLimitEntry>;
  private authTokens: Map<string, AuthToken>;

  constructor(config?: Partial<APIConfig>) {
    super();
    this.config = {
      port: 3000,
      host: '0.0.0.0',
      enableAuth: true,
      enableRateLimit: true,
      enableCORS: true,
      maxRequestSize: 10 * 1024 * 1024, // 10MB
      requestTimeout: 30000, // 30 seconds
      rateLimit: {
        windowMs: 60000, // 1 minute
        maxRequests: 100,
      },
      ...config,
    };

    this.rateLimitMap = new Map();
    this.authTokens = new Map();

    console.log('✅ API Gateway initialized');
  }

  /**
   * Start the API server
   */
  public start(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.running) {
        console.log('⚠️  API Gateway already running');
        resolve();
        return;
      }

      this.server = http.createServer(this.handleRequest.bind(this));

      this.server.listen(this.config.port, this.config.host, () => {
        this.running = true;
        console.log(`🚀 API Gateway listening on http://${this.config.host}:${this.config.port}`);
        this.emit('started');
        resolve();
      });

      this.server.on('error', (error) => {
        console.error('❌ API Gateway error:', error);
        this.emit('error', error);
        reject(error);
      });
    });
  }

  /**
   * Stop the API server
   */
  public stop(): Promise<void> {
    return new Promise((resolve) => {
      if (!this.running || !this.server) {
        resolve();
        return;
      }

      this.server.close(() => {
        this.running = false;
        console.log('🛑 API Gateway stopped');
        this.emit('stopped');
        resolve();
      });
    });
  }

  /**
   * Handle incoming HTTP request
   */
  private async handleRequest(
    req: http.IncomingMessage,
    res: http.ServerResponse
  ): Promise<void> {
    const startTime = Date.now();

    try {
      // Parse request
      const apiRequest = await this.parseRequest(req);
      this.emit('request:received', apiRequest);

      // CORS headers
      if (this.config.enableCORS) {
        this.setCORSHeaders(res);
        
        // Handle preflight
        if (req.method === 'OPTIONS') {
          res.writeHead(200);
          res.end();
          return;
        }
      }

      // Rate limiting
      if (this.config.enableRateLimit) {
        const rateLimitResult = this.checkRateLimit(apiRequest.ip);
        if (!rateLimitResult.allowed) {
          this.sendResponse(res, {
            statusCode: 429,
            headers: { 'Content-Type': 'application/json' },
            body: {
              error: 'Too many requests',
              retryAfter: rateLimitResult.retryAfter,
            },
          });
          return;
        }
      }

      // Authentication
      if (this.config.enableAuth) {
        const authResult = this.authenticate(apiRequest);
        if (!authResult.authenticated) {
          this.sendResponse(res, {
            statusCode: 401,
            headers: { 'Content-Type': 'application/json' },
            body: { error: 'Unauthorized', message: authResult.message },
          });
          return;
        }
      }

      // Route request
      const response = await this.routeRequest(apiRequest);
      this.sendResponse(res, response);

      const duration = Date.now() - startTime;
      this.emit('request:completed', { request: apiRequest, response, duration });
    } catch (error) {
      console.error('❌ Request handling error:', error);
      this.sendResponse(res, {
        statusCode: 500,
        headers: { 'Content-Type': 'application/json' },
        body: { error: 'Internal server error', message: (error as Error).message },
      });
    }
  }

  /**
   * Parse incoming request
   */
  private async parseRequest(req: http.IncomingMessage): Promise<APIRequest> {
    const parsedUrl = url.parse(req.url || '', true);
    
    // Parse body
    let body: any = undefined;
    if (req.method === 'POST' || req.method === 'PUT' || req.method === 'PATCH') {
      body = await this.parseBody(req);
    }

    return {
      method: req.method || 'GET',
      path: parsedUrl.pathname || '/',
      query: parsedUrl.query as Record<string, string>,
      headers: req.headers as Record<string, string>,
      body,
      ip: req.socket.remoteAddress || 'unknown',
      timestamp: new Date(),
    };
  }

  /**
   * Parse request body
   */
  private parseBody(req: http.IncomingMessage): Promise<any> {
    return new Promise((resolve, reject) => {
      let data = '';
      let size = 0;

      req.on('data', (chunk) => {
        size += chunk.length;
        
        if (size > this.config.maxRequestSize) {
          reject(new Error('Request body too large'));
          return;
        }
        
        data += chunk;
      });

      req.on('end', () => {
        try {
          const contentType = req.headers['content-type'] || '';
          
          if (contentType.includes('application/json')) {
            resolve(JSON.parse(data));
          } else {
            resolve(data);
          }
        } catch (error) {
          reject(error);
        }
      });

      req.on('error', reject);
    });
  }

  /**
   * Route request to appropriate handler
   */
  private async routeRequest(request: APIRequest): Promise<APIResponse> {
    const { method, path } = request;

    // Health check endpoint
    if (path === '/health' && method === 'GET') {
      return this.handleHealth(request);
    }

    // Expert endpoints
    if (path.startsWith('/api/experts')) {
      return this.handleExpertEndpoints(request);
    }

    // Task routing endpoints
    if (path.startsWith('/api/tasks')) {
      return this.handleTaskEndpoints(request);
    }

    // Coordination endpoints
    if (path.startsWith('/api/coordination')) {
      return this.handleCoordinationEndpoints(request);
    }

    // System endpoints
    if (path.startsWith('/api/system')) {
      return this.handleSystemEndpoints(request);
    }

    // Not found
    return {
      statusCode: 404,
      headers: { 'Content-Type': 'application/json' },
      body: { error: 'Not found', path },
    };
  }

  /**
   * Handle health check
   */
  private async handleHealth(request: APIRequest): Promise<APIResponse> {
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
      },
    };
  }

  /**
   * Handle expert endpoints
   */
  private async handleExpertEndpoints(request: APIRequest): Promise<APIResponse> {
    const { method, path, body } = request;

    // GET /api/experts - List all experts
    if (path === '/api/experts' && method === 'GET') {
      const experts = expertRegistry.listExperts();
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: { experts, count: experts.length },
      };
    }

    // GET /api/experts/:id - Get specific expert
    if (path.match(/^\/api\/experts\/[^/]+$/) && method === 'GET') {
      const expertId = path.split('/').pop()!;
      const expert = expertRegistry.getExpert(expertId);
      
      if (!expert) {
        return {
          statusCode: 404,
          headers: { 'Content-Type': 'application/json' },
          body: { error: 'Expert not found', expertId },
        };
      }

      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: { expert: expert.metadata },
      };
    }

    // GET /api/experts/stats - Get expert statistics
    if (path === '/api/experts/stats' && method === 'GET') {
      const stats = expertRegistry.getStats();
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: stats,
      };
    }

    return {
      statusCode: 404,
      headers: { 'Content-Type': 'application/json' },
      body: { error: 'Endpoint not found' },
    };
  }

  /**
   * Handle task endpoints
   */
  private async handleTaskEndpoints(request: APIRequest): Promise<APIResponse> {
    const { method, path, body } = request;

    // POST /api/tasks/route - Route a task
    if (path === '/api/tasks/route' && method === 'POST') {
      if (!body || !body.description) {
        return {
          statusCode: 400,
          headers: { 'Content-Type': 'application/json' },
          body: { error: 'Missing required field: description' },
        };
      }

      const task = {
        id: body.id || `task-${Date.now()}`,
        type: body.type || 'api-task',
        description: body.description,
        priority: body.priority || 'medium',
        domain: body.domain,
        requiredSkills: body.requiredSkills,
        metadata: body.metadata,
        createdAt: new Date(),
      };

      const decision = await gatingEngine.routeToExpert(task);

      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
          task,
          decision: {
            expert: decision.selectedExpert?.expert.metadata,
            matchScore: decision.selectedExpert?.matchScore,
            strategy: decision.routingStrategy,
            classification: decision.classification,
          },
        },
      };
    }

    // GET /api/tasks/stats - Get routing statistics
    if (path === '/api/tasks/stats' && method === 'GET') {
      const stats = gatingEngine.getStats();
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: stats,
      };
    }

    return {
      statusCode: 404,
      headers: { 'Content-Type': 'application/json' },
      body: { error: 'Endpoint not found' },
    };
  }

  /**
   * Handle coordination endpoints
   */
  private async handleCoordinationEndpoints(request: APIRequest): Promise<APIResponse> {
    const { method, path } = request;

    // GET /api/coordination/sessions - List sessions
    if (path === '/api/coordination/sessions' && method === 'GET') {
      const sessions = expertCoordinator.getAllSessions();
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: { sessions, count: sessions.length },
      };
    }

    // GET /api/coordination/stats - Get coordination statistics
    if (path === '/api/coordination/stats' && method === 'GET') {
      const stats = expertCoordinator.getStats();
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: stats,
      };
    }

    return {
      statusCode: 404,
      headers: { 'Content-Type': 'application/json' },
      body: { error: 'Endpoint not found' },
    };
  }

  /**
   * Handle system endpoints
   */
  private async handleSystemEndpoints(request: APIRequest): Promise<APIResponse> {
    const { method, path } = request;

    // GET /api/system/status - Get system status
    if (path === '/api/system/status' && method === 'GET') {
      return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
          status: 'running',
          version: '1.0.0',
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          experts: expertRegistry.getStats(),
          routing: gatingEngine.getStats(),
          coordination: expertCoordinator.getStats(),
        },
      };
    }

    return {
      statusCode: 404,
      headers: { 'Content-Type': 'application/json' },
      body: { error: 'Endpoint not found' },
    };
  }

  /**
   * Send HTTP response
   */
  private sendResponse(res: http.ServerResponse, response: APIResponse): void {
    res.writeHead(response.statusCode, response.headers);
    
    if (typeof response.body === 'object') {
      res.end(JSON.stringify(response.body));
    } else {
      res.end(response.body);
    }
  }

  /**
   * Set CORS headers
   */
  private setCORSHeaders(res: http.ServerResponse): void {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  }

  /**
   * Check rate limit
   */
  private checkRateLimit(ip: string): { allowed: boolean; retryAfter?: number } {
    const now = Date.now();
    const entry = this.rateLimitMap.get(ip);

    if (!entry || now > entry.resetTime) {
      // New window
      this.rateLimitMap.set(ip, {
        count: 1,
        resetTime: now + this.config.rateLimit.windowMs,
      });
      return { allowed: true };
    }

    if (entry.count >= this.config.rateLimit.maxRequests) {
      // Rate limit exceeded
      return {
        allowed: false,
        retryAfter: Math.ceil((entry.resetTime - now) / 1000),
      };
    }

    // Increment count
    entry.count++;
    return { allowed: true };
  }

  /**
   * Authenticate request
   */
  private authenticate(request: APIRequest): { authenticated: boolean; message?: string } {
    const authHeader = request.headers['authorization'];

    if (!authHeader) {
      return { authenticated: false, message: 'Missing authorization header' };
    }

    const token = authHeader.replace('Bearer ', '');
    const authToken = this.authTokens.get(token);

    if (!authToken) {
      return { authenticated: false, message: 'Invalid token' };
    }

    if (new Date() > authToken.expiresAt) {
      this.authTokens.delete(token);
      return { authenticated: false, message: 'Token expired' };
    }

    return { authenticated: true };
  }

  /**
   * Generate authentication token
   */
  public generateToken(userId: string, permissions: string[] = []): string {
    const token = `token-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours

    this.authTokens.set(token, {
      token,
      userId,
      permissions,
      expiresAt,
    });

    return token;
  }

  /**
   * Revoke authentication token
   */
  public revokeToken(token: string): void {
    this.authTokens.delete(token);
  }

  /**
   * Get API statistics
   */
  public getStats(): {
    running: boolean;
    port: number;
    activeConnections: number;
    rateLimitEntries: number;
    activeTokens: number;
  } {
    return {
      running: this.running,
      port: this.config.port,
      activeConnections: this.server?.listening ? 1 : 0,
      rateLimitEntries: this.rateLimitMap.size,
      activeTokens: this.authTokens.size,
    };
  }
}

// Export singleton instance
export const apiGateway = new APIGateway();

// Example usage:
// await apiGateway.start();
// const token = apiGateway.generateToken('user-123', ['read', 'write']);
// console.log('API Gateway running on port 3000');
