import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, ArrowRight, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';

import { Card, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import StepIndicator from '../components/wizard/StepIndicator';
import LessonInfoForm from '../components/forms/LessonInfoForm';
import { useApi } from '../hooks/useApi';
import { useLessonDraft } from '../hooks/useLocalStorage';
import { formatLessonRequest, validateLessonForm } from '../utils/helpers';
import { WIZARD_STEPS, TOAST_MESSAGES } from '../utils/constants';

const LessonWizard = () => {
  const navigate = useNavigate();
  const { generateLesson, loading, error } = useApi();
  const { saveDraft, clearDraft } = useLessonDraft();

  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    courseTitle: '',
    lessonTopic: '',
    gradeLevel: '',
    duration: '',
    preliminaryObjectives: '',
    selectedBloomLevels: [],
    additionalRequirements: ''
  });
  const [formErrors, setFormErrors] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (error) {
      toast.error(error);
    }
  }, [error]);

  const handleFormChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear error for this field if it exists
    if (formErrors[field]) {
      setFormErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateCurrentStep = () => {
    if (currentStep === 0) {
      const validation = validateLessonForm(formData);
      setFormErrors(validation.errors);
      return validation.isValid;
    }
    return true;
  };

  const handleNext = async () => {
    if (!validateCurrentStep()) {
      toast.error('Please fix the errors before continuing');
      return;
    }

    if (currentStep === 0) {
      // Move to generation step
      setCurrentStep(1);
      await handleGenerate();
    } else if (currentStep < WIZARD_STEPS.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);

    try {
      const lessonRequest = formatLessonRequest(formData);
      const lessonData = await generateLesson(lessonRequest);

      // Save to local storage and navigate to results
      saveDraft(lessonData);
      toast.success(TOAST_MESSAGES.SUCCESS.LESSON_GENERATED);

      setTimeout(() => {
        navigate('/results', { state: { lessonData } });
      }, 1000);

    } catch (err) {
      toast.error(TOAST_MESSAGES.ERROR.GENERATION_FAILED);
      setCurrentStep(0); // Go back to form
    } finally {
      setIsGenerating(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <LessonInfoForm
            formData={formData}
            errors={formErrors}
            onChange={handleFormChange}
          />
        );

      case 1:
        return (
          <div className="text-center py-12">
            <motion.div
              className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center"
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="w-10 h-10 text-white" />
            </motion.div>

            <h3 className="text-2xl font-semibold text-gray-900 mb-4">
              Generating Your Lesson Plan
            </h3>

            <p className="text-gray-600 mb-8 max-w-md mx-auto">
              Our AI is creating detailed learning objectives, lesson plans, and Gagne's nine events structure based on your requirements.
            </p>

            <div className="space-y-3 text-sm text-gray-500">
              <div className="flex items-center justify-center gap-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
                <span>Analyzing Bloom's taxonomy levels</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse delay-150" />
                <span>Creating learning objectives</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse delay-300" />
                <span>Structuring Gagne's nine events</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse delay-500" />
                <span>Finalizing lesson plan</span>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Create Your Lesson Plan
          </h1>
          <p className="text-lg text-gray-600">
            Follow the steps below to generate a comprehensive lesson plan
          </p>
        </div>

        {/* Step Indicator */}
        <div className="mb-8">
          <StepIndicator steps={WIZARD_STEPS} currentStep={currentStep} />
        </div>

        {/* Main Content */}
        <Card>
          <CardContent className="p-8">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {renderStepContent()}
              </motion.div>
            </AnimatePresence>
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between items-center mt-8">
          <Button
            variant="ghost"
            onClick={handlePrevious}
            disabled={currentStep === 0 || isGenerating}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Previous
          </Button>

          <div className="flex items-center gap-3">
            {currentStep === 0 && (
              <Button
                onClick={handleNext}
                disabled={loading || isGenerating}
                loading={loading || isGenerating}
                className="flex items-center gap-2"
              >
                Generate Lesson Plan
                <ArrowRight className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>

        {/* Progress indicator for generation */}
        {isGenerating && (
          <motion.div
            className="mt-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: '100%' }}
                transition={{ duration: 8, ease: "easeInOut" }}
              />
            </div>
            <p className="text-center text-sm text-gray-500 mt-2">
              This may take a few moments...
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default LessonWizard;