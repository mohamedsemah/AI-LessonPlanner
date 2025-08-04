import React from 'react';
import { motion } from 'framer-motion';
import { Settings, Accessibility, Users, Monitor } from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import Select from '../ui/Select';
import Checkbox from '../ui/Checkbox';
import Textarea from '../ui/Textarea';

const UDLPreferencesForm = ({ preferences, onChange }) => {
  const presentationStyles = [
    { value: 'balanced', label: 'Balanced' },
    { value: 'detailed', label: 'Detailed' },
    { value: 'concise', label: 'Concise' }
  ];

  const accessibilityLevels = [
    { value: 'standard', label: 'Standard' },
    { value: 'enhanced', label: 'Enhanced' }
  ];

  const slideDurations = [
    { value: 'balanced', label: 'Balanced' },
    { value: 'detailed', label: 'More Slides' },
    { value: 'concise', label: 'Fewer Slides' }
  ];

  const targetAudienceOptions = [
    { value: 'visual_learners', label: 'Visual Learners' },
    { value: 'auditory_learners', label: 'Auditory Learners' },
    { value: 'kinesthetic_learners', label: 'Kinesthetic Learners' },
    { value: 'students_with_disabilities', label: 'Students with Disabilities' },
    { value: 'english_language_learners', label: 'English Language Learners' },
    { value: 'gifted_students', label: 'Gifted Students' }
  ];

  const handlePreferenceChange = (field, value) => {
    onChange({
      ...preferences,
      [field]: value
    });
  };

  const handleAudienceChange = (value, checked) => {
    const currentAudience = preferences.targetAudience || [];
    const newAudience = checked
      ? [...currentAudience, value]
      : currentAudience.filter(item => item !== value);
    
    handlePreferenceChange('targetAudience', newAudience);
  };

  return (
    <div className="space-y-6">
      {/* Presentation Style */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Settings className="w-5 h-5 text-primary-600" />
              Presentation Style
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select
              label="Content Detail Level"
              options={presentationStyles}
              value={preferences.presentationStyle}
              onChange={(e) => handlePreferenceChange('presentationStyle', e.target.value)}
              helper="Choose how detailed your presentation content should be"
            />
            
            <Select
              label="Slide Duration Preference"
              options={slideDurations}
              value={preferences.slideDuration}
              onChange={(e) => handlePreferenceChange('slideDuration', e.target.value)}
              helper="Control the number of slides generated per time period"
            />
          </CardContent>
        </Card>
      </motion.div>

      {/* Accessibility Settings */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Accessibility className="w-5 h-5 text-primary-600" />
              Accessibility Features
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select
              label="Accessibility Level"
              options={accessibilityLevels}
              value={preferences.accessibilityLevel}
              onChange={(e) => handlePreferenceChange('accessibilityLevel', e.target.value)}
              helper="Standard includes basic accessibility, Enhanced includes advanced features"
            />
            
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Included Features:</h4>
              <div className="grid grid-cols-1 gap-2 text-sm">
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={preferences.accessibilityLevel === 'enhanced'}
                    disabled
                    readOnly
                  />
                  <span>Alt text for all images</span>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={preferences.accessibilityLevel === 'enhanced'}
                    disabled
                    readOnly
                  />
                  <span>Keyboard navigation support</span>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={preferences.accessibilityLevel === 'enhanced'}
                    disabled
                    readOnly
                  />
                  <span>Screen reader compatibility</span>
                </div>
                {preferences.accessibilityLevel === 'enhanced' && (
                  <>
                    <div className="flex items-center gap-2">
                      <Checkbox checked disabled readOnly />
                      <span>Audio descriptions</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox checked disabled readOnly />
                      <span>High contrast mode</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Checkbox checked disabled readOnly />
                      <span>Multiple language support</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Target Audience */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Users className="w-5 h-5 text-primary-600" />
              Target Audience
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-gray-600 mb-4">
              Select the types of learners you want to accommodate in your presentation
            </p>
            
            <div className="grid grid-cols-1 gap-3">
              {targetAudienceOptions.map((option) => (
                <div key={option.value} className="flex items-center gap-3">
                  <Checkbox
                    checked={preferences.targetAudience?.includes(option.value) || false}
                    onChange={(e) => handleAudienceChange(option.value, e.target.checked)}
                  />
                  <span className="text-sm">{option.label}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Technology Constraints */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Monitor className="w-5 h-5 text-primary-600" />
              Technology Constraints
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              label="Technology Limitations (Optional)"
              placeholder="e.g., No internet access, limited projector capabilities, specific software requirements..."
              rows={3}
              value={preferences.technologyConstraints}
              onChange={(e) => handlePreferenceChange('technologyConstraints', e.target.value)}
              helper="Describe any technology limitations that should be considered"
            />
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default UDLPreferencesForm; 