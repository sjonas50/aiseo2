import axios from 'axios';
import { io, Socket } from 'socket.io-client';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5555';

// Create axios instance
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Provider {
  id: string;
  name: string;
  enabled: boolean;
  model: string | null;
}

export interface QueryResult {
  provider: string;
  response?: string;
  model?: string;
  success: boolean;
  error?: string;
}

export interface QueryResponse {
  id: string;
  query: string;
  timestamp: string;
  status: 'processing' | 'completed' | 'error';
  results: Record<string, QueryResult>;
  analysis: Record<string, any> | null;
}

export interface AnalysisData {
  companies_mentioned: string[];
  mention_reasons: string[];
  authority_signals: string[];
  key_features: string[];
  sources_cited: string[];
  ranking_factors: string[];
  sentiment: string;
  optimization_insights: string[];
}

// API Functions
export const apiService = {
  // Get configured providers
  async getProviders(): Promise<{ providers: Provider[]; analysis_enabled: boolean }> {
    const response = await api.get('/providers');
    return response.data;
  },

  // Submit a query
  async submitQuery(query: string, providers?: string[]): Promise<{ query_id: string; websocket_room: string }> {
    const response = await api.post('/query', { query, providers });
    return response.data;
  },

  // Get query results
  async getResults(queryId: string): Promise<QueryResponse> {
    const response = await api.get(`/results/${queryId}`);
    return response.data;
  },

  // Get analysis
  async getAnalysis(queryId: string): Promise<{ query_id: string; query: string; analysis: Record<string, AnalysisData> }> {
    const response = await api.get(`/analysis/${queryId}`);
    return response.data;
  },

  // Get history
  async getHistory(): Promise<{ queries: QueryResponse[] }> {
    const response = await api.get('/history');
    return response.data;
  },

  // Export results
  async exportResults(queryId: string, format: 'json' | 'csv' = 'json'): Promise<Blob> {
    const response = await api.get(`/export/${queryId}`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },
};

// WebSocket Manager
export class WebSocketManager {
  private socket: Socket | null = null;
  private listeners: Map<string, Set<Function>> = new Map();

  connect(): Socket {
    if (!this.socket) {
      this.socket = io(API_BASE_URL, {
        transports: ['websocket', 'polling'],
      });

      this.socket.on('connect', () => {
        console.log('WebSocket connected');
      });

      this.socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
      });
    }
    return this.socket;
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  joinQuery(queryId: string): void {
    if (this.socket) {
      this.socket.emit('join_query', { query_id: queryId });
    }
  }

  leaveQuery(queryId: string): void {
    if (this.socket) {
      this.socket.emit('leave_query', { query_id: queryId });
    }
  }

  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);

    if (this.socket) {
      this.socket.on(event, callback as any);
    }
  }

  off(event: string, callback: Function): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.delete(callback);
    }

    if (this.socket) {
      this.socket.off(event, callback as any);
    }
  }
}

export const wsManager = new WebSocketManager();