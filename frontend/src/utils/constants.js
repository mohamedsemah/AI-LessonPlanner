export const GRADE_LEVELS = [
  { value: 'freshman', label: 'Freshman' },
  { value: 'sophomore', label: 'Sophomore' },
  { value: 'junior', label: 'Junior' },
  { value: 'senior', label: 'Senior' },
  { value: 'masters', label: 'Masters' },
  { value: 'postgrad', label: 'Postgraduate' }
];

export const BLOOM_LEVELS = [
  {
    value: 'remember',
    label: 'Remember',
    description: 'Recall facts, basic concepts, and answers',
    color: 'bloom-remember',
    verbs: ['define', 'list', 'recall', 'identify', 'describe', 'retrieve']
  },
  {
    value: 'understand',
    label: 'Understand',
    description: 'Explain ideas or concepts and interpret information',
    color: 'bloom-understand',
    verbs: ['explain', 'interpret', 'summarize', 'classify', 'compare', 'discuss']
  },
  {
    value: 'apply',
    label: 'Apply',
    description: 'Use information in new situations and solve problems',
    color: 'bloom-apply',
    verbs: ['use', 'demonstrate', 'implement', 'solve', 'execute', 'carry out']
  },
  {
    value: 'analyze',
    label: 'Analyze',
    description: 'Draw connections and distinguish between different parts',
    color: 'bloom-analyze',
    verbs: ['analyze', 'break down', 'examine', 'compare', 'contrast', 'investigate']
  },
  {
    value: 'evaluate',
    label: 'Evaluate',
    description: 'Justify decisions and critique work or ideas',
    color: 'bloom-evaluate',
    verbs: ['evaluate', 'critique', 'judge', 'assess', 'defend', 'justify']
  },
  {
    value: 'create',
    label: 'Create',
    description: 'Produce new or original work and combine ideas',
    color: 'bloom-create',
    verbs: ['create', 'design', 'construct', 'develop', 'formulate', 'produce']
  }
];

export const GAGNE_EVENTS = [
  {
    number: 1,
    name: 'Gain Attention',
    description: 'Capture student interest and focus attention on the lesson',
    icon: '👁️',
    strategies: ['Ask thought-provoking questions', 'Share interesting facts', 'Use multimedia', 'Tell a story']
  },
  {
    number: 2,
    name: 'Inform Learners of Objectives',
    description: 'Share learning goals and explain their relevance',
    icon: '🎯',
    strategies: ['Present clear objectives', 'Explain benefits', 'Connect to student goals', 'Provide learning roadmap']
  },
  {
    number: 3,
    name: 'Stimulate Recall of Prior Learning',
    description: 'Connect new content to existing knowledge',
    icon: '🧠',
    strategies: ['Review prerequisites', 'Ask about experiences', 'Use analogies', 'Activate schema']
  },
  {
    number: 4,
    name: 'Present the Content',
    description: 'Deliver new information and concepts',
    icon: '📚',
    strategies: ['Structured presentation', 'Multiple examples', 'Visual aids', 'Clear organization']
  },
  {
    number: 5,
    name: 'Provide Learning Guidance',
    description: 'Guide students through the learning process',
    icon: '🧭',
    strategies: ['Provide hints', 'Model procedures', 'Use mnemonics', 'Offer coaching']
  },
  {
    number: 6,
    name: 'Elicit Performance',
    description: 'Have students practice and demonstrate learning',
    icon: '🎭',
    strategies: ['Practice exercises', 'Problem solving', 'Simulations', 'Hands-on activities']
  },
  {
    number: 7,
    name: 'Provide Feedback',
    description: 'Give informative feedback on performance',
    icon: '💬',
    strategies: ['Immediate feedback', 'Corrective guidance', 'Positive reinforcement', 'Specific comments']
  },
  {
    number: 8,
    name: 'Assess Performance',
    description: 'Evaluate student learning and understanding',
    icon: '📊',
    strategies: ['Formal tests', 'Observations', 'Portfolios', 'Self-assessment']
  },
  {
    number: 9,
    name: 'Enhance Retention and Transfer',
    description: 'Promote long-term retention and application',
    icon: '🚀',
    strategies: ['Real-world applications', 'Summary activities', 'Reflection', 'Future connections']
  }
];

export const WIZARD_STEPS = [
  {
    id: 'info',
    title: 'Lesson Information',
    description: 'Basic lesson details and Bloom\'s taxonomy selection',
    icon: '📝'
  },
  {
    id: 'generate',
    title: 'Generate Content',
    description: 'AI generates your lesson plan and objectives',
    icon: '⚡'
  },
  {
    id: 'review',
    title: 'Review & Edit',
    description: 'Review and refine the generated content',
    icon: '✏️'
  },
  {
    id: 'export',
    title: 'Export & Save',
    description: 'Download your completed lesson plan',
    icon: '💾'
  }
];

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const TOAST_MESSAGES = {
  SUCCESS: {
    LESSON_GENERATED: 'Lesson plan generated successfully!',
    CONTENT_REFINED: 'Content refined successfully!',
    DURATION_CHANGED: 'Lesson duration updated successfully!',
    OBJECTIVES_OPTIMIZED: 'Learning objectives optimized!',
    PDF_EXPORTED: 'PDF exported successfully!',
    DATA_SAVED: 'Data saved locally!',
    BLOOM_LEVELS_UPDATED: 'Bloom\'s taxonomy levels updated!'
  },
  ERROR: {
    GENERATION_FAILED: 'Failed to generate lesson plan. Please try again.',
    REFINEMENT_FAILED: 'Failed to refine content. Please try again.',
    DURATION_CHANGE_FAILED: 'Failed to update lesson duration. Please try again.',
    OBJECTIVES_FAILED: 'Failed to optimize objectives. Please try again.',
    EXPORT_FAILED: 'Failed to export PDF. Please try again.',
    INVALID_INPUT: 'Please check your input and try again.',
    NETWORK_ERROR: 'Network error. Please check your connection.',
    INVALID_DURATION: 'Duration must be between 5 and 480 minutes.',
    MISSING_OBJECTIVES: 'Learning objectives are missing or invalid.',
    INVALID_BLOOM_LEVELS: 'Invalid Bloom\'s taxonomy levels detected.',
    DATA_CORRUPTION: 'Lesson data appears to be corrupted. Please regenerate.'
  },
  INFO: {
    GENERATING: 'Generating your lesson plan...',
    REFINING: 'Refining content...',
    CHANGING_DURATION: 'Updating lesson duration and recalculating objectives...',
    OPTIMIZING_OBJECTIVES: 'Optimizing learning objectives...',
    EXPORTING: 'Preparing your PDF...',
    VALIDATING: 'Validating lesson structure...',
    PROCESSING: 'Processing your request...'
  },
  WARNING: {
    UNSAVED_CHANGES: 'You have unsaved changes. Do you want to continue?',
    SUBOPTIMAL_OBJECTIVES: 'Your current objective count may not be optimal for this duration.',
    MISSING_BLOOM_LEVELS: 'Some Bloom\'s taxonomy levels are not represented in your objectives.',
    LONG_DURATION: 'Lessons longer than 3 hours may be challenging for student attention.',
    SHORT_DURATION: 'Very short lessons may not allow sufficient depth of learning.'
  }
};

export const VALIDATION_RULES = {
  COURSE_TITLE: {
    required: 'Course title is required',
    minLength: { value: 2, message: 'Course title must be at least 2 characters' },
    maxLength: { value: 200, message: 'Course title must be less than 200 characters' }
  },
  LESSON_TOPIC: {
    required: 'Lesson topic is required',
    minLength: { value: 2, message: 'Lesson topic must be at least 2 characters' },
    maxLength: { value: 200, message: 'Lesson topic must be less than 200 characters' }
  },
  DURATION: {
    required: 'Duration is required',
    min: { value: 5, message: 'Duration must be at least 5 minutes' },
    max: { value: 480, message: 'Duration must be less than 8 hours' }
  },
  PRELIMINARY_OBJECTIVES: {
    required: 'Preliminary objectives are required',
    minLength: { value: 10, message: 'Please provide more detailed objectives (at least 10 characters)' },
    maxLength: { value: 1000, message: 'Objectives must be less than 1000 characters' }
  },
  BLOOM_LEVELS: {
    required: 'Please select at least one Bloom\'s taxonomy level',
    minItems: { value: 1, message: 'At least one Bloom\'s level must be selected' },
    maxItems: { value: 6, message: 'Cannot select more than 6 Bloom\'s levels' }
  }
};

// Duration-based optimization constants
export const DURATION_THRESHOLDS = {
  VERY_SHORT: 30,    // <= 30 minutes
  SHORT: 60,         // <= 60 minutes
  STANDARD: 90,      // <= 90 minutes
  LONG: 120,         // <= 120 minutes
  VERY_LONG: 480     // <= 480 minutes (8 hours)
};

// Optimal objectives count based on cognitive load theory
export const OPTIMAL_OBJECTIVES = {
  [DURATION_THRESHOLDS.VERY_SHORT]: 2,
  [DURATION_THRESHOLDS.SHORT]: 3,
  [DURATION_THRESHOLDS.STANDARD]: 4,
  [DURATION_THRESHOLDS.LONG]: 5,
  [DURATION_THRESHOLDS.VERY_LONG]: 6
};

// Bloom's taxonomy complexity weights for calculating cognitive load
export const BLOOM_COMPLEXITY_WEIGHTS = {
  remember: 0.1,
  understand: 0.2,
  apply: 0.4,
  analyze: 0.6,
  evaluate: 0.8,
  create: 1.0
};

// Grade level adjustments for objective count
export const GRADE_LEVEL_ADJUSTMENTS = {
  freshman: -1,    // Need more time for foundational skills
  sophomore: 0,    // Standard
  junior: 0,       // Standard
  senior: 1,       // Can handle slightly more complexity
  masters: 1,      // Graduate-level cognitive capacity
  postgrad: 1      // Advanced analytical skills
};

// Gagne event time distribution patterns
export const GAGNE_TIME_DISTRIBUTIONS = {
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

// Lesson focus classification
export const LESSON_FOCUS_TYPES = {
  THEORETICAL: 'theoretical',
  PRACTICAL: 'practical',
  BALANCED: 'balanced'
};

// Classification of Bloom's levels by focus type
export const BLOOM_LEVEL_CLASSIFICATION = {
  theoretical: ['remember', 'understand'],
  practical: ['apply', 'analyze', 'evaluate', 'create']
};

// Local storage keys
export const STORAGE_KEYS = {
  LESSON_DRAFT: 'lessonDraft',
  FORM_DATA: 'formData',
  USER_PREFERENCES: 'userPreferences',
  RECENT_LESSONS: 'recentLessons'
};

// API configuration
export const API_CONFIG = {
  TIMEOUT: 120000,  // 2 minutes for AI generation
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  PDF_TIMEOUT: 60000  // 1 minute for PDF generation
};

// File export settings
export const EXPORT_SETTINGS = {
  PDF: {
    DEFAULT_FILENAME: 'lesson_plan.pdf',
    INCLUDE_COVER_PAGE: true,
    INCLUDE_APPENDICES: true,
    MAX_FILE_SIZE: 10 * 1024 * 1024  // 10MB
  },
  JSON: {
    DEFAULT_FILENAME: 'lesson_data.json',
    INDENT_SPACES: 2
  }
};

// UI configuration
export const UI_CONFIG = {
  ANIMATION_DURATION: 300,
  DEBOUNCE_DELAY: 500,
  TOAST_DURATION: 4000,
  MODAL_TRANSITION_DURATION: 200,
  LOADING_SPINNER_DELAY: 200
};

// Feature flags
export const FEATURE_FLAGS = {
  ENABLE_DRAFT_AUTOSAVE: true,
  ENABLE_OFFLINE_MODE: false,
  ENABLE_ADVANCED_EXPORT: true,
  ENABLE_COLLABORATION: false,
  ENABLE_ANALYTICS: false
};

// Error categories for enhanced error handling
export const ERROR_CATEGORIES = {
  NETWORK: 'network',
  VALIDATION: 'validation',
  API: 'api',
  STORAGE: 'storage',
  PARSING: 'parsing',
  TIMEOUT: 'timeout',
  UNKNOWN: 'unknown'
};

// Progress tracking for multi-step operations
export const PROGRESS_STEPS = {
  DURATION_CHANGE: {
    VALIDATING: 10,
    CALCULATING: 20,
    GENERATING_OBJECTIVES: 40,
    UPDATING_EVENTS: 60,
    PROCESSING_RESPONSE: 80,
    FINALIZING: 100
  },
  LESSON_GENERATION: {
    VALIDATING_INPUT: 10,
    GENERATING_OBJECTIVES: 30,
    GENERATING_LESSON_PLAN: 50,
    GENERATING_GAGNE_EVENTS: 70,
    PROCESSING_RESULTS: 90,
    COMPLETE: 100
  }
};