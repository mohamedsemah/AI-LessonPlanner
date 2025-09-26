import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Download, Edit3, Eye, RefreshCw, ArrowLeft } from 'lucide-react';
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
  downloadFile
} from '../utils/helpers';
import { TOAST_MESSAGES } from '../utils/constants';

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { exportToPDF, refineContent, loading } = useApi();
  const { draft, clearDraft } = useLessonDraft();

  const [lessonData, setLessonData] = useState(location.state?.lessonData || draft);
  const [showPDFPreview, setShowPDFPreview] = useState(false);
  const [editingSection, setEditingSection] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [refinementInstructions, setRefinementInstructions] = useState('');

  useEffect(() => {
    if (!lessonData) {
      navigate('/create');
    }
  }, [lessonData, navigate]);

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

  const handleRefineContent = async () => {
    if (!refinementInstructions.trim()) {
      toast.error('Please provide refinement instructions');
      return;
    }

    try {
      const refinementRequest = {
        section_type: editingSection,
        section_content: editContent,
        refinement_instructions: refinementInstructions,
        lesson_context: lessonData.lesson_info
      };

      const result = await refineContent(refinementRequest);

      // Update lesson data with refined content
      const updatedData = { ...lessonData };
      // Parse and update the specific section
      // This would need more sophisticated parsing based on section type

      setLessonData(updatedData);
      setEditingSection(null);
      toast.success(TOAST_MESSAGES.SUCCESS.CONTENT_REFINED);

    } catch (error) {
      toast.error(TOAST_MESSAGES.ERROR.REFINEMENT_FAILED);
    }
  };

  const objectivesByBloom = groupObjectivesByBloom(lessonData.objectives);
  const totalDuration = lessonData.total_duration;

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
            {/* Lesson Overview */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Lesson Overview</CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditSection('overview', lessonData.lesson_plan)}
                  >
                    <Edit3 className="w-4 h-4" />
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <span className="text-sm font-medium text-gray-500">Duration</span>
                      <p className="text-lg font-semibold">{formatDuration(totalDuration)}</p>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-500">Grade Level</span>
                      <p className="text-lg font-semibold capitalize">{lessonData.lesson_info.grade_level}</p>
                    </div>
                  </div>
                  <p className="text-gray-700">{lessonData.lesson_plan.overview}</p>
                </CardContent>
              </Card>
            </motion.div>

            {/* Learning Objectives */}
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
                    onClick={() => handleEditSection('objectives', lessonData.objectives)}
                  >
                    <Edit3 className="w-4 h-4" />
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {Object.entries(objectivesByBloom).map(([level, objectives]) => (
                      <div key={level}>
                        <div className="flex items-center gap-2 mb-3">
                          <Badge variant={level} size="sm">
                            {level.charAt(0).toUpperCase() + level.slice(1)}
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
                    {lessonData.gagne_events.map((event, index) => (
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
                    ))}
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
                      <span className="font-semibold">{lessonData.objectives.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Bloom's Levels</span>
                      <span className="font-semibold">{Object.keys(objectivesByBloom).length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Duration</span>
                      <span className="font-semibold">{formatDuration(totalDuration)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Events</span>
                      <span className="font-semibold">{lessonData.gagne_events.length}</span>
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
                    {lessonData.lesson_plan.prerequisites && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">Prerequisites</h5>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {lessonData.lesson_plan.prerequisites.map((prereq, index) => (
                            <li key={index}>• {prereq}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {lessonData.lesson_plan.materials && (
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

                    {lessonData.lesson_plan.assessment_methods && (
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