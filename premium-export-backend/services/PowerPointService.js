const PptxGenJS = require('pptxgenjs');

class PowerPointService {
  constructor() {
    this.themes = {
      modern: {
        primary: '#2563eb',
        secondary: '#64748b',
        accent: '#f59e0b',
        background: '#ffffff',
        text: '#1e293b',
        lightBg: '#f8fafc',
        border: '#e2e8f0'
      },
      corporate: {
        primary: '#1f2937',
        secondary: '#6b7280',
        accent: '#10b981',
        background: '#ffffff',
        text: '#111827',
        lightBg: '#f9fafb',
        border: '#e5e7eb'
      },
      creative: {
        primary: '#8b5cf6',
        secondary: '#a78bfa',
        accent: '#f97316',
        background: '#ffffff',
        text: '#1e293b',
        lightBg: '#faf5ff',
        border: '#e9d5ff'
      },
      minimal: {
        primary: '#000000',
        secondary: '#6b7280',
        accent: '#3b82f6',
        background: '#ffffff',
        text: '#111827',
        lightBg: '#fafafa',
        border: '#e5e5e5'
      }
    };
  }

  async generatePremiumPresentation(courseContent, lessonData, designPreferences = {}) {
    try {
      console.log('🎨 Creating premium PowerPoint presentation...');
      
      // Validate input data
      if (!courseContent || !lessonData) {
        throw new Error('Course content and lesson data are required');
      }
      
      // Create new presentation
      const pptx = new PptxGenJS();
      
      // Set basic presentation properties
      const lessonInfo = lessonData.lesson_info || {};
      pptx.author = 'Lesson Planning Tool';
      pptx.title = this.sanitizeText(`${lessonInfo.course_title || 'Course'} - ${lessonInfo.lesson_topic || 'Lesson'}`);
      
      // Get theme
      const theme = this.themes[designPreferences.theme || 'modern'];
      
      // Add title slide
      this.createPremiumTitleSlide(pptx, lessonData, theme);
      
      // Add content slides
      const slides = courseContent.slides || [];
      let slideNumber = 2;
      
      for (let i = 0; i < slides.length; i++) {
        const slideData = slides[i];
        
        // Skip invalid slides
        if (!slideData || typeof slideData !== 'object') {
          continue;
        }
        
        this.createPremiumContentSlide(pptx, slideData, theme, slideNumber);
        slideNumber++;
      }
      
      // Generate buffer
      const buffer = await pptx.write('nodebuffer');
      console.log('✅ Premium PowerPoint created successfully');
      
      return buffer;
    } catch (error) {
      console.error('❌ PowerPoint generation error:', error);
      throw error;
    }
  }

  createPremiumTitleSlide(pptx, lessonData, theme) {
    try {
      const slide = pptx.addSlide();
      const lessonInfo = lessonData.lesson_info || {};
      
      // Simple background
      slide.background = { color: theme.background };
      
      // Decorative header bar
      slide.addShape('rect', {
        x: 0, y: 0, w: 10, h: 0.4,
        fill: { color: theme.accent }
      });
      
      // Main title with premium typography
      slide.addText(this.sanitizeText(lessonInfo.course_title || 'Course Title'), {
        x: 0.5, y: 1.5, w: 9, h: 1.8,
        fontSize: 42,
        fontFace: 'Calibri',
        color: theme.primary,
        bold: true,
        align: 'center',
        valign: 'middle',
        lineSpacing: 1.2
      });
      
      // Subtitle with different font
      slide.addText(this.sanitizeText(lessonInfo.lesson_topic || 'Lesson Topic'), {
        x: 0.5, y: 3.5, w: 9, h: 1,
        fontSize: 28,
        fontFace: 'Segoe UI',
        color: theme.secondary,
        align: 'center',
        valign: 'middle',
        lineSpacing: 1.1
      });
      
      // Decorative line
      slide.addShape('line', {
        x: 2, y: 4.8, w: 6, h: 0,
        line: { color: theme.accent, width: 2 }
      });
      
      // Footer with premium styling
      slide.addText('UDL-Compliant Course Content', {
        x: 0.5, y: 6.2, w: 9, h: 0.6,
        fontSize: 16,
        fontFace: 'Segoe UI',
        color: theme.secondary,
        align: 'center',
        valign: 'middle',
        italic: true
      });
    } catch (error) {
      console.error('Error creating title slide:', error);
      // Fallback to simple title slide
      this.createSimpleTitleSlide(pptx, lessonData, theme);
    }
  }

  createPremiumContentSlide(pptx, slideData, theme, slideNumber) {
    try {
      const slide = pptx.addSlide();
      
      // Background
      slide.background = { color: theme.background };
      
      // Header accent bar
      slide.addShape('rect', {
        x: 0, y: 0, w: 10, h: 0.3,
        fill: { color: theme.accent }
      });
      
      // Slide title with premium typography
      const title = this.sanitizeText(slideData.title || 'Slide Title');
      slide.addText(title, {
        x: 0.5, y: 0.5, w: 9, h: 0.8,
        fontSize: 24,
        fontFace: 'Calibri',
        color: theme.primary,
        bold: true,
        align: 'left',
        valign: 'middle'
      });
      
      // Main content area - handle long content properly
      if (slideData.main_content) {
        const cleanContent = this.cleanMarkdown(this.sanitizeText(slideData.main_content));
        if (cleanContent) {
          this.addContentWithOverflowHandling(slide, cleanContent, theme);
        }
      }
      
      // Visual elements section - positioned below content
      if (slideData.visual_elements && Array.isArray(slideData.visual_elements) && slideData.visual_elements.length > 0) {
        const visualText = 'Visual Elements:\n' + slideData.visual_elements.slice(0, 2).map(element => {
          if (typeof element === 'string') {
            return `• ${element}`;
          } else if (typeof element === 'object') {
            return `• ${element.description || 'Visual element'}`;
          }
          return '• Visual element';
        }).join('\n');
        
        slide.addText(visualText, {
          x: 0.5, y: 6.2, w: 9, h: 1,
          fontSize: 12,
          fontFace: 'Segoe UI',
          color: theme.secondary,
          align: 'left',
          valign: 'top'
        });
      }
      
      // Slide number - positioned at bottom
      slide.addText(`${slideNumber}`, {
        x: 9, y: 6.5, w: 0.8, h: 0.4,
        fontSize: 10,
        fontFace: 'Calibri',
        color: theme.secondary,
        align: 'center',
        valign: 'middle'
      });
      
      // Duration indicator
      if (slideData.duration_minutes) {
        slide.addText(`${slideData.duration_minutes} min`, {
          x: 0.2, y: 6.5, w: 1.5, h: 0.4,
          fontSize: 10,
          fontFace: 'Segoe UI',
          color: theme.accent,
          align: 'left',
          valign: 'middle'
        });
      }
    } catch (error) {
      console.error('Error creating content slide:', error);
      // Fallback to simple content slide
      this.createSimpleContentSlide(pptx, slideData, theme, slideNumber);
    }
  }

  // Fallback methods for error handling
  createSimpleTitleSlide(pptx, lessonData, theme) {
    try {
      const slide = pptx.addSlide();
      const lessonInfo = lessonData.lesson_info || {};
      
      slide.background = { color: theme.background };
      
      slide.addText(this.sanitizeText(lessonInfo.course_title || 'Course Title'), {
        x: 0.5, y: 2, w: 9, h: 1.5,
        fontSize: 36,
        fontFace: 'Arial',
        color: theme.primary,
        bold: true,
        align: 'center',
        valign: 'middle'
      });
      
      slide.addText(this.sanitizeText(lessonInfo.lesson_topic || 'Lesson Topic'), {
        x: 0.5, y: 3.8, w: 9, h: 0.8,
        fontSize: 24,
        fontFace: 'Arial',
        color: theme.secondary,
        align: 'center',
        valign: 'middle'
      });
    } catch (error) {
      console.error('Error creating fallback title slide:', error);
    }
  }

  createSimpleContentSlide(pptx, slideData, theme, slideNumber) {
    try {
      const slide = pptx.addSlide();
      
      slide.background = { color: theme.background };
      
      const title = this.sanitizeText(slideData.title || 'Slide Title');
      slide.addText(title, {
        x: 0.5, y: 0.5, w: 9, h: 0.8,
        fontSize: 24,
        fontFace: 'Arial',
        color: theme.primary,
        bold: true,
        align: 'left',
        valign: 'middle'
      });
      
      if (slideData.main_content) {
        const cleanContent = this.cleanMarkdown(this.sanitizeText(slideData.main_content));
        if (cleanContent) {
          // Use the same overflow handling method
          this.addContentWithOverflowHandling(slide, cleanContent, theme);
        }
      }
      
      slide.addText(`${slideNumber}`, {
        x: 9, y: 6.5, w: 0.8, h: 0.4,
        fontSize: 10,
        fontFace: 'Arial',
        color: theme.secondary,
        align: 'center',
        valign: 'middle'
      });
    } catch (error) {
      console.error('Error creating fallback content slide:', error);
    }
  }

  // Helper methods for text handling
  truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    
    // Try to truncate at a sentence boundary first
    const truncated = text.substring(0, maxLength);
    const lastPeriod = truncated.lastIndexOf('.');
    const lastExclamation = truncated.lastIndexOf('!');
    const lastQuestion = truncated.lastIndexOf('?');
    
    // Find the last sentence ending
    const lastSentenceEnd = Math.max(lastPeriod, lastExclamation, lastQuestion);
    
    if (lastSentenceEnd > maxLength * 0.7) {
      return truncated.substring(0, lastSentenceEnd + 1);
    }
    
    // If no good sentence boundary, try word boundary
    const lastSpace = truncated.lastIndexOf(' ');
    
    if (lastSpace > maxLength * 0.8) {
      return truncated.substring(0, lastSpace) + '...';
    }
    
    return truncated + '...';
  }

  processVisualElements(visualElements) {
    if (!Array.isArray(visualElements)) return [];
    
    return visualElements.map(element => {
      if (typeof element === 'string') {
        const fileType = element.split('.').pop()?.toLowerCase();
        const fileName = element.replace(/\.[^/.]+$/, '');
        
        let icon = '📄';
        let description = fileName.replace(/_/g, ' ');
        
        if (fileType === 'png' || fileType === 'jpg' || fileType === 'jpeg') {
          icon = '🖼️';
        } else if (fileType === 'gif') {
          icon = '🎬';
        } else if (fileType === 'mp4' || fileType === 'avi') {
          icon = '🎥';
        } else if (fileType === 'pdf') {
          icon = '📋';
        }
        
        return { icon, description };
      } else if (typeof element === 'object') {
        return {
          icon: element.icon || '📄',
          description: element.description || 'Visual element'
        };
      }
      
      return { icon: '📄', description: 'Visual element' };
    });
  }

  sanitizeText(text) {
    if (!text || typeof text !== 'string') return '';
    
    return text
      .replace(/[^\x00-\x7F]/g, '') // Remove non-ASCII characters
      .replace(/[<>]/g, '') // Remove potentially problematic characters
      .substring(0, 1000); // Increased length limit for better content preservation
  }

  calculateTotalDuration(courseContent) {
    const slides = courseContent.slides || [];
    return slides.reduce((total, slide) => total + (slide.duration_minutes || 0), 0);
  }

  countVisualElements(courseContent) {
    const slides = courseContent.slides || [];
    return slides.reduce((total, slide) => {
      const visualElements = slide.visual_elements || [];
      return total + visualElements.length;
    }, 0);
  }

  cleanMarkdown(text) {
    if (!text) return '';
    
    return text
      .replace(/^#+\s*/gm, '') // Remove markdown headers
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold
      .replace(/\*(.*?)\*/g, '$1') // Remove italic
      .replace(/`(.*?)`/g, '$1') // Remove code
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links
      .replace(/\n\n/g, '\n') // Remove extra newlines
      .trim();
  }

  addContentWithOverflowHandling(slide, content, theme) {
    // Convert content to bullet points for better spacing
    const bulletedContent = this.convertToBulletPoints(content);
    
    // If content is short, add it as a single text box with bullets
    if (bulletedContent.length <= 500) {
      slide.addText(bulletedContent, {
        x: 0.5, y: 1.5, w: 9, h: 5.5,
        fontSize: 13,
        fontFace: 'Segoe UI',
        color: theme.text,
        align: 'left',
        valign: 'top',
        wrap: true,
        autoFit: false,
        margin: 0.4,
        bullet: { type: 'bullet', level: 0 }
      });
      return;
    }
    
    // For longer content, split into multiple text boxes with bullets
    const maxCharsPerBox = 250;
    const paragraphs = bulletedContent.split('\n\n');
    let currentY = 1.5;
    let boxHeight = 4.5;
    
    for (let i = 0; i < paragraphs.length; i++) {
      const paragraph = paragraphs[i].trim();
      if (!paragraph) continue;
      
      // Add the paragraph as a single text box with bullets
      slide.addText(paragraph, {
        x: 0.5, y: currentY, w: 9, h: boxHeight,
        fontSize: 13,
        fontFace: 'Segoe UI',
        color: theme.text,
        align: 'left',
        valign: 'top',
        wrap: true,
        autoFit: false,
        margin: 0.3,
        bullet: { type: 'bullet', level: 0 }
      });
      currentY += boxHeight + 1.0; // Increased spacing between boxes
    }
  }

  convertToBulletPoints(content) {
    if (!content) return '';
    
    // Split content into sentences and convert to bullet points
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 10);
    
    // Convert to bullet points with proper spacing
    return sentences.map(sentence => `• ${sentence.trim()}`).join('\n\n');
  }

  formatContentWithSpacing(content) {
    if (!content) return '';
    
    // Add double line breaks between bullet points and sections
    return content
      .replace(/\n•/g, '\n\n•')  // Add space before bullet points
      .replace(/\n-/g, '\n\n-')   // Add space before dash points
      .replace(/\n\n\n+/g, '\n\n') // Remove excessive line breaks
      .trim();
  }
}

module.exports = PowerPointService; 