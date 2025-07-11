// Update to frontend/src/components/lesson/PDFPreview.jsx

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Download,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Eye,
  Settings,
  FileText,
  Maximize2,
  Minimize2
} from 'lucide-react';
import Button from '../ui/Button';
import { formatDuration, formatGradeLevel, cleanOverviewText, capitalize } from '../../utils/helpers';
import {
  TableOfContentsPage,
  LessonOverviewPage,
  LearningObjectivesPage,
  LessonPlanPage,
  GagneEventsPage,
  BloomAppendixPage,
  GagneAppendixPage
} from './PDFPreviewPages';

const PDFPreview = ({ lessonData, isOpen, onClose, onExport }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageInputValue, setPageInputValue] = useState('1');
  const [zoomLevel, setZoomLevel] = useState(85);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showExportOptions, setShowExportOptions] = useState(false);
  const [exportOptions, setExportOptions] = useState({
    includeCoverPage: true,
    includeAppendices: true,
    includeTableOfContents: true
  });

  const previewRef = useRef(null);

  // Calculate total pages based on export options
  const calculateTotalPages = () => {
    let pages = 0;

    // Cover page (conditional based on export options)
    if (exportOptions.includeCoverPage) pages += 1;

    if (exportOptions.includeTableOfContents) pages += 1; // TOC
    pages += 1; // Overview
    pages += 1; // Objectives
    pages += 1; // Lesson Plan

    // Gagne Events (3 per page)
    const gagneEventsPerPage = 3;
    const gagnePageCount = Math.ceil((lessonData.gagne_events?.length || 0) / gagneEventsPerPage);
    pages += gagnePageCount;

    if (exportOptions.includeAppendices) pages += 2; // Bloom + Gagne appendices

    return pages;
  };

  const totalPages = calculateTotalPages();

  // Handle page adjustment when export options change
  useEffect(() => {
    const newTotalPages = calculateTotalPages();

    // If current page exceeds new total pages, go to last page
    if (currentPage > newTotalPages) {
      setCurrentPage(newTotalPages);
      setPageInputValue(newTotalPages.toString());
    }

    // If we're on page 1 and cover page gets disabled, stay on page 1 (which will now be different content)
    // If cover page gets enabled and we're on page 1, stay on page 1 (which will now be the cover page)
    // This provides smooth transitions

  }, [exportOptions.includeCoverPage, exportOptions.includeTableOfContents, exportOptions.includeAppendices]);

  // Sync input value when currentPage changes (from navigation buttons, thumbnails, etc.)
  useEffect(() => {
    setPageInputValue(currentPage.toString());
  }, [currentPage]);

  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 15, 150));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 15, 50));
  const handleResetZoom = () => setZoomLevel(85);

  const handlePrevPage = () => setCurrentPage(prev => Math.max(prev - 1, 1));
  const handleNextPage = () => setCurrentPage(prev => Math.min(prev + 1, totalPages));

  const handleExport = () => {
    onExport(lessonData, exportOptions);
    onClose();
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowLeft':
          handlePrevPage();
          break;
        case 'ArrowRight':
          handleNextPage();
          break;
        case 'Escape':
          onClose();
          break;
        case '+':
        case '=':
          handleZoomIn();
          break;
        case '-':
          handleZoomOut();
          break;
        case '0':
          handleResetZoom();
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [isOpen]);

  // Generate current date for display
  const currentDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const renderPage = () => {
    let pageIndex = 1;

    // Cover Page (conditional based on export options)
    if (exportOptions.includeCoverPage) {
      if (currentPage === pageIndex) {
        return <CoverPage lessonData={lessonData} currentDate={currentDate} />;
      }
      pageIndex++;
    }

    // Table of Contents
    if (exportOptions.includeTableOfContents && currentPage === pageIndex) {
      return <TableOfContentsPage />;
    }
    if (exportOptions.includeTableOfContents) pageIndex++;

    // Lesson Overview
    if (currentPage === pageIndex) {
      return <LessonOverviewPage lessonData={lessonData} />;
    }
    pageIndex++;

    // Learning Objectives
    if (currentPage === pageIndex) {
      return <LearningObjectivesPage lessonData={lessonData} />;
    }
    pageIndex++;

    // Lesson Plan Details
    if (currentPage === pageIndex) {
      return <LessonPlanPage lessonData={lessonData} />;
    }
    pageIndex++;

    // Gagne Events (3 per page)
    const gagneEventsPerPage = 3;
    const gagnePageCount = Math.ceil((lessonData.gagne_events?.length || 0) / gagneEventsPerPage);

    if (currentPage >= pageIndex && currentPage < pageIndex + gagnePageCount) {
      const gagnePageIndex = currentPage - pageIndex;
      const startIndex = gagnePageIndex * gagneEventsPerPage;
      const endIndex = Math.min(startIndex + gagneEventsPerPage, lessonData.gagne_events?.length || 0);
      const eventsForPage = lessonData.gagne_events?.slice(startIndex, endIndex) || [];

      return (
        <GagneEventsPage
          events={eventsForPage}
          pageNumber={gagnePageIndex + 1}
          totalGagnePages={gagnePageCount}
        />
      );
    }
    pageIndex += gagnePageCount;

    // Appendices
    if (exportOptions.includeAppendices) {
      if (currentPage === pageIndex) {
        return <BloomAppendixPage />;
      }
      pageIndex++;

      if (currentPage === pageIndex) {
        return <GagneAppendixPage />;
      }
    }

    return <div className="h-full flex items-center justify-center text-gray-500">Page not found</div>;
  };

  const getPageTitle = () => {
    let pageIndex = 1;

    if (exportOptions.includeCoverPage) {
      if (currentPage === pageIndex) return 'Cover Page';
      pageIndex++;
    }

    if (exportOptions.includeTableOfContents && currentPage === pageIndex) return 'Table of Contents';
    if (exportOptions.includeTableOfContents) pageIndex++;

    if (currentPage === pageIndex) return 'Lesson Overview';
    pageIndex++;

    if (currentPage === pageIndex) return 'Learning Objectives';
    pageIndex++;

    if (currentPage === pageIndex) return 'Lesson Plan Details';
    pageIndex++;

    const gagnePageCount = Math.ceil((lessonData.gagne_events?.length || 0) / 3);
    if (currentPage >= pageIndex && currentPage < pageIndex + gagnePageCount) {
      return 'Gagne\'s Nine Events';
    }
    pageIndex += gagnePageCount;

    if (exportOptions.includeAppendices) {
      if (currentPage === pageIndex) return 'Bloom\'s Taxonomy Reference';
      pageIndex++;
      if (currentPage === pageIndex) return 'Gagne\'s Events Reference';
    }

    return 'Page';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-gray-900/95 backdrop-blur-sm">
      <div className={`h-full flex flex-col ${isFullscreen ? '' : 'p-4'}`}>
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">PDF Preview</h2>
            </div>
            <div className="text-sm text-gray-500">
              {lessonData.lesson_info?.course_title} - {lessonData.lesson_info?.lesson_topic}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowExportOptions(!showExportOptions)}
              className="flex items-center gap-2"
            >
              <Settings className="w-4 h-4" />
              Options
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="flex items-center gap-2"
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </Button>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Export Options Panel */}
        <AnimatePresence>
          {showExportOptions && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200 px-6 py-4"
            >
              <div className="flex items-center gap-6">
                <h3 className="text-sm font-medium text-gray-700">Export Options:</h3>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={exportOptions.includeCoverPage}
                    onChange={(e) => setExportOptions(prev => ({ ...prev, includeCoverPage: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Cover Page</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={exportOptions.includeTableOfContents}
                    onChange={(e) => setExportOptions(prev => ({ ...prev, includeTableOfContents: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Table of Contents</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={exportOptions.includeAppendices}
                    onChange={(e) => setExportOptions(prev => ({ ...prev, includeAppendices: e.target.checked }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">Appendices</span>
                </label>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* Sidebar Toolbar */}
          <div className="bg-white border-r border-gray-200 px-4 py-6 flex flex-col gap-6 min-w-[220px] shadow-sm">
            {/* Current Page Info */}
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-900 mb-1">{getPageTitle()}</h3>
              <p className="text-xs text-gray-500">Page {currentPage} of {totalPages}</p>
            </div>

            {/* Navigation Controls */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-900">Navigation</h3>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handlePrevPage}
                  disabled={currentPage <= 1}
                  className="flex items-center justify-center gap-1"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span className="text-xs">Prev</span>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleNextPage}
                  disabled={currentPage >= totalPages}
                  className="flex items-center justify-center gap-1"
                >
                  <span className="text-xs">Next</span>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>

              {/* Page Input */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Go to:</span>
                <input
                  type="text"
                  value={pageInputValue}
                  onChange={(e) => setPageInputValue(e.target.value)}
                  onBlur={() => {
                    const page = parseInt(pageInputValue);
                    if (page >= 1 && page <= totalPages) {
                      setCurrentPage(page);
                    } else {
                      // Reset to current page if invalid
                      setPageInputValue(currentPage.toString());
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      const page = parseInt(pageInputValue);
                      if (page >= 1 && page <= totalPages) {
                        setCurrentPage(page);
                      } else {
                        setPageInputValue(currentPage.toString());
                      }
                      e.target.blur();
                    }
                    if (e.key === 'Escape') {
                      setPageInputValue(currentPage.toString());
                      e.target.blur();
                    }
                  }}
                  className="w-16 px-2 py-1 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center"
                  placeholder={totalPages.toString()}
                />
              </div>
            </div>

            {/* Zoom Controls */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-900">Zoom</h3>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" onClick={handleZoomOut} disabled={zoomLevel <= 50}>
                  <ZoomOut className="w-4 h-4" />
                </Button>
                <span className="text-sm text-gray-600 min-w-[50px] text-center font-mono">{zoomLevel}%</span>
                <Button variant="ghost" size="sm" onClick={handleZoomIn} disabled={zoomLevel >= 150}>
                  <ZoomIn className="w-4 h-4" />
                </Button>
              </div>
              <Button variant="ghost" size="sm" onClick={handleResetZoom} className="w-full text-xs">
                <RotateCcw className="w-3 h-3 mr-1" />
                Reset Zoom
              </Button>

              {/* Preset Zoom Levels */}
              <div className="grid grid-cols-3 gap-1">
                {[75, 100, 125].map(zoom => (
                  <button
                    key={zoom}
                    onClick={() => setZoomLevel(zoom)}
                    className={`px-2 py-1 text-xs rounded transition-colors ${
                      zoomLevel === zoom 
                        ? 'bg-blue-100 text-blue-800 font-medium' 
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    {zoom}%
                  </button>
                ))}
              </div>
            </div>

            {/* Page Navigation Thumbnails */}
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-900">Pages</h3>
              <div className="space-y-1 max-h-64 overflow-y-auto custom-scrollbar">
                {Array.from({ length: totalPages }, (_, i) => {
                  const pageNum = i + 1;
                  let pageTitle = 'Page';
                  let pageIndex = 1;

                  // Determine page title based on current export options
                  if (exportOptions.includeCoverPage) {
                    if (pageNum === pageIndex) pageTitle = 'Cover';
                    pageIndex++;
                  }

                  if (exportOptions.includeTableOfContents) {
                    if (pageNum === pageIndex) pageTitle = 'Contents';
                    pageIndex++;
                  }

                  if (pageNum === pageIndex) pageTitle = 'Overview';
                  else if (pageNum === pageIndex + 1) pageTitle = 'Objectives';
                  else if (pageNum === pageIndex + 2) pageTitle = 'Plan';
                  else if (pageNum >= pageIndex + 3 && pageNum < totalPages - (exportOptions.includeAppendices ? 1 : -1)) pageTitle = 'Events';
                  else if (exportOptions.includeAppendices && pageNum >= totalPages - 1) pageTitle = pageNum === totalPages - 1 ? 'Bloom' : 'Gagne';

                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`w-full text-left px-3 py-2 text-xs rounded transition-all duration-200 ${
                        currentPage === pageNum 
                          ? 'bg-blue-100 text-blue-800 font-medium shadow-sm border border-blue-200' 
                          : 'text-gray-600 hover:bg-gray-100 border border-transparent'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span>{pageNum}. {pageTitle}</span>
                        {currentPage === pageNum && <Eye className="w-3 h-3" />}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>


          </div>

          {/* Preview Area */}
          <div className="flex-1 bg-gradient-to-br from-gray-100 to-gray-200 relative">
            <div className="absolute inset-0 overflow-auto custom-scrollbar pdf-preview-scroll-area">
              <div className="p-8 flex justify-center" style={{ minHeight: '100%' }}>
                <div
                  ref={previewRef}
                  className="bg-white shadow-2xl transition-all duration-300 border border-gray-300 mb-8"
                  style={{
                    transform: `scale(${zoomLevel / 100})`,
                    transformOrigin: 'top center',
                    width: '210mm',
                    height: 'auto',
                    maxWidth: '210mm',
                    minHeight: `${297 * (zoomLevel / 100)}mm`
                  }}
                >
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={`${currentPage}-${exportOptions.includeCoverPage}-${exportOptions.includeTableOfContents}-${exportOptions.includeAppendices}`}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.2 }}
                      className="w-full h-full"
                    >
                      {renderPage()}
                    </motion.div>
                  </AnimatePresence>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-white border-t border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-4">
            <div className="text-sm text-gray-500">
              {lessonData.objectives?.length || 0} objectives • {formatDuration(lessonData.total_duration)} • {totalPages} pages
            </div>
            <div className="text-xs text-gray-400">
              Press Esc to close • Use arrow keys to navigate
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={onClose}>
              Close Preview
            </Button>
            <Button onClick={handleExport} className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export PDF
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Cover Page Component
const CoverPage = ({ lessonData, currentDate }) => (
  <div className="h-full p-16 flex flex-col justify-center items-center text-center bg-gradient-to-br from-blue-50 via-white to-indigo-50 relative overflow-hidden">
    {/* Background Pattern */}
    <div className="absolute inset-0 opacity-10">
      <svg className="w-full h-full" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#3B82F6" strokeWidth="0.5"/>
          </pattern>
        </defs>
        <rect width="100" height="100" fill="url(#grid)" />
      </svg>
    </div>

    {/* Header Accent */}
    <div className="absolute top-0 left-0 w-full h-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600"></div>

    <div className="relative z-10 max-w-2xl">
      {/* Institution Logo Area */}
      <div className="mb-8">
        <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
          <FileText className="w-10 h-10 text-white" />
        </div>
        <p className="text-sm text-gray-600 font-semibold tracking-wider uppercase">Professional Lesson Plan</p>
      </div>

      {/* Main Title */}
      <h1 className="text-4xl font-bold text-gray-900 mb-4 leading-tight">
        {lessonData.lesson_info?.course_title}
      </h1>

      {/* Subtitle */}
      <h2 className="text-2xl font-semibold text-blue-700 mb-12">
        {lessonData.lesson_info?.lesson_topic}
      </h2>

      {/* Details Grid */}
      <div className="grid grid-cols-2 gap-8 mb-12 text-left">
        <div className="space-y-4">
          <div className="border-l-4 border-blue-500 pl-4 bg-white bg-opacity-60 p-3 rounded-r-lg">
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Grade Level</p>
            <p className="text-lg font-bold text-gray-900">
              {formatGradeLevel(lessonData.lesson_info?.grade_level)}
            </p>
          </div>
          <div className="border-l-4 border-green-500 pl-4 bg-white bg-opacity-60 p-3 rounded-r-lg">
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Duration</p>
            <p className="text-lg font-bold text-gray-900">
              {formatDuration(lessonData.total_duration || lessonData.lesson_info?.duration_minutes)}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="border-l-4 border-purple-500 pl-4 bg-white bg-opacity-60 p-3 rounded-r-lg">
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Learning Objectives</p>
            <p className="text-lg font-bold text-gray-900">
              {lessonData.objectives?.length || 0} Objectives
            </p>
          </div>
          <div className="border-l-4 border-orange-500 pl-4 bg-white bg-opacity-60 p-3 rounded-r-lg">
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Created</p>
            <p className="text-lg font-bold text-gray-900">{currentDate}</p>
          </div>
        </div>
      </div>

      {/* Bloom's Levels Preview */}
      <div className="mb-12">
        <p className="text-sm font-medium text-gray-500 mb-4 uppercase tracking-wide">Cognitive Levels Addressed</p>
        <div className="flex flex-wrap justify-center gap-3">
          {[...new Set(lessonData.objectives?.map(obj => obj.bloom_level) || [])].map(level => (
            <span
              key={level}
              className={`px-4 py-2 rounded-full text-sm font-semibold shadow-sm ${getBloomColorClass(level)}`}
            >
              {capitalize(level)}
            </span>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center text-sm text-gray-600 bg-white bg-opacity-80 p-4 rounded-lg shadow-sm">
        <p className="mb-2 font-medium">Generated using AI-Powered Lesson Planning</p>
        <p className="text-xs">Based on Bloom's Taxonomy & Gagne's Nine Events of Instruction</p>
      </div>
    </div>
  </div>
);

// Helper function for Bloom's level colors
const getBloomColorClass = (level) => {
  const colorMap = {
    remember: 'bg-red-100 text-red-800 border border-red-200',
    understand: 'bg-orange-100 text-orange-800 border border-orange-200',
    apply: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
    analyze: 'bg-green-100 text-green-800 border border-green-200',
    evaluate: 'bg-blue-100 text-blue-800 border border-blue-200',
    create: 'bg-purple-100 text-purple-800 border border-purple-200'
  };
  return colorMap[level] || 'bg-gray-100 text-gray-800 border border-gray-200';
};

export default PDFPreview;