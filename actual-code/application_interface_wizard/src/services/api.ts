/**
 * API Service for Interface Wizard
 * Centralized API configuration and endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Upload and processing endpoints
  upload: `${API_BASE_URL}/api/v1/preview`,
  confirm: `${API_BASE_URL}/api/v1/confirm`,

  // Dashboard endpoints
  dashboardStats: `${API_BASE_URL}/api/v1/health/detailed`,
  systemStatus: `${API_BASE_URL}/api/v1/health/detailed`,

  // Health check
  health: `${API_BASE_URL}/api/v1/health`,
};

export default API_ENDPOINTS;
