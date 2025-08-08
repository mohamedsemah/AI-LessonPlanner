const puppeteer = require('puppeteer');
const path = require('path');

class PDFService {
  constructor() {
    this.themes = {
      modern: {
        primary: '#2563eb',
        secondary: '#64748b',
        accent: '#f59e0b',
        background: '#ffffff',
        text: '#1e293b',
        gradient: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)'
      },
      corporate: {
        primary: '#1f2937',
        secondary: '#6b7280',
        accent: '#10b981',
        background: '#ffffff',
        text: '#111827',
        gradient: 'linear-gradient(135deg, #1f2937 0%, #374151 100%)'
      },
      creative: {
        primary: '#8b5cf6',
        secondary: '#a78bfa',
        accent: '#f97316',
        background: '#ffffff',
        text: '#1e293b',
        gradient: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)'
      },
      minimal: {
        primary: '#000000',
        secondary: '#6b7280',
        accent: '#3b82f6',
        background: '#ffffff',
        text: '#111827',
        gradient: 'linear-gradient(135deg, #000000 0%, #374151 100%)'
      }
    };
  }

  async generatePremiumPDF(courseContent, lessonData, designPreferences = {}) {
    try {
      console.log('📄 Creating premium PDF document...');
      
      const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });
      
      const page = await browser.newPage();
      
      // Generate HTML content
      const html = this.generatePDFHTML(courseContent, lessonData, designPreferences);
      
      await page.setContent(html, { waitUntil: 'networkidle0' });
      
      // Generate PDF
      const pdfBuffer = await page.pdf({
        format: 'A4',
        printBackground: true,
        margin: {
          top: '20mm',
          right: '20mm',
          bottom: '20mm',
          left: '20mm'
        }
      });
      
      await browser.close();
      
      console.log('✅ Premium PDF created successfully');
      return pdfBuffer;
    } catch (error) {
      console.error('❌ PDF generation error:', error);
      throw error;
    }
  }

  generatePDFHTML(courseContent, lessonData, designPreferences) {
    const theme = this.themes[designPreferences.theme || 'modern'];
    const lessonInfo = lessonData.lesson_info || {};
    const slides = courseContent.slides || [];
    
    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${lessonInfo.course_title || 'Course'} - ${lessonInfo.lesson_topic || 'Lesson'}</title>
        <style>
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: ${theme.text};
            background: ${theme.background};
          }
          
          .page {
            page-break-after: always;
            padding: 40px;
            min-height: 100vh;
            position: relative;
          }
          
          .page:last-child {
            page-break-after: avoid;
          }
          
          .title-page {
            background: ${theme.gradient};
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
          }
          
          .title-page h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
          }
          
          .title-page h2 {
            font-size: 2rem;
            font-weight: 300;
            margin-bottom: 2rem;
            opacity: 0.9;
          }
          
          .title-page .metadata {
            position: absolute;
            bottom: 40px;
            left: 40px;
            right: 40px;
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            opacity: 0.8;
          }
          
          .udl-badge {
            position: absolute;
            top: 40px;
            right: 40px;
            background: ${theme.accent};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
          }
          
          .event-header {
            background: ${theme.gradient};
            color: white;
            padding: 60px 40px;
            text-align: center;
          }
          
          .event-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
          }
          
          .event-header h2 {
            font-size: 1.8rem;
            font-weight: 300;
            margin-bottom: 2rem;
          }
          
          .event-header p {
            font-size: 1.1rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
          }
          
          .content-page {
            padding: 40px;
          }
          
          .slide-title {
            font-size: 2rem;
            font-weight: 700;
            color: ${theme.primary};
            margin-bottom: 2rem;
            border-bottom: 3px solid ${theme.primary};
            padding-bottom: 1rem;
          }
          
          .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 2rem;
          }
          
          .main-content {
            background: #f8fafc;
            padding: 30px;
            border-radius: 12px;
            border-left: 4px solid ${theme.primary};
          }
          
          .main-content h3 {
            color: ${theme.primary};
            font-size: 1.3rem;
            margin-bottom: 1rem;
          }
          
          .main-content ul {
            list-style: none;
            padding-left: 0;
          }
          
          .main-content li {
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
            position: relative;
            padding-left: 20px;
          }
          
          .main-content li:before {
            content: "•";
            color: ${theme.primary};
            font-weight: bold;
            position: absolute;
            left: 0;
          }
          
          .visual-elements {
            background: #fef3c7;
            padding: 30px;
            border-radius: 12px;
            border-left: 4px solid ${theme.accent};
          }
          
          .visual-elements h3 {
            color: ${theme.accent};
            font-size: 1.3rem;
            margin-bottom: 1rem;
          }
          
          .visual-elements ul {
            list-style: none;
            padding-left: 0;
          }
          
          .visual-elements li {
            padding: 8px 0;
            border-bottom: 1px solid #fde68a;
            position: relative;
            padding-left: 20px;
          }
          
          .visual-elements li:before {
            content: "🎨";
            position: absolute;
            left: 0;
          }
          
          .audio-script {
            background: #ecfdf5;
            padding: 20px;
            border-radius: 8px;
            margin-top: 2rem;
            border-left: 4px solid ${theme.accent};
          }
          
          .audio-script h4 {
            color: ${theme.accent};
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
          }
          
          .audio-script p {
            font-style: italic;
            color: ${theme.secondary};
          }
          
          .slide-number {
            position: absolute;
            bottom: 20px;
            right: 40px;
            font-size: 0.9rem;
            color: ${theme.secondary};
          }
          
          .summary-page {
            background: ${theme.gradient};
            color: white;
            text-align: center;
            padding: 60px 40px;
          }
          
          .summary-page h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 3rem;
          }
          
          .summary-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
            max-width: 600px;
            margin: 0 auto;
          }
          
          .summary-item {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
          }
          
          .summary-item h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
          }
          
          .summary-item p {
            font-size: 2rem;
            font-weight: 700;
          }
          
          .thank-you {
            margin-top: 4rem;
            font-size: 1.2rem;
            opacity: 0.9;
          }
        </style>
      </head>
      <body>
        <!-- Title Page -->
        <div class="page title-page">
          <div class="udl-badge">UDL-Compliant</div>
          <h1>${lessonInfo.course_title || 'Course Title'}</h1>
          <h2>${lessonInfo.lesson_topic || 'Lesson Topic'}</h2>
          <div class="metadata">
            <span>Premium Export Tool</span>
            <span>${new Date().toLocaleDateString()}</span>
          </div>
        </div>
        
        ${this.generateContentPages(slides, theme)}
        
        <!-- Summary Page -->
        <div class="page summary-page">
          <h1>Summary</h1>
          <div class="summary-grid">
            <div class="summary-item">
              <h3>Total Slides</h3>
              <p>${slides.length}</p>
            </div>
            <div class="summary-item">
              <h3>Duration</h3>
              <p>${courseContent.estimated_duration || 0} min</p>
            </div>
            <div class="summary-item">
              <h3>UDL Compliance</h3>
              <p>${Math.round((courseContent.udl_compliance_report?.overall_compliance || 0) * 100)}%</p>
            </div>
            <div class="summary-item">
              <h3>Gagne Events</h3>
              <p>${slides.filter(s => s.gagne_event).length}</p>
            </div>
          </div>
          <div class="thank-you">
            Thank you for using our Premium Export Tool!
          </div>
        </div>
      </body>
      </html>
    `;
  }

  generateContentPages(slides, theme) {
    let currentEvent = null;
    let html = '';
    
    for (let i = 0; i < slides.length; i++) {
      const slide = slides[i];
      
      // Check if this is a new event
      if (slide.gagne_event !== currentEvent) {
        currentEvent = slide.gagne_event;
        html += `
          <div class="page event-header">
            <h1>Event ${slide.gagne_event}</h1>
            <h2>${slide.gagne_event_name || 'Event'}</h2>
            ${slide.description ? `<p>${slide.description}</p>` : ''}
          </div>
        `;
      }
      
      // Content page
      html += `
        <div class="page content-page">
          <h1 class="slide-title">${slide.title || 'Slide Title'}</h1>
          <div class="content-grid">
            <div class="main-content">
              <h3>Main Content</h3>
              <ul>
                ${this.cleanMarkdown(slide.content || '').split('\n').filter(line => line.trim()).map(line => 
                  `<li>${line.trim()}</li>`
                ).join('')}
              </ul>
            </div>
            ${slide.visual_elements && slide.visual_elements.length > 0 ? `
              <div class="visual-elements">
                <h3>Visual Elements</h3>
                <ul>
                  ${slide.visual_elements.map(element => 
                    `<li>${typeof element === 'object' ? element.description || 'Visual element' : element}</li>`
                  ).join('')}
                </ul>
              </div>
            ` : ''}
          </div>
          ${slide.audio_script ? `
            <div class="audio-script">
              <h4>Audio Script</h4>
              <p>${slide.audio_script}</p>
            </div>
          ` : ''}
          <div class="slide-number">${i + 1}</div>
        </div>
      `;
    }
    
    return html;
  }

  cleanMarkdown(text) {
    if (!text) return '';
    
    return text
      .replace(/#{1,6}\s+/g, '') // Remove headers
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold
      .replace(/\*(.*?)\*/g, '$1') // Remove italic
      .replace(/`(.*?)`/g, '$1') // Remove code
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Remove links
      .replace(/^\s*[-*+]\s*/gm, '') // Remove list markers
      .trim();
  }
}

module.exports = PDFService; 