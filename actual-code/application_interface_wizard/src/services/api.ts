/**
 * API Service for Interface Wizard
 * Centralized API configuration and endpoints
 *
 * Backend: main_with_fastapi.py (v3.0)
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Upload and processing endpoints (v3.0)
  upload: `${API_BASE_URL}/api/upload`,
  confirm: `${API_BASE_URL}/api/upload/confirm`,

  // Dashboard endpoints (v3.0)
  dashboardStats: `${API_BASE_URL}/api/dashboard/stats`,
  systemStatus: `${API_BASE_URL}/api/dashboard/system-status`,

  // Health check
  health: `${API_BASE_URL}/health`,
};

export default API_ENDPOINTS;
