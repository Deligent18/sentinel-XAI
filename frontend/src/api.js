/**
 * XAI Risk Sentinel - API Service
 * Handles all backend communication including authentication, data fetching, and WebSocket
 */

// API Base URL - configure based on environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Token storage key
const TOKEN_KEY = 'xai_token';
const USER_KEY = 'xai_user';

// ============================================
// AUTHENTICATION
// ============================================

export async function login(username, password, role) {
  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password, role }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    
    // Store token and user info
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify({ username, role }));
    
    return {
      success: true,
      token: data.access_token,
      username,
      role,
    };
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error: error.message,
    };
  }
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser() {
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
}

export function isAuthenticated() {
  return !!getStoredToken();
}

// ============================================
// AUTHENTICATED FETCH
// ============================================

async function authenticatedFetch(url, options = {}) {
  const token = getStoredToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (response.status === 401) {
    // Token expired or invalid
    logout();
    window.location.reload();
    throw new Error('Session expired');
  }
  
  return response;
}

// ============================================
// STUDENTS API
// ============================================

export async function fetchStudents() {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/students`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch students');
    }
    
    const students = await response.json();
    return { success: true, students };
  } catch (error) {
    console.error('Error fetching students:', error);
    return { success: false, error: error.message };
  }
}

export async function fetchStudent(studentId) {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/students/${studentId}`);
    
    if (!response.ok) {
      throw new Error('Student not found');
    }
    
    const student = await response.json();
    return { success: true, student };
  } catch (error) {
    console.error('Error fetching student:', error);
    return { success: false, error: error.message };
  }
}

export async function updateStudent(studentId, updates) {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/students/${studentId}`, {
      method: 'POST',
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      throw new Error('Failed to update student');
    }
    
    const student = await response.json();
    return { success: true, student };
  } catch (error) {
    console.error('Error updating student:', error);
    return { success: false, error: error.message };
  }
}

// ============================================
// STATS API
// ============================================

export async function fetchStats() {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/stats`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch stats');
    }
    
    const stats = await response.json();
    return { success: true, stats };
  } catch (error) {
    console.error('Error fetching stats:', error);
    return { success: false, error: error.message };
  }
}

// ============================================
// ROLES API
// ============================================

export async function fetchRoles() {
  try {
    const response = await fetch(`${API_BASE_URL}/roles`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch roles');
    }
    
    const roles = await response.json();
    return { success: true, roles };
  } catch (error) {
    console.error('Error fetching roles:', error);
    return { success: false, error: error.message };
  }
}

// ============================================
// TIER CONFIG API
// ============================================

export async function fetchTierConfig() {
  try {
    const response = await fetch(`${API_BASE_URL}/tier`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch tier config');
    }
    
    const tier = await response.json();
    return { success: true, tier };
  } catch (error) {
    console.error('Error fetching tier config:', error);
    return { success: false, error: error.message };
  }
}

// ============================================
// AUDIT LOGS API
// ============================================

export async function fetchAuditLogs() {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/audit-logs`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch audit logs');
    }
    
    const logs = await response.json();
    return { success: true, logs };
  } catch (error) {
    console.error('Error fetching audit logs:', error);
    return { success: false, error: error.message };
  }
}

export async function createAuditLog(action, target, level) {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/audit-logs`, {
      method: 'POST',
      body: JSON.stringify({ action, target, level }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create audit log');
    }
    
    const log = await response.json();
    return { success: true, log };
  } catch (error) {
    console.error('Error creating audit log:', error);
    return { success: false, error: error.message };
  }
}

// ============================================\n// USERS API\n// ============================================\n\nexport async function createUser(userData) {\n  try {\n    const response = await authenticatedFetch(`${API_BASE_URL}/users`, {\n      method: 'POST',\n      body: JSON.stringify(userData),\n    });\n    \n    if (!response.ok) {\n      throw new Error('Failed to create user');\n    }\n    \n    const result = await response.json();\n    return { success: true, result };\n  } catch (error) {\n    console.error('Error creating user:', error);\n    return { success: false, error: error.message };\n  }\n}

export async function fetchUsers() {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/users`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }
    
    const users = await response.json();
    return { success: true, users };
  } catch (error) {
    console.error('Error fetching users:', error);
    return { success: false, error: error.message };
  }
}

// ============================================
// PIPELINE API
// ============================================

export async function getPipelineStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/status`);
    
    if (!response.ok) {
      throw new Error('Failed to get pipeline status');
    }
    
    const status = await response.json();
    return { success: true, status };
  } catch (error) {
    console.error('Error getting pipeline status:', error);
    return { success: false, error: error.message };
  }
}

export async function runPipeline() {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/pipeline/run`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to run pipeline');
    }
    
    const result = await response.json();
    return { success: true, result };
  } catch (error) {
    console.error('Error running pipeline:', error);
    return { success: false, error: error.message };
  }
}

export async function predictStudent(studentId) {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/pipeline/predict/${studentId}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to predict student');
    }
    
    const result = await response.json();
    return { success: true, result };
  } catch (error) {
    console.error('Error predicting student:', error);
    return { success: false, error: error.message };
  }
}

export async function batchUpdatePredictions() {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/students/batch`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to batch update predictions');
    }
    
    const result = await response.json();
    return { success: true, result };
  } catch (error) {
    console.error('Error batch updating predictions:', error);
    return { success: false, error: error.message };
  }
}

// ============================================
// WEBSOCKET CONNECTION
// ============================================

class WebSocketManager {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
  }

  connect() {
    const token = getStoredToken();
    const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/ws`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        
        // Authenticate after connection
        if (token) {
          this.ws.send(JSON.stringify({ type: 'auth', token }));
        }
      };
      
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.notifyListeners(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.attemptReconnect();
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.attemptReconnect();
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      setTimeout(() => this.connect(), this.reconnectDelay);
    } else {
      console.log('Max reconnection attempts reached');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  notifyListeners(message) {
    const event = message.type;
    const data = message.data;
    
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
    
    // Also notify 'any' listeners
    if (this.listeners.has('any')) {
      this.listeners.get('any').forEach(callback => callback(message));
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
}

// Singleton WebSocket manager
export const wsManager = new WebSocketManager();

// ============================================
// PREPROCESSING API
// ============================================

export async function runPreprocessing() {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/preprocessing/run`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to start preprocessing');
    }
    
    const result = await response.json();
    return { success: true, result };
  } catch (error) {
    console.error('Error running preprocessing:', error);
    return { success: false, error: error.message };
  }
}

export async function getPreprocessingStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/preprocessing/status`);
    
    if (!response.ok) {
      throw new Error('Failed to get preprocessing status');
    }
    
    const status = await response.json();
    return { success: true, status };
  } catch (error) {
    console.error('Error getting preprocessing status:', error);
    return { success: false, error: error.message };
  }
}

export async function getPreprocessingResults() {
  try {
    const response = await authenticatedFetch(`${API_BASE_URL}/preprocessing/results`);
    
    if (!response.ok) {
      throw new Error('Failed to get preprocessing results');
    }
    
    const results = await response.json();
    return { success: true, results };
  } catch (error) {
    console.error('Error getting preprocessing results:', error);
    return { success: false, error: error.message };
  }
}

// ============================================
// HEALTH CHECK
// ============================================

export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    
    const health = await response.json();
    return { success: true, health };
  } catch (error) {
    console.error('Health check error:', error);
    return { success: false, error: error.message };
  }
}

// ============================================
// EXPORT DEFAULT API OBJECT
// ============================================

export default {\n  // Auth\n  login,\n  logout,\n  getStoredToken,\n  getStoredUser,\n  isAuthenticated,\n  \n  // Students\n  fetchStudents,\n  fetchStudent,\n  updateStudent,\n  \n  // Stats\n  fetchStats,\n  \n  // Roles\n  fetchRoles,\n  \n  // Tier\n  fetchTierConfig,\n  \n  // Audit\n  fetchAuditLogs,\n  createAuditLog,\n  \n  // Users\n  fetchUsers,\n  createUser,\n  \n  // Pipeline\n  getPipelineStatus,\n  runPipeline,\n  predictStudent,\n  batchUpdatePredictions,\n  \n  // Preprocessing\n  runPreprocessing,\n  getPreprocessingStatus,\n  getPreprocessingResults,\n  \n  // WebSocket\n  wsManager,\n  \n  // Health\n  healthCheck,\n  \n  // Base URL\n  API_BASE_URL,\n};

