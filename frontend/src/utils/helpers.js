import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes with clsx
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Format duration from minutes to human-readable format
 */
export function formatDuration(minutes) {
  if (minutes < 60) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (remainingMinutes === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${remainingMinutes}m`;
}

/**
 * Capitalize first letter of string
 */
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Convert camelCase to Title Case
 */
export function camelToTitle(str) {
  if (!str) return '';
  return str
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
    .trim();
}

/**
 * Generate a random ID
 */
export function generateId() {
  return Math.random().toString(36).substr(2, 9);
}

/**
 * Debounce function
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Format date to readable string
 */
export function formatDate(date) {
  if (!date) return '';

  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };

  return new Date(date).toLocaleDateString('en-US', options);
}

/**
 * Truncate text to specified length
 */
export function truncateText(text, maxLength) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
}

/**
 * Validate email format
 */
export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Download file from blob
 */
export function downloadFile(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Convert form data to lesson request object
 */
export function formatLessonRequest(formData) {
  return {
    course_title: formData.courseTitle,
    lesson_topic: formData.lessonTopic,
    grade_level: formData.gradeLevel,
    duration_minutes: parseInt(formData.duration),
    preliminary_objectives: formData.preliminaryObjectives,
    selected_bloom_levels: formData.selectedBloomLevels,
    additional_requirements: formData.additionalRequirements || null
  };
}

/**
 * Get Bloom's taxonomy level color class
 */
export function getBloomColor(level) {
  const colorMap = {
    remember: 'bloom-remember',
    understand: 'bloom-understand',
    apply: 'bloom-apply',
    analyze: 'bloom-analyze',
    evaluate: 'bloom-evaluate',
    create: 'bloom-create'
  };

  return colorMap[level] || 'bg-gray-100 text-gray-800 border-gray-200';
}

/**
 * Calculate total duration from Gagne events
 */
export function calculateTotalDuration(gagneEvents) {
  if (!gagneEvents || !Array.isArray(gagneEvents)) return 0;

  return gagneEvents.reduce((total, event) => {
    return total + (event.duration_minutes || 0);
  }, 0);
}

/**
 * Group objectives by Bloom's level
 */
export function groupObjectivesByBloom(objectives) {
  if (!objectives || !Array.isArray(objectives)) return {};

  return objectives.reduce((groups, objective) => {
    const level = objective.bloom_level;
    if (!groups[level]) {
      groups[level] = [];
    }
    groups[level].push(objective);
    return groups;
  }, {});
}

/**
 * Validate lesson form data
 */
export function validateLessonForm(data) {
  const errors = {};

  if (!data.courseTitle?.trim()) {
    errors.courseTitle = 'Course title is required';
  } else if (data.courseTitle.length < 2) {
    errors.courseTitle = 'Course title must be at least 2 characters';
  } else if (data.courseTitle.length > 200) {
    errors.courseTitle = 'Course title must be less than 200 characters';
  }

  if (!data.lessonTopic?.trim()) {
    errors.lessonTopic = 'Lesson topic is required';
  } else if (data.lessonTopic.length < 2) {
    errors.lessonTopic = 'Lesson topic must be at least 2 characters';
  } else if (data.lessonTopic.length > 200) {
    errors.lessonTopic = 'Lesson topic must be less than 200 characters';
  }

  if (!data.gradeLevel) {
    errors.gradeLevel = 'Grade level is required';
  }

  const duration = parseInt(data.duration);
  if (!duration || duration < 5) {
    errors.duration = 'Duration must be at least 5 minutes';
  } else if (duration > 480) {
    errors.duration = 'Duration must be less than 8 hours';
  }

  if (!data.preliminaryObjectives?.trim()) {
    errors.preliminaryObjectives = 'Preliminary objectives are required';
  } else if (data.preliminaryObjectives.length < 10) {
    errors.preliminaryObjectives = 'Please provide more detailed objectives';
  } else if (data.preliminaryObjectives.length > 1000) {
    errors.preliminaryObjectives = 'Objectives must be less than 1000 characters';
  }

  if (!data.selectedBloomLevels || data.selectedBloomLevels.length === 0) {
    errors.selectedBloomLevels = 'Please select at least one Bloom\'s taxonomy level';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}

/**
 * Generate filename for PDF export
 */
export function generatePDFFilename(lessonData) {
  const courseTitle = lessonData.lesson_info.course_title || 'Lesson';
  const lessonTopic = lessonData.lesson_info.lesson_topic || 'Plan';
  const date = new Date().toISOString().split('T')[0];

  // Clean filename by removing special characters
  const cleanTitle = courseTitle.replace(/[^a-zA-Z0-9]/g, '_');
  const cleanTopic = lessonTopic.replace(/[^a-zA-Z0-9]/g, '_');

  return `${cleanTitle}_${cleanTopic}_${date}.pdf`;
}

/**
 * Parse error message from API response
 */
export function parseErrorMessage(error) {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }

  if (error.message) {
    return error.message;
  }

  return 'An unexpected error occurred';
}

/**
 * Format objectives for display
 */
export function formatObjectiveText(objective) {
  let text = objective.objective;

  if (objective.condition) {
    text += ` (${objective.condition})`;
  }

  if (objective.criteria) {
    text += ` - ${objective.criteria}`;
  }

  return text;
}

/**
 * Check if lesson data is complete
 */
export function isLessonComplete(lessonData) {
  return (
    lessonData &&
    lessonData.objectives &&
    lessonData.objectives.length > 0 &&
    lessonData.lesson_plan &&
    lessonData.gagne_events &&
    lessonData.gagne_events.length > 0
  );
}

/**
 * Get step status for wizard
 */
export function getStepStatus(currentStep, stepIndex) {
  if (stepIndex < currentStep) return 'completed';
  if (stepIndex === currentStep) return 'active';
  return 'inactive';
}