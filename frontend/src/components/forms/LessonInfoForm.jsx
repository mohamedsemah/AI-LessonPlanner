import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Target, Users } from 'lucide-react';

import Input from '../ui/Input';
import Select from '../ui/Select';
import Textarea from '../ui/Textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import FileUploadSection from './FileUploadSection';
import { GRADE_LEVELS } from '../../utils/constants';

const LessonInfoForm = ({ formData, errors, onChange }) => {
  const gradeOptions = GRADE_LEVELS.map(level => ({
    value: level.value,
    label: level.label
  }));

  return (
    <div className="space-y-6">
      {/* Basic Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              Basic Lesson Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Course Title"
                value={formData.courseTitle}
                onChange={(e) => onChange('courseTitle', e.target.value)}
                error={errors.courseTitle}
                placeholder="e.g., Introduction to Computer Science"
              />
              <Input
                label="Lesson Topic"
                value={formData.lessonTopic}
                onChange={(e) => onChange('lessonTopic', e.target.value)}
                error={errors.lessonTopic}
                placeholder="e.g., Variables and Data Types"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Select
                label="Grade Level"
                value={formData.gradeLevel}
                onChange={(e) => onChange('gradeLevel', e.target.value)}
                options={gradeOptions}
                error={errors.gradeLevel}
                placeholder="Select grade level"
              />
              <Input
                label="Duration (minutes)"
                value={formData.duration}
                onChange={(e) => onChange('duration', e.target.value)}
                error={errors.duration}
                placeholder="e.g., 45"
                type="number"
              />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* File Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5" />
              Upload Syllabus and Relevant Materials
            </CardTitle>
          </CardHeader>
          <CardContent>
            <FileUploadSection
              uploadedFiles={formData.uploadedFiles}
              onFilesChange={(files) => onChange('uploadedFiles', files)}
              error={errors.uploadedFiles}
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
              <Users className="w-5 h-5" />
              Additional Requirements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              label="Any specific requirements or preferences for this lesson?"
              value={formData.additionalRequirements}
              onChange={(e) => onChange('additionalRequirements', e.target.value)}
              placeholder="e.g., Include hands-on activities, focus on visual learners, incorporate technology..."
              rows={3}
            />
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default LessonInfoForm;