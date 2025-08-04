import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Edit3, Accessibility, Eye, Users, Brain } from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import Button from '../ui/Button';
import Select from '../ui/Select';
import Textarea from '../ui/Textarea';

const ContentRefinementModal = ({ slide, onRefine, onClose }) => {
  const [refinementType, setRefinementType] = useState('content');
  const [instructions, setInstructions] = useState('');
  const [isRefining, setIsRefining] = useState(false);

  const refinementTypes = [
    {
      value: 'content',
      label: 'Content',
      description: 'Improve the main content and messaging',
      icon: <Edit3 className="w-4 h-4" />
    },
    {
      value: 'accessibility',
      label: 'Accessibility',
      description: 'Enhance accessibility features',
      icon: <Accessibility className="w-4 h-4" />
    },
    {
      value: 'modality',
      label: 'Learning Modality',
      description: 'Adjust visual, auditory, or kinesthetic elements',
      icon: <Eye className="w-4 h-4" />
    },
    {
      value: 'udl_guidelines',
      label: 'UDL Guidelines',
      description: 'Apply specific UDL principles',
      icon: <Brain className="w-4 h-4" />
    }
  ];

  const udlGuidelines = [
    {
      value: 'representation',
      label: 'Multiple Means of Representation',
      description: 'Provide information in multiple formats'
    },
    {
      value: 'action_expression',
      label: 'Multiple Means of Action & Expression',
      description: 'Offer various ways for students to respond'
    },
    {
      value: 'engagement',
      label: 'Multiple Means of Engagement',
      description: 'Motivate learners through different approaches'
    }
  ];

  const handleRefine = async () => {
    if (!instructions.trim()) return;

    setIsRefining(true);
    try {
      await onRefine(slide.slide_number, refinementType, instructions);
      onClose();
    } catch (error) {
      console.error('Refinement failed:', error);
    } finally {
      setIsRefining(false);
    }
  };

  const getRefinementPlaceholder = () => {
    switch (refinementType) {
      case 'content':
        return 'Describe how you want to improve the slide content...';
      case 'accessibility':
        return 'Describe accessibility improvements needed...';
      case 'modality':
        return 'Describe changes to learning modalities (visual, auditory, kinesthetic)...';
      case 'udl_guidelines':
        return 'Describe specific UDL guidelines to apply...';
      default:
        return 'Describe your refinement requirements...';
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Edit3 className="w-5 h-5 text-primary-600" />
                  Refine Slide Content
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  className="p-1"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Slide Information */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2">Slide {slide.slide_number}: {slide.title}</h3>
                <p className="text-sm text-gray-600 mb-3">{slide.main_content}</p>
                <div className="flex flex-wrap gap-2">
                  {slide.udl_guidelines.map((guideline, idx) => (
                    <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      {guideline}
                    </span>
                  ))}
                </div>
              </div>

              {/* Refinement Type Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Refinement Type
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {refinementTypes.map((type) => (
                    <div
                      key={type.value}
                      className={`p-3 border rounded-lg cursor-pointer transition-all ${
                        refinementType === type.value
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-primary-300'
                      }`}
                      onClick={() => setRefinementType(type.value)}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        {type.icon}
                        <span className="font-medium text-sm">{type.label}</span>
                      </div>
                      <p className="text-xs text-gray-600">{type.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* UDL Guidelines Selection (if applicable) */}
              {refinementType === 'udl_guidelines' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    UDL Guidelines to Apply
                  </label>
                  <div className="space-y-2">
                    {udlGuidelines.map((guideline) => (
                      <div key={guideline.value} className="flex items-start gap-2">
                        <input
                          type="checkbox"
                          id={guideline.value}
                          className="mt-1"
                        />
                        <label htmlFor={guideline.value} className="text-sm">
                          <div className="font-medium">{guideline.label}</div>
                          <div className="text-gray-600">{guideline.description}</div>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Refinement Instructions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Refinement Instructions
                </label>
                <Textarea
                  placeholder={getRefinementPlaceholder()}
                  rows={4}
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  className="w-full"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Be specific about what changes you want to make to improve the slide.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={onClose}
                  disabled={isRefining}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleRefine}
                  disabled={!instructions.trim() || isRefining}
                  loading={isRefining}
                >
                  {isRefining ? 'Refining...' : 'Apply Refinement'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ContentRefinementModal; 