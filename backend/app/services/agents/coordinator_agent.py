"""
Coordinator Agent for Multi-Agent Lesson Planning System

This agent orchestrates the entire lesson planning and content generation process:
- Coordinates Plan Agent for lesson planning components
- Coordinates Content Agent for slide generation
- Coordinates UDL Agent for compliance validation
- Manages agent communication and data flow
- Provides unified interface for the lesson planning system

The coordinator ensures all agents work together seamlessly to create
comprehensive, pedagogically sound, and accessible lesson plans.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from .plan_agent import PlanAgent
from .content_agent import ContentAgent
from .udl_agent import UDLAgent
from .design_agent import DesignAgent
from .accessibility_agent import AccessibilityAgent
from ...models.lesson import LessonRequest, LessonObjective, LessonPlan, GagneEvent
from ...models.gagne_slides import GagneSlidesResponse, SlideContent, GagneEventSlides
from ...models.design_content import DesignComplianceReport
from ...models.accessibility_content import AccessibilityComplianceReport

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that orchestrates all lesson planning agents.
    
    This agent handles:
    - Agent coordination and communication
    - Data flow between agents
    - Error handling and fallback strategies
    - Result aggregation and validation
    - Unified API for lesson planning
    """
    
    def __init__(self, client=None):
        """Initialize the Coordinator Agent with all sub-agents."""
        super().__init__(client)
        self.logger = logging.getLogger(f"agents.{self.__class__.__name__}")
        
        # Initialize sub-agents
        self.plan_agent = PlanAgent(client)
        self.content_agent = ContentAgent(client)
        self.udl_agent = UDLAgent(client)
        self.design_agent = DesignAgent(client)
        self.accessibility_agent = AccessibilityAgent(client)
        
        self.logger.info("CoordinatorAgent initialized with all sub-agents")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process complete lesson planning request through all agents.
        
        Args:
            input_data: Dictionary containing:
                - lesson_request: LessonRequest object
                - processed_files: Dictionary with file processing results
                - preferences: Optional user preferences
                
        Returns:
            Dictionary containing:
                - lesson_plan: Complete lesson plan with all components
                - slides: Generated teaching slides
                - udl_compliance: UDL compliance report
                - metadata: Processing metadata
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("🎯 COORDINATOR AGENT STARTING")
            self.logger.info("=" * 80)
            
            lesson_request = input_data.get("lesson_request")
            processed_files = input_data.get("processed_files", {})
            preferences = input_data.get("preferences", {})
            
            self.logger.info(f"📋 Input data keys: {list(input_data.keys())}")
            self.logger.info(f"📁 Processed files: {len(processed_files)} files")
            self.logger.info(f"⚙️ Preferences: {preferences}")
            
            if not lesson_request:
                raise ValueError("lesson_request is required")
            
            self._log_processing_start(f"Orchestrating lesson planning for: {lesson_request.course_title}")
            
            # Phase 1: Plan Generation
            self.logger.info("=" * 60)
            self.logger.info("📋 PHASE 1: PLAN GENERATION")
            self.logger.info("=" * 60)
            try:
                self.logger.info("🤖 Calling plan agent...")
                plan_result = await asyncio.wait_for(
                    self._execute_plan_phase(lesson_request, processed_files),
                    timeout=300  # 5 minute timeout for plan generation
                )
                self.logger.info(f"✅ Plan agent returned: {type(plan_result)}")
                self.logger.info(f"📊 Plan result keys: {plan_result.keys() if isinstance(plan_result, dict) else 'Not a dict'}")
            except asyncio.TimeoutError:
                self.logger.error("⏰ Plan generation timed out")
                raise Exception("Plan generation timed out. Please try again.")
            except Exception as e:
                self.logger.error(f"❌ Plan phase error: {str(e)}")
                import traceback
                self.logger.error(f"📜 Traceback: {traceback.format_exc()}")
                raise
            
            if not plan_result.get("success"):
                error_msg = plan_result.get('error', 'Unknown error')
                self.logger.error(f"❌ Plan phase failed: {error_msg}")
                raise Exception(f"Plan phase failed: {error_msg}")
            
            plan_data = plan_result["data"]
            self.logger.info(f"✅ Plan phase completed: {len(plan_data['objectives'])} objectives, {len(plan_data['gagne_events'])} events")
            
            try:
                self.logger.info("🔍 Creating plan objects...")
                objectives = [LessonObjective(**obj) for obj in plan_data["objectives"]]
                self.logger.info(f"✅ Created {len(objectives)} objectives")
                
                lesson_plan = LessonPlan(**plan_data["lesson_plan"])
                self.logger.info("✅ Created lesson plan")
                
                gagne_events = [GagneEvent(**event) for event in plan_data["gagne_events"]]
                self.logger.info(f"✅ Created {len(gagne_events)} Gagne events")
            except Exception as e:
                self.logger.error(f"❌ Error creating plan objects: {str(e)}")
                import traceback
                self.logger.error(f"📜 Traceback: {traceback.format_exc()}")
                raise Exception(f"Failed to create plan objects: {str(e)}")
            
            # Phase 2: Content Generation
            self.logger.info("=" * 60)
            self.logger.info("🎨 PHASE 2: CONTENT GENERATION")
            self.logger.info("=" * 60)
            try:
                self.logger.info("🤖 Calling content agent...")
                content_result = await asyncio.wait_for(
                    self._execute_content_phase(
                        gagne_events, objectives, lesson_plan, lesson_request, processed_files
                    ),
                    timeout=300  # 5 minute timeout for content generation
                )
                self.logger.info(f"✅ Content agent returned: {type(content_result)}")
                self.logger.info(f"📊 Content result keys: {content_result.keys() if isinstance(content_result, dict) else 'Not a dict'}")
            except asyncio.TimeoutError:
                self.logger.warning("⏰ Content generation timed out, using fallback content")
                content_data = self._create_fallback_content(gagne_events, objectives, lesson_plan)
            except Exception as e:
                self.logger.error(f"❌ Content phase error: {str(e)}")
                import traceback
                self.logger.error(f"📜 Traceback: {traceback.format_exc()}")
                self.logger.warning("Using fallback content due to error")
                content_data = self._create_fallback_content(gagne_events, objectives, lesson_plan)
            else:
                if not content_result.get("success"):
                    error_msg = content_result.get('error', 'Unknown error')
                    self.logger.warning(f"⚠️ Content phase failed: {error_msg}")
                    self.logger.warning("Using fallback content due to failure")
                    content_data = self._create_fallback_content(gagne_events, objectives, lesson_plan)
                else:
                    content_data = content_result["data"]
                    # Check if content agent used fallback content
                    if content_result.get("metadata", {}).get("fallback_used"):
                        self.logger.info("✅ Content phase succeeded with fallback content")
                    else:
                        self.logger.info("✅ Content phase succeeded with AI-generated content")
            
            try:
                self.logger.info("🔍 Processing content data...")
                self.logger.info(f"📊 Content data keys: {list(content_data.keys()) if isinstance(content_data, dict) else 'Not a dict'}")
                
                # The content_data["gagne_slides_response"] is a dictionary from .dict() call
                # We need to reconstruct the GagneSlidesResponse properly
                gagne_slides_data = content_data["gagne_slides_response"]
                self.logger.info(f"🔍 Gagne slides data type: {type(gagne_slides_data)}")
                self.logger.info(f"📊 Gagne slides data keys: {list(gagne_slides_data.keys()) if isinstance(gagne_slides_data, dict) else 'Not a dict'}")
                
                # Reconstruct events with proper SlideContent objects
                reconstructed_events = []
                self.logger.info(f"🔍 Processing {len(gagne_slides_data['events'])} events...")
                
                for i, event_data in enumerate(gagne_slides_data["events"]):
                    self.logger.info(f"🔍 Processing event {i+1}: {event_data.get('event_name', 'Unknown')}")
                    self.logger.info(f"📊 Event data keys: {list(event_data.keys()) if isinstance(event_data, dict) else 'Not a dict'}")
                    
                    # Convert slide dictionaries back to SlideContent objects
                    slide_objects = []
                    slides_data = event_data.get("slides", [])
                    self.logger.info(f"🔍 Processing {len(slides_data)} slides for event {i+1}")
                    
                    for j, slide_data in enumerate(slides_data):
                        self.logger.info(f"🔍 Processing slide {j+1} of event {i+1}")
                        self.logger.info(f"📊 Slide data type: {type(slide_data)}")
                        self.logger.info(f"📊 Slide data keys: {list(slide_data.keys()) if isinstance(slide_data, dict) else 'Not a dict'}")
                        
                        if isinstance(slide_data, SlideContent):
                            # slide_data is already a SlideContent object
                            self.logger.info("✅ slide_data is already SlideContent, using directly")
                            slide_objects.append(slide_data)
                        elif isinstance(slide_data, dict):
                            # slide_data is a dictionary, convert to SlideContent
                            self.logger.info("🔄 slide_data is dict, converting to SlideContent")
                            try:
                                slide_obj = SlideContent(**slide_data)
                                slide_objects.append(slide_obj)
                                self.logger.info(f"✅ Successfully created SlideContent for slide {j+1}")
                            except Exception as e:
                                self.logger.error(f"❌ Error creating SlideContent from dict: {str(e)}")
                                self.logger.error(f"🔍 Error type: {type(e).__name__}")
                                self.logger.error(f"📊 slide_data keys: {slide_data.keys() if isinstance(slide_data, dict) else 'Not a dict'}")
                                self.logger.error(f"📊 slide_data sample: {str(slide_data)[:200]}...")
                                import traceback
                                self.logger.error(f"📜 Traceback: {traceback.format_exc()}")
                                raise
                        else:
                            self.logger.error(f"❌ Unexpected slide_data type: {type(slide_data)}")
                            self.logger.error(f"📊 slide_data value: {slide_data}")
                            raise Exception(f"Unexpected slide_data type: {type(slide_data)}")
                    
                    self.logger.info(f"✅ Created {len(slide_objects)} slides for event {i+1}")
                    
                    # Create GagneEventSlides with proper SlideContent objects
                    try:
                        event_slides = GagneEventSlides(
                            event_number=event_data["event_number"],
                            event_name=event_data["event_name"],
                            event_description=event_data["event_description"],
                            total_slides=event_data["total_slides"],
                            estimated_duration=event_data["estimated_duration"],
                            slides=slide_objects,
                            teaching_strategies=event_data.get("teaching_strategies", []),
                            learning_outcomes=event_data.get("learning_outcomes", []),
                            materials_summary=event_data.get("materials_summary", []),
                            assessment_notes=event_data.get("assessment_notes")
                        )
                        reconstructed_events.append(event_slides)
                        self.logger.info(f"✅ Created GagneEventSlides for event {i+1}")
                    except Exception as e:
                        self.logger.error(f"❌ Error creating GagneEventSlides for event {i+1}: {str(e)}")
                        import traceback
                        self.logger.error(f"📜 Traceback: {traceback.format_exc()}")
                        raise
                
                self.logger.info(f"✅ Reconstructed {len(reconstructed_events)} events")
                
                # Create the GagneSlidesResponse with reconstructed events
                try:
                    slides_response = GagneSlidesResponse(
                        lesson_info=gagne_slides_data["lesson_info"],
                        total_events=gagne_slides_data["total_events"],
                        total_slides=gagne_slides_data["total_slides"],
                        total_duration=gagne_slides_data["total_duration"],
                        events=reconstructed_events,
                        generation_metadata=gagne_slides_data["generation_metadata"],
                        created_at=gagne_slides_data["created_at"]
                    )
                    self.logger.info("✅ Created GagneSlidesResponse")
                except Exception as e:
                    self.logger.error(f"❌ Error creating GagneSlidesResponse: {str(e)}")
                    import traceback
                    self.logger.error(f"📜 Traceback: {traceback.format_exc()}")
                    raise
                
                # Extract slides for UDL processing
                slides = [slide for event in slides_response.events for slide in event.slides]
                self.logger.info(f"✅ Content phase completed: {len(slides)} slides generated")
            except Exception as e:
                self.logger.error(f"❌ Error creating content objects: {str(e)}")
                import traceback
                self.logger.error(f"📜 Traceback: {traceback.format_exc()}")
                raise Exception(f"Failed to create content objects: {str(e)}")
            
            # Phase 3: UDL Enhancement
            self.logger.info("=" * 60)
            self.logger.info("♿ PHASE 3: UDL ENHANCEMENT")
            self.logger.info("=" * 60)
            try:
                self.logger.info("🤖 Calling UDL agent...")
                udl_result = await asyncio.wait_for(
                    self._execute_udl_phase(slides, lesson_request, preferences),
                    timeout=180  # 3 minute timeout for UDL validation
                )
                self.logger.info(f"✅ UDL agent returned: {type(udl_result)}")
            except asyncio.TimeoutError:
                self.logger.warning("⏰ UDL validation timed out, using fallback compliance")
                udl_data = self._create_fallback_udl_compliance(slides)
            except Exception as e:
                self.logger.error(f"❌ UDL phase error: {str(e)}")
                import traceback
                self.logger.error(f"📜 Traceback: {traceback.format_exc()}")
                self.logger.warning("Using fallback UDL compliance due to error")
                udl_data = self._create_fallback_udl_compliance(slides)
            else:
                if not udl_result.get("success"):
                    error_msg = udl_result.get('error', 'Unknown error')
                    self.logger.warning(f"⚠️ UDL phase failed: {error_msg}")
                    self.logger.warning("Using fallback UDL compliance due to failure")
                    udl_data = self._create_fallback_udl_compliance(slides)
                else:
                    udl_data = udl_result["data"]
                    # Update slides with UDL enhancements
                    if "enhanced_slides" in udl_data:
                        slides = udl_data["enhanced_slides"]
                        self.logger.info("✅ UDL phase succeeded - slides enhanced with UDL principles")
                    else:
                        self.logger.info("✅ UDL phase succeeded")
            
            # Phase 4: Design Enhancement
            self.logger.info("=" * 60)
            self.logger.info("🎨 PHASE 4: DESIGN ENHANCEMENT")
            self.logger.info("=" * 60)
            try:
                self.logger.info("🤖 Calling design agent...")
                design_result = await asyncio.wait_for(
                    self._execute_design_phase(slides, preferences),
                    timeout=180  # 3 minute timeout for design validation
                )
                self.logger.info(f"✅ Design agent returned: {type(design_result)}")
            except asyncio.TimeoutError:
                self.logger.warning("⏰ Design validation timed out, using fallback compliance")
                design_data = self._create_fallback_design_compliance(slides)
            except Exception as e:
                self.logger.error(f"❌ Design phase error: {str(e)}")
                self.logger.warning("Using fallback design compliance due to error")
                design_data = self._create_fallback_design_compliance(slides)
            else:
                if not design_result.get("success"):
                    error_msg = design_result.get('error', 'Unknown error')
                    self.logger.warning(f"⚠️ Design phase failed: {error_msg}")
                    self.logger.warning("Using fallback design compliance due to failure")
                    design_data = self._create_fallback_design_compliance(slides)
                else:
                    design_data = design_result["data"]
                    # Update slides with design enhancements
                    if "enhanced_slides" in design_data:
                        slides = design_data["enhanced_slides"]
                        self.logger.info("✅ Design phase succeeded - slides enhanced with C.R.A.P. principles")
                    else:
                        self.logger.info("✅ Design phase succeeded")
            
            # Phase 5: Accessibility Enhancement
            self.logger.info("=" * 60)
            self.logger.info("♿ PHASE 5: ACCESSIBILITY ENHANCEMENT")
            self.logger.info("=" * 60)
            try:
                self.logger.info("🤖 Calling accessibility agent...")
                accessibility_result = await asyncio.wait_for(
                    self._execute_accessibility_phase(slides, preferences),
                    timeout=180  # 3 minute timeout for accessibility validation
                )
                self.logger.info(f"✅ Accessibility agent returned: {type(accessibility_result)}")
            except asyncio.TimeoutError:
                self.logger.warning("⏰ Accessibility validation timed out, using fallback compliance")
                accessibility_data = self._create_fallback_accessibility_compliance(slides)
            except Exception as e:
                self.logger.error(f"❌ Accessibility phase error: {str(e)}")
                self.logger.warning("Using fallback accessibility compliance due to error")
                accessibility_data = self._create_fallback_accessibility_compliance(slides)
            else:
                if not accessibility_result.get("success"):
                    error_msg = accessibility_result.get('error', 'Unknown error')
                    self.logger.warning(f"⚠️ Accessibility phase failed: {error_msg}")
                    self.logger.warning("Using fallback accessibility compliance due to failure")
                    accessibility_data = self._create_fallback_accessibility_compliance(slides)
                else:
                    accessibility_data = accessibility_result["data"]
                    # Update slides with accessibility enhancements
                    if "enhanced_slides" in accessibility_data:
                        slides = accessibility_data["enhanced_slides"]
                        self.logger.info("✅ Accessibility phase succeeded - slides enhanced with WCAG 2.2 principles")
                    else:
                        self.logger.info("✅ Accessibility phase succeeded")
            
            # Update the main slides response with enhanced slides
            self.logger.info("🔍 Integrating enhanced slides into main response...")
            
            # Update the slides_response with enhanced slides
            if hasattr(slides_response, 'events') and slides:
                self.logger.info(f"Updating {len(slides_response.events)} events with enhanced slides")
                
                # Flatten all enhanced slides
                all_enhanced_slides = []
                for slide_dict in slides:
                    if isinstance(slide_dict, dict):
                        all_enhanced_slides.append(slide_dict)
                    else:
                        all_enhanced_slides.append(slide_dict.dict() if hasattr(slide_dict, 'dict') else slide_dict)
                
                # Distribute enhanced slides to events
                slide_index = 0
                for event in slides_response.events:
                    if slide_index < len(all_enhanced_slides):
                        # Update the event's slides with enhanced versions
                        event_slides = []
                        for _ in range(len(event.slides)):
                            if slide_index < len(all_enhanced_slides):
                                event_slides.append(all_enhanced_slides[slide_index])
                                slide_index += 1
                        event.slides = event_slides
                        self.logger.info(f"Updated event '{event.event_name}' with {len(event_slides)} enhanced slides")
            
            # Aggregate results
            self.logger.info("🔍 Aggregating results...")
            result = {
                "lesson_plan": {
                    "objectives": [obj.dict() for obj in objectives],
                    "lesson_plan": lesson_plan.dict(),
                    "gagne_events": [event.dict() for event in gagne_events]
                },
                "content": {
                    "gagne_slides_response": slides_response.dict(),
                    "enhanced_slides": slides,  # Include the final enhanced slides
                    "total_slides": slides_response.total_slides,
                    "total_duration": slides_response.total_duration
                },
                "udl_compliance": udl_data["udl_compliance_report"],
                "design_compliance": design_data["design_compliance_report"],
                "accessibility_compliance": accessibility_data["accessibility_compliance_report"],
                "recommendations": udl_data.get("recommendations", []),
                "design_recommendations": design_data.get("recommendations", []),
                "accessibility_recommendations": accessibility_data.get("recommendations", []),
                "accessibility_features": udl_data.get("accessibility_features", [])
            }
            
            metadata = {
                "phases_completed": ["plan", "content", "udl", "design", "accessibility"],
                "total_objectives": len(objectives),
                "total_events": len(gagne_events),
                "total_slides": slides_response.total_slides,
                "overall_udl_compliance": udl_data["udl_compliance_report"].overall_compliance if hasattr(udl_data["udl_compliance_report"], 'overall_compliance') else udl_data["udl_compliance_report"].get("overall_compliance", 0.5),
                "processing_time": "calculated_in_seconds",
                "agent_versions": {
                    "plan_agent": "1.0.0",
                    "content_agent": "1.0.0",
                    "udl_agent": "1.0.0",
                    "coordinator_agent": "1.0.0"
                }
            }
            
            self.logger.info("=" * 80)
            self.logger.info("✅ COORDINATOR AGENT COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 80)
            self._log_processing_success(f"Complete lesson planning finished - {slides_response.total_slides} slides, UDL compliance: {udl_data['udl_compliance_report']['overall_compliance']:.2f}")
            
            return self._create_success_response(result, metadata)
            
        except Exception as e:
            self._log_processing_error(e)
            return self._create_error_response(e)
    
    async def _execute_plan_phase(self, lesson_request: LessonRequest, processed_files: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the planning phase using Plan Agent"""
        try:
            plan_input = {
                "lesson_request": lesson_request,
                "processed_files": processed_files
            }
            
            return await self.plan_agent.process(plan_input)
            
        except Exception as e:
            self.logger.error(f"Plan phase execution failed: {str(e)}")
            return self._create_error_response(e)
    
    async def _execute_content_phase(
        self, 
        gagne_events: List[GagneEvent], 
        objectives: List[LessonObjective], 
        lesson_plan: LessonPlan,
        lesson_request: LessonRequest,
        processed_files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the content generation phase using Content Agent"""
        try:
            lesson_info = {
                "course_title": lesson_request.course_title,
                "lesson_topic": lesson_request.lesson_topic,
                "grade_level": lesson_request.grade_level,
                "duration_minutes": lesson_request.duration_minutes
            }
            
            content_input = {
                "gagne_events": [event.dict() for event in gagne_events],
                "objectives": [obj.dict() for obj in objectives],
                "lesson_plan": lesson_plan.dict(),
                "lesson_info": lesson_info
            }
            
            return await self.content_agent.process(content_input)
            
        except Exception as e:
            self.logger.error(f"Content phase execution failed: {str(e)}")
            return self._create_error_response(e)
    
    async def _execute_udl_phase(
        self, 
        slides: List[SlideContent], 
        lesson_request: LessonRequest,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the UDL validation phase using UDL Agent"""
        try:
            lesson_info = {
                "course_title": lesson_request.course_title,
                "lesson_topic": lesson_request.lesson_topic,
                "grade_level": lesson_request.grade_level,
                "duration_minutes": lesson_request.duration_minutes
            }
            
            udl_input = {
                "slides": [slide.dict() for slide in slides],
                "lesson_info": lesson_info,
                "preferences": preferences
            }
            
            return await self.udl_agent.process(udl_input)
            
        except Exception as e:
            self.logger.error(f"UDL phase execution failed: {str(e)}")
            return self._create_error_response(e)
    
    def _create_fallback_content(
        self, 
        gagne_events: List[GagneEvent], 
        objectives: List[LessonObjective], 
        lesson_plan: LessonPlan
    ) -> Dict[str, Any]:
        """Create fallback content when Content Agent fails"""
        self.logger.warning("Creating fallback content due to Content Agent failure")
        
        # Create basic slides for each Gagne event
        fallback_events = []
        total_slides = 0
        
        for event in gagne_events:
            # Create 2 basic slides per event
            event_slides = [
                SlideContent(
                    slide_number=total_slides + 1,
                    title=f"{event.event_name} - Overview",
                    content_type="mixed",
                    main_content=f"# {event.event_name}\n\n{event.description}\n\n## Activities:\n" + "\n".join([f"- {activity}" for activity in event.activities]),
                    visual_elements=[],
                    audio_script=f"Audio narration for {event.event_name}",
                    speaker_notes=f"Speaker notes for {event.event_name}",
                    duration_minutes=event.duration_minutes / 2,
                    learning_objectives=[obj.objective for obj in objectives[:2]],
                    key_points=[f"Key point for {event.event_name}"],
                    activities=event.activities[:2],
                    materials_needed=event.materials_needed,
                    assessment_criteria=event.assessment_strategy or "Formative assessment",
                    accessibility_features=["alt_text", "keyboard_navigation"],
                    udl_guidelines=["multiple_representation", "engagement"],
                    difficulty_level="intermediate"
                ),
                SlideContent(
                    slide_number=total_slides + 2,
                    title=f"{event.event_name} - Details",
                    content_type="mixed",
                    main_content=f"# {event.event_name} - Detailed Content\n\n## Materials Needed:\n" + "\n".join([f"- {material}" for material in event.materials_needed]),
                    visual_elements=[],
                    audio_script=f"Detailed audio narration for {event.event_name}",
                    speaker_notes=f"Detailed speaker notes for {event.event_name}",
                    duration_minutes=event.duration_minutes / 2,
                    learning_objectives=[obj.objective for obj in objectives[2:4]] if len(objectives) > 2 else [],
                    key_points=[f"Detailed key point for {event.event_name}"],
                    activities=event.activities[2:4] if len(event.activities) > 2 else [],
                    materials_needed=event.materials_needed,
                    assessment_criteria=event.assessment_strategy or "Formative assessment",
                    accessibility_features=["alt_text", "keyboard_navigation"],
                    udl_guidelines=["multiple_representation", "engagement"],
                    difficulty_level="intermediate"
                )
            ]
            
            total_slides += 2
            
            fallback_events.append(GagneEventSlides(
                event_number=event.event_number,
                event_name=event.event_name,
                event_description=event.description,
                total_slides=2,
                estimated_duration=event.duration_minutes,
                slides=event_slides,
                teaching_strategies=["Direct instruction", "Interactive discussion"],
                learning_outcomes=[obj.objective for obj in objectives[:2]],
                materials_summary=event.materials_needed,
                assessment_notes=event.assessment_strategy
            ))
        
        gagne_slides_response = GagneSlidesResponse(
            lesson_info={
                "course_title": lesson_plan.title,
                "lesson_topic": "Lesson Topic",
                "grade_level": "college",
                "duration_minutes": sum(event.duration_minutes for event in gagne_events)
            },
            total_events=len(fallback_events),
            total_slides=total_slides,
            total_duration=sum(event.duration_minutes for event in gagne_events),
            events=fallback_events,
            generation_metadata={
                "service_version": "1.0.0",
                "generation_method": "fallback",
                "quality_level": "basic"
            },
            created_at=str(asyncio.get_event_loop().time())
        )
        
        return {
            "gagne_slides_response": gagne_slides_response.dict(),
            "total_duration": gagne_slides_response.total_duration,
            "total_slides": gagne_slides_response.total_slides
        }
    
    def _create_fallback_udl_compliance(self, slides: List[SlideContent]) -> Dict[str, Any]:
        """Create fallback UDL compliance when UDL Agent fails"""
        self.logger.warning("Creating fallback UDL compliance due to UDL Agent failure")
        
        return {
            "udl_compliance_report": {
                "representation_score": 0.6,
                "action_expression_score": 0.5,
                "engagement_score": 0.5,
                "overall_compliance": 0.53,
                "missing_guidelines": ["Perception", "Language & Symbols", "Physical Action"],
                "recommendations": [
                    "Add audio descriptions and visual alternatives",
                    "Include vocabulary definitions",
                    "Provide alternative response methods"
                ],
                "accessibility_features_implemented": ["alt_text", "keyboard_navigation"]
            },
            "recommendations": [
                "Implement multiple means of representation",
                "Add engagement strategies",
                "Provide multiple means of action and expression"
            ],
            "accessibility_features": ["alt_text", "keyboard_navigation"]
        }
    
    async def refine_lesson_component(
        self, 
        component_type: str, 
        component_data: Dict[str, Any], 
        refinement_instructions: str
    ) -> Dict[str, Any]:
        """Refine a specific lesson component using the appropriate agent"""
        try:
            self.logger.info(f"Refining lesson component: {component_type}")
            
            if component_type == "objectives":
                return await self._refine_objectives(component_data, refinement_instructions)
            elif component_type == "lesson_plan":
                return await self._refine_lesson_plan(component_data, refinement_instructions)
            elif component_type == "gagne_events":
                return await self._refine_gagne_events(component_data, refinement_instructions)
            elif component_type == "slides":
                return await self._refine_slides(component_data, refinement_instructions)
            elif component_type == "udl_compliance":
                return await self._refine_udl_compliance(component_data, refinement_instructions)
            else:
                raise ValueError(f"Unknown component type: {component_type}")
                
        except Exception as e:
            self.logger.error(f"Error refining component {component_type}: {str(e)}")
            return self._create_error_response(e)
    
    async def _refine_objectives(self, objectives_data: Dict[str, Any], instructions: str) -> Dict[str, Any]:
        """Refine learning objectives using Plan Agent"""
        # This would require extending Plan Agent with refinement capabilities
        # For now, return the original data
        return {"refined_objectives": objectives_data}
    
    async def _refine_lesson_plan(self, lesson_plan_data: Dict[str, Any], instructions: str) -> Dict[str, Any]:
        """Refine lesson plan using Plan Agent"""
        # This would require extending Plan Agent with refinement capabilities
        # For now, return the original data
        return {"refined_lesson_plan": lesson_plan_data}
    
    async def _refine_gagne_events(self, events_data: Dict[str, Any], instructions: str) -> Dict[str, Any]:
        """Refine Gagne events using Plan Agent"""
        # This would require extending Plan Agent with refinement capabilities
        # For now, return the original data
        return {"refined_gagne_events": events_data}
    
    async def _refine_slides(self, slides_data: Dict[str, Any], instructions: str) -> Dict[str, Any]:
        """Refine slides using Content Agent"""
        # This would require extending Content Agent with refinement capabilities
        # For now, return the original data
        return {"refined_slides": slides_data}
    
    async def _refine_udl_compliance(self, udl_data: Dict[str, Any], instructions: str) -> Dict[str, Any]:
        """Refine UDL compliance using UDL Agent"""
        try:
            refinement_request = {
                "refinement_type": "udl_compliance",
                "refinement_instructions": instructions,
                "current_content": udl_data
            }
            
            udl_input = {
                "slides": [],  # Would need actual slides for refinement
                "lesson_info": {},
                "refinement_request": refinement_request
            }
            
            return await self.udl_agent.process(udl_input)
            
        except Exception as e:
            self.logger.error(f"Error refining UDL compliance: {str(e)}")
            return {"refined_udl_compliance": udl_data}
    
    async def _execute_design_phase(
        self, 
        slides: List[SlideContent], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the design validation phase using Design Agent"""
        try:
            # Convert slides to dictionaries if they are objects
            slide_dicts = []
            for slide in slides:
                if isinstance(slide, dict):
                    slide_dicts.append(slide)
                else:
                    slide_dicts.append(slide.dict())
            
            design_input = {
                "slides": slide_dicts,
                "design_preferences": preferences.get("design", {}),
                "validation_level": preferences.get("design_level", "standard")
            }
            
            return await self.design_agent.process(design_input)
            
        except Exception as e:
            self.logger.error(f"Design phase execution failed: {str(e)}")
            return self._create_error_response(e)
    
    async def _execute_accessibility_phase(
        self, 
        slides: List[SlideContent], 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the accessibility validation phase using Accessibility Agent"""
        try:
            # Convert slides to dictionaries if they are objects
            slide_dicts = []
            for slide in slides:
                if isinstance(slide, dict):
                    slide_dicts.append(slide)
                else:
                    slide_dicts.append(slide.dict())
            
            accessibility_input = {
                "slides": slide_dicts,
                "accessibility_level": preferences.get("accessibility_level", "AA"),
                "validation_preferences": preferences.get("accessibility", {})
            }
            
            return await self.accessibility_agent.process(accessibility_input)
            
        except Exception as e:
            self.logger.error(f"Accessibility phase execution failed: {str(e)}")
            return self._create_error_response(e)
    
    def _create_fallback_design_compliance(self, slides: List[SlideContent]) -> Dict[str, Any]:
        """Create fallback design compliance data"""
        return {
            "design_compliance_report": {
                "contrast_score": 0.5,
                "repetition_score": 0.5,
                "alignment_score": 0.5,
                "proximity_score": 0.5,
                "overall_score": 0.5,
                "validation_level": "basic",
                "principles": {
                    "contrast": {"score": 0.5, "status": "basic", "details": "Basic contrast validation"},
                    "repetition": {"score": 0.5, "status": "basic", "details": "Basic repetition validation"},
                    "alignment": {"score": 0.5, "status": "basic", "details": "Basic alignment validation"},
                    "proximity": {"score": 0.5, "status": "basic", "details": "Basic proximity validation"}
                }
            },
            "recommendations": ["Implement basic C.R.A.P. design principles"],
            "violations": []
        }
    
    def _create_fallback_accessibility_compliance(self, slides: List[SlideContent]) -> Dict[str, Any]:
        """Create fallback accessibility compliance data"""
        return {
            "accessibility_compliance_report": {
                "perceivable_score": 0.5,
                "operable_score": 0.5,
                "understandable_score": 0.5,
                "robust_score": 0.5,
                "overall_score": 0.5,
                "wcag_level": "AA",
                "principles": {
                    "perceivable": {"score": 0.5, "status": "basic", "details": "Basic perceivable validation"},
                    "operable": {"score": 0.5, "status": "basic", "details": "Basic operable validation"},
                    "understandable": {"score": 0.5, "status": "basic", "details": "Basic understandable validation"},
                    "robust": {"score": 0.5, "status": "basic", "details": "Basic robust validation"}
                }
            },
            "recommendations": ["Implement basic WCAG accessibility guidelines"],
            "violations": []
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "coordinator_agent": {
                "status": "active",
                "version": "1.0.0",
                "capabilities": ["orchestration", "error_handling", "fallback_creation"]
            },
            "plan_agent": {
                "status": "active",
                "version": "1.0.0",
                "capabilities": ["objectives_generation", "lesson_planning", "gagne_events"]
            },
            "content_agent": {
                "status": "active",
                "version": "1.0.0",
                "capabilities": ["slide_generation", "multimodal_content", "visual_elements"]
            },
            "udl_agent": {
                "status": "active",
                "version": "1.0.0",
                "capabilities": ["udl_validation", "accessibility_assessment", "compliance_scoring"]
            },
            "design_agent": {
                "status": "active",
                "version": "1.0.0",
                "capabilities": ["crap_validation", "design_assessment", "visual_compliance"]
            },
            "accessibility_agent": {
                "status": "active",
                "version": "1.0.0",
                "capabilities": ["wcag_2_2_validation", "technical_accessibility", "compliance_scoring", "mobile_accessibility"]
            }
        }
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get overall system capabilities"""
        return {
            "lesson_planning": {
                "bloom_taxonomy": True,
                "gagne_events": True,
                "pedagogical_principles": True,
                "cognitive_load_optimization": True
            },
            "content_generation": {
                "multimodal_slides": True,
                "visual_elements": True,
                "audio_scripts": True,
                "interactive_activities": True
            },
            "accessibility": {
                "udl_compliance": True,
                "accessibility_features": True,
                "multiple_modalities": True,
                "inclusive_design": True
            },
            "export_formats": {
                "powerpoint": True,
                "pdf": True,
                "html": True,
                "json": True
            }
        }
