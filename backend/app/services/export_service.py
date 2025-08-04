import io
import logging
from typing import Dict, Any, List
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import markdown
import re
from .slide_design_service import SlideDesignService

logger = logging.getLogger(__name__)

class ExportService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.slide_design_service = SlideDesignService()
    
    async def export_to_powerpoint(self, course_content: Dict[str, Any], lesson_data: Dict[str, Any]) -> io.BytesIO:
        """Export course content to PowerPoint format with premium design"""
        try:
            self.logger.info("Creating premium PowerPoint presentation")
            
            # Create a new presentation
            prs = Presentation()
            
            # Get slide layouts
            title_slide_layout = prs.slide_layouts[0]  # Title slide
            content_slide_layout = prs.slide_layouts[1]  # Title and content
            section_header_layout = prs.slide_layouts[2]  # Section header
            
            # Add title slide
            title_slide = prs.slides.add_slide(title_slide_layout)
            title = title_slide.shapes.title
            subtitle = title_slide.placeholders[1]
            
            lesson_info = lesson_data.get("lesson_info", {})
            title.text = f"{lesson_info.get('course_title', 'Course')} - {lesson_info.get('lesson_topic', 'Lesson')}"
            subtitle.text = f"UDL-Compliant Course Content\n{len(course_content.get('slides', []))} slides • {course_content.get('estimated_duration', 0)} minutes"
            
            # Add slides for each Gagne event
            slides = course_content.get('slides', [])
            current_event = None
            
            for slide_data in slides:
                # Check if this is a new event
                if slide_data.get('gagne_event') != current_event:
                    current_event = slide_data.get('gagne_event')
                    
                    # Add section header for new event
                    section_slide = prs.slides.add_slide(section_header_layout)
                    section_title = section_slide.shapes.title
                    section_title.text = f"Event {current_event}: {slide_data.get('gagne_event_name', 'Unknown')}"
                
                # Add content slide
                content_slide = prs.slides.add_slide(content_slide_layout)
                slide_title = content_slide.shapes.title
                content_placeholder = content_slide.placeholders[1]
                
                # Set slide title
                slide_title.text = slide_data.get('title', 'Untitled Slide')
                
                # Add content
                content_text = ""
                
                # Add main content
                if slide_data.get('content'):
                    content_text += f"{slide_data['content']}\n\n"
                
                # Add visual elements description
                visual_elements = slide_data.get('visual_elements', [])
                if visual_elements:
                    content_text += "Visual Elements:\n"
                    for element in visual_elements:
                        if isinstance(element, dict):
                            content_text += f"• {element.get('description', 'Visual element')}\n"
                        else:
                            content_text += f"• {element}\n"
                    content_text += "\n"
                
                # Add audio script
                if slide_data.get('audio_script'):
                    content_text += f"Audio Script: {slide_data['audio_script']}\n\n"
                
                # Add speaker notes
                if slide_data.get('speaker_notes'):
                    content_text += f"Speaker Notes: {slide_data['speaker_notes']}\n\n"
                
                # Add UDL guidelines
                udl_guidelines = slide_data.get('udl_guidelines', [])
                if udl_guidelines:
                    content_text += "UDL Guidelines:\n"
                    for guideline in udl_guidelines:
                        content_text += f"• {guideline}\n"
                
                content_placeholder.text = content_text
            
            # Save to buffer
            buffer = io.BytesIO()
            prs.save(buffer)
            buffer.seek(0)
            
            self.logger.info(f"PowerPoint export completed with {len(prs.slides)} slides")
            return buffer
            
        except Exception as e:
            self.logger.error(f"Error in PowerPoint export: {str(e)}")
            raise Exception(f"Failed to create PowerPoint: {str(e)}")
    
    async def export_to_pdf(self, course_content: Dict[str, Any], lesson_data: Dict[str, Any]) -> io.BytesIO:
        """Export course content to PDF format using premium HTML/CSS design"""
        try:
            self.logger.info("Creating premium PDF document")
            
            # Generate premium HTML presentation
            slides = course_content.get('slides', [])
            presentation_title = course_content.get('presentation_title', 'Course Content')
            lesson_info = lesson_data.get("lesson_info", {})
            
            # Convert slides to list of dicts for HTML generation
            slides_data = []
            for slide in slides:
                slide_dict = slide.dict() if hasattr(slide, 'dict') else slide
                slides_data.append(slide_dict)
            
            # Generate premium HTML presentation
            html_content = self.slide_design_service.generate_presentation_html(
                slides_data, presentation_title, lesson_info
            )
            
            # Convert HTML to PDF using WeasyPrint or similar
            # For now, we'll use ReportLab as fallback
            pdf_buffer = await self._html_to_pdf_fallback(html_content, presentation_title)
            
            self.logger.info(f"PDF export completed with {len(slides)} slides")
            return pdf_buffer
            
        except Exception as e:
            self.logger.error(f"Error in PDF export: {str(e)}")
            raise Exception(f"Failed to create PDF: {str(e)}")
    
    async def _html_to_pdf_fallback(self, html_content: str, title: str) -> io.BytesIO:
        """Fallback method to convert HTML to PDF using ReportLab"""
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20
            )
            normal_style = styles['Normal']
            
            # Build story (content)
            story = []
            
            # Add title page
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # Add subtitle
            subtitle_text = f"UDL-Compliant Course Content"
            story.append(Paragraph(subtitle_text, heading_style))
            story.append(Spacer(1, 20))
            
            # Extract content from HTML (simplified)
            # This is a basic extraction - in a full implementation, you'd use a proper HTML parser
            content_lines = html_content.split('\n')
            current_section = ""
            
            for line in content_lines:
                if '<h2' in line:
                    # Extract slide title
                    title_match = re.search(r'<h2[^>]*>(.*?)</h2>', line)
                    if title_match:
                        story.append(Paragraph(title_match.group(1), heading_style))
                        story.append(Spacer(1, 6))
                elif '<p>' in line:
                    # Extract paragraph content
                    p_match = re.search(r'<p[^>]*>(.*?)</p>', line)
                    if p_match:
                        content = p_match.group(1)
                        # Remove HTML tags
                        content = re.sub(r'<[^>]+>', '', content)
                        if content.strip():
                            story.append(Paragraph(content, normal_style))
                            story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            self.logger.error(f"Error in HTML to PDF conversion: {str(e)}")
            # Return a simple PDF as fallback
            return await self._create_simple_pdf(title)
    
    async def _create_simple_pdf(self, title: str) -> io.BytesIO:
        """Create a simple PDF as fallback"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            
            styles = getSampleStyleSheet()
            story = []
            
            story.append(Paragraph(title, styles['Heading1']))
            story.append(Spacer(1, 20))
            story.append(Paragraph("Course content will be available in the HTML export.", styles['Normal']))
            
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            self.logger.error(f"Error creating simple PDF: {str(e)}")
            raise Exception("Failed to create PDF")
    
    def export_to_html(self, course_content: Dict[str, Any], lesson_data: Dict[str, Any]) -> str:
        """Export course content to premium HTML format"""
        try:
            self.logger.info("Creating premium HTML presentation")
            
            # Generate premium HTML presentation
            slides = course_content.get('slides', [])
            presentation_title = course_content.get('presentation_title', 'Course Content')
            lesson_info = lesson_data.get("lesson_info", {})
            
            # Convert slides to list of dicts for HTML generation
            slides_data = []
            for slide in slides:
                slide_dict = slide.dict() if hasattr(slide, 'dict') else slide
                slides_data.append(slide_dict)
            
            # Generate premium HTML presentation
            html_content = self.slide_design_service.generate_presentation_html(
                slides_data, presentation_title, lesson_info
            )
            
            self.logger.info(f"HTML export completed with {len(slides)} slides")
            return html_content
            
        except Exception as e:
            self.logger.error(f"Error in HTML export: {str(e)}")
            return f"<html><body><h1>Error generating HTML presentation: {str(e)}</h1></body></html>"
    
    def _convert_markdown_to_text(self, markdown_text: str) -> str:
        """Convert markdown text to plain text for PDF"""
        if not markdown_text:
            return ""
        
        # Remove markdown formatting
        text = markdown_text
        
        # Remove headers
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        
        # Remove bold and italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Remove links
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Remove lists
        text = re.sub(r'^\s*[-*+]\s*', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text 