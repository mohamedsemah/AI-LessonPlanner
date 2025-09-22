"""
Content Agent for Multi-Agent Lesson Planning System

This agent is responsible for generating multimodal teaching content:
- Comprehensive slide presentations for Gagne's Nine Events
- Visual elements and multimedia content
- Audio scripts and speaker notes
- Interactive activities and assessments
- UDL-compliant content design

The agent creates ready-to-use teaching materials that are pedagogically sound,
visually engaging, and accessible to diverse learners.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ...models.gagne_slides import (
    GagneEventSlides, SlideContent, VisualElement, SlideContentType, 
    VisualElementType, GagneSlidesResponse, SlideGenerationRequest
)
from ...models.lesson import GagneEvent, LessonObjective, LessonPlan

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):
    """
    Agent responsible for generating multimodal teaching content.
    
    This agent handles:
    - Slide generation for Gagne's Nine Events
    - Visual elements and multimedia content
    - Audio scripts and speaker notes
    - Interactive activities and assessments
    - UDL-compliant content design
    """
    
    def __init__(self, client=None):
        """Initialize the Content Agent."""
        super().__init__(client)
        self.logger = logging.getLogger(f"agents.{self.__class__.__name__}")
        self.event_templates = self._initialize_event_templates()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content generation request and create teaching materials.
        
        Args:
            input_data: Dictionary containing:
                - gagne_events: List of GagneEvent objects
                - objectives: List of LessonObjective objects
                - lesson_plan: LessonPlan object
                - lesson_info: Dictionary with lesson metadata
                
        Returns:
            Dictionary containing:
                - gagne_slides_response: GagneSlidesResponse object
                - metadata: Processing metadata
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("🎨 CONTENT AGENT STARTING")
            self.logger.info("=" * 80)
            
            gagne_events = input_data.get("gagne_events", [])
            objectives = input_data.get("objectives", [])
            lesson_plan = input_data.get("lesson_plan")
            lesson_info = input_data.get("lesson_info", {})
            
            self.logger.info(f"📊 Input data keys: {list(input_data.keys())}")
            self.logger.info(f"📋 Gagne events count: {len(gagne_events)}")
            self.logger.info(f"🎯 Objectives count: {len(objectives)}")
            self.logger.info(f"📖 Lesson plan type: {type(lesson_plan)}")
            self.logger.info(f"ℹ️ Lesson info: {lesson_info}")
            
            if not gagne_events:
                raise ValueError("gagne_events is required")
            if not objectives:
                raise ValueError("objectives is required")
            if not lesson_plan:
                raise ValueError("lesson_plan is required")
            
            self._log_processing_start(f"Generating content for {len(gagne_events)} events")
            
            # Generate comprehensive slides for all events
            self.logger.info("🤖 Calling generate_slides_for_all_events...")
            gagne_slides_response = await self.generate_slides_for_all_events(
                gagne_events, objectives, lesson_plan, lesson_info
            )
            self.logger.info(f"✅ generate_slides_for_all_events completed")
            self.logger.info(f"📊 Response type: {type(gagne_slides_response)}")
            self.logger.info(f"📊 Total slides: {gagne_slides_response.total_slides}")
            self.logger.info(f"📊 Total events: {gagne_slides_response.total_events}")
            
            self.logger.info("🔄 Converting to dictionary...")
            result = {
                "gagne_slides_response": gagne_slides_response.dict()
            }
            self.logger.info("✅ Dictionary conversion completed")
            
            metadata = {
                "total_events": len(gagne_events),
                "total_slides": gagne_slides_response.total_slides,
                "total_duration": gagne_slides_response.total_duration,
                "generation_method": "ai_enhanced",
                "quality_level": "premium"
            }
            
            self.logger.info("=" * 80)
            self.logger.info("✅ CONTENT AGENT COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 80)
            self._log_processing_success(f"Generated {gagne_slides_response.total_slides} slides across {len(gagne_events)} events")
            
            return self._create_success_response(result, metadata)
            
        except Exception as e:
            self.logger.error("=" * 80)
            self.logger.error("❌ CONTENT AGENT FAILED")
            self.logger.error("=" * 80)
            self.logger.error(f"❌ Error: {str(e)}")
            self.logger.error(f"🔍 Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"📜 Traceback: {traceback.format_exc()}")
            self._log_processing_error(e)
            return self._create_error_response(e)
    
    def _initialize_event_templates(self) -> Dict[int, Dict[str, Any]]:
        """Initialize slide templates for each Gagne event type"""
        return {
            1: {  # Gain Attention
                "slide_types": ["introduction", "activity_guide"],
                "base_slides": 2,
                "focus": "engagement",
                "visual_emphasis": "high",
                "interactive_elements": True
            },
            2: {  # Inform Learners of Objectives
                "slide_types": ["concept_explanation"],
                "base_slides": 1,
                "focus": "clarity",
                "visual_emphasis": "medium",
                "interactive_elements": False
            },
            3: {  # Stimulate Recall of Prior Learning
                "slide_types": ["activity_guide", "concept_explanation"],
                "base_slides": 2,
                "focus": "connection",
                "visual_emphasis": "medium",
                "interactive_elements": True
            },
            4: {  # Present the Content
                "slide_types": ["concept_explanation", "activity_guide"],
                "base_slides": 4,
                "focus": "comprehension",
                "visual_emphasis": "high",
                "interactive_elements": True
            },
            5: {  # Provide Learning Guidance
                "slide_types": ["activity_guide", "concept_explanation"],
                "base_slides": 3,
                "focus": "guidance",
                "visual_emphasis": "medium",
                "interactive_elements": True
            },
            6: {  # Elicit Performance
                "slide_types": ["activity_guide", "assessment"],
                "base_slides": 3,
                "focus": "practice",
                "visual_emphasis": "medium",
                "interactive_elements": True
            },
            7: {  # Provide Feedback
                "slide_types": ["assessment", "reflection"],
                "base_slides": 2,
                "focus": "improvement",
                "visual_emphasis": "low",
                "interactive_elements": False
            },
            8: {  # Assess Performance
                "slide_types": ["assessment"],
                "base_slides": 2,
                "focus": "evaluation",
                "visual_emphasis": "low",
                "interactive_elements": False
            },
            9: {  # Enhance Retention and Transfer
                "slide_types": ["reflection", "concept_explanation"],
                "base_slides": 2,
                "focus": "retention",
                "visual_emphasis": "medium",
                "interactive_elements": True
            }
        }
    
    async def generate_slides_for_all_events(
        self, 
        gagne_events: List[Any], 
        objectives: List[Any],
        lesson_plan: Any,
        lesson_info: Dict[str, Any]
    ) -> GagneSlidesResponse:
        """Generate comprehensive slides for all Gagne events"""
        try:
            self.logger.info("Starting slide generation for all Gagne events")
            
            # Generate slides for each event concurrently
            event_slide_tasks = []
            for event in gagne_events:
                task = self._generate_slides_for_event(
                    event, objectives, lesson_plan, lesson_info
                )
                event_slide_tasks.append(task)
            
            # Wait for all events to complete
            event_slides = await asyncio.gather(*event_slide_tasks)
            
            # Calculate totals
            total_slides = sum(len(event.slides) for event in event_slides)
            total_duration = sum(event.estimated_duration for event in event_slides)
            
            self.logger.info(f"Generated {total_slides} slides across {len(event_slides)} events")
            
            return GagneSlidesResponse(
                lesson_info=lesson_info,
                total_events=len(event_slides),
                total_slides=total_slides,
                total_duration=total_duration,
                events=event_slides,
                generation_metadata={
                    "service_version": "1.0.0",
                    "generation_method": "ai_enhanced",
                    "quality_level": "premium"
                },
                created_at=str(asyncio.get_event_loop().time())
            )
            
        except Exception as e:
            self.logger.error(f"Error in generate_slides_for_all_events: {str(e)}")
            raise
    
    async def _generate_slides_for_event(
        self, 
        event: Any, 
        objectives: List[Any],
        lesson_plan: Any,
        lesson_info: Dict[str, Any]
    ) -> GagneEventSlides:
        """Generate slides for a specific Gagne event"""
        try:
            # Handle both dictionary and object formats
            if isinstance(event, dict):
                event_number = event.get("event_number", 1)
                event_name = event.get("event_name", "Unknown Event")
                event_description = event.get("description", "No description")
                activities = event.get("activities", [])
                duration_minutes = event.get("duration_minutes", 10)
                materials_needed = event.get("materials_needed", [])
                assessment_strategy = event.get("assessment_strategy", "Formative assessment")
            else:
                event_number = event.event_number
                event_name = event.event_name
                event_description = event.description
                activities = event.activities
                duration_minutes = event.duration_minutes
                materials_needed = event.materials_needed
                assessment_strategy = event.assessment_strategy
            
            # Get event template
            template = self.event_templates.get(event_number, self.event_templates[4])  # Default to event 4
            
            # Calculate intelligent slide count
            slide_count = self._calculate_slide_count(
                event_number, duration_minutes, activities, lesson_info
            )
            
            self.logger.info(f"Generating {slide_count} slides for Event {event_number}: {event_name}")
            
            # Generate slides using AI
            slides = await self._create_ai_generated_slides(
                event, objectives, lesson_plan, lesson_info, slide_count, template
            )
            
            # Calculate event totals
            total_duration = sum(slide.duration_minutes for slide in slides)
            
            # Extract teaching strategies and learning outcomes
            teaching_strategies = self._extract_teaching_strategies(activities, event_name)
            learning_outcomes = self._extract_learning_outcomes(objectives, event_number)
            
            return GagneEventSlides(
                event_number=event_number,
                event_name=event_name,
                event_description=event_description,
                total_slides=len(slides),
                estimated_duration=total_duration,
                slides=slides,
                teaching_strategies=teaching_strategies,
                learning_outcomes=learning_outcomes,
                materials_summary=materials_needed,
                assessment_notes=assessment_strategy
            )
            
        except Exception as e:
            self.logger.error(f"Error generating slides for event {event.event_number}: {str(e)}")
            # Return fallback slides
            return self._create_fallback_event_slides(event, objectives, lesson_info)
    
    def _calculate_slide_count(
        self, 
        event_number: int, 
        duration_minutes: int, 
        activities: List[str], 
        lesson_info: Dict[str, Any]
    ) -> int:
        """Calculate intelligent slide count based on event complexity and duration"""
        template = self.event_templates.get(event_number, self.event_templates[4])
        base_slides = template["base_slides"]
        
        # Duration factor (more time = more slides)
        duration_factor = max(1, duration_minutes // 15)  # 1 slide per 15 minutes
        
        # Activity complexity factor
        activity_factor = min(2, len(activities) // 2)  # More activities = more slides
        
        # Grade level factor
        grade_level = lesson_info.get("grade_level", "junior")
        grade_factors = {
            "freshman": 1.2,  # More detailed explanations needed
            "sophomore": 1.1,
            "junior": 1.0,    # Baseline
            "senior": 0.9,    # Can handle more complex slides
            "masters": 0.8,   # More concise, advanced content
            "postgrad": 0.7
        }
        grade_factor = grade_factors.get(grade_level, 1.0)
        
        # Calculate final count
        calculated_count = int(base_slides * duration_factor * activity_factor * grade_factor)
        
        # Apply reasonable bounds
        min_slides = max(1, base_slides // 2)
        max_slides = min(8, base_slides * 3)  # Cap at 8 slides per event
        
        return max(min_slides, min(calculated_count, max_slides))
    
    async def _create_ai_generated_slides(
        self, 
        event: GagneEvent, 
        objectives: List[LessonObjective],
        lesson_plan: LessonPlan,
        lesson_info: Dict[str, Any],
        slide_count: int,
        template: Dict[str, Any]
    ) -> List[SlideContent]:
        """Create AI-generated slides for the event"""
        try:
            # Prepare context for AI
            if isinstance(objectives[0], dict):
                objectives_text = "\n".join([f"- {obj.get('objective', 'No objective')}" for obj in objectives])
            else:
                objectives_text = "\n".join([f"- {obj.objective}" for obj in objectives])
            
            if isinstance(event, dict):
                activities_text = "\n".join([f"- {activity}" for activity in event.get('activities', [])])
            else:
                activities_text = "\n".join([f"- {activity}" for activity in event.activities])
            
            # Create comprehensive prompt
            event_number = event.get("event_number", 1) if isinstance(event, dict) else event.event_number
            event_name = event.get("event_name", "Unknown Event") if isinstance(event, dict) else event.event_name
            
            prompt = f"""
Create {slide_count} comprehensive, ready-to-use teaching slides for Gagne's Event {event_number}: {event_name}

LESSON CONTEXT:
Course: {lesson_info.get('course_title', '')}
Topic: {lesson_info.get('lesson_topic', '')}
Grade Level: {lesson_info.get('grade_level', '')}
Event Duration: {event.duration_minutes} minutes

LEARNING OBJECTIVES:
{objectives_text}

EVENT ACTIVITIES:
{activities_text}

MATERIALS NEEDED:
{', '.join(event.materials_needed)}

ASSESSMENT STRATEGY:
{event.assessment_strategy or 'Formative assessment throughout'}

SLIDE REQUIREMENTS:
- Create authentic, ready-to-use educational content
- Include actual teaching material, not just templates
- Each slide should be comprehensive and actionable
- Include specific examples, explanations, and activities
- Add visual elements and interactive components where appropriate
- Ensure content is appropriate for {lesson_info.get('grade_level', 'college')} level
- Focus on {template['focus']} with {template['visual_emphasis']} visual emphasis

SLIDE TYPES TO INCLUDE:
{', '.join(template['slide_types'])}

CONTENT REQUIREMENTS:
1. **Title**: Clear, engaging slide title
2. **Main Content**: Detailed markdown-formatted content with:
   - Headings and subheadings
   - Bullet points and numbered lists
   - Key concepts and definitions
   - Examples and explanations
   - Step-by-step instructions where applicable
3. **Visual Elements**: Suggest relevant images, diagrams, charts, or videos
4. **Audio Script**: Detailed narration for the slide
5. **Speaker Notes**: Teaching tips and additional context
6. **Learning Objectives**: Specific objectives this slide addresses
7. **Key Points**: Main takeaways from the slide
8. **Activities**: Specific activities or exercises
9. **Materials**: Required materials for this slide
10. **Assessment**: How to assess understanding from this slide

RETURN FORMAT:
Return ONLY a JSON array with exactly {slide_count} slides:
[
    {{
        "slide_number": 1,
        "title": "Engaging slide title",
        "content_type": "concept_explanation",
        "main_content": "# Main Heading\\n\\n## Subheading\\n\\n- Bullet point 1\\n- Bullet point 2\\n\\n**Key concept**: Detailed explanation with examples",
        "visual_elements": [
            {{
                "type": "diagram",
                "url": "concept_diagram.png",
                "alt_text": "Visual representation of the concept",
                "description": "A diagram showing the relationship between key concepts",
                "position": "center",
                "size": "large"
            }}
        ],
        "audio_script": "Detailed narration explaining the slide content...",
        "speaker_notes": "Teaching tips and additional context for instructors...",
        "duration_minutes": 3.5,
        "learning_objectives": ["Students will understand...", "Students will be able to..."],
        "key_points": ["Key point 1", "Key point 2", "Key point 3"],
        "activities": ["Activity 1: Description", "Activity 2: Description"],
        "materials_needed": ["Material 1", "Material 2"],
        "assessment_criteria": "Students demonstrate understanding by...",
        "accessibility_features": ["alt_text", "keyboard_navigation", "screen_reader"],
        "udl_guidelines": ["multiple_representation", "engagement"],
        "difficulty_level": "intermediate",
        "estimated_reading_time": 2
    }}
]

CRITICAL: Return ONLY the JSON array, no markdown, no code blocks, no explanations.
"""
            
            # Generate slides with multiple attempts for reliability
            for attempt in range(3):
                try:
                    response = await self._call_openai(
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are an expert instructional designer and educational content creator. Create comprehensive, ready-to-use teaching slides with authentic educational content. Return ONLY valid JSON arrays with no additional text."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,  # Lower temperature for consistency
                        max_tokens=6000   # Increased for comprehensive content
                    )
                    
                    # Clean and parse response
                    cleaned_content = self._clean_json_response(response)
                    slides_data = self._parse_json_response(cleaned_content, "array")
                    
                    # Ensure it's an array
                    if isinstance(slides_data, dict) and 'slides' in slides_data:
                        slides_data = slides_data['slides']
                    elif not isinstance(slides_data, list):
                        slides_data = [slides_data]
                    
                    # Validate slide count
                    if len(slides_data) != slide_count:
                        self.logger.warning(f"Generated {len(slides_data)} slides, expected {slide_count}")
                        if attempt < 2:
                            continue
                    
                    # Convert to SlideContent objects
                    slides = []
                    for i, slide_data in enumerate(slides_data):
                        slide = self._create_slide_object(slide_data, i + 1)
                        slides.append(slide)
                    
                    self.logger.info(f"Successfully generated {len(slides)} slides for event {event.event_number}")
                    return slides
                    
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed for event {event.event_number}: {str(e)}")
                    if attempt < 2:
                        continue
                    else:
                        # Final attempt failed, use fallback
                        self.logger.warning(f"All attempts failed for event {event.event_number}, using fallback")
                        return self._create_fallback_slides(event, objectives, slide_count)
            
        except Exception as e:
            self.logger.error(f"Error in _create_ai_generated_slides: {str(e)}")
            return self._create_fallback_slides(event, objectives, slide_count)
    
    def _create_slide_object(self, slide_data: Dict[str, Any], slide_number: int) -> SlideContent:
        """Convert slide data to SlideContent object"""
        try:
            # Handle visual elements
            visual_elements = []
            for element_data in slide_data.get("visual_elements", []):
                element = VisualElement(
                    type=VisualElementType(element_data.get("type", "image")),
                    url=element_data.get("url", ""),
                    alt_text=element_data.get("alt_text", ""),
                    description=element_data.get("description", ""),
                    position=element_data.get("position", "center"),
                    size=element_data.get("size", "medium"),
                    caption=element_data.get("caption")
                )
                visual_elements.append(element)
            
            return SlideContent(
                slide_number=slide_number,
                title=slide_data.get("title", f"Slide {slide_number}"),
                content_type=SlideContentType(slide_data.get("content_type", "mixed")),
                main_content=slide_data.get("main_content", ""),
                visual_elements=visual_elements,
                audio_script=slide_data.get("audio_script"),
                speaker_notes=slide_data.get("speaker_notes"),
                duration_minutes=float(slide_data.get("duration_minutes", 3.0)),
                learning_objectives=slide_data.get("learning_objectives", []),
                key_points=slide_data.get("key_points", []),
                activities=slide_data.get("activities", []),
                materials_needed=slide_data.get("materials_needed", []),
                assessment_criteria=slide_data.get("assessment_criteria"),
                accessibility_features=slide_data.get("accessibility_features", []),
                udl_guidelines=slide_data.get("udl_guidelines", []),
                difficulty_level=slide_data.get("difficulty_level", "intermediate"),
                estimated_reading_time=slide_data.get("estimated_reading_time")
            )
            
        except Exception as e:
            self.logger.error(f"Error creating slide object: {str(e)}")
            return self._create_basic_slide(slide_number, "Unknown Event")
    
    def _create_fallback_slides(
        self, 
        event: GagneEvent, 
        objectives: List[LessonObjective], 
        slide_count: int
    ) -> List[SlideContent]:
        """Create fallback slides when AI generation fails"""
        slides = []
        
        for i in range(slide_count):
            slide = self._create_basic_slide(i + 1, event.event_name, event.activities)
            slides.append(slide)
        
        return slides
    
    def _create_basic_slide(
        self, 
        slide_number: int, 
        event_name: str, 
        activities: List[str] = None
    ) -> SlideContent:
        """Create a basic slide as fallback"""
        activities = activities or []
        
        return SlideContent(
            slide_number=slide_number,
            title=f"{event_name} - Slide {slide_number}",
            content_type=SlideContentType.MIXED,
            main_content=f"# {event_name}\n\n## Key Activities\n\n" + "\n".join([f"- {activity}" for activity in activities]),
            visual_elements=[],
            audio_script=f"Audio narration for {event_name}",
            speaker_notes=f"Speaker notes for {event_name}",
            duration_minutes=3.0,
            learning_objectives=[],
            key_points=[],
            activities=activities,
            materials_needed=[],
            accessibility_features=["alt_text", "keyboard_navigation"],
            udl_guidelines=["multiple_representation", "engagement"],
            difficulty_level="intermediate"
        )
    
    def _create_fallback_event_slides(
        self, 
        event: GagneEvent, 
        objectives: List[LessonObjective], 
        lesson_info: Dict[str, Any]
    ) -> GagneEventSlides:
        """Create fallback event slides when generation fails"""
        slides = self._create_fallback_slides(event, objectives, 2)
        
        return GagneEventSlides(
            event_number=event.event_number,
            event_name=event.event_name,
            event_description=event.description,
            total_slides=len(slides),
            estimated_duration=sum(slide.duration_minutes for slide in slides),
            slides=slides,
            teaching_strategies=[],
            learning_outcomes=[],
            materials_summary=event.materials_needed,
            assessment_notes=event.assessment_strategy
        )
    
    def _extract_teaching_strategies(self, activities: List[str], event_name: str) -> List[str]:
        """Extract teaching strategies from activities"""
        strategies = []
        
        for activity in activities:
            if "discussion" in activity.lower():
                strategies.append("Interactive discussion")
            elif "demonstration" in activity.lower():
                strategies.append("Demonstration")
            elif "practice" in activity.lower():
                strategies.append("Guided practice")
            elif "group" in activity.lower():
                strategies.append("Collaborative learning")
            elif "visual" in activity.lower():
                strategies.append("Visual learning")
        
        return list(set(strategies)) if strategies else ["Direct instruction"]
    
    def _extract_learning_outcomes(self, objectives: List[LessonObjective], event_number: int) -> List[str]:
        """Extract learning outcomes relevant to the event"""
        outcomes = []
        
        for obj in objectives:
            if event_number <= 4:  # Events 1-4: Knowledge and comprehension
                if obj.bloom_level.value in ["remember", "understand"]:
                    outcomes.append(obj.objective)
            elif event_number <= 6:  # Events 5-6: Application and analysis
                if obj.bloom_level.value in ["apply", "analyze"]:
                    outcomes.append(obj.objective)
            else:  # Events 7-9: Evaluation and creation
                if obj.bloom_level.value in ["evaluate", "create"]:
                    outcomes.append(obj.objective)
        
        return outcomes[:3] if outcomes else ["Students will demonstrate understanding"]
