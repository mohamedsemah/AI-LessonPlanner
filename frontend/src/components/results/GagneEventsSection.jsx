import React from 'react';
import { motion } from 'framer-motion';
import { Edit3, BookOpen, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { formatDuration } from '../../utils/helpers';

const GagneEventsSection = ({
  lessonData,
  setEditingSection,
  setEditContent,
  setRefinementInstructions,
  setOriginalGagneEvents,
  lastRedistribution,
  setShowRedistributionInfo
}) => {
  const handleEditSection = (sectionType, content) => {
    if (sectionType === 'gagne_events') {
      setOriginalGagneEvents([...content]);
    }
    setEditingSection(sectionType);
    setEditContent(JSON.stringify(content, null, 2));
    setRefinementInstructions('');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            Gagne's Nine Events of Instruction
            {lastRedistribution && lastRedistribution.adjustments.length > 0 && (
              <button
                onClick={() => setShowRedistributionInfo(true)}
                className="ml-2 p-1 text-blue-600 hover:text-blue-800 transition-colors"
                title="View time redistribution details"
              >
                <Info className="w-4 h-4" />
              </button>
            )}
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleEditSection('gagne_events', lessonData.gagne_events)}
          >
            <Edit3 className="w-4 h-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {lessonData.gagne_events && lessonData.gagne_events.length > 0 ? (
              lessonData.gagne_events.map((event, index) => (
                <div key={index} className="border-l-4 border-primary-200 pl-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-900">
                      Event {event.event_number}: {event.event_name}
                    </h4>
                    <Badge variant="default" size="sm">
                      {formatDuration(event.duration_minutes)}
                    </Badge>
                  </div>
                  <p className="text-gray-600 text-sm mb-3">{event.description}</p>

                  {event.activities && event.activities.length > 0 && (
                    <div className="mb-3">
                      <span className="text-sm font-medium text-gray-700">Activities:</span>
                      <ul className="ml-4 mt-1 space-y-1">
                        {event.activities.map((activity, actIndex) => (
                          <li key={actIndex} className="text-sm text-gray-600">
                            • {activity}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {event.materials_needed && event.materials_needed.length > 0 && (
                    <div className="mb-3">
                      <span className="text-sm font-medium text-gray-700">Materials:</span>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {event.materials_needed.map((material, matIndex) => (
                          <Badge key={matIndex} variant="secondary" size="sm">
                            {material}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No Gagne events found</p>
                <p className="text-sm text-gray-400 mt-1">
                  Try regenerating the lesson or editing the content
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default GagneEventsSection;