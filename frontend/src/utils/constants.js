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
    PDF_EXPORTED: 'PDF exported successfully!',
    DATA_SAVED: 'Data saved locally!'
  },
  ERROR: {
    GENERATION_FAILED: 'Failed to generate lesson plan. Please try again.',
    REFINEMENT_FAILED: 'Failed to refine content. Please try again.',
    EXPORT_FAILED: 'Failed to export PDF. Please try again.',
    INVALID_INPUT: 'Please check your input and try again.',
    NETWORK_ERROR: 'Network error. Please check your connection.'
  },
  INFO: {
    GENERATING: 'Generating your lesson plan...',
    REFINING: 'Refining content...',
    EXPORTING: 'Preparing your PDF...'
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
    required: 'Please select at least one Bloom\'s taxonomy level'
  }
};