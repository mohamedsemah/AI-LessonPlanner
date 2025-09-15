import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Presentation, 
  Eye, 
  Download, 
  Settings, 
  Accessibility, 
  Brain, 
  Users,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react';
import toast from 'react-hot-toast';

import Button from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { useApi } from '../hooks/useApi';
import { useLessonDraft } from '../hooks/useLocalStorage';
import { TOAST_MESSAGES } from '../utils/constants';

import UDLPreferencesForm from '../components/udl/UDLPreferencesForm';
import CourseContentPreview from '../components/udl/CourseContentPreview';
import UDLComplianceReport from '../components/udl/UDLComplianceReport';
import ContentRefinementModal from '../components/udl/ContentRefinementModal';

const CourseContent = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { generateCourseContent, refineContent, exportToPowerPoint, exportToPDF, loading } = useApi();
  const { draft } = useLessonDraft();

  const [lessonData, setLessonData] = useState(location.state?.lessonData || draft);
  const [courseContent, setCourseContent] = useState(null);
  const [udlPreferences, setUdlPreferences] = useState({
    presentationStyle: 'balanced',
    accessibilityLevel: 'standard',
    targetAudience: [],
    technologyConstraints: '',
    slideDuration: 'balanced'
  });
  
  const [designPreferences, setDesignPreferences] = useState({
    theme: 'modern',
    template: 'modern'
  });
  const [showRefinementModal, setShowRefinementModal] = useState(false);
  const [selectedSlide, setSelectedSlide] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (!lessonData) {
      navigate('/create');
    }
  }, [lessonData, navigate]);

  // Debug logging for courseContent state
  useEffect(() => {
    console.log('🔄 courseContent state changed:', {
      hasContent: !!courseContent,
      totalSlides: courseContent?.total_slides,
      presentationTitle: courseContent?.presentation_title,
      slidesLength: courseContent?.slides?.length
    });
  }, [courseContent]);

  const handleGenerateContent = async () => {
    if (!lessonData) {
      toast.error('No lesson data available');
      return;
    }

    console.log('🚀 Starting content generation...');
    console.log('📋 Lesson data:', lessonData);
    console.log('⚙️ UDL preferences:', udlPreferences);

    setIsGenerating(true);
    const loadingToast = toast.loading('Generating UDL-compliant course content...');

    try {
      const request = {
        lesson_data: lessonData,
        presentation_preferences: {
          style: udlPreferences.presentationStyle,
          slide_duration: udlPreferences.slideDuration
        },
        accessibility_requirements: udlPreferences.accessibilityLevel === 'enhanced' 
          ? ['alt_text', 'captions', 'keyboard_navigation', 'screen_reader', 'high_contrast']
          : ['alt_text', 'keyboard_navigation'],
        target_audience_needs: udlPreferences.targetAudience,
        technology_constraints: udlPreferences.technologyConstraints,
        slide_duration_preference: udlPreferences.slideDuration
      };

      console.log('📤 Sending request to backend:', request);

      const content = await generateCourseContent(request);
      
      console.log('📥 Received content from backend:', content);
      console.log('📊 Content summary:', {
        total_slides: content?.total_slides,
        estimated_duration: content?.estimated_duration,
        presentation_title: content?.presentation_title,
        slides_count: content?.slides?.length
      });

      setCourseContent(content);
      
      toast.dismiss(loadingToast);
      toast.success('Course content generated successfully!');
    } catch (error) {
      console.error('❌ Content generation error:', error);
      toast.dismiss(loadingToast);
      toast.error('Failed to generate course content. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRefineSlide = async (slideId, refinementType, instructions) => {
    if (!courseContent) return;

    const slide = courseContent.slides.find(s => s.slide_number === slideId);
    if (!slide) return;

    try {
      const request = {
        slide_id: slideId,
        refinement_type: refinementType,
        refinement_instructions: instructions,
        current_content: slide
      };

      const refinedContent = await refineContent(request);
      
      // Update the slide with refined content
      const updatedSlides = courseContent.slides.map(s => 
        s.slide_number === slideId 
          ? { ...s, ...refinedContent.refined_content }
          : s
      );

      setCourseContent({
        ...courseContent,
        slides: updatedSlides
      });

      toast.success('Slide content refined successfully!');
      setShowRefinementModal(false);
    } catch (error) {
      console.error('Refinement error:', error);
      toast.error('Failed to refine slide content.');
    }
  };

  const handleExportContent = async (format) => {
    if (!courseContent || !lessonData) {
      toast.error('No course content available for export');
      return;
    }

    try {
      const loadingToast = toast.loading(`Exporting to ${format.toUpperCase()}...`);
      
      let blob;
      if (format === 'pptx') {
        blob = await exportToPowerPoint(courseContent, lessonData, designPreferences);
      } else if (format === 'pdf') {
        blob = await exportToPDF(courseContent, lessonData, designPreferences);
      } else {
        toast.error(`Unsupported format: ${format}`);
        return;
      }

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename
      const lessonInfo = lessonData.lesson_info || {};
      const filename = `${lessonInfo.course_title || 'Course'}_${lessonInfo.lesson_topic || 'Lesson'}.${format}`;
      link.download = filename.replace(/\s+/g, '_').replace(/[\/\\]/g, '_');
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up
      window.URL.revokeObjectURL(url);
      
      toast.dismiss(loadingToast);
      toast.success(`${format.toUpperCase()} exported successfully!`);
      
    } catch (error) {
      console.error(`Export error:`, error);
      toast.error(`Failed to export ${format.toUpperCase()}: ${error.message}`);
    }
  };

  if (!lessonData) return null;

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Presentation className="w-8 h-8 text-primary-600" />
                Course Content Generator
              </h1>
              <p className="mt-2 text-gray-600">
                Generate UDL-compliant multimodal presentations from your lesson plan
              </p>
            </div>
            <Button
              onClick={() => navigate('/results')}
              variant="outline"
              className="flex items-center gap-2"
            >
              <Eye className="w-4 h-4" />
              View Lesson Plan
            </Button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* UDL Preferences Panel */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5 text-primary-600" />
                  UDL Preferences
                </CardTitle>
              </CardHeader>
              <CardContent>
                <UDLPreferencesForm
                  preferences={udlPreferences}
                  onChange={setUdlPreferences}
                />
                
                {/* Design Preferences */}
                <div className="mt-6 border-t pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Eye className="w-5 h-5 text-primary-600" />
                    Design Preferences
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Theme
                      </label>
                      <select
                        value={designPreferences.theme}
                        onChange={(e) => setDesignPreferences(prev => ({ ...prev, theme: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="modern">Modern</option>
                        <option value="corporate">Corporate</option>
                        <option value="creative">Creative</option>
                        <option value="minimal">Minimal</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Template
                      </label>
                      <select
                        value={designPreferences.template}
                        onChange={(e) => setDesignPreferences(prev => ({ ...prev, template: e.target.value }))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        <option value="modern">Modern</option>
                        <option value="corporate">Corporate</option>
                        <option value="creative">Creative</option>
                        <option value="minimal">Minimal</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6 space-y-4">
                  <Button
                    onClick={handleGenerateContent}
                    disabled={isGenerating || loading}
                    className="w-full"
                    size="lg"
                  >
                    {isGenerating ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                        Generating Content...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Generate Course Content
                      </>
                    )}
                  </Button>
                  
                  {courseContent && (
                    <div className="space-y-2">
                      <Button
                        onClick={() => handleExportContent('pptx')}
                        variant="outline"
                        className="w-full"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Export as PowerPoint
                      </Button>
                      <Button
                        onClick={() => handleExportContent('pdf')}
                        variant="outline"
                        className="w-full"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Export as PDF
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Content Preview */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-2"
          >
            {(() => {
              console.log('🎨 Rendering content preview section:', {
                hasCourseContent: !!courseContent,
                courseContentType: typeof courseContent,
                courseContentKeys: courseContent ? Object.keys(courseContent) : null
              });
              
              return courseContent ? (
                <div className="space-y-6">
                  {/* Content Overview */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                          <Presentation className="w-5 h-5 text-primary-600" />
                          {courseContent.presentation_title}
                        </span>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {courseContent.estimated_duration} min
                          </span>
                          <span className="flex items-center gap-1">
                            <Eye className="w-4 h-4" />
                            {courseContent.total_slides} slides
                          </span>
                        </div>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
                          <CheckCircle className="w-5 h-5 text-green-600" />
                          <div>
                            <p className="font-medium text-green-900">UDL Compliant</p>
                            <p className="text-sm text-green-700">
                              {Math.round(courseContent.udl_compliance_report.overall_compliance * 100)}% compliance
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
                          <Accessibility className="w-5 h-5 text-blue-600" />
                          <div>
                            <p className="font-medium text-blue-900">Accessible</p>
                            <p className="text-sm text-blue-700">
                              {courseContent.accessibility_features.length} features
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg">
                          <Users className="w-5 h-5 text-purple-600" />
                          <div>
                            <p className="font-medium text-purple-900">Multimodal</p>
                            <p className="text-sm text-purple-700">
                              Multiple learning modalities
                            </p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* UDL Compliance Report */}
                  <UDLComplianceReport 
                    compliance={courseContent.udl_compliance_report}
                    recommendations={courseContent.udl_compliance_report.recommendations}
                  />

                  {/* Slides Preview */}
                  <CourseContentPreview
                    slides={courseContent.slides}
                    onRefineSlide={(slide) => {
                      setSelectedSlide(slide);
                      setShowRefinementModal(true);
                    }}
                  />
                </div>
              ) : (
                <Card>
                  <CardContent className="py-12">
                    <div className="text-center">
                      <Presentation className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Ready to Generate Course Content
                      </h3>
                      <p className="text-gray-600 mb-6">
                        Configure your UDL preferences and generate multimodal course content 
                        based on your lesson plan.
                      </p>
                      <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Accessibility className="w-4 h-4" />
                          UDL Compliant
                        </span>
                        <span className="flex items-center gap-1">
                          <Brain className="w-4 h-4" />
                          AI Generated
                        </span>
                        <span className="flex items-center gap-1">
                          <Eye className="w-4 h-4" />
                          Multimodal
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })()}
          </motion.div>
        </div>

        {/* Content Refinement Modal */}
        {showRefinementModal && selectedSlide && (
          <ContentRefinementModal
            slide={selectedSlide}
            onRefine={handleRefineSlide}
            onClose={() => {
              setShowRefinementModal(false);
              setSelectedSlide(null);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default CourseContent; 