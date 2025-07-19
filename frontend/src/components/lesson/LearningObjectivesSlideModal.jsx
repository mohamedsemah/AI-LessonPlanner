import React from 'react';
import { motion } from 'framer-motion';
import { X, Target, BookOpen, Clock, Users } from 'lucide-react';
import { Modal, ModalBody } from '../ui/Modal';
import Button from '../ui/Button';
import { formatDuration, formatGradeLevel, capitalize } from '../../utils/helpers';

const LearningObjectivesSlideModal = ({ isOpen, onClose, lessonData }) => {
  if (!lessonData) return null;

  const { lesson_info, objectives, total_duration } = lessonData;

  // Group objectives by Bloom's level for better organization
  const objectivesByLevel = objectives?.reduce((groups, obj) => {
    const level = obj.bloom_level;
    if (!groups[level]) groups[level] = [];
    groups[level].push(obj);
    return groups;
  }, {}) || {};

  // Calculate total number of objectives
  const totalObjectives = objectives?.length || 0;

  // Dynamic sizing based on number of objectives - More aggressive compression
  const getDynamicSizes = (count) => {
    if (count <= 3) {
      return {
        titleSize: 'text-base',
        objectiveSpacing: 'space-y-2',
        levelSpacing: 'space-y-1',
        objectivePadding: 'p-2',
        objectiveTextSize: 'text-sm',
        conditionTextSize: 'text-xs',
        badgeSize: 'w-5 h-5 text-xs',
        levelHeaderSize: 'text-xs',
        containerSpacing: 'mb-3'
      };
    } else if (count <= 6) {
      return {
        titleSize: 'text-sm',
        objectiveSpacing: 'space-y-1',
        levelSpacing: 'space-y-0.5',
        objectivePadding: 'p-1.5',
        objectiveTextSize: 'text-xs',
        conditionTextSize: 'text-xs',
        badgeSize: 'w-4 h-4 text-xs',
        levelHeaderSize: 'text-xs',
        containerSpacing: 'mb-2'
      };
    } else if (count <= 8) {
      return {
        titleSize: 'text-xs',
        objectiveSpacing: 'space-y-0.5',
        levelSpacing: 'space-y-0.5',
        objectivePadding: 'p-1',
        objectiveTextSize: 'text-xs',
        conditionTextSize: 'text-xs',
        badgeSize: 'w-4 h-4 text-xs',
        levelHeaderSize: 'text-xs',
        containerSpacing: 'mb-1'
      };
    } else {
      return {
        titleSize: 'text-xs',
        objectiveSpacing: 'space-y-0.5',
        levelSpacing: 'space-y-0',
        objectivePadding: 'p-1',
        objectiveTextSize: 'text-xs',
        conditionTextSize: 'text-xs',
        badgeSize: 'w-3 h-3 text-xs',
        levelHeaderSize: 'text-xs',
        containerSpacing: 'mb-1'
      };
    }
  };

  const sizes = getDynamicSizes(totalObjectives);

  // Get Bloom's level colors
  const getBloomColor = (level) => {
    const colorMap = {
      remember: 'bg-red-100 text-red-800 border-red-200',
      understand: 'bg-orange-100 text-orange-800 border-orange-200',
      apply: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      analyze: 'bg-green-100 text-green-800 border-green-200',
      evaluate: 'bg-blue-100 text-blue-800 border-blue-200',
      create: 'bg-purple-100 text-purple-800 border-purple-200'
    };
    return colorMap[level] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" className="max-w-5xl">
      <ModalBody className="p-0">
        {/* Modal Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Learning Objectives Slide Preview</h2>
              <p className="text-sm text-gray-600">Preview how this slide will appear to students</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Slide Preview Container */}
        <div className="p-2 bg-gradient-to-br from-gray-100 to-gray-200">
          <motion.div
            className="bg-white rounded-lg shadow-lg mx-auto"
            style={{
              width: '100%',
              maxWidth: '1000px',
              height: '85vh', // Increased to 85vh
              minHeight: '750px' // Increased minimum height
            }}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            {/* Slide Content */}
            <div className="h-full flex flex-col p-4 relative overflow-hidden">
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-5">
                <svg className="w-full h-full" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                      <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#3B82F6" strokeWidth="0.5"/>
                    </pattern>
                  </defs>
                  <rect width="100" height="100" fill="url(#grid)" />
                </svg>
              </div>

              {/* Simplified Header Section - Only Title */}
              <div className="relative z-10 text-center mb-4">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-full flex items-center justify-center shadow-lg">
                    <Target className="w-5 h-5 text-white" />
                  </div>
                  <h1 className="text-xl font-bold text-gray-900">Learning Objectives</h1>
                </div>
              </div>

              {/* Learning Objectives Content */}
              <div className="relative z-10 flex-1 flex flex-col">
                <div className="text-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-800">By the end of this lesson, you will be able to:</h3>
                </div>

                {/* Always use single column layout for better readability */}
                <div className="space-y-4 flex-1">
                  {Object.entries(objectivesByLevel).map(([level, levelObjectives], levelIndex) => (
                    <motion.div
                      key={level}
                      className="space-y-3"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: levelIndex * 0.1 }}
                    >
                      {/* Bloom's Level Header */}
                      <div className="flex items-center gap-3">
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getBloomColor(level)}`}>
                          {capitalize(level)}
                        </span>
                        <div className="flex-1 h-px bg-gray-200"></div>
                      </div>

                      {/* Level Objectives */}
                      <div className="space-y-2">
                        {levelObjectives.map((objective, index) => (
                          <div
                            key={index}
                            className="flex items-start gap-3 bg-gray-50 p-3 rounded-lg border border-gray-200"
                          >
                            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold ${getBloomColor(level)} flex-shrink-0`}>
                              {index + 1}
                            </div>
                            <div className="flex-1">
                              <p className="text-sm text-gray-800 font-medium leading-relaxed">
                                {objective.objective}
                              </p>
                              {objective.condition && (
                                <p className="text-xs text-gray-600 mt-1">
                                  <span className="font-medium">Condition:</span> {objective.condition}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Footer */}
              <div className="relative z-10 text-center mt-4 pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500 italic">
                  These objectives are designed using Bloom's Taxonomy to ensure comprehensive learning
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              This preview shows how the learning objectives slide will appear during instruction
            </div>
            <div className="flex gap-3">
              <Button variant="outline" onClick={onClose}>
                Close Preview
              </Button>
              <Button onClick={() => {
                // Future enhancement: Add slide export functionality
                alert('Slide export functionality coming soon!');
              }}>
                Export Slide
              </Button>
            </div>
          </div>
        </div>
      </ModalBody>
    </Modal>
  );
};

export default LearningObjectivesSlideModal;