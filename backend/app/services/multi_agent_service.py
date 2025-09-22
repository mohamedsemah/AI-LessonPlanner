"""
Multi-Agent Service for Lesson Planning System

This service provides a unified interface to the multi-agent lesson planning system,
maintaining backward compatibility with the existing API while leveraging the new
agent-based architecture for enhanced functionality and reliability.
"""

import logging
from typing import Dict, Any, Optional
from .agents.coordinator_agent import CoordinatorAgent
from .agents.plan_agent import PlanAgent
from .agents.content_agent import ContentAgent
from .agents.udl_agent import UDLAgent
from ..models.lesson import LessonRequest, LessonResponse, RefineRequest
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
            logger.info(f"Generating lesson content for: {request.course_title}")
            
            # Prepare input for coordinator agent
            coordinator_input = {
                "lesson_request": request,
                "processed_files": {},  # Will be populated from file processing if needed
                "preferences": {}
            }
            
            # Execute multi-agent lesson planning
            result = await self.coordinator.process(coordinator_input)
            
            if not result.get("success"):
                raise Exception(f"Multi-agent processing failed: {result.get('error', 'Unknown error')}")
            
            data = result["data"]
            
            # Extract components from multi-agent result
            lesson_plan_data = data["lesson_plan"]
            content_data = data["content"]
            udl_data = data["udl_compliance"]
            
            # Create GagneSlidesResponse from content data
            gagne_slides_response = GagneSlidesResponse(**content_data["gagne_slides_response"])
            
            # Create LessonResponse maintaining backward compatibility
            lesson_response = LessonResponse(
                lesson_info={
                    "course_title": request.course_title,
                    "lesson_topic": request.lesson_topic,
                    "grade_level": request.grade_level,
                    "duration_minutes": request.duration_minutes
                },
                objectives=lesson_plan_data["objectives"],
                lesson_plan=lesson_plan_data["lesson_plan"],
                gagne_events=lesson_plan_data["gagne_events"],
                gagne_slides=gagne_slides_response,
                udl_compliance=udl_data,
                recommendations=data.get("recommendations", []),
                accessibility_features=data.get("accessibility_features", []),
                metadata={
                    "generation_method": "multi_agent",
                    "agent_versions": result["metadata"].get("agent_versions", {}),
                    "processing_phases": result["metadata"].get("phases_completed", []),
                    "total_slides": content_data["total_slides"],
                    "total_duration": content_data["total_duration"],
                    "udl_compliance_score": udl_data.get("overall_compliance", 0.0)
                }
            )
            
            logger.info(f"Successfully generated lesson with {content_data['total_slides']} slides")
            return lesson_response
            
        except Exception as e:
            logger.error(f"Error in generate_lesson_content: {str(e)}")
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
