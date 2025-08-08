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
    console.log('📤 Request details:', {
      section_type: refinementRequest.section_type,
      instructions_length: refinementRequest.refinement_instructions?.length,
      has_lesson_context: !!refinementRequest.lesson_context,
      content_preview: refinementRequest.section_content?.substring(0, 100) + '...'
    });

    // Set loading state manually for refinement since it doesn't use executeRequest
    setLoading(true);
    setError(null);

    try {
      const result = await apiService.refineContent(refinementRequest);
      console.log('🔧 useApi: API call successful');
      console.log('📥 Response preview:', result?.refined_content?.substring(0, 100) + '...');

      // Validate response structure
      if (!result || typeof result !== 'object') {
        throw new Error('Invalid response format from API');
      }

      if (!result.refined_content) {
        throw new Error('No refined content received from API');
      }

      // Additional validation for JSON content
      if (refinementRequest.section_type !== 'duration_change') {
        try {
          JSON.parse(result.refined_content);
        } catch (jsonError) {
          console.warn('⚠️ Refined content is not valid JSON, but proceeding anyway');
        }
      }

      return result;
    } catch (err) {
      console.error('🔧 useApi: API call failed:', err);
      const errorMessage = parseErrorMessage(err);
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const generateCourseContent = useCallback(async (request) => {
    return executeRequest(() => apiService.generateCourseContent(request));
  }, [executeRequest]);

  const exportToPowerPoint = useCallback(async (courseContent, lessonData, designPreferences = {}) => {
    return executeRequest(() => apiService.exportCourseContentToPowerPoint(courseContent, lessonData, designPreferences));
  }, [executeRequest]);

  const exportToPDF = useCallback(async (courseContent, lessonData, designPreferences = {}) => {
    return executeRequest(() => apiService.exportCourseContentToPDF(courseContent, lessonData, designPreferences));
  }, [executeRequest]);

  const refineUDLContent = useCallback(async (refinementRequest) => {
    return executeRequest(() => apiService.refineUDLContent(refinementRequest));
  }, [executeRequest]);

  const getUDLGuidelines = useCallback(async () => {
    return executeRequest(() => apiService.getUDLGuidelines());
  }, [executeRequest]);

  const getContentModalities = useCallback(async () => {
    return executeRequest(() => apiService.getContentModalities());
  }, [executeRequest]);

  const getAccessibilityFeatures = useCallback(async () => {
    return executeRequest(() => apiService.getAccessibilityFeatures());
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
    generateCourseContent,
    exportToPowerPoint,
    exportToPDF,
    refineUDLContent,
    getUDLGuidelines,
    getContentModalities,
    getAccessibilityFeatures,
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

/**
 * Specialized hook for duration change operations
 */
export function useDurationChange() {
  const [state, setState] = useState({
    loading: false,
    error: null,
    progress: 0
  });

  const changeDuration = useCallback(async (currentData, newDuration, refineContentFn) => {
    setState({ loading: true, error: null, progress: 10 });

    try {
      // Validate inputs
      if (!currentData || !newDuration || !refineContentFn) {
        throw new Error('Missing required parameters for duration change');
      }

      setState(prev => ({ ...prev, progress: 20 }));

      // Calculate optimal objectives for new duration
      const calculateOptimalObjectives = (duration) => {
        if (duration <= 30) return 2;
        if (duration <= 60) return 3;
        if (duration <= 90) return 4;
        if (duration <= 120) return 5;
        return 6;
      };

      const currentObjectivesCount = currentData.objectives?.length || 0;
      const optimalObjectivesCount = calculateOptimalObjectives(newDuration);
      const objectiveChangeNeeded = Math.abs(optimalObjectivesCount - currentObjectivesCount) >= 1;

      setState(prev => ({ ...prev, progress: 40 }));

      // Prepare refinement request
      const refinementRequest = {
        section_type: 'duration_change',
        section_content: JSON.stringify({
          current_duration: currentData.lesson_info.duration_minutes,
          new_duration: newDuration,
          gagne_events: currentData.gagne_events,
          lesson_plan: currentData.lesson_plan,
          current_objectives: currentData.objectives
        }),
        refinement_instructions: `Change the lesson duration from ${currentData.lesson_info.duration_minutes} minutes to ${newDuration} minutes. Recalculate the time distribution for all Gagne events. Update the lesson overview. ${objectiveChangeNeeded ? `Recalculate learning objectives from ${currentObjectivesCount} to ${optimalObjectivesCount} objectives for optimal cognitive load.` : 'Keep existing objectives but ensure they are achievable in the new timeframe.'}`,
        lesson_context: {
          ...currentData.lesson_info,
          selected_bloom_levels: currentData.lesson_info.selected_bloom_levels
        }
      };

      setState(prev => ({ ...prev, progress: 60 }));

      // Execute API call
      const result = await refineContentFn(refinementRequest);

      setState(prev => ({ ...prev, progress: 80 }));

      // Validate and parse result
      if (!result || !result.refined_content) {
        throw new Error('No refined content received from API');
      }

      const refinedData = JSON.parse(result.refined_content);

      setState(prev => ({ ...prev, progress: 100, loading: false }));

      return {
        refinedData,
        objectiveChangeNeeded,
        currentObjectivesCount,
        optimalObjectivesCount
      };

    } catch (error) {
      const errorMessage = parseErrorMessage(error);
      setState({ loading: false, error: errorMessage, progress: 0 });
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ loading: false, error: null, progress: 0 });
  }, []);

  return {
    ...state,
    changeDuration,
    reset
  };
}

/**
 * Hook for content refinement operations
 */
export function useContentRefinement() {
  const [state, setState] = useState({
    loading: false,
    error: null,
    lastRefinedSection: null
  });

  const refineSection = useCallback(async (sectionType, content, instructions, lessonContext, refineContentFn) => {
    setState({ loading: true, error: null, lastRefinedSection: sectionType });

    try {
      // Validate inputs
      if (!sectionType || !content || !instructions || !refineContentFn) {
        throw new Error('Missing required parameters for content refinement');
      }

      const refinementRequest = {
        section_type: sectionType,
        section_content: content,
        refinement_instructions: instructions,
        lesson_context: lessonContext
      };

      const result = await refineContentFn(refinementRequest);

      if (!result || !result.refined_content) {
        throw new Error('No refined content received from API');
      }

      // Validate JSON structure based on section type
      let parsedContent;
      try {
        parsedContent = JSON.parse(result.refined_content);
      } catch (jsonError) {
        throw new Error(`Invalid JSON structure in refined content: ${jsonError.message}`);
      }

      // Section-specific validation
      switch (sectionType) {
        case 'objectives':
          if (!Array.isArray(parsedContent)) {
            throw new Error('Refined objectives must be an array');
          }
          break;
        case 'lesson_plan':
          if (typeof parsedContent !== 'object' || Array.isArray(parsedContent)) {
            throw new Error('Refined lesson plan must be an object');
          }
          break;
        case 'gagne_events':
          if (!Array.isArray(parsedContent) || parsedContent.length !== 9) {
            throw new Error('Refined Gagne events must be an array of 9 events');
          }
          break;
      }

      setState({ loading: false, error: null, lastRefinedSection: sectionType });

      return {
        refinedContent: parsedContent,
        sectionType
      };

    } catch (error) {
      const errorMessage = parseErrorMessage(error);
      setState({ loading: false, error: errorMessage, lastRefinedSection: null });
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ loading: false, error: null, lastRefinedSection: null });
  }, []);

  return {
    ...state,
    refineSection,
    reset
  };
}