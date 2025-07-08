import React from 'react';
import { motion } from 'framer-motion';
import { Edit3, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { groupObjectivesByBloom, capitalize } from '../../utils/helpers';

const LearningObjectivesSection = ({
  lessonData,
  setEditingSection,
  setEditContent,
  setRefinementInstructions
}) => {
  const handleEditSection = (sectionType, content) => {
    setEditingSection(sectionType);
    setEditContent(JSON.stringify(content, null, 2));
    setRefinementInstructions('');
  };

  const safeObjectives = lessonData.objectives || [];
  const objectivesByBloom = groupObjectivesByBloom(safeObjectives);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Learning Objectives</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleEditSection('objectives', safeObjectives)}
          >
            <Edit3 className="w-4 h-4" />
          </Button>
        </CardHeader>
        <CardContent>
          {safeObjectives.length > 0 ? (
            <div className="space-y-6">
              {Object.entries(objectivesByBloom).map(([level, objectives]) => (
                <div key={level}>
                  <div className="flex items-center gap-2 mb-3">
                    <Badge variant={level} size="sm">
                      {capitalize(level)}
                    </Badge>
                    <span className="text-sm text-gray-500">
                      {objectives.length} objective{objectives.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <ul className="space-y-2 ml-4">
                    {objectives.map((objective, index) => (
                      <li key={index} className="text-gray-700 text-sm">
                        • {objective.objective}
                        {objective.condition && (
                          <span className="text-gray-500"> ({objective.condition})</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No learning objectives found</p>
              <p className="text-sm text-gray-400 mt-1">
                Try regenerating the lesson or editing the content
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default LearningObjectivesSection;