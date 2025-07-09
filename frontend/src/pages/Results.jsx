import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Download, ArrowLeft, Eye } from 'lucide-react';
import toast from 'react-hot-toast';

import Button from '../components/ui/Button';
import { useApi } from '../hooks/useApi';
import { useLessonDraft } from '../hooks/useLocalStorage';
import { generatePDFFilename, downloadFile } from '../utils/helpers';
import { TOAST_MESSAGES } from '../utils/constants';

import LessonOverviewSection from '../components/results/LessonOverviewSection';
import LearningObjectivesSection from '../components/results/LearningObjectivesSection';
import GagneEventsSection from '../components/results/GagneEventsSection';
import SidebarSection from '../components/results/SidebarSection';
import WYSIWYGEditingModals from '../components/results/WYSIWYGEditingModals';
import PDFPreview from '../components/lesson/PDFPreview';

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { exportToPDF, refineContent, loading } = useApi();
  const { draft, saveDraft } = useLessonDraft();

  const [lessonData, setLessonData] = useState(location.state?.lessonData || draft);
  const [showPDFPreview, setShowPDFPreview] = useState(false);
  const [editingSection, setEditingSection] = useState(null);
  const [refinementInstructions, setRefinementInstructions] = useState('');
  const [showDurationModal, setShowDurationModal] = useState(false);
  const [newDuration, setNewDuration] = useState('');
  const [showRedistributionInfo, setShowRedistributionInfo] = useState(false);
  const [lastRedistribution, setLastRedistribution] = useState(null);
  const [originalGagneEvents, setOriginalGagneEvents] = useState(null);

  useEffect(() => {
    if (!lessonData) {
      navigate('/create');
    }
  }, [lessonData, navigate]);

  if (!lessonData) return null;

  const handleExportPDF = async (lessonDataToExport = lessonData, options = {}) => {
    try {
      const pdfBlob = await exportToPDF(lessonDataToExport, {
        includeCoverPage: options.includeCoverPage ?? true,
        includeAppendices: options.includeAppendices ?? true,
        includeTableOfContents: options.includeTableOfContents ?? true
      });
      const filename = generatePDFFilename(lessonDataToExport);
      downloadFile(pdfBlob, filename);
      toast.success(TOAST_MESSAGES.SUCCESS.PDF_EXPORTED);
    } catch (error) {
      console.error('PDF Export Error:', error);
      toast.error(TOAST_MESSAGES.ERROR.EXPORT_FAILED);
    }
  };

  const handlePreviewPDF = () => {
    setShowPDFPreview(true);
  };

  const commonProps = {
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
    setShowRedistributionInfo
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Lesson Plan</h1>
            {lessonData.lesson_plan?.title && (
              <h2 className="text-xl font-semibold text-gray-800">
                {lessonData.lesson_plan.title}
              </h2>
            )}
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={() => navigate('/create')} className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Create New
            </Button>
            <Button
              variant="outline"
              onClick={handlePreviewPDF}
              className="flex items-center gap-2"
            >
              <Eye className="w-4 h-4" />
              Preview
            </Button>
            <Button onClick={() => handleExportPDF()} loading={loading} className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export PDF
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <LessonOverviewSection {...commonProps} setShowDurationModal={setShowDurationModal} setNewDuration={setNewDuration} />
            <LearningObjectivesSection {...commonProps} />
            <GagneEventsSection {...commonProps} showRedistributionInfo={showRedistributionInfo} setShowRedistributionInfo={setShowRedistributionInfo} />
          </div>
          <div className="space-y-6">
            <SidebarSection lessonData={lessonData} />
          </div>
        </div>

        {/* WYSIWYG Editing Modals */}
        <WYSIWYGEditingModals
          {...commonProps}
          showDurationModal={showDurationModal}
          setShowDurationModal={setShowDurationModal}
          newDuration={newDuration}
          setNewDuration={setNewDuration}
          showRedistributionInfo={showRedistributionInfo}
          setShowRedistributionInfo={setShowRedistributionInfo}
        />

        {/* PDF Preview Modal */}
        <PDFPreview
          lessonData={lessonData}
          isOpen={showPDFPreview}
          onClose={() => setShowPDFPreview(false)}
          onExport={handleExportPDF}
        />
      </div>
    </div>
  );
};

export default Results;