import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Eye, 
  Edit3, 
  Play, 
  Clock, 
  Accessibility, 
  Image, 
  Volume2, 
  Type,
  MousePointer,
  CheckCircle,
  Maximize2,
  X
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import Button from '../ui/Button';

const CourseContentPreview = ({ slides, onRefineSlide }) => {
  const [selectedSlide, setSelectedSlide] = useState(null);
  const [showFullSlide, setShowFullSlide] = useState(false);

  const getContentTypeIcon = (contentType) => {
    switch (contentType) {
      case 'text':
        return <Type className="w-4 h-4" />;
      case 'image':
        return <Image className="w-4 h-4" />;
      case 'video':
        return <Play className="w-4 h-4" />;
      case 'interactive':
        return <MousePointer className="w-4 h-4" />;
      case 'mixed':
        return <Eye className="w-4 h-4" />;
      default:
        return <Type className="w-4 h-4" />;
    }
  };

  const getAccessibilityIcon = (features) => {
    if (features.includes('audio_script')) return <Volume2 className="w-4 h-4" />;
    if (features.includes('alt_text')) return <Image className="w-4 h-4" />;
    if (features.includes('keyboard_navigation')) return <MousePointer className="w-4 h-4" />;
    return <Accessibility className="w-4 h-4" />;
  };

  const getUDLGuidelineColor = (guideline) => {
    if (guideline.includes('representation')) return 'bg-blue-100 text-blue-800';
    if (guideline.includes('action')) return 'bg-green-100 text-green-800';
    if (guideline.includes('engagement')) return 'bg-purple-100 text-purple-800';
    return 'bg-gray-100 text-gray-800';
  };

  const renderMarkdownContent = (content) => {
    if (!content) return '';
    
    // Simple markdown rendering
    return content
      .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mb-4">$1</h1>')
      .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mb-3">$1</h2>')
      .replace(/^### (.*$)/gim, '<h3 class="text-lg font-medium mb-2">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^- (.*$)/gim, '<li class="ml-4">$1</li>')
      .replace(/^(\d+)\. (.*$)/gim, '<li class="ml-4">$2</li>')
      .replace(/\n\n/g, '</p><p class="mb-2">')
      .replace(/^/g, '<p class="mb-2">')
      .replace(/$/g, '</p>');
  };

  const renderSlidePreview = (slide) => {
    return (
      <div className="bg-white border rounded-lg p-6 shadow-sm min-h-[300px]">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">{slide.title}</h2>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">
              {slide.duration_minutes} min
            </span>
            <span className={`px-2 py-1 text-xs rounded-full ${getUDLGuidelineColor(slide.udl_guidelines[0] || '')}`}>
              {slide.content_type}
            </span>
          </div>
        </div>
        
        <div className="mb-4">
          <div 
            className="prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: renderMarkdownContent(slide.main_content) }}
          />
        </div>

        {slide.visual_elements && slide.visual_elements.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium text-gray-700 mb-2">Visual Elements:</h4>
            <div className="flex flex-wrap gap-2">
              {slide.visual_elements.map((element, idx) => (
                <span key={idx} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                  {typeof element === 'string' ? element : element.url || element}
                </span>
              ))}
            </div>
          </div>
        )}

        {slide.audio_script && (
          <div className="mb-4">
            <h4 className="font-medium text-gray-700 mb-2">Audio Script:</h4>
            <p className="text-sm text-gray-600 italic">
              {slide.audio_script.substring(0, 150)}...
            </p>
          </div>
        )}

        <div className="flex flex-wrap gap-2 mb-4">
          {slide.udl_guidelines.map((guideline, idx) => (
            <span
              key={idx}
              className={`px-2 py-1 text-xs rounded-full ${getUDLGuidelineColor(guideline)}`}
            >
              {guideline.replace('_', ' ')}
            </span>
          ))}
        </div>

        {slide.notes && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3">
            <h4 className="font-medium text-yellow-800 mb-1">Speaker Notes:</h4>
            <p className="text-sm text-yellow-700">{slide.notes}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Eye className="w-5 h-5 text-primary-600" />
          Course Content Preview
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {slides.map((slide, index) => (
            <motion.div
              key={slide.slide_number}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`border rounded-lg p-4 transition-all duration-200 ${
                selectedSlide?.slide_number === slide.slide_number
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold">
                    {slide.slide_number}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{slide.title}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        {getContentTypeIcon(slide.content_type)}
                        {slide.content_type}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {slide.duration_minutes} min
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedSlide(slide);
                      setShowFullSlide(true);
                    }}
                    className="flex items-center gap-1"
                  >
                    <Maximize2 className="w-3 h-3" />
                    Preview
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRefineSlide(slide);
                    }}
                    className="flex items-center gap-1"
                  >
                    <Edit3 className="w-3 h-3" />
                    Refine
                  </Button>
                </div>
              </div>

              {/* Content Preview */}
              <div className="mb-3">
                <div 
                  className="text-sm text-gray-700 line-clamp-3 prose prose-sm"
                  dangerouslySetInnerHTML={{ __html: renderMarkdownContent(slide.main_content.substring(0, 200) + '...') }}
                />
              </div>

              {/* UDL Features */}
              <div className="flex flex-wrap gap-2 mb-3">
                {slide.udl_guidelines.map((guideline, idx) => (
                  <span
                    key={idx}
                    className={`px-2 py-1 text-xs rounded-full ${getUDLGuidelineColor(guideline)}`}
                  >
                    {guideline.replace('_', ' ')}
                  </span>
                ))}
              </div>

              {/* Accessibility Features */}
              {slide.accessibility_features.length > 0 && (
                <div className="flex items-center gap-2 text-xs text-gray-600">
                  <Accessibility className="w-3 h-3" />
                  <span>Accessibility:</span>
                  <div className="flex items-center gap-1">
                    {slide.accessibility_features.map((feature, idx) => (
                      <span key={idx} className="flex items-center gap-1">
                        {getAccessibilityIcon([feature])}
                        {feature.replace('_', ' ')}
                        {idx < slide.accessibility_features.length - 1 && <span>,</span>}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Visual Elements */}
              {slide.visual_elements && slide.visual_elements.length > 0 && (
                <div className="flex items-center gap-2 text-xs text-gray-600 mt-2">
                  <Image className="w-3 h-3" />
                  <span>Visual elements: {slide.visual_elements.length}</span>
                </div>
              )}

              {/* Audio Script */}
              {slide.audio_script && (
                <div className="flex items-center gap-2 text-xs text-gray-600 mt-2">
                  <Volume2 className="w-3 h-3" />
                  <span>Audio script available</span>
                </div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Full Slide Modal */}
        {showFullSlide && selectedSlide && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-4 border-b">
                <h2 className="text-xl font-bold">Slide {selectedSlide.slide_number}: {selectedSlide.title}</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowFullSlide(false)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="p-6">
                {renderSlidePreview(selectedSlide)}
              </div>
            </div>
          </div>
        )}

        {/* Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg"
        >
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <h4 className="font-semibold text-gray-900">Content Summary</h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="font-medium">Total Slides:</span>
              <div className="text-lg font-bold text-primary-600">{slides.length}</div>
            </div>
            <div>
              <span className="font-medium">Total Duration:</span>
              <div className="text-lg font-bold text-primary-600">
                {Math.round(slides.reduce((sum, slide) => sum + slide.duration_minutes, 0))} min
              </div>
            </div>
            <div>
              <span className="font-medium">UDL Guidelines:</span>
              <div className="text-lg font-bold text-primary-600">
                {new Set(slides.flatMap(slide => slide.udl_guidelines)).size}
              </div>
            </div>
            <div>
              <span className="font-medium">Accessibility Features:</span>
              <div className="text-lg font-bold text-primary-600">
                {new Set(slides.flatMap(slide => slide.accessibility_features)).size}
              </div>
            </div>
          </div>
        </motion.div>
      </CardContent>
    </Card>
  );
};

export default CourseContentPreview; 