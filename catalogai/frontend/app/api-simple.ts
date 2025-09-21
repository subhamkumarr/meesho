/**
 * Simple API client for CatalogAI backend
 * This version avoids TypeScript complexity
 */

// @ts-nocheck
import axios from 'axios';

// Types matching backend schemas
export interface ScanResult {
  filename: string;
  size: number;
  mime_type: string;
  score: number;
  label: 'authentic' | 'suspicious' | 'synthetic' | 'error';
  reasons: string[];
  processing_time_ms?: number;
}

export interface ScanResponse {
  results: ScanResult[];
  total_processed: number;
  total_time_ms: number;
}

// API Client class
class ApiClient {
  private client: any;

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
    
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config: any) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error: any) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: any) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error: any) => {
        console.error('API Response Error:', error.response?.data || error.message);
        
        if (error.response?.status === 413) {
          throw new Error('File too large. Please reduce file size and try again.');
        } else if (error.response?.status === 400) {
          throw new Error(error.response.data?.detail || 'Invalid request');
        } else if (error.response?.status === 500) {
          throw new Error('Server error. Please try again later.');
        } else if (error.code === 'ECONNABORTED') {
          throw new Error('Request timeout. Please try again.');
        } else if (!error.response) {
          throw new Error('Network error. Please check your connection.');
        }
        
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async healthCheck() {
    const response = await this.client.get('/health/');
    return response.data;
  }

  // Scan images
  async scanImages(files: File[]) {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await this.client.post('/scans/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000,
    });

    return response.data;
  }

  // Get scan history
  async getScans(page = 1, perPage = 20) {
    const response = await this.client.get('/scans/', {
      params: {
        page,
        per_page: perPage,
      },
    });
    return response.data;
  }

  // Get thresholds
  async getThresholds() {
    const response = await this.client.get('/admin/thresholds');
    return response.data;
  }

  // Update thresholds
  async updateThresholds(thresholds: any) {
    const response = await this.client.put('/admin/thresholds', thresholds);
    return response.data;
  }

  // Retrain model
  async retrainModel() {
    const response = await this.client.post('/admin/train', {}, {
      timeout: 120000,
    });
    return response.data;
  }

  // Get model metrics
  async getModelMetrics() {
    const response = await this.client.get('/admin/metrics');
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Utility functions
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatProcessingTime = (ms: number): string => {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
};

export const getLabelColor = (label: string): string => {
  switch (label) {
    case 'authentic':
      return 'text-green-700 bg-green-100 border-green-200';
    case 'suspicious':
      return 'text-yellow-700 bg-yellow-100 border-yellow-200';
    case 'synthetic':
      return 'text-red-700 bg-red-100 border-red-200';
    case 'error':
      return 'text-gray-700 bg-gray-100 border-gray-200';
    default:
      return 'text-gray-700 bg-gray-100 border-gray-200';
  }
};

export const getLabelText = (label: string): string => {
  switch (label) {
    case 'authentic':
      return 'Verified';
    case 'suspicious':
      return 'Suspicious';
    case 'synthetic':
      return 'Synthetic';
    case 'error':
      return 'Error';
    default:
      return 'Unknown';
  }
};