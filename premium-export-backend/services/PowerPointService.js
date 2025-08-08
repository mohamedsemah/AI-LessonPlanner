const PptxGenJS = require('pptxgenjs');
const path = require('path');

class PowerPointService {
  constructor() {
    this.themes = {
      modern: {
        primary: '#2563eb',
        secondary: '#64748b',
        accent: '#f59e0b',
        background: '#ffffff',
        text: '#1e293b',
        gradient: ['#2563eb', '#1d4ed8']
      },
      corporate: {
        primary: '#1f2937',
        secondary: '#6b7280',
        accent: '#10b981',
        background: '#ffffff',
        text: '#111827',
        gradient: ['#1f2937', '#374151']
      },
      creative: {
        primary: '#8b5cf6',
        secondary: '#a78bfa',
        accent: '#f97316',
        background: '#ffffff',
        text: '#1e293b',
        gradient: ['#8b5cf6', '#a78bfa']
      },
      minimal: {
        primary: '#000000',
        secondary: '#6b7280',
        accent: '#3b82f6',
        background: '#ffffff',
        text: '#111827',
        gradient: ['#000000', '#374151']
      }
    };
  }

  async generatePremiumPresentation(courseContent, lessonData, designPreferences = {}) {
    try {
      console.log('🎨 Creating premium PowerPoint presentation...');
      
      // Create new presentation
      const pptx = new PptxGenJS();
      
      // Set presentation properties
      const lessonInfo = lessonData.lesson_info || {};
      pptx.author = 'Lesson Planning Tool';
      pptx.company = 'Premium Export';
      pptx.title = `${lessonInfo.course_title || 'Course'} - ${lessonInfo.lesson_topic || 'Lesson'}`;
      pptx.subject = 'UDL-Compliant Course Content';
      
      // Get theme
      const theme = this.themes[designPreferences.theme || 'modern'];
      
      // Add title slide
      this.createTitleSlide(pptx, lessonData, theme);
      
      // Add content slides
      const slides = courseContent.slides || [];
      let currentEvent = null;
      
      for (let i = 0; i < slides.length; i++) {
        const slideData = slides[i];
        
        // Check if this is a new event
        if (slideData.gagne_event !== currentEvent) {
          currentEvent = slideData.gagne_event;
          this.createEventHeaderSlide(pptx, slideData, theme);
        }
        
        // Create content slide
        this.createContentSlide(pptx, slideData, theme, i + 1);
      }
      
      // Add summary slide
      this.createSummarySlide(pptx, courseContent, lessonData, theme);
      
      // Generate buffer
      const buffer = await pptx.write('nodebuffer');
      console.log('✅ Premium PowerPoint created successfully');
      
      return buffer;
    } catch (error) {
      console.error('❌ PowerPoint generation error:', error);
      throw error;
    }
  }

  createTitleSlide(pptx, lessonData, theme) {
    const slide = pptx.addSlide();
    const lessonInfo = lessonData.lesson_info || {};
    
    // Background gradient
    slide.background = { color: theme.background };
    
    // Title
    slide.addText(lessonInfo.course_title || 'Course Title', {
      x: 0.5,
      y: 2,
      w: 9,
      h: 1.5,
      fontSize: 44,
      fontFace: 'Arial',
      color: theme.primary,
      bold: true,
      align: 'center',
      valign: 'middle'
    });
    
    // Subtitle
    slide.addText(lessonInfo.lesson_topic || 'Lesson Topic', {
      x: 0.5,
      y: 3.8,
      w: 9,
      h: 0.8,
      fontSize: 28,
      fontFace: 'Arial',
      color: theme.secondary,
      align: 'center',
      valign: 'middle'
    });
    
    // Decorative elements
    slide.addShape('rect', {
      x: 0.5,
      y: 5.2,
      w: 9,
      h: 0.1,
      fill: { color: theme.primary },
      line: { color: theme.primary }
    });
    
    // UDL Badge
    slide.addText('UDL-Compliant', {
      x: 8,
      y: 0.2,
      w: 1.5,
      h: 0.4,
      fontSize: 12,
      fontFace: 'Arial',
      color: theme.accent,
      bold: true,
      align: 'center',
      valign: 'middle',
      fill: { color: theme.background },
      line: { color: theme.accent, width: 1 }
    });
  }

  createEventHeaderSlide(pptx, slideData, theme) {
    const slide = pptx.addSlide();
    
    // Background
    slide.background = { color: theme.background };
    
    // Event number and title
    const eventNumber = slideData.gagne_event || 1;
    const eventName = slideData.gagne_event_name || 'Event';
    
    slide.addText(`Event ${eventNumber}`, {
      x: 0.5,
      y: 1,
      w: 9,
      h: 0.8,
      fontSize: 24,
      fontFace: 'Arial',
      color: theme.primary,
      bold: true,
      align: 'center'
    });
    
    slide.addText(eventName, {
      x: 0.5,
      y: 2,
      w: 9,
      h: 1.2,
      fontSize: 36,
      fontFace: 'Arial',
      color: theme.text,
      bold: true,
      align: 'center'
    });
    
    // Decorative line
    slide.addShape('rect', {
      x: 2,
      y: 3.5,
      w: 6,
      h: 0.05,
      fill: { color: theme.primary }
    });
    
    // Description
    if (slideData.description) {
      slide.addText(slideData.description, {
        x: 1,
        y: 4,
        w: 8,
        h: 1.5,
        fontSize: 16,
        fontFace: 'Arial',
        color: theme.secondary,
        align: 'center',
        valign: 'middle'
      });
    }
  }

  createContentSlide(pptx, slideData, theme, slideNumber) {
    const slide = pptx.addSlide();
    
    // Background
    slide.background = { color: theme.background };
    
    // Slide title
    slide.addText(slideData.title || 'Slide Title', {
      x: 0.5,
      y: 0.3,
      w: 9,
      h: 0.8,
      fontSize: 28,
      fontFace: 'Arial',
      color: theme.primary,
      bold: true
    });
    
    // Content area
    const contentY = 1.2;
    const contentHeight = 4;
    
    // Main content
    if (slideData.content) {
      slide.addText(this.cleanMarkdown(slideData.content), {
        x: 0.5,
        y: contentY,
        w: 4.5,
        h: contentHeight,
        fontSize: 16,
        fontFace: 'Arial',
        color: theme.text,
        align: 'left',
        valign: 'top',
        bullet: { type: 'number' }
      });
    }
    
    // Visual elements section
    if (slideData.visual_elements && slideData.visual_elements.length > 0) {
      slide.addText('Visual Elements:', {
        x: 5.5,
        y: contentY,
        w: 4,
        h: 0.5,
        fontSize: 14,
        fontFace: 'Arial',
        color: theme.primary,
        bold: true
      });
      
      const visualElementsText = slideData.visual_elements
        .map(element => {
          if (typeof element === 'object') {
            return `• ${element.description || 'Visual element'}`;
          }
          return `• ${element}`;
        })
        .join('\n');
      
      slide.addText(visualElementsText, {
        x: 5.5,
        y: contentY + 0.6,
        w: 4,
        h: contentHeight - 0.6,
        fontSize: 12,
        fontFace: 'Arial',
        color: theme.secondary,
        align: 'left',
        valign: 'top',
        bullet: { type: 'bullet' }
      });
    }
    
    // Audio script
    if (slideData.audio_script) {
      slide.addText('Audio Script:', {
        x: 0.5,
        y: 5.5,
        w: 9,
        h: 0.4,
        fontSize: 12,
        fontFace: 'Arial',
        color: theme.accent,
        bold: true
      });
      
      slide.addText(slideData.audio_script, {
        x: 0.5,
        y: 6,
        w: 9,
        h: 1,
        fontSize: 10,
        fontFace: 'Arial',
        color: theme.secondary,
        italic: true
      });
    }
    
    // Slide number
    slide.addText(`${slideNumber}`, {
      x: 8.5,
      y: 6.8,
      w: 1,
      h: 0.2,
      fontSize: 10,
      fontFace: 'Arial',
      color: theme.secondary,
      align: 'right'
    });
  }

  createSummarySlide(pptx, courseContent, lessonData, theme) {
    const slide = pptx.addSlide();
    
    // Background
    slide.background = { color: theme.background };
    
    // Title
    slide.addText('Summary', {
      x: 0.5,
      y: 0.5,
      w: 9,
      h: 1,
      fontSize: 36,
      fontFace: 'Arial',
      color: theme.primary,
      bold: true,
      align: 'center'
    });
    
    // Summary content
    const summaryItems = [
      `Total Slides: ${courseContent.total_slides || courseContent.slides?.length || 0}`,
      `Estimated Duration: ${courseContent.estimated_duration || 0} minutes`,
      `UDL Compliance: ${(courseContent.udl_compliance_report?.overall_compliance || 0) * 100}%`,
      `Gagne Events: ${courseContent.slides?.filter(s => s.gagne_event).length || 0}`
    ];
    
    slide.addText(summaryItems.join('\n'), {
      x: 1,
      y: 2,
      w: 8,
      h: 3,
      fontSize: 18,
      fontFace: 'Arial',
      color: theme.text,
      align: 'left',
      valign: 'middle',
      bullet: { type: 'bullet' }
    });
    
    // Thank you message
    slide.addText('Thank you for using our Premium Export Tool!', {
      x: 0.5,
      y: 5.5,
      w: 9,
      h: 0.8,
      fontSize: 16,
      fontFace: 'Arial',
      color: theme.accent,
      align: 'center',
      italic: true
    });
  }

  cleanMarkdown(text) {
    if (!text) return '';
    
    // Remove markdown formatting
    return text
      .replace(/#{1,6}\s+/g, '') // Remove headers
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold
      .replace(/\*(.*?)\*/g, '$1') // Remove italic
      .replace(/`(.*?)`/g, '$1') // Remove code
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links
      .replace(/^\s*[-*+]\s*/gm, '• ') // Convert lists
      .trim();
  }
}

module.exports = PowerPointService; 