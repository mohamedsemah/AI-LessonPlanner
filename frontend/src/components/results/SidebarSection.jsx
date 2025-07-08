import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import Badge from '../ui/Badge';
import { formatDuration } from '../../utils/helpers';

const SidebarSection = ({ lessonData }) => {
  const calculateOptimalObjectives = (duration) => {
    if (duration <= 30) return 2;
    if (duration <= 60) return 3;
    if (duration <= 90) return 4;
    if (duration <= 120) return 5;
    return 6;
  };

  const safeObjectives = lessonData.objectives || [];
  const totalDuration = lessonData.total_duration || lessonData.lesson_info?.duration_minutes || 0;
  const currentObjectivesCount = safeObjectives.length;
  const optimalObjectivesForDuration = calculateOptimalObjectives(totalDuration);
  const bloomLevelsUsed = [...new Set(safeObjectives.map(obj => obj.bloom_level))].filter(Boolean);

  return (
    <>
      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Stats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Objectives</span>
                <span className="font-semibold">{currentObjectivesCount}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Bloom's Levels</span>
                <span className="font-semibold">{bloomLevelsUsed.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Duration</span>
                <span className="font-semibold">{formatDuration(totalDuration)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Events</span>
                <span className="font-semibold">{lessonData.gagne_events?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Optimal Objectives</span>
                <span className={`font-semibold ${
                  Math.abs(currentObjectivesCount - optimalObjectivesForDuration) <= 1 
                    ? 'text-green-600' 
                    : 'text-yellow-600'
                }`}>
                  {optimalObjectivesForDuration}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Lesson Plan Details */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Lesson Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {lessonData.lesson_plan?.prerequisites && lessonData.lesson_plan.prerequisites.length > 0 && (
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Prerequisites</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {lessonData.lesson_plan.prerequisites.map((prereq, index) => (
                      <li key={index}>• {prereq}</li>
                    ))}
                  </ul>
                </div>
              )}

              {lessonData.lesson_plan?.materials && lessonData.lesson_plan.materials.length > 0 && (
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Materials</h5>
                  <div className="flex flex-wrap gap-2">
                    {lessonData.lesson_plan.materials.map((material, index) => (
                      <Badge key={index} variant="secondary" size="sm">
                        {material}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {lessonData.lesson_plan?.assessment_methods && lessonData.lesson_plan.assessment_methods.length > 0 && (
                <div>
                  <h5 className="font-medium text-gray-900 mb-2">Assessment</h5>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {lessonData.lesson_plan.assessment_methods.map((method, index) => (
                      <li key={index}>• {method}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </>
  );
};

export default SidebarSection;