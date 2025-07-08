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
  if (!minutes || minutes <= 0) return '0 min';

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
 * Validate duration change
 */
export function validateDurationChange(currentDuration, newDuration) {
  const errors = [];

  const duration = parseInt(newDuration);

  if (!duration) {
    errors.push('Duration must be a valid number');
  } else if (duration < 5) {
    errors.push('Duration must be at least 5 minutes');
  } else if (duration > 480) {
    errors.push('Duration must be less than 8 hours (480 minutes)');
  } else if (duration === currentDuration) {
    errors.push('New duration must be different from current duration');
  }

  return {
    isValid: errors.length === 0,
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

/**
 * Format grade level for display
 */
export function formatGradeLevel(gradeLevel) {
  const gradeMap = {
    'freshman': 'Freshman',
    'sophomore': 'Sophomore',
    'junior': 'Junior',
    'senior': 'Senior',
    'masters': 'Master\'s',
    'postgrad': 'Postgraduate'
  };

  return gradeMap[gradeLevel] || capitalize(gradeLevel);
}

/**
 * Clean overview text from template variables
 */
export function cleanOverviewText(overview) {
  if (!overview) return "This lesson provides comprehensive coverage of the topic with engaging activities and assessments.";

  // Clean up any remaining template variables
  let cleanText = overview
    .replace(/GradeLevel\.MASTERS/g, 'master\'s')
    .replace(/GradeLevel\.FRESHMAN/g, 'freshman')
    .replace(/GradeLevel\.SOPHOMORE/g, 'sophomore')
    .replace(/GradeLevel\.JUNIOR/g, 'junior')
    .replace(/GradeLevel\.SENIOR/g, 'senior')
    .replace(/GradeLevel\.POSTGRAD/g, 'postgraduate')
    .replace(/GradeLevel\./g, '');

  return cleanText;
}

/**
 * Calculate time distribution for Gagne events
 */
export function calculateGagneTimeDistribution(totalDuration, focusType = 'balanced') {
  const baseDistributions = {
    theoretical: {
      1: 0.05, 2: 0.05, 3: 0.12, 4: 0.35, 5: 0.15, 6: 0.15, 7: 0.08, 8: 0.05, 9: 0.06
    },
    practical: {
      1: 0.05, 2: 0.03, 3: 0.08, 4: 0.25, 5: 0.20, 6: 0.25, 7: 0.10, 8: 0.04, 9: 0.06
    },
    balanced: {
      1: 0.05, 2: 0.04, 3: 0.10, 4: 0.30, 5: 0.18, 6: 0.20, 7: 0.09, 8: 0.05, 9: 0.06
    }
  };

  const distribution = baseDistributions[focusType] || baseDistributions.balanced;
  const timeDistribution = {};
  let totalAllocated = 0;

  // Calculate time for events 1-8
  for (let event = 1; event <= 8; event++) {
    const minutes = Math.round(distribution[event] * totalDuration);
    timeDistribution[event] = Math.max(1, minutes); // Minimum 1 minute
    totalAllocated += timeDistribution[event];
  }

  // Event 9 gets remaining time
  timeDistribution[9] = Math.max(1, totalDuration - totalAllocated);

  return timeDistribution;
}

/**
 * Validate time distribution
 */
export function validateTimeDistribution(timeDistribution, expectedTotal) {
  const actualTotal = Object.values(timeDistribution).reduce((sum, time) => sum + time, 0);
  const tolerance = 2; // Allow 2 minute tolerance

  return Math.abs(actualTotal - expectedTotal) <= tolerance;
}

/**
 * Get lesson focus type based on Bloom's levels
 */
export function getLessonFocusType(bloomLevels) {
  if (!bloomLevels || bloomLevels.length === 0) return 'balanced';

  const practicalLevels = ['apply', 'analyze', 'evaluate', 'create'];
  const theoreticalLevels = ['remember', 'understand'];

  const practicalCount = bloomLevels.filter(level => practicalLevels.includes(level)).length;
  const theoreticalCount = bloomLevels.filter(level => theoreticalLevels.includes(level)).length;

  if (practicalCount > theoreticalCount) return 'practical';
  if (theoreticalCount > practicalCount) return 'theoretical';
  return 'balanced';
}

/**
 * Format time distribution for display
 */
export function formatTimeDistribution(timeDistribution, totalDuration) {
  const eventNames = {
    1: "Gain Attention",
    2: "Inform Objectives",
    3: "Stimulate Recall",
    4: "Present Content",
    5: "Provide Guidance",
    6: "Elicit Performance",
    7: "Provide Feedback",
    8: "Assess Performance",
    9: "Enhance Retention"
  };

  return Object.entries(timeDistribution).map(([eventNum, minutes]) => {
    const percentage = ((minutes / totalDuration) * 100).toFixed(1);
    return {
      event: parseInt(eventNum),
      name: eventNames[eventNum],
      minutes: minutes,
      percentage: percentage
    };
  });
}

/**
 * Deep clone object
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === 'object') {
    const clonedObj = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
}

/**
 * Compare two lesson data objects for changes
 */
export function compareLessonData(oldData, newData) {
  const changes = [];

  // Check duration change
  if (oldData.total_duration !== newData.total_duration) {
    changes.push({
      type: 'duration',
      old: oldData.total_duration,
      new: newData.total_duration
    });
  }

  // Check objectives count change
  if (oldData.objectives.length !== newData.objectives.length) {
    changes.push({
      type: 'objectives_count',
      old: oldData.objectives.length,
      new: newData.objectives.length
    });
  }

  // Check overview change
  if (oldData.lesson_plan.overview !== newData.lesson_plan.overview) {
    changes.push({
      type: 'overview',
      old: oldData.lesson_plan.overview.substring(0, 50) + '...',
      new: newData.lesson_plan.overview.substring(0, 50) + '...'
    });
  }

  return changes;
}

/**
 * Export lesson data for external use
 */
export function exportLessonData(lessonData, format = 'json') {
  const exportData = {
    meta: {
      exported_at: new Date().toISOString(),
      format: format,
      version: '1.0.0'
    },
    lesson: lessonData
  };

  switch (format) {
    case 'json':
      return JSON.stringify(exportData, null, 2);
    case 'csv':
      return convertLessonToCSV(lessonData);
    default:
      return exportData;
  }
}

/**
 * Convert lesson data to CSV format
 */
function convertLessonToCSV(lessonData) {
  const rows = [];

  // Header
  rows.push(['Section', 'Type', 'Content', 'Duration', 'Notes']);

  // Basic info
  rows.push(['Info', 'Course', lessonData.lesson_info.course_title, '', '']);
  rows.push(['Info', 'Topic', lessonData.lesson_info.lesson_topic, lessonData.total_duration, '']);
  rows.push(['Info', 'Grade Level', lessonData.lesson_info.grade_level, '', '']);

  // Objectives
  lessonData.objectives.forEach((obj, index) => {
    rows.push([
      'Objectives',
      obj.bloom_level,
      obj.objective,
      '',
      `${obj.action_verb} - ${obj.content}`
    ]);
  });

  // Gagne Events
  lessonData.gagne_events.forEach(event => {
    rows.push([
      'Gagne Events',
      `Event ${event.event_number}`,
      event.event_name,
      event.duration_minutes,
      event.description
    ]);
  });

  return rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
}

/**
 * Check if browser supports localStorage
 */
export function isLocalStorageAvailable() {
  try {
    const test = '__localStorage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Safe localStorage operations
 */
export function safeLocalStorage() {
  return {
    getItem: (key) => {
      try {
        return localStorage.getItem(key);
      } catch (e) {
        console.warn('localStorage getItem failed:', e);
        return null;
      }
    },
    setItem: (key, value) => {
      try {
        localStorage.setItem(key, value);
        return true;
      } catch (e) {
        console.warn('localStorage setItem failed:', e);
        return false;
      }
    },
    removeItem: (key) => {
      try {
        localStorage.removeItem(key);
        return true;
      } catch (e) {
        console.warn('localStorage removeItem failed:', e);
        return false;
      }
    }
  };
}

/**
 * Validate objective structure and normalize it
 */
export function validateObjectiveStructure(obj, index = 0) {
  const validLevels = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'];

  let bloomLevel = (obj.bloom_level || obj.level || 'understand').toLowerCase();
  if (!validLevels.includes(bloomLevel)) {
    console.warn(`Invalid bloom level: ${bloomLevel}, defaulting to 'understand'`);
    bloomLevel = 'understand';
  }

  return {
    bloom_level: bloomLevel,
    objective: obj.objective || obj.description || `Learning objective ${index + 1}`,
    action_verb: obj.action_verb || obj.verb || obj.action || 'understand',
    content: obj.content || obj.topic || 'core concepts',
    condition: obj.condition || null,
    criteria: obj.criteria || null
  };
}

/**
 * Extract unique Bloom levels from objectives
 */
export function extractBloomLevelsFromObjectives(objectives) {
  if (!objectives || !Array.isArray(objectives)) return [];
  return [...new Set(objectives.map(obj => obj.bloom_level).filter(Boolean))];
}

/**
 * Ensure lesson data consistency
 */
export function ensureLessonDataConsistency(lessonData) {
  if (!lessonData) return null;

  // Ensure objectives are properly structured
  const validatedObjectives = (lessonData.objectives || []).map(validateObjectiveStructure);

  // Extract bloom levels from objectives
  const bloomLevelsFromObjectives = extractBloomLevelsFromObjectives(validatedObjectives);

  return {
    ...lessonData,
    objectives: validatedObjectives,
    lesson_info: {
      ...lessonData.lesson_info,
      selected_bloom_levels: bloomLevelsFromObjectives
    }
  };
}

/**
 * Calculate optimal objectives count based on duration and cognitive load theory
 */
export function calculateOptimalObjectivesCount(duration) {
  if (duration <= 30) return 2;
  if (duration <= 60) return 3;
  if (duration <= 90) return 4;
  if (duration <= 120) return 5;
  return 6;
}

/**
 * Format lesson data for API request
 */
export function formatLessonDataForAPI(lessonData) {
  return {
    lesson_data: {
      ...lessonData,
      // Ensure all arrays are properly formatted
      objectives: lessonData.objectives?.map(obj => ({
        ...obj,
        bloom_level: obj.bloom_level?.toLowerCase()
      })) || [],
      gagne_events: lessonData.gagne_events?.map(event => ({
        ...event,
        activities: Array.isArray(event.activities) ? event.activities : [event.activities].filter(Boolean),
        materials_needed: Array.isArray(event.materials_needed) ? event.materials_needed : [event.materials_needed].filter(Boolean)
      })) || []
    }
  };
}

/**
 * Merge lesson data updates while preserving structure
 */
export function mergeLessonDataUpdates(currentData, updates) {
  const merged = deepClone(currentData);

  // Handle different update types
  if (updates.objectives) {
    merged.objectives = updates.objectives.map(validateObjectiveStructure);
    merged.lesson_info.selected_bloom_levels = extractBloomLevelsFromObjectives(merged.objectives);
  }

  if (updates.lesson_plan) {
    merged.lesson_plan = { ...merged.lesson_plan, ...updates.lesson_plan };
  }

  if (updates.gagne_events) {
    merged.gagne_events = updates.gagne_events;
  }

  if (updates.duration_minutes || updates.total_duration) {
    const newDuration = updates.duration_minutes || updates.total_duration;
    merged.lesson_info.duration_minutes = newDuration;
    merged.total_duration = newDuration;
  }

  return merged;
}

/**
 * Validate lesson data structure
 */
export function validateLessonDataStructure(lessonData) {
  const issues = [];

  if (!lessonData) {
    issues.push('Lesson data is null or undefined');
    return { isValid: false, issues };
  }

  // Check required fields
  if (!lessonData.lesson_info) {
    issues.push('Missing lesson_info');
  } else {
    if (!lessonData.lesson_info.course_title) issues.push('Missing course_title');
    if (!lessonData.lesson_info.lesson_topic) issues.push('Missing lesson_topic');
    if (!lessonData.lesson_info.grade_level) issues.push('Missing grade_level');
    if (!lessonData.lesson_info.duration_minutes) issues.push('Missing duration_minutes');
  }

  // Check objectives
  if (!lessonData.objectives || !Array.isArray(lessonData.objectives)) {
    issues.push('Objectives must be an array');
  } else if (lessonData.objectives.length === 0) {
    issues.push('At least one objective is required');
  }

  // Check Gagne events
  if (!lessonData.gagne_events || !Array.isArray(lessonData.gagne_events)) {
    issues.push('Gagne events must be an array');
  } else if (lessonData.gagne_events.length !== 9) {
    issues.push('Must have exactly 9 Gagne events');
  }

  // Check lesson plan
  if (!lessonData.lesson_plan) {
    issues.push('Missing lesson_plan');
  }

  return {
    isValid: issues.length === 0,
    issues
  };
}

/**
 * Generate lesson summary for display
 */
export function generateLessonSummary(lessonData) {
  if (!lessonData) return null;

  const objectivesCount = lessonData.objectives?.length || 0;
  const bloomLevels = extractBloomLevelsFromObjectives(lessonData.objectives || []);
  const duration = lessonData.total_duration || lessonData.lesson_info?.duration_minutes || 0;
  const eventsCount = lessonData.gagne_events?.length || 0;

  return {
    title: `${lessonData.lesson_info?.course_title} - ${lessonData.lesson_info?.lesson_topic}`,
    duration: formatDuration(duration),
    objectives_count: objectivesCount,
    bloom_levels_count: bloomLevels.length,
    bloom_levels: bloomLevels.map(capitalize).join(', '),
    events_count: eventsCount,
    grade_level: formatGradeLevel(lessonData.lesson_info?.grade_level),
    optimal_objectives: calculateOptimalObjectivesCount(duration),
    is_optimized: Math.abs(objectivesCount - calculateOptimalObjectivesCount(duration)) <= 1
  };
}