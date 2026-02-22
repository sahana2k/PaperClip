import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '120000');

const getErrorMessage = (error) => {
  const rawMessage = error.response?.data?.detail || error.message || 'Request failed';
  if (rawMessage.toLowerCase().includes('timeout')) {
    return 'Request timed out. Try again or increase REACT_APP_API_TIMEOUT in your frontend env.';
  }
  return rawMessage;
};

const api = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
};

export const apiService = {
  setAuthToken,

  // Auth
  register: async (email, password, name = null) => {
    try {
      const response = await api.post('/auth/register', { email, password, name });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  getMe: async () => {
    try {
      const response = await api.get('/auth/me');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  // Health check
  checkHealth: async () => {
    try {
      const response = await api.get('/health');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Chat query
  query: async (message, conversationHistory = [], workspaceId = null, toolType = null) => {
    try {
      const response = await api.post('/query', {
        query: message,
        conversation_history: conversationHistory,
        workspace_id: workspaceId,
        tool_type: toolType,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  // Get available tools
  getTools: async () => {
    try {
      const response = await api.get('/tools');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Get statistics
  getStats: async () => {
    try {
      const response = await api.get('/stats');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Quick search
  quickSearch: async (query) => {
    try {
      const response = await api.get(`/quick-search?q=${encodeURIComponent(query)}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Get popular topics
  getPopularTopics: async () => {
    try {
      const response = await api.get('/popular-topics');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Export chat
  exportChat: async (format = 'json') => {
    try {
      const response = await api.get(`/export-chat?format=${format}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Phase 3 Workspaces & Memory
  getWorkspaces: async () => {
    try {
      const response = await api.get('/workspaces');
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  createWorkspace: async (name, description = null) => {
    try {
      const response = await api.post('/workspaces', { name, description });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  deleteWorkspace: async (workspaceId) => {
    try {
      const response = await api.delete(`/workspaces/${workspaceId}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  getWorkspaceMessages: async (workspaceId, limit = 200, offset = 0) => {
    try {
      const response = await api.get(`/workspaces/${workspaceId}/messages?limit=${limit}&offset=${offset}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  getWorkspaceResources: async (workspaceId) => {
    try {
      const response = await api.get(`/workspaces/${workspaceId}/resources`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  createWorkspaceResource: async (workspaceId, type, title, content, metadata = {}) => {
    try {
      const response = await api.post(`/workspaces/${workspaceId}/resources`, {
        type,
        title,
        content,
        metadata
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  deleteWorkspaceResource: async (workspaceId, resourceId) => {
    try {
      const response = await api.delete(`/workspaces/${workspaceId}/resources/${resourceId}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  getWorkspaceMemory: async (workspaceId) => {
    try {
      const response = await api.get(`/workspaces/${workspaceId}/memory`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  addWorkspaceMemory: async (workspaceId, key, value) => {
    try {
      const response = await api.post(`/workspaces/${workspaceId}/memory`, { key, value });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  deleteWorkspaceMemory: async (workspaceId, key) => {
    try {
      const response = await api.delete(`/workspaces/${workspaceId}/memory/${encodeURIComponent(key)}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  // Phase 2 Enhanced Features
  // Generate mind map
  generateMindMap: async (topic) => {
    try {
      const response = await api.post(`/mindmap?topic=${encodeURIComponent(topic)}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  // Generate podcast script
  generatePodcast: async (topic) => {
    try {
      const response = await api.post(`/podcast?topic=${encodeURIComponent(topic)}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  // Get citations with BibTeX
  getCitations: async (topic) => {
    try {
      const response = await api.post(`/citations?topic=${encodeURIComponent(topic)}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  // Phase 4 Ideation & Experiment Design
  generateIdeation: async (topic, goal = null, constraints = null, workspaceId = null) => {
    try {
      const response = await api.post('/ideation', {
        topic,
        goal,
        constraints,
        workspace_id: workspaceId,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  generateExperimentDesign: async (topic, idea = null, constraints = null, workspaceId = null) => {
    try {
      const response = await api.post('/experiment-design', {
        topic,
        idea,
        constraints,
        workspace_id: workspaceId,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  getWorkspaceIdeation: async (workspaceId) => {
    try {
      const response = await api.get(`/workspaces/${workspaceId}/ideation`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  getWorkspaceExperiments: async (workspaceId) => {
    try {
      const response = await api.get(`/workspaces/${workspaceId}/experiments`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },

  // Full research suite
  getResearchSuite: async (topic) => {
    try {
      const response = await api.post(`/research-suite?topic=${encodeURIComponent(topic)}`);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: getErrorMessage(error) };
    }
  },
};

