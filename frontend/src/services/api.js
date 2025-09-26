import axios from 'axios';
import { API_BASE_URL, PREMIUM_API_BASE_URL } from '../utils/constants';

// Create axios instance for Python backend (lesson planning)
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10 minutes for enhanced AI generation with validation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create axios instance for Node.js backend (premium exports)
const premiumApi = axios.create({
  baseURL: PREMIUM_API_BASE_URL,
  timeout: 180000, // 3 minutes for premium generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for Python backend
api.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for Python backend
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timeout. Please try again.';
    } else if (error.response?.status === 500) {
      error.message = 'Server error. Please try again later.';
    } else if (error.response?.status === 429) {
      error.message = 'Too many requests. Please wait a moment and try again.';
    } else if (!error.response) {
      error.message = 'Network error. Please check your connection.';
    }

    return Promise.reject(error);
  }
);

// Request interceptor for Node.js backend
premiumApi.interceptors.request.use(
  (config) => {
    // Add any auth headers here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for Node.js backend
premiumApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timeout. Please try again.';
    } else if (error.response?.status === 500) {
      error.message = 'Server error. Please try again later.';
    } else if (error.response?.status === 429) {
      error.message = 'Too many requests. Please wait a moment and try again.';
    } else if (!error.response) {
      error.message = 'Network error. Please check your connection.';
    }

    return Promise.reject(error);
  }
);

/**
 * API service class
 */
class APIService {
  /**
   * Generate lesson content
   */
  async generateLesson(lessonRequest) {
    try {
      console.log('🌐 API: Sending request to /api/lesson/generate');
      console.log('🌐 API: Request data:', JSON.stringify(lessonRequest, null, 2));
      const response = await api.post('/api/lesson/generate', lessonRequest);
      console.log('🌐 API: Response received:', response.status);
      return response.data;
    } catch (error) {
      console.error('🌐 API: Error response:', error.response?.status, error.response?.data);
      throw new Error(error.response?.data?.detail || error.message);
    }
  }

  /**
   * Refine specific content section
   */
  async refineContent(refinementRequest) {
    try {
      const response = await api.post('/api/lesson/refine', refinementRequest);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  }

  /**
   * Export lesson to PDF
   */
  async exportToPDF(lessonData, options = {}) {
    try {
      const requestData = {
        lesson_data: lessonData,
        include_cover_page: options.includeCoverPage ?? true,
        include_appendices: options.includeAppendices ?? true
      };

      const response = await api.post('/api/lesson/export/pdf', requestData, {
        responseType: 'blob',
        timeout: 60000 // 1 minute for PDF generation
      });

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to export PDF');
    }
  }

  /**
   * Generate UDL-compliant course content
   */
  async generateCourseContent(request) {
    try {
      const response = await api.post('/api/udl-content/generate', request, {
        timeout: 300000 // 5 minutes for UDL content generation
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  }

  /**
   * Export course content to PowerPoint (Premium)
   */
  async exportCourseContentToPowerPoint(courseContent, lessonData, designPreferences = {}) {
    try {
      const requestData = {
        courseContent: courseContent,
        lessonData: lessonData,
        designPreferences: designPreferences
      };

      const response = await premiumApi.post('/api/premium/export/pptx', requestData, {
        responseType: 'blob',
        timeout: 180000 // 3 minutes for premium PowerPoint generation
      });

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to export PowerPoint');
    }
  }

  /**
   * Export course content to PDF (Premium)
   */
  async exportCourseContentToPDF(courseContent, lessonData, designPreferences = {}) {
    try {
      const requestData = {
        courseContent: courseContent,
        lessonData: lessonData,
        designPreferences: designPreferences
      };

      const response = await premiumApi.post('/api/premium/export/pdf', requestData, {
        responseType: 'blob',
        timeout: 180000 // 3 minutes for premium PDF generation
      });

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to export PDF');
    }
  }

  /**
   * Refine UDL content
   */
  async refineUDLContent(refinementRequest) {
    try {
      const response = await api.post('/api/udl-content/refine', refinementRequest);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  }

  /**
   * Get UDL guidelines
   */
  async getUDLGuidelines() {
    try {
      const response = await api.get('/api/udl-content/guidelines');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  }

  /**
   * Get content modalities
   */
  async getContentModalities() {
    try {
      const response = await api.get('/api/udl-content/modalities');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  }

  /**
   * Get accessibility features
   */
  async getAccessibilityFeatures() {
    try {
      const response = await api.get('/api/udl-content/accessibility');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  }

  /**
   * Get available Bloom's taxonomy levels
   */
  async getBloomLevels() {
    try {
      const response = await api.get('/api/lesson/bloom-levels');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  }

  /**
   * Get Gagne's Nine Events information
   */
  async getGagneEvents() {
    try {
      const response = await api.get('/api/lesson/gagne-events');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message);
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await api.get('/api/lesson/health');
      return response.data;
    } catch (error) {
      throw new Error('API health check failed');
    }
  }
}

// Create and export singleton instance
const apiService = new APIService();
export default apiService;