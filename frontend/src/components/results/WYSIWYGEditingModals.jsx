import React, { useState, useEffect } from 'react';
import { Clock, RefreshCw, CheckCircle, Plus, Trash2, Save } from 'lucide-react';
import toast from 'react-hot-toast';
import { Modal, ModalBody, ModalFooter } from '../ui/Modal';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import RichTextEditor from '../editor/RichTextEditor';
import Input from '../ui/Input';
import Select from '../ui/Select';
import Textarea from '../ui/Textarea';
import { formatDuration, capitalize } from '../../utils/helpers';
import { intelligentAutoBalance } from '../../utils/timeRedistribution';
import { BLOOM_LEVELS } from '../../utils/constants';

const WYSIWYGEditingModals = ({
  lessonData,
  setLessonData,
  saveDraft,
  refineContent,
  loading,
  editingSection,
  setEditingSection,
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
  // Local editing states for different sections
  const [editingObjectives, setEditingObjectives] = useState([]);
  const [editingLessonPlan, setEditingLessonPlan] = useState({});
  const [editingGagneEvents, setEditingGagneEvents] = useState([]);

  // Initialize editing states when modal opens
  useEffect(() => {
    if (editingSection === 'objectives') {
      setEditingObjectives(lessonData.objectives || []);
    } else if (editingSection === 'lesson_plan') {
      setEditingLessonPlan(lessonData.lesson_plan || {});
    } else if (editingSection === 'gagne_events') {
      setEditingGagneEvents(lessonData.gagne_events || []);
    }
  }, [editingSection, lessonData]);

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

  const handleSaveChanges = async () => {
    const loadingToast = toast.loading('Saving changes...');

    try {
      const updatedData = { ...lessonData };
      let hasChanges = false;

      if (editingSection === 'objectives') {
        updatedData.objectives = editingObjectives.filter(obj => obj.objective.trim());
        hasChanges = true;
      } else if (editingSection === 'lesson_plan') {
        updatedData.lesson_plan = editingLessonPlan;
        hasChanges = true;
      } else if (editingSection === 'gagne_events') {
        // Apply intelligent auto-balance for Gagne events
        const targetDuration = lessonData.total_duration || lessonData.lesson_info.duration_minutes;
        const bloomLevels = lessonData.lesson_info.selected_bloom_levels || [];

        const autoBalanceResult = intelligentAutoBalance(editingGagneEvents, targetDuration, originalGagneEvents, bloomLevels);

        updatedData.gagne_events = autoBalanceResult.events;
        setLastRedistribution(autoBalanceResult);
        hasChanges = true;

        if (autoBalanceResult.adjustments.length > 0) {
          toast.dismiss(loadingToast);
          toast.success(`✅ Changes saved!\n🤖 ${autoBalanceResult.summary}`, { duration: 8000 });
          setTimeout(() => setShowRedistributionInfo(true), 1000);

          setLessonData(updatedData);
          saveDraft(updatedData);
          setEditingSection(null);
          setOriginalGagneEvents(null);
          return;
        }
      }

      if (hasChanges) {
        setLessonData(updatedData);
        saveDraft(updatedData);
      }

      setEditingSection(null);
      setOriginalGagneEvents(null);
      toast.dismiss(loadingToast);
      toast.success('Changes saved successfully! ✅');
    } catch (error) {
      toast.dismiss(loadingToast);
      toast.error(`Failed to save changes: ${error.message}`);
    }
  };

  const handleAIRefinement = async () => {
    if (!refinementInstructions.trim()) {
      toast.error('Please provide refinement instructions');
      return;
    }

    const loadingToast = toast.loading('AI is refining your content...');

    try {
      // Convert current editing state back to JSON for AI processing
      let currentContent;
      if (editingSection === 'objectives') {
        currentContent = editingObjectives;
      } else if (editingSection === 'lesson_plan') {
        currentContent = editingLessonPlan;
      } else if (editingSection === 'gagne_events') {
        currentContent = editingGagneEvents;
      }

      const result = await refineContent({
        section_type: editingSection,
        section_content: JSON.stringify(currentContent),
        refinement_instructions: refinementInstructions,
        lesson_context: lessonData.lesson_info
      });

      if (!result?.refined_content) throw new Error('No refined content received from AI');

      const refinedData = JSON.parse(result.refined_content);

      // Update local editing state with AI refinements
      if (editingSection === 'objectives' && Array.isArray(refinedData)) {
        setEditingObjectives(refinedData.map(obj => ({
          bloom_level: obj.bloom_level || obj.level || 'understand',
          objective: obj.objective || 'Learning objective',
          action_verb: obj.action_verb || obj.verb || 'understand',
          content: obj.content || 'core concepts',
          condition: obj.condition || '',
          criteria: obj.criteria || ''
        })));
      } else if (editingSection === 'lesson_plan' && typeof refinedData === 'object') {
        setEditingLessonPlan({ ...editingLessonPlan, ...refinedData });
      } else if (editingSection === 'gagne_events' && Array.isArray(refinedData)) {
        setEditingGagneEvents(refinedData.map(event => ({
          event_number: event.event_number,
          event_name: event.event_name,
          description: event.description,
          activities: Array.isArray(event.activities) ? event.activities : [event.activities || ''],
          duration_minutes: event.duration_minutes || 5,
          materials_needed: Array.isArray(event.materials_needed) ? event.materials_needed : [event.materials_needed || ''],
          assessment_strategy: event.assessment_strategy || ''
        })));
      }

      setRefinementInstructions('');
      toast.dismiss(loadingToast);
      toast.success('Content refined by AI! ✨ Review and save when ready.');
    } catch (error) {
      toast.dismiss(loadingToast);
      toast.error(`AI refinement failed: ${error.message}`);
    }
  };

  // Objectives editing functions
  const addObjective = () => {
    setEditingObjectives([...editingObjectives, {
      bloom_level: 'understand',
      objective: '',
      action_verb: 'understand',
      content: '',
      condition: '',
      criteria: ''
    }]);
  };

  const removeObjective = (index) => {
    setEditingObjectives(editingObjectives.filter((_, i) => i !== index));
  };

  const updateObjective = (index, field, value) => {
    const updated = [...editingObjectives];
    updated[index] = { ...updated[index], [field]: value };
    setEditingObjectives(updated);
  };

  // Gagne events editing functions
  const updateGagneEvent = (index, field, value) => {
    const updated = [...editingGagneEvents];
    updated[index] = { ...updated[index], [field]: value };
    setEditingGagneEvents(updated);
  };

  const addActivity = (eventIndex) => {
    const updated = [...editingGagneEvents];
    updated[eventIndex].activities.push('');
    setEditingGagneEvents(updated);
  };

  const removeActivity = (eventIndex, activityIndex) => {
    const updated = [...editingGagneEvents];
    updated[eventIndex].activities = updated[eventIndex].activities.filter((_, i) => i !== activityIndex);
    setEditingGagneEvents(updated);
  };

  const updateActivity = (eventIndex, activityIndex, value) => {
    const updated = [...editingGagneEvents];
    updated[eventIndex].activities[activityIndex] = value;
    setEditingGagneEvents(updated);
  };

  const addMaterial = (eventIndex) => {
    const updated = [...editingGagneEvents];
    updated[eventIndex].materials_needed.push('');
    setEditingGagneEvents(updated);
  };

  const removeMaterial = (eventIndex, materialIndex) => {
    const updated = [...editingGagneEvents];
    updated[eventIndex].materials_needed = updated[eventIndex].materials_needed.filter((_, i) => i !== materialIndex);
    setEditingGagneEvents(updated);
  };

  const updateMaterial = (eventIndex, materialIndex, value) => {
    const updated = [...editingGagneEvents];
    updated[eventIndex].materials_needed[materialIndex] = value;
    setEditingGagneEvents(updated);
  };

  const totalDuration = lessonData.total_duration || lessonData.lesson_info?.duration_minutes || 0;
  const currentObjectivesCount = lessonData.objectives?.length || 0;

  const bloomOptions = BLOOM_LEVELS.map(level => ({
    value: level.value,
    label: level.label
  }));

  return (
    <>
      {/* Duration Change Modal */}
      <Modal isOpen={showDurationModal} onClose={() => setShowDurationModal(false)} title="Change Lesson Duration" size="md">
        <ModalBody>
          <div className="space-y-4">
            <Input
              label="New Duration (minutes)"
              type="number"
              min="5"
              max="480"
              value={newDuration}
              onChange={(e) => setNewDuration(e.target.value)}
              placeholder="Enter duration in minutes (5-480)"
              helper={`Current: ${formatDuration(totalDuration)} | Optimal objectives: ${calculateOptimalObjectives(parseInt(newDuration) || totalDuration)}`}
            />

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

      {/* WYSIWYG Edit Modal */}
      <Modal
        isOpen={!!editingSection}
        onClose={() => setEditingSection(null)}
        title={`Edit ${editingSection ? editingSection.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) : ''}`}
        size="xl"
      >
        <ModalBody>
          <div className="space-y-6">
            {/* AI Refinement Section */}
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-purple-800 mb-2">🤖 AI Assistance</h4>
              <Textarea
                placeholder="Ask AI to refine your content... (e.g., 'Make it more engaging', 'Add practical examples', 'Simplify the language')"
                value={refinementInstructions}
                onChange={(e) => setRefinementInstructions(e.target.value)}
                rows={2}
              />
              <div className="flex justify-end mt-2">
                <Button
                  size="sm"
                  onClick={handleAIRefinement}
                  disabled={!refinementInstructions.trim() || loading}
                  loading={loading}
                  className="flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refine with AI
                </Button>
              </div>
            </div>

            {/* Content Editing Based on Section */}
            <div className="max-h-96 overflow-y-auto">
              {editingSection === 'objectives' && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h5 className="font-medium text-gray-900">Learning Objectives</h5>
                    <Button size="sm" onClick={addObjective} className="flex items-center gap-2">
                      <Plus className="w-4 h-4" />
                      Add Objective
                    </Button>
                  </div>

                  {editingObjectives.map((objective, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-700">Objective {index + 1}</span>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => removeObjective(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <Select
                          label="Bloom's Level"
                          options={bloomOptions}
                          value={objective.bloom_level}
                          onChange={(e) => updateObjective(index, 'bloom_level', e.target.value)}
                        />
                        <Input
                          label="Action Verb"
                          value={objective.action_verb}
                          onChange={(e) => updateObjective(index, 'action_verb', e.target.value)}
                          placeholder="e.g., analyze, create, explain"
                        />
                      </div>

                      <Textarea
                        label="Learning Objective"
                        value={objective.objective}
                        onChange={(e) => updateObjective(index, 'objective', e.target.value)}
                        placeholder="Students will be able to..."
                        rows={2}
                      />

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <Input
                          label="Condition (optional)"
                          value={objective.condition}
                          onChange={(e) => updateObjective(index, 'condition', e.target.value)}
                          placeholder="e.g., using provided materials"
                        />
                        <Input
                          label="Criteria (optional)"
                          value={objective.criteria}
                          onChange={(e) => updateObjective(index, 'criteria', e.target.value)}
                          placeholder="e.g., with 80% accuracy"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {editingSection === 'lesson_plan' && (
                <div className="space-y-4">
                  <h5 className="font-medium text-gray-900">Lesson Plan Details</h5>

                  <Input
                    label="Lesson Title"
                    value={editingLessonPlan.title || ''}
                    onChange={(e) => setEditingLessonPlan({...editingLessonPlan, title: e.target.value})}
                    placeholder="Enter a descriptive title for your lesson..."
                  />

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Overview</label>
                    <RichTextEditor
                      content={editingLessonPlan.overview || ''}
                      onChange={(content) => setEditingLessonPlan({...editingLessonPlan, overview: content})}
                      placeholder="Describe what students will learn and how..."
                      minHeight="120px"
                    />
                  </div>

                  <Textarea
                    label="Prerequisites (one per line)"
                    value={Array.isArray(editingLessonPlan.prerequisites) ? editingLessonPlan.prerequisites.join('\n') : ''}
                    onChange={(e) => setEditingLessonPlan({...editingLessonPlan, prerequisites: e.target.value.split('\n').filter(p => p.trim())})}
                    placeholder="Basic understanding of..."
                    rows={3}
                  />

                  <Textarea
                    label="Materials (one per line)"
                    value={Array.isArray(editingLessonPlan.materials) ? editingLessonPlan.materials.join('\n') : ''}
                    onChange={(e) => setEditingLessonPlan({...editingLessonPlan, materials: e.target.value.split('\n').filter(m => m.trim())})}
                    placeholder="Textbook, handouts, computer..."
                    rows={3}
                  />

                  <Textarea
                    label="Assessment Methods (one per line)"
                    value={Array.isArray(editingLessonPlan.assessment_methods) ? editingLessonPlan.assessment_methods.join('\n') : ''}
                    onChange={(e) => setEditingLessonPlan({...editingLessonPlan, assessment_methods: e.target.value.split('\n').filter(a => a.trim())})}
                    placeholder="Quiz, discussion, project..."
                    rows={3}
                  />

                  <Textarea
                    label="Differentiation Strategies (one per line)"
                    value={Array.isArray(editingLessonPlan.differentiation_strategies) ? editingLessonPlan.differentiation_strategies.join('\n') : ''}
                    onChange={(e) => setEditingLessonPlan({...editingLessonPlan, differentiation_strategies: e.target.value.split('\n').filter(d => d.trim())})}
                    placeholder="Visual aids, multiple learning modalities..."
                    rows={3}
                  />

                  <Textarea
                    label="Technology Requirements (one per line)"
                    value={Array.isArray(editingLessonPlan.technology_requirements) ? editingLessonPlan.technology_requirements.join('\n') : ''}
                    onChange={(e) => setEditingLessonPlan({...editingLessonPlan, technology_requirements: e.target.value.split('\n').filter(t => t.trim())})}
                    placeholder="Computer/tablet, Internet access..."
                    rows={3}
                  />

                  <Textarea
                    label="Closure Activities (one per line)"
                    value={Array.isArray(editingLessonPlan.closure_activities) ? editingLessonPlan.closure_activities.join('\n') : ''}
                    onChange={(e) => setEditingLessonPlan({...editingLessonPlan, closure_activities: e.target.value.split('\n').filter(c => c.trim())})}
                    placeholder="Summary discussion, Q&A session..."
                    rows={3}
                  />
                </div>
              )}

              {editingSection === 'gagne_events' && (
                <div className="space-y-6">
                  <h5 className="font-medium text-gray-900">Gagne's Nine Events of Instruction</h5>

                  {editingGagneEvents.map((event, eventIndex) => (
                    <div key={eventIndex} className="border border-gray-200 rounded-lg p-4 space-y-4">
                      <div className="flex justify-between items-center">
                        <h6 className="font-medium text-gray-800">
                          Event {event.event_number}: {event.event_name}
                        </h6>
                        <Input
                          type="number"
                          min="1"
                          max="60"
                          value={event.duration_minutes}
                          onChange={(e) => updateGagneEvent(eventIndex, 'duration_minutes', parseInt(e.target.value) || 1)}
                          className="w-20"
                        />
                      </div>

                      <Textarea
                        label="Description"
                        value={event.description}
                        onChange={(e) => updateGagneEvent(eventIndex, 'description', e.target.value)}
                        rows={2}
                      />

                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <label className="text-sm font-medium text-gray-700">Activities</label>
                          <Button size="sm" onClick={() => addActivity(eventIndex)}>
                            <Plus className="w-4 h-4" />
                          </Button>
                        </div>
                        {event.activities.map((activity, actIndex) => (
                          <div key={actIndex} className="flex gap-2 mb-2">
                            <Input
                              value={activity}
                              onChange={(e) => updateActivity(eventIndex, actIndex, e.target.value)}
                              placeholder="Activity description..."
                              className="flex-1"
                            />
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => removeActivity(eventIndex, actIndex)}
                              className="text-red-600"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        ))}
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <label className="text-sm font-medium text-gray-700">Materials Needed</label>
                          <Button size="sm" onClick={() => addMaterial(eventIndex)}>
                            <Plus className="w-4 h-4" />
                          </Button>
                        </div>
                        {event.materials_needed.map((material, matIndex) => (
                          <div key={matIndex} className="flex gap-2 mb-2">
                            <Input
                              value={material}
                              onChange={(e) => updateMaterial(eventIndex, matIndex, e.target.value)}
                              placeholder="Material description..."
                              className="flex-1"
                            />
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => removeMaterial(eventIndex, matIndex)}
                              className="text-red-600"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        ))}
                      </div>

                      <Input
                        label="Assessment Strategy (optional)"
                        value={event.assessment_strategy || ''}
                        onChange={(e) => updateGagneEvent(eventIndex, 'assessment_strategy', e.target.value)}
                        placeholder="How will you assess this event..."
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" onClick={() => setEditingSection(null)}>Cancel</Button>
          <Button onClick={handleSaveChanges} loading={loading} className="flex items-center gap-2">
            <Save className="w-4 h-4" />
            Save Changes
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

export default WYSIWYGEditingModals;