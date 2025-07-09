import io
import os
from datetime import datetime
from typing import BinaryIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate
from reportlab.lib import colors

from ..models.lesson import LessonResponse, PDFRequest


class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom styles for the PDF document"""
        # Title style
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=HexColor('#2563eb'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))

        # Subtitle style
        if 'CustomSubtitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomSubtitle',
                parent=self.styles['Heading2'],
                fontSize=16,
                spaceAfter=20,
                textColor=HexColor('#374151'),
                alignment=TA_CENTER,
                fontName='Helvetica'
            ))

        # Section heading style
        if 'SectionHeading' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeading',
                parent=self.styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20,
                textColor=HexColor('#1f2937'),
                fontName='Helvetica-Bold',
                leftIndent=0
            ))

        # Subsection heading style
        if 'SubsectionHeading' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SubsectionHeading',
                parent=self.styles['Heading3'],
                fontSize=12,
                spaceAfter=8,
                spaceBefore=12,
                textColor=HexColor('#374151'),
                fontName='Helvetica-Bold',
                leftIndent=20
            ))

        # Custom Body text style (using different name to avoid conflict)
        if 'CustomBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                textColor=HexColor('#374151'),
                fontName='Helvetica',
                alignment=TA_JUSTIFY,
                leftIndent=20
            ))

        # List item style
        if 'ListItem' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ListItem',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=4,
                textColor=HexColor('#4b5563'),
                fontName='Helvetica',
                leftIndent=40,
                bulletIndent=30
            ))

        # Objective style
        if 'Objective' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='Objective',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                textColor=HexColor('#1f2937'),
                fontName='Helvetica',
                leftIndent=30,
                rightIndent=20
            ))

    def generate_pdf(self, request: PDFRequest) -> BinaryIO:
        """Generate a formatted PDF from lesson data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        story = []
        lesson_data = request.lesson_data

        # Cover page
        if request.include_cover_page:
            story.extend(self._create_cover_page(lesson_data))
            story.append(PageBreak())

        # Table of contents
        story.extend(self._create_table_of_contents())
        story.append(PageBreak())

        # Lesson overview
        story.extend(self._create_lesson_overview(lesson_data))

        # Learning objectives
        story.extend(self._create_objectives_section(lesson_data))

        # Lesson plan
        story.extend(self._create_lesson_plan_section(lesson_data))

        # Gagne's Nine Events
        story.extend(self._create_gagne_events_section(lesson_data))

        # Appendices
        if request.include_appendices:
            story.extend(self._create_appendices(lesson_data))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def _create_cover_page(self, lesson_data: LessonResponse) -> list:
        """Create the cover page"""
        story = []

        # Main title
        title = f"{lesson_data.lesson_info['course_title']}"
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))

        # Lesson topic
        subtitle = f"Lesson: {lesson_data.lesson_info['lesson_topic']}"
        story.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
        story.append(Spacer(1, 40))

        # Details table
        details_data = [
            ['Grade Level:', lesson_data.lesson_info['grade_level'].title()],
            ['Duration:', f"{lesson_data.lesson_info['duration_minutes']} minutes"],
            ['Generated:', datetime.now().strftime('%B %d, %Y')],
            ['Total Objectives:', str(len(lesson_data.objectives))],
            ['Bloom\'s Levels:', ', '.join([obj.bloom_level.title() for obj in lesson_data.objectives[:3]]) + '...']
        ]

        details_table = Table(details_data, colWidths=[2 * inch, 3 * inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(details_table)
        story.append(Spacer(1, 60))

        # Academic disclaimer
        disclaimer = """
        This lesson plan was generated using AI-assisted instructional design principles 
        based on Bloom's Taxonomy and Gagne's Nine Events of Instruction. Please review 
        and adapt as needed for your specific teaching context and student needs.
        """
        story.append(Paragraph(disclaimer, self.styles['CustomBodyText']))

        return story

    def _create_table_of_contents(self) -> list:
        """Create table of contents"""
        story = []

        story.append(Paragraph("Table of Contents", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))

        toc_data = [
            ['1. Lesson Overview', '3'],
            ['2. Learning Objectives', '4'],
            ['3. Lesson Plan Details', '5'],
            ['4. Gagne\'s Nine Events of Instruction', '6'],
            ['5. Assessment Strategies', '8'],
            ['6. Resources and Materials', '9'],
            ['7. Appendices', '10']
        ]

        toc_table = Table(toc_data, colWidths=[4 * inch, 1 * inch])
        toc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        story.append(toc_table)
        return story

    def _create_lesson_overview(self, lesson_data: LessonResponse) -> list:
        """Create lesson overview section"""
        story = []

        story.append(Paragraph("1. Lesson Overview", self.styles['SectionHeading']))

        # Basic information
        info = lesson_data.lesson_info
        overview_text = f"""
        <b>Course:</b> {info['course_title']}<br/>
        <b>Lesson Topic:</b> {info['lesson_topic']}<br/>
        <b>Grade Level:</b> {info['grade_level'].title()}<br/>
        <b>Duration:</b> {info['duration_minutes']} minutes<br/>
        <b>Date Created:</b> {datetime.now().strftime('%B %d, %Y')}
        """

        story.append(Paragraph(overview_text, self.styles['CustomBodyText']))
        story.append(Spacer(1, 15))

        # Preliminary objectives
        story.append(Paragraph("Preliminary Learning Goals", self.styles['SubsectionHeading']))
        story.append(Paragraph(info['preliminary_objectives'], self.styles['CustomBodyText']))
        story.append(Spacer(1, 15))

        # Selected Bloom's levels
        bloom_levels = [level.title() for level in info['selected_bloom_levels']]
        story.append(Paragraph("Selected Bloom's Taxonomy Levels", self.styles['SubsectionHeading']))
        story.append(Paragraph(', '.join(bloom_levels), self.styles['CustomBodyText']))

        story.append(Spacer(1, 20))
        return story

    def _create_objectives_section(self, lesson_data: LessonResponse) -> list:
        """Create learning objectives section"""
        story = []

        story.append(Paragraph("2. Learning Objectives", self.styles['SectionHeading']))

        # Group objectives by Bloom's level
        objectives_by_level = {}
        for obj in lesson_data.objectives:
            level = obj.bloom_level.title()
            if level not in objectives_by_level:
                objectives_by_level[level] = []
            objectives_by_level[level].append(obj)

        for level, objectives in objectives_by_level.items():
            story.append(Paragraph(f"{level} Level Objectives", self.styles['SubsectionHeading']))

            for i, obj in enumerate(objectives, 1):
                objective_text = f"{i}. {obj.objective}"
                if obj.condition:
                    objective_text += f" ({obj.condition})"
                if obj.criteria:
                    objective_text += f" - {obj.criteria}"

                story.append(Paragraph(objective_text, self.styles['Objective']))

            story.append(Spacer(1, 10))

        return story

    def _create_lesson_plan_section(self, lesson_data: LessonResponse) -> list:
        """Create lesson plan section"""
        story = []

        story.append(Paragraph("3. Lesson Plan Details", self.styles['SectionHeading']))

        plan = lesson_data.lesson_plan

        # Overview
        story.append(Paragraph("Lesson Overview", self.styles['SubsectionHeading']))
        story.append(Paragraph(plan.overview, self.styles['CustomBodyText']))
        story.append(Spacer(1, 10))

        # Prerequisites
        if plan.prerequisites:
            story.append(Paragraph("Prerequisites", self.styles['SubsectionHeading']))
            for prereq in plan.prerequisites:
                story.append(Paragraph(f"• {prereq}", self.styles['ListItem']))
            story.append(Spacer(1, 10))

        # Materials
        if plan.materials:
            story.append(Paragraph("Materials and Resources", self.styles['SubsectionHeading']))
            for material in plan.materials:
                story.append(Paragraph(f"• {material}", self.styles['ListItem']))
            story.append(Spacer(1, 10))

        # Technology requirements
        if plan.technology_requirements:
            story.append(Paragraph("Technology Requirements", self.styles['SubsectionHeading']))
            for tech in plan.technology_requirements:
                story.append(Paragraph(f"• {tech}", self.styles['ListItem']))
            story.append(Spacer(1, 10))

        # Assessment methods
        if plan.assessment_methods:
            story.append(Paragraph("Assessment Methods", self.styles['SubsectionHeading']))
            for method in plan.assessment_methods:
                story.append(Paragraph(f"• {method}", self.styles['ListItem']))
            story.append(Spacer(1, 10))

        # Differentiation strategies
        if plan.differentiation_strategies:
            story.append(Paragraph("Differentiation Strategies", self.styles['SubsectionHeading']))
            for strategy in plan.differentiation_strategies:
                story.append(Paragraph(f"• {strategy}", self.styles['ListItem']))
            story.append(Spacer(1, 10))

        return story

    def _create_gagne_events_section(self, lesson_data: LessonResponse) -> list:
        """Create Gagne's Nine Events section"""
        story = []

        story.append(Paragraph("4. Gagne's Nine Events of Instruction", self.styles['SectionHeading']))

        for event in lesson_data.gagne_events:
            # Event title
            event_title = f"Event {event.event_number}: {event.event_name}"
            story.append(Paragraph(event_title, self.styles['SubsectionHeading']))

            # Description
            story.append(Paragraph(f"<b>Purpose:</b> {event.description}", self.styles['CustomBodyText']))
            story.append(Paragraph(f"<b>Duration:</b> {event.duration_minutes} minutes", self.styles['CustomBodyText']))

            # Activities
            if event.activities:
                story.append(Paragraph("<b>Activities:</b>", self.styles['CustomBodyText']))
                for activity in event.activities:
                    story.append(Paragraph(f"• {activity}", self.styles['ListItem']))

            # Materials
            if event.materials_needed:
                story.append(Paragraph("<b>Materials Needed:</b>", self.styles['CustomBodyText']))
                for material in event.materials_needed:
                    story.append(Paragraph(f"• {material}", self.styles['ListItem']))

            # Assessment strategy
            if event.assessment_strategy:
                story.append(
                    Paragraph(f"<b>Assessment Strategy:</b> {event.assessment_strategy}", self.styles['CustomBodyText']))

            story.append(Spacer(1, 15))

        return story

    def _create_appendices(self, lesson_data: LessonResponse) -> list:
        """Create appendices section"""
        story = []

        story.append(PageBreak())
        story.append(Paragraph("Appendices", self.styles['SectionHeading']))

        # Appendix A: Bloom's Taxonomy Reference
        story.append(Paragraph("Appendix A: Bloom's Taxonomy Quick Reference", self.styles['SubsectionHeading']))

        bloom_reference = [
            ['Level', 'Definition', 'Key Verbs'],
            ['Remember', 'Recall facts and basic concepts', 'define, duplicate, list, memorize, recall, repeat, state'],
            ['Understand', 'Explain ideas or concepts',
             'classify, describe, discuss, explain, identify, locate, recognize, report, select, translate'],
            ['Apply', 'Use information in new situations',
             'execute, implement, solve, use, demonstrate, interpret, operate, schedule, sketch'],
            ['Analyze', 'Draw connections among ideas',
             'differentiate, organize, relate, compare, contrast, distinguish, examine, experiment, question, test'],
            ['Evaluate', 'Justify a stand or decision',
             'appraise, argue, defend, judge, select, support, value, critique, weigh'],
            ['Create', 'Produce new or original work',
             'design, assemble, construct, conjecture, develop, formulate, author, investigate']
        ]

        bloom_table = Table(bloom_reference, colWidths=[1.2 * inch, 2.3 * inch, 2.5 * inch])
        bloom_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f9fafb')])
        ]))

        story.append(bloom_table)
        story.append(Spacer(1, 20))

        # Appendix B: Gagne's Events Reference
        story.append(Paragraph("Appendix B: Gagne's Nine Events Quick Reference", self.styles['SubsectionHeading']))

        gagne_reference = [
            ['Event', 'Purpose', 'Example Strategies'],
            ['1. Gain Attention', 'Capture student interest', 'Question, story, demonstration, multimedia'],
            ['2. Inform Objectives', 'Share learning goals', 'Present objectives, explain relevance'],
            ['3. Stimulate Recall', 'Connect to prior knowledge', 'Review, prerequisites, bridging'],
            ['4. Present Content', 'Deliver new information', 'Lecture, reading, multimedia, examples'],
            ['5. Provide Guidance', 'Guide learning process', 'Coaching, hints, prompts, modeling'],
            ['6. Elicit Performance', 'Students practice', 'Exercises, problems, simulations'],
            ['7. Provide Feedback', 'Give constructive feedback', 'Corrections, explanations, reinforcement'],
            ['8. Assess Performance', 'Evaluate learning', 'Tests, observations, portfolios'],
            ['9. Enhance Retention', 'Promote transfer', 'Summary, real-world applications, reflection']
        ]

        gagne_table = Table(gagne_reference, colWidths=[1.2 * inch, 2 * inch, 2.8 * inch])
        gagne_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f0fdf4')])
        ]))

        story.append(gagne_table)

        return story