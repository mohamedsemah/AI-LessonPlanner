const path = require('path');

class TemplateService {
  constructor() {
    this.templates = {
      modern: {
        name: 'Modern',
        description: 'Clean and professional design with blue accent colors',
        preview: 'modern-preview.png'
      },
      corporate: {
        name: 'Corporate',
        description: 'Professional business design with dark colors',
        preview: 'corporate-preview.png'
      },
      creative: {
        name: 'Creative',
        description: 'Vibrant and colorful design for creative presentations',
        preview: 'creative-preview.png'
      },
      minimal: {
        name: 'Minimal',
        description: 'Simple and clean design with minimal distractions',
        preview: 'minimal-preview.png'
      }
    };

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

  async getAvailableTemplates() {
    return Object.entries(this.templates).map(([key, template]) => ({
      id: key,
      ...template
    }));
  }

  getAvailableThemes() {
    return Object.entries(this.themes).map(([key, theme]) => ({
      id: key,
      name: this.templates[key]?.name || key,
      colors: theme
    }));
  }

  async generateSlideHTML(slideData, template = 'modern', theme = 'modern') {
    const selectedTheme = this.themes[theme] || this.themes.modern;
    
    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Slide Preview</title>
        <style>
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }
          
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: ${selectedTheme.text};
            background: ${selectedTheme.background};
            padding: 40px;
            min-height: 100vh;
          }
          
          .slide-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            overflow: hidden;
          }
          
          .slide-header {
            background: linear-gradient(135deg, ${selectedTheme.gradient[0]} 0%, ${selectedTheme.gradient[1]} 100%);
            color: white;
            padding: 40px;
            text-align: center;
          }
          
          .slide-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
          }
          
          .slide-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
          }
          
          .slide-content {
            padding: 40px;
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
            border-left: 4px solid ${selectedTheme.primary};
          }
          
          .main-content h3 {
            color: ${selectedTheme.primary};
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
            color: ${selectedTheme.primary};
            font-weight: bold;
            position: absolute;
            left: 0;
          }
          
          .visual-elements {
            background: #fef3c7;
            padding: 30px;
            border-radius: 12px;
            border-left: 4px solid ${selectedTheme.accent};
          }
          
          .visual-elements h3 {
            color: ${selectedTheme.accent};
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
            border-left: 4px solid ${selectedTheme.accent};
          }
          
          .audio-script h4 {
            color: ${selectedTheme.accent};
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
          }
          
          .audio-script p {
            font-style: italic;
            color: ${selectedTheme.secondary};
          }
          
          .udl-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            background: ${selectedTheme.accent};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
          }
          
          .slide-number {
            position: absolute;
            bottom: 20px;
            right: 20px;
            font-size: 0.9rem;
            color: ${selectedTheme.secondary};
          }
        </style>
      </head>
      <body>
        <div class="slide-container">
          <div class="slide-header">
            <div class="udl-badge">UDL-Compliant</div>
            <h1 class="slide-title">${slideData.title || 'Slide Title'}</h1>
            <p class="slide-subtitle">${slideData.gagne_event_name || 'Event'}</p>
          </div>
          
          <div class="slide-content">
            <div class="content-grid">
              <div class="main-content">
                <h3>Main Content</h3>
                <ul>
                  ${this.cleanMarkdown(slideData.content || '').split('\n').filter(line => line.trim()).map(line => 
                    `<li>${line.trim()}</li>`
                  ).join('')}
                </ul>
              </div>
              
              ${slideData.visual_elements && slideData.visual_elements.length > 0 ? `
                <div class="visual-elements">
                  <h3>Visual Elements</h3>
                  <ul>
                    ${slideData.visual_elements.map(element => 
                      `<li>${typeof element === 'object' ? element.description || 'Visual element' : element}</li>`
                    ).join('')}
                  </ul>
                </div>
              ` : ''}
            </div>
            
            ${slideData.audio_script ? `
              <div class="audio-script">
                <h4>Audio Script</h4>
                <p>${slideData.audio_script}</p>
              </div>
            ` : ''}
            
            <div class="slide-number">1</div>
          </div>
        </div>
      </body>
      </html>
    `;
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

module.exports = TemplateService; 