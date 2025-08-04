import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
import base64
import requests
from PIL import Image
import io
import re

logger = logging.getLogger(__name__)

class SlideDesignService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.logger = logging.getLogger(__name__)
        
        # Premium color schemes for different slide types
        self.color_schemes = {
            "title": {
                "primary": "#1e40af",      # Blue
                "secondary": "#3b82f6",
                "accent": "#fbbf24",       # Yellow
                "background": "#f8fafc",
                "text": "#1e293b"
            },
            "content": {
                "primary": "#059669",      # Green
                "secondary": "#10b981",
                "accent": "#f59e0b",       # Orange
                "background": "#ffffff",
                "text": "#374151"
            },
            "activity": {
                "primary": "#7c3aed",      # Purple
                "secondary": "#8b5cf6",
                "accent": "#ec4899",       # Pink
                "background": "#faf5ff",
                "text": "#1f2937"
            },
            "assessment": {
                "primary": "#dc2626",      # Red
                "secondary": "#ef4444",
                "accent": "#fbbf24",       # Yellow
                "background": "#fef2f2",
                "text": "#1f2937"
            }
        }
    
    async def generate_slide_image(self, slide_content: Dict[str, Any], slide_type: str) -> Optional[str]:
        """Generate relevant image using DALL-E 3 for a slide"""
        try:
            # Create a descriptive prompt for the image
            prompt = self._create_image_prompt(slide_content, slide_type)
            
            self.logger.info(f"Generating image for slide: {slide_content.get('title', 'Untitled')}")
            self.logger.info(f"Image prompt: {prompt}")
            
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            self.logger.info(f"Image generated successfully: {image_url}")
            
            # Download and convert to base64 for embedding
            image_base64 = await self._download_and_convert_image(image_url)
            return image_base64
            
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            return None
    
    def _create_image_prompt(self, slide_content: Dict[str, Any], slide_type: str) -> str:
        """Create a detailed prompt for DALL-E 3 based on slide content"""
        title = slide_content.get('title', '')
        content = slide_content.get('content', '')
        gagne_event = slide_content.get('gagne_event_name', '')
        
        # Base prompt structure
        base_prompt = f"Create a professional, educational illustration for a slide about '{title}'. "
        
        # Add context based on Gagne event type
        event_prompts = {
            "Gain Attention": "The image should be engaging and attention-grabbing, suitable for the beginning of a lesson. ",
            "Inform Learners of Objectives": "The image should represent learning goals and objectives in a clear, motivational way. ",
            "Stimulate Recall of Prior Learning": "The image should show connections to previous knowledge or concepts. ",
            "Present the Content": "The image should clearly illustrate the main concept or topic being taught. ",
            "Provide Learning Guidance": "The image should show guidance, examples, or step-by-step processes. ",
            "Elicit Performance": "The image should represent active learning, practice, or hands-on activities. ",
            "Provide Feedback": "The image should show assessment, evaluation, or constructive feedback. ",
            "Assess Performance": "The image should represent testing, evaluation, or measurement of learning. ",
            "Enhance Retention and Transfer": "The image should show application, real-world use, or knowledge transfer. "
        }
        
        event_context = event_prompts.get(gagne_event, "")
        
        # Add content-specific details
        content_context = ""
        if "queue" in content.lower() or "data structure" in content.lower():
            content_context = "Include visual elements related to computer science, programming, or data structures. "
        elif "algorithm" in content.lower():
            content_context = "Include visual elements related to algorithms, flowcharts, or computational thinking. "
        elif "programming" in content.lower():
            content_context = "Include visual elements related to coding, software development, or programming concepts. "
        
        # Style requirements
        style_requirements = "Use a modern, clean, professional style suitable for educational content. The image should be colorful but not overwhelming, with clear visual hierarchy. Avoid text in the image. Use a flat design style with subtle shadows and depth. "
        
        # Accessibility considerations
        accessibility = "Ensure the image has good contrast and is accessible to viewers with different visual abilities. "
        
        full_prompt = base_prompt + event_context + content_context + style_requirements + accessibility
        
        return full_prompt
    
    async def _download_and_convert_image(self, image_url: str) -> str:
        """Download image and convert to base64"""
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Convert to base64
            image_data = response.content
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            return f"data:image/png;base64,{base64_image}"
            
        except Exception as e:
            self.logger.error(f"Error downloading image: {str(e)}")
            return ""
    
    def generate_slide_html(self, slide_data: Dict[str, Any], slide_number: int, total_slides: int) -> str:
        """Generate premium HTML for a single slide"""
        try:
            # Determine slide type and color scheme
            slide_type = self._determine_slide_type(slide_data)
            colors = self.color_schemes.get(slide_type, self.color_schemes["content"])
            
            # Get slide content
            title = slide_data.get('title', 'Untitled Slide')
            content = slide_data.get('content', '')
            visual_elements = slide_data.get('visual_elements', [])
            audio_script = slide_data.get('audio_script', '')
            speaker_notes = slide_data.get('speaker_notes', '')
            udl_guidelines = slide_data.get('udl_guidelines', [])
            
            # Generate image if available
            image_html = ""
            if slide_data.get('generated_image'):
                image_html = f"""
                <div class="slide-image">
                    <img src="{slide_data['generated_image']}" alt="Slide illustration" />
                </div>
                """
            
            # Create visual elements HTML
            visual_elements_html = ""
            if visual_elements:
                visual_elements_html = """
                <div class="visual-elements">
                    <h4>Visual Elements</h4>
                    <ul>
                """
                for element in visual_elements:
                    if isinstance(element, dict):
                        desc = element.get('description', 'Visual element')
                    else:
                        desc = str(element)
                    visual_elements_html += f"<li>{desc}</li>"
                visual_elements_html += "</ul></div>"
            
            # Create UDL guidelines HTML
            udl_html = ""
            if udl_guidelines:
                udl_html = """
                <div class="udl-guidelines">
                    <h4>UDL Guidelines</h4>
                    <ul>
                """
                for guideline in udl_guidelines:
                    udl_html += f"<li>{guideline}</li>"
                udl_html += "</ul></div>"
            
            # Generate the complete slide HTML
            slide_html = f"""
            <div class="slide slide-{slide_type}" style="--primary-color: {colors['primary']}; --secondary-color: {colors['secondary']}; --accent-color: {colors['accent']}; --background-color: {colors['background']}; --text-color: {colors['text']};">
                <div class="slide-header">
                    <div class="slide-number">{slide_number} / {total_slides}</div>
                    <div class="slide-type">{slide_type.title()}</div>
                </div>
                
                <div class="slide-content">
                    <h2 class="slide-title">{title}</h2>
                    
                    <div class="slide-main">
                        <div class="content-section">
                            <div class="content-text">
                                {self._convert_markdown_to_html(content)}
                            </div>
                            {image_html}
                        </div>
                        
                        <div class="slide-details">
                            {visual_elements_html}
                            {udl_html}
                        </div>
                    </div>
                    
                    {self._generate_audio_section(audio_script)}
                    {self._generate_speaker_notes(speaker_notes)}
                </div>
                
                <div class="slide-footer">
                    <div class="progress-bar">
                        <div class="progress" style="width: {(slide_number / total_slides) * 100}%"></div>
                    </div>
                </div>
            </div>
            """
            
            return slide_html
            
        except Exception as e:
            self.logger.error(f"Error generating slide HTML: {str(e)}")
            return self._generate_fallback_slide_html(slide_data, slide_number, total_slides)
    
    def _determine_slide_type(self, slide_data: Dict[str, Any]) -> str:
        """Determine the type of slide for styling"""
        gagne_event = slide_data.get('gagne_event_name', '').lower()
        
        if 'attention' in gagne_event:
            return 'title'
        elif 'objectives' in gagne_event:
            return 'content'
        elif 'performance' in gagne_event or 'practice' in gagne_event:
            return 'activity'
        elif 'assess' in gagne_event or 'feedback' in gagne_event:
            return 'assessment'
        else:
            return 'content'
    
    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown content to HTML"""
        if not markdown_text:
            return ""
        
        # Simple markdown to HTML conversion
        html = markdown_text
        
        # Headers
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold and italic
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Lists
        html = re.sub(r'^\* (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # Wrap lists in ul tags
        lines = html.split('\n')
        in_list = False
        result = []
        
        for line in lines:
            if line.strip().startswith('<li>'):
                if not in_list:
                    result.append('<ul>')
                    in_list = True
                result.append(line)
            else:
                if in_list:
                    result.append('</ul>')
                    in_list = False
                result.append(line)
        
        if in_list:
            result.append('</ul>')
        
        html = '\n'.join(result)
        
        # Paragraphs
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'
        
        return html
    
    def _generate_audio_section(self, audio_script: str) -> str:
        """Generate HTML for audio script section"""
        if not audio_script:
            return ""
        
        return f"""
        <div class="audio-section">
            <h4>Audio Script</h4>
            <p>{audio_script}</p>
        </div>
        """
    
    def _generate_speaker_notes(self, speaker_notes: str) -> str:
        """Generate HTML for speaker notes section"""
        if not speaker_notes:
            return ""
        
        return f"""
        <div class="speaker-notes">
            <h4>Speaker Notes</h4>
            <p>{speaker_notes}</p>
        </div>
        """
    
    def _generate_fallback_slide_html(self, slide_data: Dict[str, Any], slide_number: int, total_slides: int) -> str:
        """Generate a simple fallback slide HTML"""
        title = slide_data.get('title', 'Untitled Slide')
        content = slide_data.get('content', '')
        
        return f"""
        <div class="slide slide-content">
            <div class="slide-header">
                <div class="slide-number">{slide_number} / {total_slides}</div>
            </div>
            
            <div class="slide-content">
                <h2 class="slide-title">{title}</h2>
                <div class="content-text">
                    <p>{content}</p>
                </div>
            </div>
        </div>
        """
    
    def generate_presentation_html(self, slides: List[Dict[str, Any]], presentation_title: str, lesson_info: Dict[str, Any]) -> str:
        """Generate complete presentation HTML with CSS styling"""
        try:
            # Generate all slide HTML
            slide_htmls = []
            for i, slide_data in enumerate(slides, 1):
                slide_html = self.generate_slide_html(slide_data, i, len(slides))
                slide_htmls.append(slide_html)
            
            # Create the complete presentation HTML
            presentation_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{presentation_title}</title>
                <style>
                    {self._generate_css_styles()}
                </style>
            </head>
            <body>
                <div class="presentation">
                    <div class="presentation-header">
                        <h1 class="presentation-title">{presentation_title}</h1>
                        <div class="presentation-meta">
                            <span>Course: {lesson_info.get('course_title', 'Unknown')}</span>
                            <span>Topic: {lesson_info.get('lesson_topic', 'Unknown')}</span>
                            <span>Duration: {lesson_info.get('duration_minutes', 0)} minutes</span>
                        </div>
                    </div>
                    
                    <div class="slides-container">
                        {''.join(slide_htmls)}
                    </div>
                    
                    <div class="presentation-footer">
                        <div class="udl-compliance">
                            <span>UDL Compliant</span>
                            <span>Accessible Design</span>
                            <span>Multimodal Content</span>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return presentation_html
            
        except Exception as e:
            self.logger.error(f"Error generating presentation HTML: {str(e)}")
            return f"<html><body><h1>Error generating presentation: {str(e)}</h1></body></html>"
    
    def _generate_css_styles(self) -> str:
        """Generate premium CSS styles for the presentation"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .presentation {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .presentation-header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .presentation-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .presentation-meta {
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .slides-container {
            padding: 40px;
        }
        
        .slide {
            margin-bottom: 40px;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            background: var(--background-color);
            border-left: 8px solid var(--primary-color);
        }
        
        .slide-header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 15px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .slide-number {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .slide-type {
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .slide-content {
            padding: 30px;
        }
        
        .slide-title {
            color: var(--primary-color);
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 25px;
            line-height: 1.2;
        }
        
        .slide-main {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 30px;
            margin-bottom: 25px;
        }
        
        .content-section {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .content-text {
            color: var(--text-color);
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        .content-text h1, .content-text h2, .content-text h3 {
            color: var(--primary-color);
            margin-bottom: 15px;
        }
        
        .content-text p {
            margin-bottom: 15px;
        }
        
        .content-text ul, .content-text ol {
            margin-left: 20px;
            margin-bottom: 15px;
        }
        
        .content-text li {
            margin-bottom: 8px;
        }
        
        .slide-image {
            text-align: center;
            margin: 20px 0;
        }
        
        .slide-image img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .slide-details {
            background: rgba(var(--primary-color-rgb, 59, 130, 246), 0.05);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid var(--accent-color);
        }
        
        .slide-details h4 {
            color: var(--primary-color);
            font-size: 1.2rem;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .slide-details ul {
            list-style: none;
            margin-left: 0;
        }
        
        .slide-details li {
            padding: 8px 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
            color: var(--text-color);
        }
        
        .slide-details li:last-child {
            border-bottom: none;
        }
        
        .audio-section, .speaker-notes {
            background: rgba(var(--accent-color-rgb, 251, 191, 36), 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            border-left: 4px solid var(--accent-color);
        }
        
        .audio-section h4, .speaker-notes h4 {
            color: var(--accent-color);
            font-size: 1.1rem;
            margin-bottom: 10px;
            font-weight: 600;
        }
        
        .slide-footer {
            padding: 15px 25px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .progress {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            transition: width 0.3s ease;
        }
        
        .presentation-footer {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px 30px;
            text-align: center;
        }
        
        .udl-compliance {
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 1rem;
            opacity: 0.9;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .slide-main {
                grid-template-columns: 1fr;
            }
            
            .presentation-meta {
                flex-direction: column;
                gap: 10px;
            }
            
            .slide-title {
                font-size: 1.5rem;
            }
            
            .presentation-title {
                font-size: 2rem;
            }
        }
        
        /* Print styles for PDF export */
        @media print {
            body {
                background: white;
                padding: 0;
            }
            
            .presentation {
                box-shadow: none;
                border-radius: 0;
            }
            
            .slide {
                page-break-after: always;
                margin-bottom: 0;
            }
        }
        """ 