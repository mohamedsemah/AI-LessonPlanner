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
    uploaded_files: formData.uploadedFiles && formData.uploadedFiles.length > 0 ? formData.uploadedFiles : null,
    selected_bloom_levels: ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'],
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

  // File upload is now optional - only validate if files are provided
  if (data.uploadedFiles && data.uploadedFiles.length > 5) {
    errors.uploadedFiles = 'Maximum 5 files allowed';
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
 * Clean overview text from template variables and sanitize HTML
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

  // Basic HTML sanitization - allow common formatting tags but remove dangerous ones
  cleanText = cleanText
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remove script tags
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '') // Remove iframe tags
    .replace(/on\w+="[^"]*"/gi, '') // Remove event handlers
    .replace(/javascript:/gi, ''); // Remove javascript: urls

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
 * Enhanced time redistribution helpers
 */

/**
 * Analyze time imbalance and suggest redistribution strategies
 */
export function analyzeTimeImbalance(events, targetDuration) {
  const currentTotal = calculateTotalDuration(events);
  const timeDifference = currentTotal - targetDuration;

  if (Math.abs(timeDifference) <= 1) {
    return {
      needsRedistribution: false,
      timeDifference: 0,
      severity: 'none'
    };
  }

  const severity = Math.abs(timeDifference) <= 5 ? 'minor' :
                   Math.abs(timeDifference) <= 15 ? 'moderate' : 'major';

  return {
    needsRedistribution: true,
    timeDifference,
    severity,
    recommendation: getRedistributionRecommendation(timeDifference, severity)
  };
}

/**
 * Get redistribution recommendation based on time difference
 */
function getRedistributionRecommendation(timeDifference, severity) {
  const isOvertime = timeDifference > 0;

  switch (severity) {
    case 'minor':
      return {
        strategy: 'adjacent',
        message: `${isOvertime ? 'Reduce' : 'Increase'} time in nearby events to maintain lesson flow`,
        priority: 'low'
      };
    case 'moderate':
      return {
        strategy: 'pedagogical',
        message: `Apply pedagogical priorities to ${isOvertime ? 'compress' : 'expand'} appropriate events`,
        priority: 'medium'
      };
    case 'major':
      return {
        strategy: 'comprehensive',
        message: `Significant restructuring needed - consider revising lesson scope or duration`,
        priority: 'high'
      };
    default:
      return {
        strategy: 'proportional',
        message: 'Apply balanced redistribution across all events',
        priority: 'medium'
      };
  }
}

/**
 * Format redistribution summary for user display
 */
export function formatRedistributionSummary(redistributionResult) {
  if (!redistributionResult || !redistributionResult.adjustments) {
    return 'No time adjustments were made.';
  }

  const { strategy, adjustments, timeDifference, finalDifference } = redistributionResult;
  const adjustmentCount = adjustments.length;

  if (adjustmentCount === 0) {
    return 'Time was already balanced - no adjustments needed.';
  }

  const strategyNames = {
    'adjacent': 'Adjacent Events Strategy',
    'pedagogical': 'Pedagogical Priority Strategy',
    'proportional': 'Proportional Distribution Strategy'
  };

  const strategyName = strategyNames[strategy] || 'Smart Auto-Balance';
  const accuracy = finalDifference <= 1 ? 'perfect balance' : `±${finalDifference} minute${finalDifference !== 1 ? 's' : ''} difference`;

  return `${strategyName} applied: ${adjustmentCount} event${adjustmentCount !== 1 ? 's' : ''} adjusted, ${accuracy} achieved.`;
}

/**
 * Get event flexibility score for redistribution
 */
export function getEventFlexibility(eventNumber, lessonFocus = 'balanced') {
  const flexibilityScores = {
    theoretical: {
      1: 0.3, 2: 0.8, 3: 0.5, 4: 0.2, 5: 0.6,
      6: 0.4, 7: 0.7, 8: 0.5, 9: 0.8
    },
    practical: {
      1: 0.4, 2: 0.9, 3: 0.6, 4: 0.4, 5: 0.3,
      6: 0.2, 7: 0.3, 8: 0.4, 9: 0.7
    },
    balanced: {
      1: 0.35, 2: 0.85, 3: 0.55, 4: 0.3, 5: 0.45,
      6: 0.3, 7: 0.5, 8: 0.45, 9: 0.75
    }
  };

  return flexibilityScores[lessonFocus]?.[eventNumber] || 0.5;
}

/**
 * Validate Gagne events structure
 */
export function validateGagneEvents(events) {
  const errors = [];

  if (!Array.isArray(events)) {
    errors.push('Events must be an array');
    return { isValid: false, errors };
  }

  if (events.length !== 9) {
    errors.push(`Expected 9 events, got ${events.length}`);
  }

  events.forEach((event, index) => {
    if (!event.event_number || event.event_number !== index + 1) {
      errors.push(`Event ${index + 1} has incorrect event_number: ${event.event_number}`);
    }

    if (!event.event_name || typeof event.event_name !== 'string') {
      errors.push(`Event ${index + 1} missing or invalid event_name`);
    }

    if (!event.duration_minutes || event.duration_minutes < 1) {
      errors.push(`Event ${index + 1} has invalid duration: ${event.duration_minutes}`);
    }

    if (!Array.isArray(event.activities) || event.activities.length === 0) {
      errors.push(`Event ${index + 1} missing or empty activities array`);
    }
  });

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Calculate pedagogical balance score
 */
export function calculatePedagogicalBalance(events) {
  // Calculate time distribution across pedagogical phases
  const phases = {
    preparation: [1, 2, 3], // Gain attention, inform objectives, stimulate recall
    delivery: [4, 5],       // Present content, provide guidance
    practice: [6, 7],       // Elicit performance, provide feedback
    assessment: [8, 9]      // Assess performance, enhance retention
  };

  const totalDuration = calculateTotalDuration(events);
  const phaseDistribution = {};

  Object.entries(phases).forEach(([phase, eventNumbers]) => {
    const phaseTime = eventNumbers.reduce((sum, eventNum) => {
      const event = events.find(e => e.event_number === eventNum);
      return sum + (event ? event.duration_minutes : 0);
    }, 0);

    phaseDistribution[phase] = {
      minutes: phaseTime,
      percentage: totalDuration > 0 ? (phaseTime / totalDuration) * 100 : 0
    };
  });

  // Ideal distribution (research-based)
  const idealDistribution = {
    preparation: 20,  // 20%
    delivery: 40,     // 40%
    practice: 30,     // 30%
    assessment: 10    // 10%
  };

  // Calculate balance score (0-100, higher is better)
  let balanceScore = 100;
  Object.entries(idealDistribution).forEach(([phase, idealPercentage]) => {
    const actualPercentage = phaseDistribution[phase].percentage;
    const deviation = Math.abs(actualPercentage - idealPercentage);
    balanceScore -= deviation * 2; // Penalize deviation
  });

  return {
    score: Math.max(0, Math.round(balanceScore)),
    distribution: phaseDistribution,
    recommendations: generateBalanceRecommendations(phaseDistribution, idealDistribution)
  };
}

/**
 * Generate recommendations for improving pedagogical balance
 */
function generateBalanceRecommendations(actual, ideal) {
  const recommendations = [];

  Object.entries(ideal).forEach(([phase, idealPercentage]) => {
    const actualPercentage = actual[phase].percentage;
    const difference = actualPercentage - idealPercentage;

    if (Math.abs(difference) > 5) { // Significant deviation
      if (difference > 0) {
        recommendations.push({
          phase,
          type: 'reduce',
          message: `Consider reducing ${phase} time by ${Math.round(difference)}%`,
          severity: Math.abs(difference) > 10 ? 'high' : 'medium'
        });
      } else {
        recommendations.push({
          phase,
          type: 'increase',
          message: `Consider increasing ${phase} time by ${Math.round(Math.abs(difference))}%`,
          severity: Math.abs(difference) > 10 ? 'high' : 'medium'
        });
      }
    }
  });

  return recommendations;
}

/**
 * Enhanced lesson data validation with pedagogical insights
 */
export function validateLessonDataComprehensive(lessonData) {
  const validation = {
    isValid: true,
    errors: [],
    warnings: [],
    insights: {}
  };

  // Basic structure validation
  if (!lessonData) {
    validation.errors.push('Lesson data is missing');
    validation.isValid = false;
    return validation;
  }

  // Validate objectives
  if (!lessonData.objectives || lessonData.objectives.length === 0) {
    validation.errors.push('No learning objectives found');
    validation.isValid = false;
  }

  // Validate Gagne events
  const gagneValidation = validateGagneEvents(lessonData.gagne_events || []);
  if (!gagneValidation.isValid) {
    validation.errors.push(...gagneValidation.errors);
    validation.isValid = false;
  }

  // Calculate pedagogical insights
  if (lessonData.gagne_events) {
    validation.insights.pedagogicalBalance = calculatePedagogicalBalance(lessonData.gagne_events);

    if (validation.insights.pedagogicalBalance.score < 70) {
      validation.warnings.push('Pedagogical balance could be improved');
    }
  }

  // Time distribution analysis
  if (lessonData.gagne_events && lessonData.total_duration) {
    const timeAnalysis = analyzeTimeImbalance(lessonData.gagne_events, lessonData.total_duration);
    validation.insights.timeBalance = timeAnalysis;

    if (timeAnalysis.needsRedistribution && timeAnalysis.severity !== 'minor') {
      validation.warnings.push(`Time imbalance detected: ${timeAnalysis.recommendation.message}`);
    }
  }

  return validation;
}