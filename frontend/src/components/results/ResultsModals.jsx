import React from 'react';
import { Clock, RefreshCw, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import { Modal, ModalBody, ModalFooter } from '../ui/Modal';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { formatDuration } from '../../utils/helpers';
import { intelligentAutoBalance } from '../../utils/timeRedistribution';

const ResultsModals = ({
  lessonData,
  setLessonData,
  saveDraft,
  refineContent,
  loading,
  editingSection,
  setEditingSection,
  editContent,
  setEditContent,
  refinementInstructions,
  setRefinementInstructions,
  originalGagneEvents,
  setOriginalGagneEvents,
  lastRedistribution,
  setLastRedistribution,
  setShowRedistributionInfo,
  showDurationModal,
  setShowDurationModal,
  newDuration,
  setNewDuration,
  showRedistributionInfo
}) => {
  const calculateOptimalObjectives = (duration) => {
    if (duration <= 30) return 2;
    if (duration <= 60) return 3;
    if (duration <= 90) return 4;
    if (duration <= 120) return 5;
    return 6;
  };

  const handleDurationChange = async () => {
    const durationMinutes = parseInt(newDuration);
    if (!durationMinutes || durationMinutes < 5 || durationMinutes > 480) {
      toast.error('Duration must be between 5 and 480 minutes');
      return;
    }

    const loadingToast = toast.loading('Adjusting lesson duration...');
    try {
      const refinementRequest = {
        section_type: 'duration_change',
        section_content: JSON.stringify({
          current_duration: lessonData.lesson_info.duration_minutes,
          new_duration: durationMinutes,
          gagne_events: lessonData.gagne_events,
          lesson_plan: lessonData.lesson_plan,
          current_objectives: lessonData.objectives
        }),
        refinement_instructions: `Change duration from ${lessonData.lesson_info.duration_minutes} to ${durationMinutes} minutes`,
        lesson_context: lessonData.lesson_info
      };

      const result = await refineContent(refinementRequest);
      if (!result?.refined_content) throw new Error('No refined content received');

      const refinedData = JSON.parse(result.refined_content);
      const updatedData = {
        ...lessonData,
        lesson_info: { ...lessonData.lesson_info, duration_minutes: durationMinutes },
        total_duration: durationMinutes,
        gagne_events: refinedData.gagne_events || lessonData.gagne_events,
        lesson_plan: { ...lessonData.lesson_plan, overview: refinedData.overview || lessonData.lesson_plan.overview }
      };

      if (refinedData.objectives?.length) {
        updatedData.objectives = refinedData.objectives.map(obj => ({
          bloom_level: obj.bloom_level || 'understand',
          objective: obj.objective || 'Learning objective',
          action_verb: obj.action_verb || 'understand',
          content: obj.content || 'core concepts',
          condition: obj.condition || null,
          criteria: obj.criteria || null
        }));
      }

      setLessonData(updatedData);
      saveDraft(updatedData);
      setShowDurationModal(false);
      setNewDuration('');
      toast.dismiss(loadingToast);
      toast.success(`Lesson updated to ${formatDuration(durationMinutes)}!`);
    } catch (error) {
      toast.dismiss(loadingToast);
      toast.error(`Failed to update duration: ${error.message}`);
    }
  };

  const handleRefineContent = async () => {
    if (!refinementInstructions.trim()) {
      toast.error('Please provide refinement instructions');
      return;
    }

    const loadingToast = toast.loading('Refining content...');
    try {
      const result = await refineContent({
        section_type: editingSection,
        section_content: editContent,
        refinement_instructions: refinementInstructions,
        lesson_context: lessonData.lesson_info
      });

      if (!result?.refined_content) throw new Error('No refined content received');

      const refinedData = JSON.parse(result.refined_content);
      const updatedData = { ...lessonData };
      let updateSuccessful = false;

      switch (editingSection) {
        case 'objectives':
          if (Array.isArray(refinedData)) {
            updatedData.objectives = refinedData.map(obj => ({
              bloom_level: obj.bloom_level || obj.level,
              objective: obj.objective,
              action_verb: obj.action_verb || obj.verb,
              content: obj.content,
              condition: obj.condition,
              criteria: obj.criteria
            }));
            updateSuccessful = true;
          }
          break;

        case 'lesson_plan':
          if (typeof refinedData === 'object' && !Array.isArray(refinedData)) {
            updatedData.lesson_plan = { ...updatedData.lesson_plan, ...refinedData };
            updateSuccessful = true;
          }
          break;

        case 'gagne_events':
          if (Array.isArray(refinedData)) {
            const targetDuration = lessonData.total_duration || lessonData.lesson_info.duration_minutes;
            const bloomLevels = lessonData.lesson_info.selected_bloom_levels || [];

            const autoBalanceResult = intelligentAutoBalance(refinedData, targetDuration, originalGagneEvents, bloomLevels);

            updatedData.gagne_events = autoBalanceResult.events.map(event => ({
              event_number: event.event_number,
              event_name: event.event_name,
              description: event.description,
              activities: Array.isArray(event.activities) ? event.activities : [event.activities],
              duration_minutes: event.duration_minutes,
              materials_needed: Array.isArray(event.materials_needed) ? event.materials_needed : [event.materials_needed],
              assessment_strategy: event.assessment_strategy
            }));

            setLastRedistribution(autoBalanceResult);
            updateSuccessful = true;

            if (autoBalanceResult.adjustments.length > 0) {
              toast.dismiss(loadingToast);
              toast.success(`✅ Content refined!\n🤖 ${autoBalanceResult.summary}`, { duration: 8000 });
              setTimeout(() => setShowRedistributionInfo(true), 1000);
              updateSuccessful = 'with_redistribution';
            }
          }
          break;
      }

      if (!updateSuccessful) throw new Error('Failed to update lesson data');

      setLessonData(updatedData);
      saveDraft(updatedData);
      setEditingSection(null);
      setRefinementInstructions('');
      setEditContent('');
      setOriginalGagneEvents(null);

      if (updateSuccessful !== 'with_redistribution') {
        toast.dismiss(loadingToast);
        toast.success('Content refined successfully! ✅');
      }
    } catch (error) {
      toast.dismiss(loadingToast);
      toast.error(`Refinement failed: ${error.message}`);
    }
  };

  const totalDuration = lessonData.total_duration || lessonData.lesson_info?.duration_minutes || 0;
  const currentObjectivesCount = lessonData.objectives?.length || 0;

  return (
    <>
      {/* Duration Change Modal */}
      <Modal isOpen={showDurationModal} onClose={() => setShowDurationModal(false)} title="Change Lesson Duration" size="md">
        <ModalBody>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">New Duration (minutes)</label>
              <input
                type="number"
                min="5"
                max="480"
                value={newDuration}
                onChange={(e) => setNewDuration(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter duration in minutes (5-480)"
              />
              <p className="text-xs text-gray-500 mt-1">
                Current: {formatDuration(totalDuration)} | Optimal objectives: {calculateOptimalObjectives(parseInt(newDuration) || totalDuration)}
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <h4 className="text-sm font-medium text-blue-800 mb-1">What will happen:</h4>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• All Gagne events will be recalculated for the new duration</li>
                <li>• Lesson overview will be updated to reflect the change</li>
                <li>• Learning objectives will be optimized for cognitive load</li>
                <li>• Time distribution will follow pedagogical best practices</li>
              </ul>
            </div>

            {newDuration && parseInt(newDuration) !== totalDuration && (
              <div className={`border rounded-lg p-3 ${
                Math.abs(calculateOptimalObjectives(parseInt(newDuration)) - currentObjectivesCount) >= 1
                  ? 'bg-yellow-50 border-yellow-200'
                  : 'bg-green-50 border-green-200'
              }`}>
                <h4 className={`text-sm font-medium mb-1 ${
                  Math.abs(calculateOptimalObjectives(parseInt(newDuration)) - currentObjectivesCount) >= 1
                    ? 'text-yellow-800'
                    : 'text-green-800'
                }`}>
                  Objective Impact:
                </h4>
                <p className={`text-xs ${
                  Math.abs(calculateOptimalObjectives(parseInt(newDuration)) - currentObjectivesCount) >= 1
                    ? 'text-yellow-700'
                    : 'text-green-700'
                }`}>
                  {currentObjectivesCount} current objectives → {calculateOptimalObjectives(parseInt(newDuration))} optimal objectives
                  {Math.abs(calculateOptimalObjectives(parseInt(newDuration)) - currentObjectivesCount) >= 1
                    ? ' (will be recalculated)'
                    : ' (no change needed)'
                  }
                </p>
              </div>
            )}
          </div>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" onClick={() => setShowDurationModal(false)}>Cancel</Button>
          <Button onClick={handleDurationChange} loading={loading} className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Update Duration & Objectives
          </Button>
        </ModalFooter>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={!!editingSection}
        onClose={() => setEditingSection(null)}
        title={`Edit ${editingSection ? editingSection.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : ''}`}
        size="lg"
      >
        <ModalBody>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Refinement Instructions</label>
              <textarea
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                rows={3}
                placeholder="Describe how you want to modify this section..."
                value={refinementInstructions}
                onChange={(e) => setRefinementInstructions(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                Example: "Make the language more engaging", "Add more practical examples", "Focus on real-world applications"
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Current Content (JSON)</label>
              <textarea
                className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                rows={10}
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                You can also manually edit the JSON structure above if needed.
              </p>
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" onClick={() => setEditingSection(null)}>Cancel</Button>
          <Button onClick={handleRefineContent} loading={loading} className="flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refine Content
          </Button>
        </ModalFooter>
      </Modal>

      {/* Time Redistribution Info Modal */}
      <Modal
        isOpen={showRedistributionInfo}
        onClose={() => setShowRedistributionInfo(false)}
        title="🤖 Intelligent Time Redistribution"
        size="lg"
      >
        <ModalBody>
          {lastRedistribution && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-blue-800 mb-1">Auto-Balance Applied</h4>
                    <p className="text-sm text-blue-700">{lastRedistribution.summary}</p>
                    <p className="text-xs text-blue-600 mt-1 italic">{lastRedistribution.rationale}</p>
                  </div>
                </div>
              </div>

              <div>
                <h5 className="font-medium text-gray-900 mb-3">Time Adjustments Made:</h5>
                <div className="space-y-2">
                  {lastRedistribution.adjustments.map((adj, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <span className="font-medium text-gray-900">Event {adj.eventNumber}:</span>
                        <span className="text-sm text-gray-600">{adj.eventName}</span>
                        {adj.wasModified && (
                          <Badge variant="primary" size="sm">User Modified</Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">
                          {formatDuration(adj.originalDuration)} → {formatDuration(adj.newDuration)}
                        </span>
                        <span className={`text-sm font-medium ${
                          adj.adjustment > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          ({adj.adjustment > 0 ? '+' : ''}{adj.adjustment} min)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h6 className="font-medium text-gray-800 mb-2">🎓 Why This Strategy?</h6>
                <div className="text-sm text-gray-600 space-y-2">
                  {lastRedistribution.strategy.includes('adjacent') && (
                    <p><strong>Adjacent Events:</strong> Small changes were made to events near your modifications to minimize disruption to the lesson flow.</p>
                  )}
                  {lastRedistribution.strategy.includes('pedagogical') && (
                    <p><strong>Pedagogical Priority:</strong> Time was redistributed based on educational importance, protecting core learning activities.</p>
                  )}
                  {lastRedistribution.strategy.includes('proportional') && (
                    <p><strong>Proportional Distribution:</strong> Changes were spread evenly across events to maintain balanced lesson structure.</p>
                  )}
                  {lastRedistribution.strategy.includes('micro') && (
                    <p><strong>Fine-tuning:</strong> Additional micro-adjustments were made to achieve perfect time balance.</p>
                  )}
                </div>
              </div>

              <div className="border-t pt-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Original Time Difference:</span>
                    <span className="ml-2 font-medium">{lastRedistribution.timeDifference} minutes</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Final Accuracy:</span>
                    <span className={`ml-2 font-medium ${
                      lastRedistribution.finalDifference <= 1 ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      ±{lastRedistribution.finalDifference} minute{lastRedistribution.finalDifference !== 1 ? 's' : ''}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </ModalBody>
        <ModalFooter>
          <Button onClick={() => setShowRedistributionInfo(false)}>Got It</Button>
        </ModalFooter>
      </Modal>
    </>
  );
};

export default ResultsModals;