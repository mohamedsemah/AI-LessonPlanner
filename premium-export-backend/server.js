const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;

// Import our premium export services
const PowerPointService = require('./services/PowerPointService');
const PDFService = require('./services/PDFService');
const TemplateService = require('./services/TemplateService');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Initialize services
const powerpointService = new PowerPointService();
const pdfService = new PDFService();
const templateService = new TemplateService();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'premium-export-backend',
    version: '1.0.0',
    features: ['powerpoint', 'pdf', 'templates']
  });
});

// Premium PowerPoint export
app.post('/api/premium/export/pptx', async (req, res) => {
  try {
    console.log('🎨 Starting premium PowerPoint export...');
    console.log('📦 Request body keys:', Object.keys(req.body));
    console.log('📦 courseContent type:', typeof req.body.courseContent);
    console.log('📦 lessonData type:', typeof req.body.lessonData);
    console.log('📦 designPreferences:', req.body.designPreferences);
    
    const { courseContent, lessonData, designPreferences } = req.body;
    
    if (!courseContent || !lessonData) {
      console.log('❌ Missing required data - courseContent:', !!courseContent, 'lessonData:', !!lessonData);
      return res.status(400).json({ error: 'Course content and lesson data are required' });
    }

    const pptxBuffer = await powerpointService.generatePremiumPresentation(
      courseContent, 
      lessonData, 
      designPreferences
    );

    // Generate filename
    const lessonInfo = lessonData.lesson_info || {};
    const filename = `${lessonInfo.course_title || 'Course'}_${lessonInfo.lesson_topic || 'Lesson'}_Premium.pptx`
      .replace(/[^a-zA-Z0-9.-]/g, '_');

    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.presentationml.presentation');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.send(pptxBuffer);

    console.log('✅ Premium PowerPoint export completed');
  } catch (error) {
    console.error('❌ Premium PowerPoint export error:', error);
    res.status(500).json({ error: `Failed to export PowerPoint: ${error.message}` });
  }
});

// Premium PDF export
app.post('/api/premium/export/pdf', async (req, res) => {
  try {
    console.log('📄 Starting premium PDF export...');
    console.log('📦 Request body keys:', Object.keys(req.body));
    console.log('📦 courseContent type:', typeof req.body.courseContent);
    console.log('📦 lessonData type:', typeof req.body.lessonData);
    console.log('📦 designPreferences:', req.body.designPreferences);
    
    const { courseContent, lessonData, designPreferences } = req.body;
    
    if (!courseContent || !lessonData) {
      console.log('❌ Missing required data - courseContent:', !!courseContent, 'lessonData:', !!lessonData);
      return res.status(400).json({ error: 'Course content and lesson data are required' });
    }

    const pdfBuffer = await pdfService.generatePremiumPDF(
      courseContent, 
      lessonData, 
      designPreferences
    );

    // Generate filename
    const lessonInfo = lessonData.lesson_info || {};
    const filename = `${lessonInfo.course_title || 'Course'}_${lessonInfo.lesson_topic || 'Lesson'}_Premium.pdf`
      .replace(/[^a-zA-Z0-9.-]/g, '_');

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.send(pdfBuffer);

    console.log('✅ Premium PDF export completed');
  } catch (error) {
    console.error('❌ Premium PDF export error:', error);
    res.status(500).json({ error: `Failed to export PDF: ${error.message}` });
  }
});

// Get available templates
app.get('/api/premium/templates', async (req, res) => {
  try {
    const templates = await templateService.getAvailableTemplates();
    res.json(templates);
  } catch (error) {
    console.error('❌ Template fetch error:', error);
    res.status(500).json({ error: `Failed to fetch templates: ${error.message}` });
  }
});

// Get design themes
app.get('/api/premium/themes', async (req, res) => {
  try {
    const themes = templateService.getAvailableThemes();
    res.json(themes);
  } catch (error) {
    console.error('❌ Theme fetch error:', error);
    res.status(500).json({ error: `Failed to fetch themes: ${error.message}` });
  }
});

// Preview slide HTML
app.post('/api/premium/preview', async (req, res) => {
  try {
    const { slideData, template, theme } = req.body;
    const html = await templateService.generateSlideHTML(slideData, template, theme);
    res.json({ html });
  } catch (error) {
    console.error('❌ Preview generation error:', error);
    res.status(500).json({ error: `Failed to generate preview: ${error.message}` });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Premium Export Backend running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🎨 Premium PowerPoint: POST http://localhost:${PORT}/api/premium/export/pptx`);
  console.log(`📄 Premium PDF: POST http://localhost:${PORT}/api/premium/export/pdf`);
});

module.exports = app; 