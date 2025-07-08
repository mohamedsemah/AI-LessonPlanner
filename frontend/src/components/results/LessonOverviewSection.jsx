import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Edit3, Clock, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { formatDuration, capitalize, cleanOverviewText, formatGradeLevel } from '../../utils/helpers';

const LessonOverviewSection = ({
  lessonData,
  setEditingSection,
  setEditContent,
  setRefinementInstructions,
  setShowDurationModal,
  setNewDuration
}) => {
  const calculateOptimalObjectives = (duration) => {
    if (duration <= 30) return 2;
    if (duration <= 60) return 3;
    if (duration <= 90) return 4;
    if (duration <= 120) return 5;
    return 6;
  };

  const handleEditSection = (sectionType, content) => {
    setEditingSection(sectionType);
    setEditContent(JSON.stringify(content, null, 2));
    setRefinementInstructions('');
  };

  const safeObjectives = lessonData.objectives || [];
  const totalDuration = lessonData.total_duration || lessonData.lesson_info?.duration_minutes || 0;
  const optimalObjectivesForDuration = calculateOptimalObjectives(totalDuration);
  const currentObjectivesCount = safeObjectives.length;
  const bloomLevelsUsed = [...new Set(safeObjectives.map(obj => obj.bloom_level))].filter(Boolean);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-primary-600" />
            Lesson Overview
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={() => handleEditSection('lesson_plan', lessonData.lesson_plan)}>
            <Edit3 className="w-4 h-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200 relative group">
              <span className="text-sm font-medium text-blue-700">Duration</span>
              <div className="flex items-center justify-between">
                <p className="text-xl font-bold text-blue-900 mt-1">{formatDuration(totalDuration)}</p>
                <button
                  onClick={() => {
                    setNewDuration(totalDuration.toString());
                    setShowDurationModal(true);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-blue-200 rounded"
                  title="Change duration"
                >
                  <Clock className="w-4 h-4 text-blue-600" />
                </button>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
              <span className="text-sm font-medium text-green-700">Grade Level</span>
              <p className="text-xl font-bold text-green-900 mt-1">{formatGradeLevel(lessonData.lesson_info.grade_level)}</p>
            </div>

            <div className={`bg-gradient-to-br p-4 rounded-lg border relative ${
              Math.abs(currentObjectivesCount - optimalObjectivesForDuration) <= 1 
                ? 'from-green-50 to-green-100 border-green-200' 
                : 'from-yellow-50 to-yellow-100 border-yellow-200'
            }`}>
              <span className={`text-sm font-medium ${
                Math.abs(currentObjectivesCount - optimalObjectivesForDuration) <= 1 
                  ? 'text-green-700' 
                  : 'text-yellow-700'
              }`}>
                Objectives
              </span>
              <div className="flex items-center justify-between">
                <p className={`text-xl font-bold mt-1 ${
                  Math.abs(currentObjectivesCount - optimalObjectivesForDuration) <= 1 
                    ? 'text-green-900' 
                    : 'text-yellow-900'
                }`}>
                  {currentObjectivesCount}
                </p>
                {Math.abs(currentObjectivesCount - optimalObjectivesForDuration) > 1 && (
                  <div className="text-xs text-yellow-600" title={`Optimal: ${optimalObjectivesForDuration} for ${formatDuration(totalDuration)}`}>
                    <Target className="w-4 h-4" />
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="text-sm font-medium text-gray-500">Course</span>
                <p className="text-base font-semibold text-gray-900">{lessonData.lesson_info.course_title}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500">Topic</span>
                <p className="text-base font-semibold text-gray-900">{lessonData.lesson_info.lesson_topic}</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Overview</h4>
            <div
              className="text-gray-700 leading-relaxed prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{
                __html: cleanOverviewText(lessonData.lesson_plan.overview)
              }}
            />
          </div>

          <div className="mt-6">
            <h5 className="text-sm font-medium text-gray-700 mb-2">Cognitive Levels</h5>
            <div className="flex flex-wrap gap-2">
              {bloomLevelsUsed.length > 0 ? (
                bloomLevelsUsed.map(level => (
                  <Badge key={level} variant={level} size="sm">
                    {capitalize(level)}
                  </Badge>
                ))
              ) : (
                <span className="text-sm text-gray-500">No levels defined</span>
              )}
            </div>
          </div>

          {Math.abs(currentObjectivesCount - optimalObjectivesForDuration) > 1 && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <Target className="w-4 h-4 inline mr-1" />
                <strong>Optimization Tip:</strong> For a {formatDuration(totalDuration)} lesson, {optimalObjectivesForDuration} objectives would be optimal for cognitive load management.
                <button
                  onClick={() => {
                    setNewDuration(totalDuration.toString());
                    setShowDurationModal(true);
                  }}
                  className="ml-2 text-yellow-600 hover:text-yellow-800 underline"
                >
                  Optimize now
                </button>
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default LessonOverviewSection;