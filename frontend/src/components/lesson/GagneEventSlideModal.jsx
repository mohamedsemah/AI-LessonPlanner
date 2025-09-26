import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  X, 
  ChevronLeft, 
  ChevronRight, 
  Play, 
  Pause, 
  Volume2, 
  VolumeX,
  Eye,
  Clock,
  BookOpen,
  Users,
  ArrowLeft,
  ArrowRight
} from 'lucide-react';
import Button from '../ui/Button';
import Badge from '../ui/Badge';

const GagneEventSlideModal = ({ isOpen, onClose, eventSlides }) => {
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);
  const [showNotes, setShowNotes] = useState(false);
  const [showFullscreen, setShowFullscreen] = useState(false);

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen && eventSlides) {
      setCurrentSlideIndex(0);
      setIsPlaying(false);
      setIsAudioPlaying(false);
      setShowNotes(false);
    }
  }, [isOpen, eventSlides]);

  // Auto-play functionality
  useEffect(() => {
    if (isPlaying && eventSlides) {
      const interval = setInterval(() => {
        setCurrentSlideIndex(prev => {
          const nextIndex = prev + 1;
          if (nextIndex >= eventSlides.slides.length) {
            setIsPlaying(false);
            return prev;
          }
          return nextIndex;
        });
      }, 5000); // 5 seconds per slide

      return () => clearInterval(interval);
    }
  }, [isPlaying, eventSlides]);

  const currentSlide = eventSlides?.slides?.[currentSlideIndex];
  const totalSlides = eventSlides?.slides?.length || 0;

  const handlePreviousSlide = () => {
    setCurrentSlideIndex(prev => Math.max(0, prev - 1));
  };

  const handleNextSlide = () => {
    setCurrentSlideIndex(prev => Math.min(totalSlides - 1, prev + 1));
  };

  const handleSlideSelect = (index) => {
    setCurrentSlideIndex(index);
  };

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const toggleAudio = () => {
    setIsAudioPlaying(!isAudioPlaying);
  };

  const toggleNotes = () => {
    setShowNotes(!showNotes);
  };

  const toggleFullscreen = () => {
    setShowFullscreen(!showFullscreen);
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowLeft':
          handlePreviousSlide();
          break;
        case 'ArrowRight':
          handleNextSlide();
          break;
        case ' ':
          e.preventDefault();
          togglePlayPause();
          break;
        case 'Escape':
          onClose();
          break;
        case 'n':
        case 'N':
          toggleNotes();
          break;
        case 'f':
        case 'F':
          toggleFullscreen();
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [isOpen, currentSlideIndex, totalSlides]);

  // Don't render if not open or no slides data
  if (!isOpen || !eventSlides) return null;

  const renderSlideContent = () => {
    if (!currentSlide) return null;

    return (
      <div className="relative w-full h-full bg-white rounded-lg shadow-lg flex flex-col">
        {/* Slide Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">{currentSlide.title}</h2>
              <p className="text-blue-100 text-sm">
                Event {eventSlides.event_number}: {eventSlides.event_name}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" size="sm">
                Slide {currentSlide.slide_number} of {totalSlides}
              </Badge>
              <Badge variant="outline" size="sm" className="text-blue-100 border-blue-300">
                {currentSlide.duration_minutes} min
              </Badge>
            </div>
          </div>
        </div>

        {/* Slide Content */}
        <div 
          className="p-6 flex-1 overflow-y-auto"
          style={{
            backgroundColor: currentSlide.background_color || '#ffffff',
            color: currentSlide.text_color || '#000000',
            fontFamily: currentSlide.font_family || 'Arial, sans-serif',
            fontSize: currentSlide.font_size || '16px',
            lineHeight: currentSlide.line_height || '1.5'
          }}
        >
          <div className="max-w-4xl mx-auto pb-8">
            {/* Main Content */}
            <div 
              className="prose prose-lg max-w-none mb-6"
              style={{
                '--tw-prose-headings': currentSlide.heading_color || '#1a365d',
                '--tw-prose-body': currentSlide.text_color || '#000000',
                '--tw-prose-bold': currentSlide.text_color || '#000000',
                '--tw-prose-links': currentSlide.link_color || '#0000ff',
                '--tw-prose-bullets': currentSlide.text_color || '#000000'
              }}
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {currentSlide.main_content}
              </ReactMarkdown>
            </div>

            {/* Visual Elements */}
            {currentSlide.visual_elements && currentSlide.visual_elements.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Eye className="w-5 h-5" />
                  Visual Elements
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {currentSlide.visual_elements.map((element, index) => (
                    <div 
                      key={index} 
                      className="rounded-lg p-4"
                      style={{
                        border: element.border || '1px solid #e5e7eb',
                        backgroundColor: element.background_color || '#ffffff',
                        color: element.text_color || '#000000',
                        fontFamily: element.font_family || 'Arial, sans-serif',
                        borderRadius: element.border_radius || '8px',
                        padding: element.padding || '16px',
                        margin: element.margin || '0',
                        textAlign: element.text_align || 'left'
                      }}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" size="sm">
                          {element.type}
                        </Badge>
                        <span className="text-sm text-gray-600">{element.size}</span>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{element.description}</p>
                      <p className="text-xs text-gray-500 italic">{element.alt_text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}


            {/* Key Points */}
            {currentSlide.key_points && currentSlide.key_points.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  Key Points
                </h3>
                <ul className="space-y-2">
                  {currentSlide.key_points.map((point, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-gray-700">{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Activities */}
            {currentSlide.activities && currentSlide.activities.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Activities
                </h3>
                <ul className="space-y-2">
                  {currentSlide.activities.map((activity, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-gray-700">{activity}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}


          </div>
        </div>

        {/* Speaker Notes Overlay */}
        {showNotes && currentSlide.speaker_notes && (
          <div className="absolute bottom-0 left-0 right-0 bg-gray-900 text-white p-4 max-h-48 overflow-y-auto">
            <h4 className="font-semibold mb-2">Speaker Notes</h4>
            <div className="text-sm prose prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {currentSlide.speaker_notes}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* Audio Script Overlay */}
        {isAudioPlaying && currentSlide.audio_script && (
          <div className="absolute top-20 right-4 bg-black bg-opacity-75 text-white p-4 rounded-lg max-w-sm">
            <h4 className="font-semibold mb-2">Audio Script</h4>
            <div className="text-sm prose prose-invert max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {currentSlide.audio_script}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-75 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            className={`fixed inset-4 bg-white rounded-lg shadow-2xl overflow-hidden flex flex-col ${
              showFullscreen ? 'inset-0 rounded-none' : ''
            }`}
          >
            {/* Header */}
            <div className="bg-gray-50 border-b border-gray-200 p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <h1 className="text-xl font-bold text-gray-900">
                  {eventSlides.event_name} - Slides
                </h1>
                <Badge variant="outline" size="sm">
                  {totalSlides} slides
                </Badge>
                <Badge variant="outline" size="sm">
                  {eventSlides.estimated_duration} min total
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleNotes}
                  className={showNotes ? 'bg-blue-100' : ''}
                >
                  <BookOpen className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleAudio}
                  className={isAudioPlaying ? 'bg-green-100' : ''}
                >
                  {isAudioPlaying ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleFullscreen}
                >
                  <Eye className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Main Content */}
            <div className="flex flex-1 min-h-0">
              {/* Slide Content */}
              <div className="flex-1 relative overflow-hidden">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentSlideIndex}
                    initial={{ opacity: 0, x: 50 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -50 }}
                    transition={{ duration: 0.3 }}
                    className="h-full overflow-y-auto"
                  >
                    {renderSlideContent()}
                  </motion.div>
                </AnimatePresence>

                {/* Navigation Controls */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex items-center gap-4 bg-white bg-opacity-90 backdrop-blur-sm rounded-full px-4 py-2 shadow-lg">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handlePreviousSlide}
                    disabled={currentSlideIndex === 0}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={togglePlayPause}
                    className={isPlaying ? 'bg-blue-100' : ''}
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleNextSlide}
                    disabled={currentSlideIndex === totalSlides - 1}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Slide Thumbnails Sidebar */}
              <div className="w-64 bg-gray-50 border-l border-gray-200 p-4 overflow-y-auto flex-shrink-0">
                <h3 className="font-semibold text-gray-900 mb-4">Slides</h3>
                <div className="space-y-2">
                  {eventSlides.slides.map((slide, index) => (
                    <button
                      key={index}
                      onClick={() => handleSlideSelect(index)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        index === currentSlideIndex
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-gray-900">
                          Slide {slide.slide_number}
                        </span>
                        <Badge variant="outline" size="sm" className="text-xs">
                          {slide.duration_minutes}min
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 truncate">{slide.title}</p>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Keyboard Shortcuts Help */}
            <div className="absolute bottom-4 right-4 bg-black bg-opacity-75 text-white text-xs p-2 rounded">
              <div>← → Navigate</div>
              <div>Space Play/Pause</div>
              <div>N Notes</div>
              <div>F Fullscreen</div>
              <div>Esc Close</div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default GagneEventSlideModal;
