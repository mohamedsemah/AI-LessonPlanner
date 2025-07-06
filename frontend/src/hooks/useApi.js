import { useState, useCallback } from 'react';
import apiService from '../services/api';
import { parseErrorMessage } from '../utils/helpers';

/**
 * Custom hook for API calls with loading and error states
 */
export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const executeRequest = useCallback(async (apiCall) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      return result;
    } catch (err) {
      const errorMessage = parseErrorMessage(err);
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const generateLesson = useCallback(async (lessonRequest) => {
    return executeRequest(() => apiService.generateLesson(lessonRequest));
  }, [executeRequest]);

  const refineContent = useCallback(async (refinementRequest) => {
    console.log('🔧 useApi: refineContent called');

    try {
      const result = await apiService.refineContent(refinementRequest);
      console.log('🔧 useApi: API call successful');
      return result;
    } catch (err) {
      console.error('🔧 useApi: API call failed:', err);
      throw err; // Re-throw to let the caller handle it
    }
  }, []);

  const exportToPDF = useCallback(async (lessonData, options) => {
    return executeRequest(() => apiService.exportToPDF(lessonData, options));
  }, [executeRequest]);

  const getBloomLevels = useCallback(async () => {
    return executeRequest(() => apiService.getBloomLevels());
  }, [executeRequest]);

  const getGagneEvents = useCallback(async () => {
    return executeRequest(() => apiService.getGagneEvents());
  }, [executeRequest]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    generateLesson,
    refineContent,
    exportToPDF,
    getBloomLevels,
    getGagneEvents,
    clearError
  };
}

/**
 * Hook for individual API operations with their own loading states
 */
export function useAsyncOperation() {
  const [state, setState] = useState({
    loading: false,
    error: null,
    data: null
  });

  const execute = useCallback(async (asyncOperation) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data = await asyncOperation();
      setState({ loading: false, error: null, data });
      return data;
    } catch (error) {
      const errorMessage = parseErrorMessage(error);
      setState({ loading: false, error: errorMessage, data: null });
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ loading: false, error: null, data: null });
  }, []);

  return {
    ...state,
    execute,
    reset
  };
}