import os
import json
import asyncio
import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI
from ..models.udl_content import (
    CourseContentRequest, CourseContentResponse, SlideContent, 
    UDLComplianceReport, UDLPrinciple, ContentModality
)

# Set up logging
logger = logging.getLogger(__name__)


class UDLContentService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.udl_guidelines = self._initialize_udl_guidelines()
        logger.info("UDLContentService initialized successfully")

    def _initialize_udl_guidelines(self) -> Dict[str, Any]:
        """Initialize UDL guidelines with implementation strategies"""
        return {
            "representation": {
                1: {
                    "name": "Provide Multiple Means of Representation",
                    "guidelines": {
                        "perception": {
                            "name": "Perception",
                            "strategies": ["Customize display", "Provide alternatives for auditory info", "Provide alternatives for visual info"],
                            "modalities": ["visual", "auditory", "textual"]
                        },
                        "language": {
                            "name": "Language & Symbols",
                            "strategies": ["Clarify vocabulary", "Clarify syntax", "Support decoding", "Promote understanding across languages"],
                            "modalities": ["textual", "visual", "interactive"]
                        },
                        "comprehension": {
                            "name": "Comprehension",
                            "strategies": ["Activate background knowledge", "Highlight patterns", "Guide information processing", "Maximize transfer"],
                            "modalities": ["textual", "visual", "interactive", "kinesthetic"]
                        }
                    }
                }
            },
            "action_expression": {
                1: {
                    "name": "Provide Multiple Means of Action & Expression",
                    "guidelines": {
                        "physical_action": {
                            "name": "Physical Action",
                            "strategies": ["Vary methods for response", "Optimize access to tools"],
                            "modalities": ["kinesthetic", "interactive"]
                        },
                        "expression": {
                            "name": "Expression & Communication",
                            "strategies": ["Use multiple media", "Build fluencies", "Practice with graduated support"],
                            "modalities": ["textual", "visual", "auditory", "interactive"]
                        },
                        "executive_functions": {
                            "name": "Executive Functions",
                            "strategies": ["Guide goal setting", "Support planning", "Manage resources", "Enhance capacity for monitoring"],
                            "modalities": ["textual", "visual", "interactive"]
                        }
                    }
                }
            },
            "engagement": {
                1: {
                    "name": "Provide Multiple Means of Engagement",
                    "guidelines": {
                        "recruiting_interest": {
                            "name": "Recruiting Interest",
                            "strategies": ["Optimize individual choice", "Optimize relevance", "Minimize threats"],
                            "modalities": ["visual", "interactive", "kinesthetic"]
                        },
                        "sustaining_effort": {
                            "name": "Sustaining Effort & Persistence",
                            "strategies": ["Heighten salience of goals", "Vary demands", "Foster collaboration", "Increase mastery-oriented feedback"],
                            "modalities": ["interactive", "visual", "textual"]
                        },
                        "self_regulation": {
                            "name": "Self-Regulation",
                            "strategies": ["Guide personal coping skills", "Develop self-assessment", "Promote expectations and beliefs"],
                            "modalities": ["textual", "interactive", "visual"]
                        }
                    }
                }
            }
        }

    async def generate_course_content(self, request: CourseContentRequest) -> CourseContentResponse:
        """Generate multimodal course content based on lesson plan with UDL compliance"""
        try:
            logger.info("Starting course content generation")
            
            # Extract lesson information
            lesson_info = request.lesson_data.get("lesson_info", {})
            objectives = request.lesson_data.get("objectives", [])
            gagne_events = request.lesson_data.get("gagne_events", [])
            
            logger.info(f"Processing lesson: {lesson_info.get('course_title', 'Unknown')} with {len(gagne_events)} Gagne events")
            
            # Generate slides for each Gagne event
            slides = await self._generate_slides_for_gagne_events(
                gagne_events, objectives, lesson_info, request
            )
            
            logger.info(f"Generated {len(slides)} slides")
            
            # Calculate UDL compliance
            compliance_report = await self._calculate_udl_compliance(slides, request)
            
            # Generate presentation metadata
            presentation_title = f"{lesson_info.get('course_title', 'Course')} - {lesson_info.get('lesson_topic', 'Lesson')}"
            total_duration = sum(slide.duration_minutes for slide in slides)
            
            logger.info("Course content generation completed successfully")
            
            return CourseContentResponse(
                presentation_title=presentation_title,
                total_slides=len(slides),
                estimated_duration=int(total_duration),
                slides=slides,
                udl_compliance_report=compliance_report.dict(),
                accessibility_features=self._extract_accessibility_features(slides),
                export_formats=["pptx", "pdf", "html"],
                created_at=str(asyncio.get_event_loop().time())
            )
        except Exception as e:
            logger.error(f"Error in generate_course_content: {str(e)}")
            raise

    async def _generate_slides_for_gagne_events(
        self, gagne_events: List[Dict], objectives: List[Dict], 
        lesson_info: Dict, request: CourseContentRequest
    ) -> List[SlideContent]:
        """Generate slides for each Gagne event with UDL principles"""
        try:
            slides = []
            slide_number = 1
            
            for event in gagne_events:
                logger.info(f"Generating slides for Gagne event {event.get('event_number', 'unknown')}")
                event_slides = await self._create_slides_for_event(
                    event, objectives, lesson_info, slide_number, request
                )
                slides.extend(event_slides)
                slide_number += len(event_slides)
            
            return slides
        except Exception as e:
            logger.error(f"Error in _generate_slides_for_gagne_events: {str(e)}")
            raise

    async def _create_slides_for_event(
        self, event: Dict, objectives: List[Dict], lesson_info: Dict, 
        start_slide_number: int, request: CourseContentRequest
    ) -> List[SlideContent]:
        """Create slides for a specific Gagne event"""
        try:
            event_number = event.get("event_number", 1)
            event_name = event.get("event_name", "")
            activities = event.get("activities", [])
            duration = event.get("duration_minutes", 10)
            
            # Calculate number of slides based on duration and preference
            slide_count = self._calculate_slide_count(duration, request.slide_duration_preference)
            
            logger.info(f"Creating {slide_count} slides for event {event_number}: {event_name}")
            
            prompt = f"""
            Create {slide_count} presentation slides for Gagne's Event {event_number}: {event_name}
            
            LESSON CONTEXT:
            Course: {lesson_info.get('course_title', '')}
            Topic: {lesson_info.get('lesson_topic', '')}
            Level: {lesson_info.get('grade_level', '')}
            Event Duration: {duration} minutes
            
            LEARNING OBJECTIVES:
            {json.dumps([obj.get('objective', '') for obj in objectives], indent=2)}
            
            ACTIVITIES:
            {json.dumps(activities, indent=2)}
            
            UDL REQUIREMENTS:
            - Provide multiple means of representation (visual, auditory, textual)
            - Include accessibility features (alt text, captions, keyboard navigation)
            - Support multiple means of action and expression
            - Engage learners through various modalities
            
            REQUIREMENTS:
            - Return ONLY valid JSON array with exactly {slide_count} slides
            - Each slide must have: title, main_content, content_type, visual_elements (array), audio_script, accessibility_features (array), udl_guidelines (array), duration_minutes, notes
            - content_type must be one of: "text", "image", "video", "interactive", "mixed"
            - duration_minutes should be a number
            - All arrays should contain strings
            - visual_elements should be an array of strings (image/video filenames)
            
            SLIDE CONTENT REQUIREMENTS:
            - Create actual slide content with bullet points, headings, and real presentation material
            - Include specific examples, definitions, and explanations
            - Add visual elements like diagrams, charts, images, or videos
            - Provide detailed speaker notes with teaching tips
            - Include interactive elements where appropriate
            - Make content engaging and accessible
            
            EXAMPLE FORMAT:
            [
                {{
                    "title": "Introduction to Queues",
                    "main_content": "# Introduction to Queues\\n\\n## What is a Queue?\\n\\n- A **First-In-First-Out (FIFO)** data structure\\n- Elements are added at the **rear** and removed from the **front**\\n- Like a line of people waiting for service\\n\\n## Key Characteristics:\\n\\n1. **Ordered collection** of elements\\n2. **Two main operations**:\\n   - Enqueue (add to rear)\\n   - Dequeue (remove from front)\\n3. **No random access** - can only access front element\\n\\n## Real-World Examples:\\n\\n- Print queue\\n- Customer service line\\n- Task scheduling\\n- Breadth-first search",
                    "content_type": "mixed",
                    "visual_elements": ["queue_diagram.png", "fifo_animation.gif", "real_world_examples.jpg"],
                    "audio_script": "Welcome to our lesson on queues. A queue is a First-In-First-Out data structure, meaning the first element added is the first one removed. Think of it like a line of people waiting for service - the first person in line is the first one served. Queues have two main operations: enqueue, which adds an element to the rear, and dequeue, which removes an element from the front. Real-world examples include print queues, customer service lines, and task scheduling systems.",
                    "accessibility_features": ["alt_text", "keyboard_navigation", "screen_reader", "high_contrast"],
                    "udl_guidelines": ["multiple_representation", "comprehension", "engagement"],
                    "duration_minutes": 3.0,
                    "notes": "Start with the real-world analogy of a line of people. Show the queue diagram and explain FIFO principle. Use the animation to demonstrate enqueue/dequeue operations. Connect to students' everyday experiences with waiting in lines."
                }}
            ]
            
            CRITICAL: Return ONLY the JSON array, no markdown, no code blocks, no explanations.
            """
            
            # Try multiple approaches to get valid JSON
            for attempt in range(3):
                try:
                    response = await self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are an expert instructional designer. Return ONLY valid JSON arrays. No markdown, no explanations."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,  # Lower temperature for more consistent output
                        max_tokens=4000
                    )
                    
                    content = response.choices[0].message.content
                    if content is None:
                        raise ValueError("AI returned null content")
                    
                    content = content.strip()
                    
                    # Remove any markdown formatting if present
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    
                    # Try to parse as JSON
                    slides_data = json.loads(content)
                    
                    # Ensure it's an array
                    if isinstance(slides_data, dict) and 'slides' in slides_data:
                        slides_data = slides_data['slides']
                    elif not isinstance(slides_data, list):
                        slides_data = [slides_data]
                    
                    logger.info(f"Successfully generated {len(slides_data)} slides for event {event_number} (attempt {attempt + 1})")
                    return [self._create_slide_object(slide_data, start_slide_number + i) for i, slide_data in enumerate(slides_data)]
                    
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.warning(f"Attempt {attempt + 1} failed for event {event_number}: {str(e)}")
                    if attempt < 2:  # Try again
                        continue
                    else:
                        # Final attempt failed, use fallback
                        logger.warning(f"All attempts failed for event {event_number}, using enhanced fallback")
                        return [self._create_enhanced_fallback_slide(event, objectives, start_slide_number)]
                
        except Exception as e:
            logger.error(f"Error in _create_slides_for_event: {str(e)}")
            # Return enhanced fallback slide
            return [self._create_enhanced_fallback_slide(event, objectives, start_slide_number)]

    def _calculate_slide_count(self, duration: int, preference: str) -> int:
        """Calculate optimal number of slides based on duration and preference"""
        base_slides = max(1, duration // 5)  # 1 slide per 5 minutes
        
        if preference == "detailed":
            return min(base_slides * 2, 8)  # More slides, max 8
        elif preference == "concise":
            return max(base_slides // 2, 1)  # Fewer slides, min 1
        else:  # balanced
            return min(base_slides, 6)  # Balanced approach, max 6

    def _create_slide_object(self, slide_data: Dict, slide_number: int) -> SlideContent:
        """Convert slide data to SlideContent object"""
        try:
            # Ensure all required fields are present with defaults
            title = slide_data.get("title", f"Slide {slide_number}")
            main_content = slide_data.get("main_content", "")
            content_type = slide_data.get("content_type", "mixed")
            
            # Validate content_type
            valid_content_types = ["text", "image", "video", "interactive", "mixed"]
            if content_type not in valid_content_types:
                content_type = "mixed"
            
            # Handle visual_elements - convert strings to proper format
            visual_elements_raw = slide_data.get("visual_elements", [])
            visual_elements = []
            if isinstance(visual_elements_raw, list):
                for element in visual_elements_raw:
                    if isinstance(element, str):
                        # Convert string to proper format
                        visual_elements.append({
                            "type": "image" if element.endswith(('.png', '.jpg', '.jpeg', '.gif')) else "video" if element.endswith(('.mp4', '.avi', '.mov')) else "diagram",
                            "url": element,
                            "alt_text": f"Visual element: {element}",
                            "description": element
                        })
                    elif isinstance(element, dict):
                        visual_elements.append(element)
                    else:
                        # Skip invalid elements
                        continue
            
            accessibility_features = slide_data.get("accessibility_features", [])
            if not isinstance(accessibility_features, list):
                accessibility_features = ["alt_text", "keyboard_navigation"]
            
            udl_guidelines = slide_data.get("udl_guidelines", [])
            if not isinstance(udl_guidelines, list):
                udl_guidelines = ["multiple_representation", "engagement"]
            
            # Ensure duration is a number
            duration_minutes = slide_data.get("duration_minutes", 2.0)
            if not isinstance(duration_minutes, (int, float)):
                duration_minutes = 2.0
            
            # Ensure optional fields
            audio_script = slide_data.get("audio_script")
            notes = slide_data.get("notes")
            
            return SlideContent(
                slide_number=slide_number,
                title=title,
                content_type=content_type,
                main_content=main_content,
                visual_elements=visual_elements,
                audio_script=audio_script,
                accessibility_features=accessibility_features,
                udl_guidelines=udl_guidelines,
                duration_minutes=float(duration_minutes),
                notes=notes
            )
        except Exception as e:
            logger.error(f"Error creating slide object: {str(e)}")
            # Return a basic slide if there's an error
            return SlideContent(
                slide_number=slide_number,
                title=f"Slide {slide_number}",
                content_type="mixed",
                main_content="Content for this slide",
                visual_elements=[],
                accessibility_features=["alt_text", "keyboard_navigation"],
                udl_guidelines=["multiple_representation", "engagement"],
                duration_minutes=2.0
            )

    def _create_enhanced_fallback_slide(self, event: Dict, objectives: List[Dict], slide_number: int) -> SlideContent:
        """Create an enhanced fallback slide with more meaningful content"""
        event_name = event.get("event_name", "Activity")
        event_number = event.get("event_number", 1)
        activities = event.get("activities", [])
        
        # Create meaningful content based on the event
        if "attention" in event_name.lower():
            title = f"Event {event_number}: {event_name}"
            content = f"Engage students with an attention-grabbing activity related to the lesson topic."
            guidelines = ["recruiting_interest", "multiple_representation"]
        elif "objectives" in event_name.lower():
            title = f"Event {event_number}: {event_name}"
            content = f"Present clear learning objectives to help students understand what they will learn."
            guidelines = ["comprehension", "engagement"]
        elif "recall" in event_name.lower():
            title = f"Event {event_number}: {event_name}"
            content = f"Help students connect new learning to their prior knowledge and experiences."
            guidelines = ["comprehension", "multiple_representation"]
        elif "present" in event_name.lower():
            title = f"Event {event_number}: {event_name}"
            content = f"Present the main content using multiple modalities and clear explanations."
            guidelines = ["multiple_representation", "comprehension"]
        elif "guidance" in event_name.lower():
            title = f"Event {event_number}: {event_name}"
            content = f"Provide learning guidance and support to help students process information."
            guidelines = ["comprehension", "action_expression"]
        elif "elicit" in event_name.lower():
            title = f"Event {event_number}: {event_name}"
            content = f"Encourage active participation and practice of the new skills or knowledge."
            guidelines = ["action_expression", "engagement"]
        elif "feedback" in event_name.lower():
            title = f"Event {event_number}: {event_name}"
            content = f"Provide constructive feedback to help students improve their performance."
            guidelines = ["engagement", "action_expression"]
        elif "assess" in event_name.lower():
            title = f"Event {event_number}: {event_name}"
            content = f"Assess student understanding and provide opportunities for demonstration."
            guidelines = ["action_expression", "comprehension"]
        elif "retention" in event_name.lower():
            title = f"Event {event_number}: {event_name}"
            content = f"Help students retain and transfer their learning to new situations."
            guidelines = ["comprehension", "engagement"]
        else:
            title = f"Event {event_number}: {event_name}"
            content = f"Content for {event_name} - {', '.join(activities) if activities else 'this activity'}"
            guidelines = ["multiple_representation", "engagement"]
        
        return SlideContent(
            slide_number=slide_number,
            title=title,
            content_type="mixed",
            main_content=content,
            visual_elements=[{
                "type": "image",
                "url": "placeholder_image.png",
                "alt_text": f"Visual element for {event_name}",
                "description": f"Visual representation for {event_name}"
            }],
            audio_script=f"Audio narration for {event_name}",
            accessibility_features=["alt_text", "keyboard_navigation", "screen_reader"],
            udl_guidelines=guidelines,
            duration_minutes=event.get("duration_minutes", 10),
            notes=f"Speaker notes for {event_name}: {content}"
        )

    async def _calculate_udl_compliance(self, slides: List[SlideContent], request: CourseContentRequest) -> UDLComplianceReport:
        """Calculate UDL compliance score and provide recommendations"""
        try:
            # Analyze representation
            representation_score = self._calculate_principle_score(slides, "representation")
            action_expression_score = self._calculate_principle_score(slides, "action_expression")
            engagement_score = self._calculate_principle_score(slides, "engagement")
            
            overall_compliance = (representation_score + action_expression_score + engagement_score) / 3
            
            # Identify missing guidelines
            missing_guidelines = self._identify_missing_guidelines(slides)
            
            # Generate recommendations
            recommendations = self._generate_udl_recommendations(slides, missing_guidelines)
            
            return UDLComplianceReport(
                representation_score=representation_score,
                action_expression_score=action_expression_score,
                engagement_score=engagement_score,
                overall_compliance=overall_compliance,
                missing_guidelines=missing_guidelines,
                recommendations=recommendations,
                accessibility_features_implemented=self._extract_accessibility_features(slides)
            )
        except Exception as e:
            logger.error(f"Error in _calculate_udl_compliance: {str(e)}")
            # Return default compliance report
            return UDLComplianceReport(
                representation_score=0.5,
                action_expression_score=0.5,
                engagement_score=0.5,
                overall_compliance=0.5,
                missing_guidelines=[],
                recommendations=["Unable to calculate compliance due to error"],
                accessibility_features_implemented=[]
            )

    def _calculate_principle_score(self, slides: List[SlideContent], principle: str) -> float:
        """Calculate compliance score for a UDL principle"""
        try:
            if principle not in self.udl_guidelines:
                logger.warning(f"Principle '{principle}' not found in UDL guidelines")
                return 0.5
                
            principle_data = self.udl_guidelines[principle]
            if 1 not in principle_data:
                logger.warning(f"Principle '{principle}' data structure is invalid")
                return 0.5
                
            total_guidelines = len(principle_data[1]["guidelines"])
            if total_guidelines == 0:
                logger.warning(f"No guidelines found for principle '{principle}'")
                return 0.5
                
            implemented_guidelines = 0
            
            for slide in slides:
                for guideline in slide.udl_guidelines:
                    if principle in guideline.lower():
                        implemented_guidelines += 1
            
            return min(1.0, implemented_guidelines / total_guidelines)
        except Exception as e:
            logger.error(f"Error calculating principle score for {principle}: {str(e)}")
            return 0.5

    def _identify_missing_guidelines(self, slides: List[SlideContent]) -> List[str]:
        """Identify UDL guidelines that are not implemented"""
        try:
            implemented = set()
            for slide in slides:
                implemented.update(slide.udl_guidelines)
            
            all_guidelines = set()
            for principle_name, principle_data in self.udl_guidelines.items():
                if 1 in principle_data and "guidelines" in principle_data[1]:
                    for guideline_group in principle_data[1]["guidelines"].values():
                        if "name" in guideline_group:
                            all_guidelines.add(guideline_group["name"])
            
            return list(all_guidelines - implemented)
        except Exception as e:
            logger.error(f"Error identifying missing guidelines: {str(e)}")
            return []

    def _generate_udl_recommendations(self, slides: List[SlideContent], missing_guidelines: List[str]) -> List[str]:
        """Generate specific recommendations for improving UDL compliance"""
        try:
            recommendations = []
            
            if "Perception" in missing_guidelines:
                recommendations.append("Add audio descriptions and visual alternatives for all content")
            
            if "Language & Symbols" in missing_guidelines:
                recommendations.append("Include vocabulary definitions and multiple language support")
            
            if "Physical Action" in missing_guidelines:
                recommendations.append("Provide alternative response methods and optimize tool access")
            
            if "Recruiting Interest" in missing_guidelines:
                recommendations.append("Add choice-based activities and relevant real-world examples")
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating UDL recommendations: {str(e)}")
            return ["Ensure all UDL principles are properly implemented"]

    def _extract_accessibility_features(self, slides: List[SlideContent]) -> List[str]:
        """Extract all accessibility features from slides"""
        try:
            features = set()
            for slide in slides:
                features.update(slide.accessibility_features)
            return list(features)
        except Exception as e:
            logger.error(f"Error extracting accessibility features: {str(e)}")
            return []

    async def refine_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Refine specific slide content based on UDL principles"""
        try:
            slide_id = request.get("slide_id")
            refinement_type = request.get("refinement_type")
            instructions = request.get("refinement_instructions")
            current_content = request.get("current_content", {})
            
            prompt = f"""
            Refine the following slide content to improve {refinement_type}:
            
            CURRENT CONTENT:
            {json.dumps(current_content, indent=2)}
            
            REFINEMENT INSTRUCTIONS:
            {instructions}
            
            UDL PRINCIPLES TO APPLY:
            - Representation: Multiple means of presenting information
            - Action & Expression: Multiple ways for students to respond
            - Engagement: Multiple ways to motivate and engage learners
            
            Return the refined content in the same JSON format.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in UDL principles and accessible content creation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            try:
                refined_content = json.loads(response.choices[0].message.content)
                return {"refined_content": refined_content}
            except json.JSONDecodeError:
                return {"refined_content": current_content}
        except Exception as e:
            logger.error(f"Error in refine_content: {str(e)}")
            return {"refined_content": request.get("current_content", {})} 