import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Clock, Target, Users } from 'lucide-react';

import Input from '../ui/Input';
import Select from '../ui/Select';
import Textarea from '../ui/Textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import BloomsTaxonomySelector from './BloomsTaxonomySelector';
import { GRADE_LEVELS } from '../../utils/constants';

const LessonInfoForm = ({ formData, errors, onChange }) => {
  const gradeOptions = GRADE_LEVELS.map(level => ({
    value: level.value,
    label: level.label
  }));

  return (
    <div className="space-y-8">
      {/* Basic Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-primary-600" />
              Basic Lesson Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Input
                label="Course Title"
                placeholder="e.g., Introduction to Psychology"
                value={formData.courseTitle}
                onChange={(e) => onChange('courseTitle', e.target.value)}
                error={errors.courseTitle}
                icon={<BookOpen className="w-4 h-4" />}
              />

              <Input
                label="Lesson Topic"
                placeholder="e.g., Cognitive Development Theories"
                value={formData.lessonTopic}
                onChange={(e) => onChange('lessonTopic', e.target.value)}
                error={errors.lessonTopic}
                icon={<Target className="w-4 h-4" />}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Select
                label="Grade Level"
                placeholder="Select grade level..."
                options={gradeOptions}
                value={formData.gradeLevel}
                onChange={(e) => onChange('gradeLevel', e.target.value)}
                error={errors.gradeLevel}
              />

              <Input
                label="Duration (minutes)"
                type="number"
                placeholder="e.g., 90"
                min="5"
                max="480"
                value={formData.duration}
                onChange={(e) => onChange('duration', e.target.value)}
                error={errors.duration}
                icon={<Clock className="w-4 h-4" />}
                helper="Enter lesson duration in minutes (5-480)"
              />
            </div>

            <Textarea
              label="Preliminary Learning Objectives"
              placeholder="Describe what you want students to learn in this lesson..."
              rows={4}
              value={formData.preliminaryObjectives}
              onChange={(e) => onChange('preliminaryObjectives', e.target.value)}
              error={errors.preliminaryObjectives}
              helper="Provide a brief description of your learning goals for this lesson"
            />
          </CardContent>
        </Card>
      </motion.div>

      {/* Bloom's Taxonomy Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-primary-600" />
              Bloom's Taxonomy Levels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <BloomsTaxonomySelector
              selectedLevels={formData.selectedBloomLevels}
              onChange={(levels) => onChange('selectedBloomLevels', levels)}
              error={errors.selectedBloomLevels}
            />
          </CardContent>
        </Card>
      </motion.div>

      {/* Additional Requirements */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-primary-600" />
              Additional Requirements (Optional)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              label="Special Requirements or Considerations"
              placeholder="e.g., Include group activities, focus on practical applications, accommodate different learning styles..."
              rows={3}
              value={formData.additionalRequirements}
              onChange={(e) => onChange('additionalRequirements', e.target.value)}
              helper="Any specific requirements, teaching methods, or considerations for this lesson"
            />
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default LessonInfoForm;