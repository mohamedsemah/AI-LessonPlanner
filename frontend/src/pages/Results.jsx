import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Download, Edit3, Eye, RefreshCw, ArrowLeft, BookOpen, Clock, Target } from 'lucide-react';
import toast from 'react-hot-toast';

import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../components/ui/Modal';
import RichTextEditor from '../components/editor/RichTextEditor';
import { useApi } from '../hooks/useApi';
import { useLessonDraft } from '../hooks/useLocalStorage';
import {
  formatDuration,
  groupObjectivesByBloom,
  generatePDFFilename,
  downloadFile,
  capitalize
} from '../utils/helpers';
import { TOAST_MESSAGES } from '../utils/constants';

// Helper functions for data validation and consistency
const validateObjectiveStructure = (obj, index) => {
  const validLevels = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'];

  let bloomLevel = (obj.bloom_level || obj.level || 'understand').toLowerCase();
  if (!validLevels.includes(bloomLevel)) {
    console.warn(`Invalid bloom level: ${bloomLevel}, defaulting to 'understand'`);
    bloomLevel = 'understand';
  }

  return {
    bloom_level: bloomLevel,
    objective: obj.objective || obj.description || `Learning objective ${index + 1}`,
    action_verb: obj.action_verb || obj.verb || obj.action || 'understand',
    content: obj.content || obj.topic || 'core concepts',
    condition: obj.condition || null,
    criteria: obj.criteria || null
  };
};

// Extract unique Bloom levels from objectives
const extractBloomLevelsFromObjectives = (objectives) => {
  if (!objectives || !Array.isArray(objectives)) return [];
  return [...new Set(objectives.map(obj => obj.bloom_level).filter(Boolean))];
};

// Ensure lesson data consistency
const ensureLessonDataConsistency = (lessonData) => {
  // Ensure objectives are properly structured
  const validatedObjectives = (lessonData.objectives || []).map(validateObjectiveStructure);

  // Extract bloom levels from objectives
  const bloomLevelsFromObjectives = extractBloomLevelsFromObjectives(validatedObjectives);

  return {
    ...lessonData,
    objectives: validatedObjectives,
    lesson_info: {
      ...lessonData.lesson_info,
      selected_bloom_levels: bloomLevelsFromObjectives
    }
  };
};

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { exportToPDF, refineContent, loading } = useApi();
  const { draft, clearDraft, saveDraft } = useLessonDraft();

  const [lessonData, setLessonData] = useState(location.state?.lessonData || draft);
  const [showPDFPreview, setShowPDFPreview] = useState(false);
  const [editingSection, setEditingSection] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [refinementInstructions, setRefinementInstructions] = useState('');

  // Duration change states
  const [showDurationModal, setShowDurationModal] = useState(false);
  const [newDuration, setNewDuration] = useState('');

  useEffect(() => {
    if (!lessonData) {
      navigate('/create');
    } else {
      // Ensure data consistency when component loads
      const consistentData = ensureLessonDataConsistency(lessonData);

      // Only update state if there were changes
      if (JSON.stringify(consistentData) !== JSON.stringify(lessonData)) {
        console.log('🔧 Fixing lesson data consistency on load');
        setLessonData(consistentData);
        saveDraft(consistentData);
      }

      // Debug logging to see the data structure
      console.log('📊 Lesson Data Structure:', consistentData);
      console.log('🎯 Objectives Data:', consistentData.objectives);
      console.log('🏷️ Bloom Levels:', consistentData.lesson_info.selected_bloom_levels);
    }
  }, [lessonData?.id]); // Use a stable identifier to prevent infinite loops

  if (!lessonData) {
    return null;
  }

  const handleExportPDF = async () => {
    try {
      const pdfBlob = await exportToPDF(lessonData, {
        includeCoverPage: true,
        includeAppendices: true
      });

      const filename = generatePDFFilename(lessonData);
      downloadFile(pdfBlob, filename);

      toast.success(TOAST_MESSAGES.SUCCESS.PDF_EXPORTED);
    } catch (error) {
      toast.error(TOAST_MESSAGES.ERROR.EXPORT_FAILED);
    }
  };

  const handleEditSection = (sectionType, content) => {
    setEditingSection(sectionType);
    setEditContent(JSON.stringify(content, null, 2));
    setRefinementInstructions('');
  };

  const calculateOptimalObjectives = (duration) => {
    // Replicate the backend logic for calculating optimal objectives
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

    const loadingToast = toast.loading('Adjusting lesson duration and recalculating objectives...');

    try {
      // Calculate if objectives need to be recalculated
      const currentObjectivesCount = lessonData.objectives.length;
      const optimalObjectivesCount = calculateOptimalObjectives(durationMinutes);
      const objectiveChangeNeeded = Math.abs(optimalObjectivesCount - currentObjectivesCount) >= 1;

      // Create a comprehensive refinement request that handles duration, objectives, and events
      const refinementRequest = {
        section_type: 'duration_change',
        section_content: JSON.stringify({
          current_duration: lessonData.lesson_info.duration_minutes,
          new_duration: durationMinutes,
          gagne_events: lessonData.gagne_events,
          lesson_plan: lessonData.lesson_plan,
          current_objectives: lessonData.objectives
        }),
        refinement_instructions: `Change the lesson duration from ${lessonData.lesson_info.duration_minutes} minutes to ${durationMinutes} minutes. Recalculate the time distribution for all Gagne events. Update the lesson overview. ${objectiveChangeNeeded ? `Recalculate learning objectives from ${currentObjectivesCount} to ${optimalObjectivesCount} objectives for optimal cognitive load.` : 'Keep existing objectives but ensure they are achievable in the new timeframe.'}`,
        lesson_context: {
          ...lessonData.lesson_info,
          selected_bloom_levels: lessonData.lesson_info.selected_bloom_levels
        }
      };

      console.log('🔄 Starting duration change with objective recalculation');
      console.log('📊 Current objectives:', currentObjectivesCount, '→ Optimal:', optimalObjectivesCount);

      const result = await refineContent(refinementRequest);

      if (!result || !result.refined_content) {
        throw new Error('No refined content received from API');
      }

      const refinedData = JSON.parse(result.refined_content);
      console.log('📥 Refined data received:', refinedData);

      // Update the entire lesson data with new duration, objectives, and events
      const updatedData = {
        ...lessonData,
        lesson_info: {
          ...lessonData.lesson_info,
          duration_minutes: durationMinutes
        },
        total_duration: durationMinutes,
        gagne_events: refinedData.gagne_events || lessonData.gagne_events,
        lesson_plan: {
          ...lessonData.lesson_plan,
          overview: refinedData.overview || lessonData.lesson_plan.overview
        }
      };

      // FIXED: Enhanced objective processing with proper structure validation
      if (refinedData.objectives && Array.isArray(refinedData.objectives)) {
        console.log('🎯 Processing new objectives:', refinedData.objectives.length);

        // Process and validate each objective
        const processedObjectives = [];

        for (let i = 0; i < refinedData.objectives.length; i++) {
          const rawObj = refinedData.objectives[i];
          console.log(`🔍 Processing objective ${i + 1}:`, rawObj);

          const processedObjective = validateObjectiveStructure(rawObj, i + 1);
          console.log(`✅ Processed objective ${i + 1}:`, processedObjective);
          processedObjectives.push(processedObjective);
        }

        updatedData.objectives = processedObjectives;
        console.log('✅ Final processed objectives:', updatedData.objectives);

      } else {
        console.log('⚠️ No objectives in refined data or invalid format, keeping existing objectives');
        // Keep existing objectives but ensure they have proper structure
        updatedData.objectives = lessonData.objectives.map(validateObjectiveStructure);
      }

      // CRITICAL: Ensure lesson_info.selected_bloom_levels is properly maintained
      const finalObjectives = updatedData.objectives;
      const bloomLevelsFromObjectives = extractBloomLevelsFromObjectives(finalObjectives);

      // Update the lesson_info with the current bloom levels from objectives
      updatedData.lesson_info = {
        ...updatedData.lesson_info,
        selected_bloom_levels: bloomLevelsFromObjectives
      };

      console.log('🔍 Final validation:');
      console.log('📊 Final objectives count:', updatedData.objectives.length);
      console.log('🎯 Bloom levels in objectives:', bloomLevelsFromObjectives);
      console.log('📋 Lesson info bloom levels:', updatedData.lesson_info.selected_bloom_levels);
      console.log('🏷️ Sample objective structure:', updatedData.objectives[0]);

      // Update state and storage
      setLessonData(updatedData);
      saveDraft(updatedData);
      setShowDurationModal(false);
      setNewDuration('');

      toast.dismiss(loadingToast);

      // Show comprehensive success message
      const changesSummary = refinedData.duration_change_summary;
      if (changesSummary && changesSummary.objectives_changed) {
        toast.success(
          `✅ Lesson updated to ${formatDuration(durationMinutes)}!\n` +
          `📊 Objectives: ${changesSummary.old_objectives_count} → ${changesSummary.new_objectives_count}\n` +
          `⏱️ All Gagne events recalculated`,
          { duration: 6000 }
        );
      } else {
        toast.success(`Lesson duration updated to ${formatDuration(durationMinutes)}!`);
      }

    } catch (error) {
      toast.dismiss(loadingToast);
      console.error('Duration change error:', error);
      toast.error(`Failed to update duration: ${error.message}`);
    }
  };

  const handleRefineContent = async () => {
    if (!refinementInstructions.trim()) {
      toast.error('Please provide refinement instructions');
      return;
    }

    // Show loading toast
    const loadingToast = toast.loading('Refining content...');

    try {
      const refinementRequest = {
        section_type: editingSection,
        section_content: editContent,
        refinement_instructions: refinementInstructions,
        lesson_context: lessonData.lesson_info
      };

      console.log('🔄 Starting refinement process');
      console.log('📤 Refinement request:', refinementRequest);

      const result = await refineContent(refinementRequest);
      console.log('📥 Raw API result:', result);

      // Check if we got a valid response
      if (!result || !result.refined_content) {
        console.error('❌ No refined content in response');
        toast.dismiss(loadingToast);
        throw new Error('No refined content received from API');
      }

      console.log('✅ Received refined content:', result.refined_content.substring(0, 200) + '...');

      // Parse the refined content based on section type
      let refinedData;
      try {
        refinedData = JSON.parse(result.refined_content);
        console.log('✅ Successfully parsed JSON:', refinedData);
      } catch (parseError) {
        console.error('❌ JSON parse error:', parseError);
        console.log('📄 Raw content that failed to parse:', result.refined_content);
        toast.dismiss(loadingToast);
        throw new Error(`Failed to parse refined content as JSON: ${parseError.message}`);
      }

      // Update lesson data with refined content
      const updatedData = { ...lessonData };
      let updateSuccessful = false;

      switch (editingSection) {
        case 'objectives':
          if (Array.isArray(refinedData)) {
            console.log('🎯 Processing objectives refinement');
            updatedData.objectives = refinedData.map(validateObjectiveStructure);

            // Update bloom levels in lesson_info
            const bloomLevels = extractBloomLevelsFromObjectives(updatedData.objectives);
            updatedData.lesson_info = {
              ...updatedData.lesson_info,
              selected_bloom_levels: bloomLevels
            };

            updateSuccessful = true;
            console.log('✅ Updated objectives count:', updatedData.objectives.length);
          } else {
            console.error('❌ Refined data is not an array:', typeof refinedData);
            toast.dismiss(loadingToast);
            throw new Error('Refined objectives data is not an array');
          }
          break;

        case 'lesson_plan':
          if (typeof refinedData === 'object' && refinedData !== null && !Array.isArray(refinedData)) {
            console.log('📋 Processing lesson plan refinement');
            updatedData.lesson_plan = {
              ...updatedData.lesson_plan,
              ...refinedData
            };
            updateSuccessful = true;
            console.log('✅ Updated lesson plan');
          } else {
            console.error('❌ Refined data is not an object:', typeof refinedData);
            toast.dismiss(loadingToast);
            throw new Error('Refined lesson plan data is not an object');
          }
          break;

        case 'gagne_events':
          if (Array.isArray(refinedData)) {
            console.log('🎭 Processing Gagne events refinement');
            updatedData.gagne_events = refinedData.map(event => ({
              event_number: event.event_number,
              event_name: event.event_name,
              description: event.description,
              activities: Array.isArray(event.activities) ? event.activities : [event.activities],
              duration_minutes: event.duration_minutes,
              materials_needed: Array.isArray(event.materials_needed) ? event.materials_needed : [event.materials_needed],
              assessment_strategy: event.assessment_strategy
            }));
            updateSuccessful = true;
            console.log('✅ Updated Gagne events count:', updatedData.gagne_events.length);
          } else {
            console.error('❌ Refined data is not an array:', typeof refinedData);
            toast.dismiss(loadingToast);
            throw new Error('Refined Gagne events data is not an array');
          }
          break;

        default:
          console.error('❌ Unknown section type:', editingSection);
          toast.dismiss(loadingToast);
          throw new Error(`Unknown section type: ${editingSection}`);
      }

      if (!updateSuccessful) {
        toast.dismiss(loadingToast);
        throw new Error('Failed to update lesson data with refined content');
      }

      console.log('🔄 Updating React state and local storage');

      // Update the lesson data state
      setLessonData(updatedData);

      // Update local storage with refined content
      saveDraft(updatedData);

      // Close modal and clear form
      setEditingSection(null);
      setRefinementInstructions('');
      setEditContent('');

      // Dismiss loading toast BEFORE showing success
      toast.dismiss(loadingToast);

      // Show success message
      console.log('🎉 Refinement completed successfully!');
      toast.success('Content refined successfully! ✅');

    } catch (error) {
      // Ensure loading toast is dismissed even if not done earlier
      toast.dismiss(loadingToast);

      console.error('💥 Refinement error occurred:');
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
      console.error('Section:', editingSection);
      console.error('Instructions:', refinementInstructions);

      toast.error(`Refinement failed: ${error.message}`);
    }
  };

  // Helper function to clean and format grade level
  const formatGradeLevel = (gradeLevel) => {
    const gradeMap = {
      'freshman': 'Freshman',
      'sophomore': 'Sophomore',
      'junior': 'Junior',
      'senior': 'Senior',
      'masters': 'Master\'s',
      'postgrad': 'Postgraduate'
    };

    return gradeMap[gradeLevel] || capitalize(gradeLevel);
  };

  // Helper function to clean overview text
  const cleanOverviewText = (overview) => {
    if (!overview) return "This lesson provides comprehensive coverage of the topic with engaging activities and assessments.";

    // Clean up any remaining template variables
    let cleanText = overview
      .replace(/GradeLevel\.MASTERS/g, 'master\'s')
      .replace(/GradeLevel\.FRESHMAN/g, 'freshman')
      .replace(/GradeLevel\.SOPHOMORE/g, 'sophomore')
      .replace(/GradeLevel\.JUNIOR/g, 'junior')
      .replace(/GradeLevel\.SENIOR/g, 'senior')
      .replace(/GradeLevel\.POSTGRAD/g, 'postgraduate')
      .replace(/GradeLevel\./g, '');

    return cleanText;
  };

  // FIXED: Ensure objectives exist and are properly structured
  const safeObjectives = lessonData.objectives || [];
  const objectivesByBloom = groupObjectivesByBloom(safeObjectives);
  const totalDuration = lessonData.total_duration || lessonData.lesson_info?.duration_minutes || 0;
  const optimalObjectivesForDuration = calculateOptimalObjectives(totalDuration);
  const currentObjectivesCount = safeObjectives.length;

  // FIXED: Get unique Bloom's levels from objectives
  const bloomLevelsUsed = [...new Set(safeObjectives.map(obj => obj.bloom_level))].filter(Boolean);
  const bloomLevelsDisplay = bloomLevelsUsed.length > 0
    ? bloomLevelsUsed.map(level => capitalize(level)).join(', ')
    : 'Not defined';

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Your Lesson Plan
            </h1>
            <p className="text-gray-600">
              {lessonData.lesson_info.course_title} - {lessonData.lesson_info.lesson_topic}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              onClick={() => navigate('/create')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Create New
            </Button>

            <Button
              variant="outline"
              onClick={() => setShowPDFPreview(true)}
              className="flex items-center gap-2"
            >
              <Eye className="w-4 h-4" />
              Preview
            </Button>

            <Button
              onClick={handleExportPDF}
              loading={loading}
              className="flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export PDF
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Enhanced Lesson Overview */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-primary-600" />
                    Lesson Overview
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditSection('lesson_plan', lessonData.lesson_plan)}
                  >
                    <Edit3 className="w-4 h-4" />
                  </Button>
                </CardHeader>
                <CardContent>
                  {/* Enhanced Stats Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                    {/* Duration Card with Edit Functionality */}
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

                    {/* Objectives Count with Smart Indicator */}
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

                  {/* Course and Topic Info */}
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

                  {/* Overview Description */}
                  <div className="space-y-3">
                    <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Overview</h4>
                    <p className="text-gray-700 leading-relaxed">{cleanOverviewText(lessonData.lesson_plan.overview)}</p>
                  </div>

                  {/* FIXED: Bloom's Levels Preview */}
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

                  {/* Objective Optimization Notice */}
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

            {/* FIXED: Learning Objectives */}
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

            {/* Gagne's Nine Events */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Gagne's Nine Events of Instruction</CardTitle>
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
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
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
          </div>
        </div>

        {/* Enhanced Duration Change Modal */}
        <Modal
          isOpen={showDurationModal}
          onClose={() => setShowDurationModal(false)}
          title="Change Lesson Duration"
          size="md"
        >
          <ModalBody>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  New Duration (minutes)
                </label>
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

              {/* Objective Impact Preview */}
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
            <Button variant="ghost" onClick={() => setShowDurationModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleDurationChange}
              loading={loading}
              className="flex items-center gap-2"
            >
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
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Refinement Instructions
                </label>
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
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Content (JSON)
                </label>
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
            <Button variant="ghost" onClick={() => setEditingSection(null)}>
              Cancel
            </Button>
            <Button
              onClick={handleRefineContent}
              loading={loading}
              className="flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refine Content
            </Button>
          </ModalFooter>
        </Modal>
      </div>
    </div>
  );
};

export default Results;