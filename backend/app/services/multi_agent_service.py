"""
Multi-Agent Service for Lesson Planning System

This service provides a unified interface to the multi-agent lesson planning system,
maintaining backward compatibility with the existing API while leveraging the new
agent-based architecture for enhanced functionality and reliability.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from .agents.coordinator_agent import CoordinatorAgent
from .agents.plan_agent import PlanAgent
from .agents.content_agent import ContentAgent
from .agents.udl_agent import UDLAgent
from ..models.lesson import LessonRequest, LessonResponse, RefineRequest, LessonObjective, LessonPlan, GagneEvent
from ..models.gagne_slides import GagneSlidesResponse

logger = logging.getLogger(__name__)


class MultiAgentService:
    """
    Unified service that provides access to the multi-agent lesson planning system.
    
    This service maintains backward compatibility with the existing API while
    leveraging the new agent-based architecture for enhanced functionality.
    """
    
    def __init__(self):
        """Initialize the multi-agent service."""
        self.coordinator = CoordinatorAgent()
        self.plan_agent = PlanAgent()
        self.content_agent = ContentAgent()
        self.udl_agent = UDLAgent()
        
        logger.info("MultiAgentService initialized with all agents")
    
    async def generate_lesson_content(self, request: LessonRequest) -> LessonResponse:
        """
        Generate complete lesson content using the multi-agent system.
        
        This method maintains backward compatibility with the existing API
        while leveraging the new agent-based architecture.
        
        Args:
            request: LessonRequest object with lesson parameters
            
        Returns:
            LessonResponse object with complete lesson content
        """
        try:
            logger.info("=" * 80)
            logger.info("🚀 STARTING LESSON GENERATION")
            logger.info("=" * 80)
            logger.info(f"📚 Course: {request.course_title}")
            logger.info(f"📖 Topic: {request.lesson_topic}")
            logger.info(f"🎓 Grade Level: {request.grade_level}")
            logger.info(f"⏱️ Duration: {request.duration_minutes} minutes")
            logger.info(f"🧠 Bloom Levels: {request.selected_bloom_levels}")
            
            # Prepare input for coordinator agent
            coordinator_input = {
                "lesson_request": request,
                "processed_files": {},  # Will be populated from file processing if needed
                "preferences": {}
            }
            
            logger.info("🔄 Starting multi-agent processing...")
            logger.info(f"📋 Coordinator input keys: {list(coordinator_input.keys())}")
            
            # Execute multi-agent lesson planning with timeout
            try:
                logger.info("🤖 Calling coordinator.process...")
                result = await asyncio.wait_for(
                    self.coordinator.process(coordinator_input),
                    timeout=600  # 10 minute timeout for enhanced validation
                )
                logger.info(f"✅ Coordinator returned: {type(result)}")
                logger.info(f"📊 Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                logger.info(f"🎯 Result success: {result.get('success', 'No success key')}")
            except asyncio.TimeoutError:
                logger.error("⏰ Multi-agent processing timed out after 5 minutes")
                raise Exception("Request timeout. The lesson generation is taking longer than expected. Please try again.")
            except Exception as e:
                logger.error(f"❌ Error in coordinator.process: {str(e)}")
                logger.error(f"🔍 Error type: {type(e).__name__}")
                import traceback
                logger.error(f"📜 Traceback: {traceback.format_exc()}")
                raise
            
            logger.info("✅ Multi-agent processing completed")
            
            if not result.get("success"):
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"❌ Multi-agent processing failed: {error_msg}")
                raise Exception(f"Multi-agent processing failed: {error_msg}")
            
            data = result["data"]
            logger.info("📦 Extracting components from multi-agent result...")
            logger.info(f"📋 Data keys: {list(data.keys())}")
            
            # Extract components from multi-agent result
            lesson_plan_data = data["lesson_plan"]
            content_data = data["content"]
            udl_compliance_report = data["udl_compliance"]
            design_compliance_report = data["design_compliance"]
            accessibility_compliance_report = data["accessibility_compliance"]
            recommendations = data.get("recommendations", [])
            design_recommendations = data.get("design_recommendations", [])
            accessibility_recommendations = data.get("accessibility_recommendations", [])
            accessibility_features = data.get("accessibility_features", [])
            
            logger.info(f"📊 Lesson plan data keys: {list(lesson_plan_data.keys()) if isinstance(lesson_plan_data, dict) else 'Not a dict'}")
            logger.info(f"📊 Content data keys: {list(content_data.keys()) if isinstance(content_data, dict) else 'Not a dict'}")
            logger.info(f"📊 UDL data keys: {list(udl_compliance_report.keys()) if isinstance(udl_compliance_report, dict) else 'Not a dict'}")
            
            logger.info("🎨 Creating GagneSlidesResponse...")
            
            # Create GagneSlidesResponse from content data
            try:
                logger.info(f"🔍 Content data gagne_slides_response type: {type(content_data['gagne_slides_response'])}")
                gagne_slides_response = GagneSlidesResponse(**content_data["gagne_slides_response"])
                logger.info(f"✅ GagneSlidesResponse created with {gagne_slides_response.total_slides} slides")
                logger.info(f"📊 Events count: {len(gagne_slides_response.events)}")
            except Exception as e:
                logger.error(f"❌ Error creating GagneSlidesResponse: {str(e)}")
                logger.error(f"🔍 Error type: {type(e).__name__}")
                import traceback
                logger.error(f"📜 Traceback: {traceback.format_exc()}")
                raise Exception(f"Failed to create slides response: {str(e)}")
            
            logger.info("📝 Creating LessonResponse...")
            
            # Create LessonResponse maintaining backward compatibility
            try:
                logger.info("🔍 Creating objectives...")
                objectives = [LessonObjective(**obj) for obj in lesson_plan_data["objectives"]]
                logger.info(f"✅ Created {len(objectives)} objectives")
                
                logger.info("🔍 Creating lesson plan...")
                lesson_plan = LessonPlan(**lesson_plan_data["lesson_plan"])
                logger.info("✅ Lesson plan created")
                
                logger.info("🔍 Creating Gagne events...")
                gagne_events = [GagneEvent(**event) for event in lesson_plan_data["gagne_events"]]
                logger.info(f"✅ Created {len(gagne_events)} Gagne events")
                
                logger.info("🔍 Creating final LessonResponse...")
                lesson_response = LessonResponse(
                    lesson_info={
                        "course_title": request.course_title,
                        "lesson_topic": request.lesson_topic,
                        "grade_level": request.grade_level,
                        "duration_minutes": request.duration_minutes
                    },
                    objectives=objectives,
                    lesson_plan=lesson_plan,
                    gagne_events=gagne_events,
                    gagne_slides=gagne_slides_response.dict(),
                    total_duration=content_data["total_duration"],
                    created_at=str(asyncio.get_event_loop().time()),
                    # Multi-agent validation results
                    udl_compliance=udl_compliance_report,
                    design_compliance=design_compliance_report,
                    accessibility_compliance=accessibility_compliance_report,
                    recommendations=recommendations,
                    design_recommendations=design_recommendations,
                    accessibility_recommendations=accessibility_recommendations,
                    accessibility_features=accessibility_features
                )
                logger.info("✅ LessonResponse created successfully")
            except Exception as e:
                logger.error(f"❌ Error creating LessonResponse: {str(e)}")
                logger.error(f"🔍 Error type: {type(e).__name__}")
                import traceback
                logger.error(f"📜 Traceback: {traceback.format_exc()}")
                raise Exception(f"Failed to create lesson response: {str(e)}")
            
            logger.info(f"🎉 Successfully generated lesson with {content_data['total_slides']} slides")
            logger.info("=" * 80)
            logger.info("✅ LESSON GENERATION COMPLETED")
            logger.info("=" * 80)
            return lesson_response
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error("❌ LESSON GENERATION FAILED")
            logger.error("=" * 80)
            logger.error(f"❌ Error: {str(e)}")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            import traceback
            logger.error(f"📜 Traceback: {traceback.format_exc()}")
            raise
    
    async def refine_content(self, request: RefineRequest) -> Dict[str, Any]:
        """
        Refine specific lesson content using the multi-agent system.
        
        Args:
            request: RefineRequest object with refinement parameters
            
        Returns:
            Dictionary with refined content
        """
        try:
            logger.info(f"Refining content for section: {request.section_type}")
            
            # Determine which agent to use based on section type
            if request.section_type in ["objectives", "lesson_plan", "gagne_events"]:
                # Use Plan Agent for planning components
                agent_input = {
                    "lesson_request": request.lesson_data.lesson_info,
                    "processed_files": {},
                    "refinement_request": {
                        "section_type": request.section_type,
                        "section_content": request.section_content,
                        "refinement_instructions": request.refinement_instructions
                    }
                }
                
                result = await self.plan_agent.process(agent_input)
                
            elif request.section_type in ["slides", "content"]:
                # Use Content Agent for content components
                agent_input = {
                    "gagne_events": request.lesson_data.gagne_events,
                    "objectives": request.lesson_data.objectives,
                    "lesson_plan": request.lesson_data.lesson_plan,
                    "lesson_info": request.lesson_data.lesson_info,
                    "refinement_request": {
                        "section_type": request.section_type,
                        "section_content": request.section_content,
                        "refinement_instructions": request.refinement_instructions
                    }
                }
                
                result = await self.content_agent.process(agent_input)
                
            elif request.section_type in ["udl_compliance", "accessibility"]:
                # Use UDL Agent for UDL components
                agent_input = {
                    "slides": request.lesson_data.gagne_slides.events if hasattr(request.lesson_data, 'gagne_slides') else [],
                    "lesson_info": request.lesson_data.lesson_info,
                    "refinement_request": {
                        "section_type": request.section_type,
                        "section_content": request.section_content,
                        "refinement_instructions": request.refinement_instructions
                    }
                }
                
                result = await self.udl_agent.process(agent_input)
                
            else:
                # Use Coordinator Agent for general refinement
                result = await self.coordinator.refine_lesson_component(
                    request.section_type,
                    request.section_content,
                    request.refinement_instructions
                )
            
            if result.get("success"):
                return {"refined_content": result["data"]}
            else:
                return {"refined_content": request.section_content}
                
        except Exception as e:
            logger.error(f"Error in refine_content: {str(e)}")
            return {"refined_content": request.section_content}
    
    async def generate_slides_only(self, gagne_events: list, objectives: list, lesson_plan: dict, lesson_info: dict) -> GagneSlidesResponse:
        """
        Generate slides only using the Content Agent.
        
        Args:
            gagne_events: List of Gagne events
            objectives: List of learning objectives
            lesson_plan: Lesson plan data
            lesson_info: Lesson information
            
        Returns:
            GagneSlidesResponse object
        """
        try:
            logger.info("Generating slides using Content Agent")
            
            content_input = {
                "gagne_events": gagne_events,
                "objectives": objectives,
                "lesson_plan": lesson_plan,
                "lesson_info": lesson_info
            }
            
            result = await self.content_agent.process(content_input)
            
            if result.get("success"):
                return GagneSlidesResponse(**result["data"]["gagne_slides_response"])
            else:
                raise Exception(f"Content generation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in generate_slides_only: {str(e)}")
            raise
    
    async def validate_udl_compliance(self, slides: list, lesson_info: dict) -> Dict[str, Any]:
        """
        Validate UDL compliance using the UDL Agent.
        
        Args:
            slides: List of slide content
            lesson_info: Lesson information
            
        Returns:
            Dictionary with UDL compliance data
        """
        try:
            logger.info("Validating UDL compliance using UDL Agent")
            
            udl_input = {
                "slides": slides,
                "lesson_info": lesson_info
            }
            
            result = await self.udl_agent.process(udl_input)
            
            if result.get("success"):
                return result["data"]
            else:
                raise Exception(f"UDL validation failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in validate_udl_compliance: {str(e)}")
            raise
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents in the system."""
        return self.coordinator.get_agent_status()
    
    def get_system_capabilities(self) -> Dict[str, Any]:
        """Get overall system capabilities."""
        return self.coordinator.get_system_capabilities()
    
    def get_udl_guidelines(self) -> Dict[str, Any]:
        """Get UDL guidelines and implementation strategies."""
        return self.udl_agent.get_udl_guidelines()
    
    def get_content_modalities(self) -> Dict[str, Any]:
        """Get available content modalities for multimodal learning."""
        return self.udl_agent.get_content_modalities()
    
    def get_accessibility_features(self) -> Dict[str, Any]:
        """Get available accessibility features for course content."""
        return self.udl_agent.get_accessibility_features()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents."""
        try:
            agent_status = self.get_agent_status()
            
            # Check if all agents are active
            all_active = all(
                agent_info["status"] == "active" 
                for agent_info in agent_status.values()
            )
            
            return {
                "status": "healthy" if all_active else "degraded",
                "agents": agent_status,
                "multi_agent_system": "operational" if all_active else "degraded"
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "multi_agent_system": "offline"
            }
