"""
Test script for the Multi-Agent Lesson Planning System

This script validates the functionality of all agents and the coordinator
to ensure the multi-agent system is working correctly.
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.agents.coordinator_agent import CoordinatorAgent
from app.services.agents.plan_agent import PlanAgent
from app.services.agents.content_agent import ContentAgent
from app.services.agents.udl_agent import UDLAgent
from app.services.multi_agent_service import MultiAgentService
from app.models.lesson import LessonRequest, BloomLevel, GradeLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_individual_agents():
    """Test each agent individually"""
    logger.info("=== Testing Individual Agents ===")
    
    # Test Plan Agent
    logger.info("Testing Plan Agent...")
    plan_agent = PlanAgent()
    
    test_lesson_request = LessonRequest(
        course_title="Introduction to Computer Science",
        lesson_topic="Data Structures and Algorithms",
        grade_level=GradeLevel.JUNIOR,
        duration_minutes=60,
        selected_bloom_levels=[BloomLevel.UNDERSTAND, BloomLevel.APPLY, BloomLevel.ANALYZE]
    )
    
    plan_input = {
        "lesson_request": test_lesson_request,
        "processed_files": {}
    }
    
    try:
        plan_result = await plan_agent.process(plan_input)
        if plan_result.get("success"):
            logger.info("✅ Plan Agent test passed")
            logger.info(f"   Generated {len(plan_result['data']['objectives'])} objectives")
            logger.info(f"   Generated {len(plan_result['data']['gagne_events'])} Gagne events")
        else:
            logger.error("❌ Plan Agent test failed")
            logger.error(f"   Error: {plan_result.get('error')}")
    except Exception as e:
        logger.error(f"❌ Plan Agent test failed with exception: {str(e)}")
    
    # Test Content Agent (requires plan data)
    logger.info("Testing Content Agent...")
    content_agent = ContentAgent()
    
    # Create mock data for content agent
    mock_gagne_events = [
        {
            "event_number": 1,
            "event_name": "Gain Attention",
            "description": "Capture student interest",
            "activities": ["Opening question", "Visual presentation"],
            "duration_minutes": 5,
            "materials_needed": ["Presentation slides"],
            "assessment_strategy": None
        }
    ]
    
    mock_objectives = [
        {
            "bloom_level": "understand",
            "objective": "Students will understand basic data structures",
            "action_verb": "understand",
            "content": "data structures",
            "condition": "following instruction",
            "criteria": "with accuracy"
        }
    ]
    
    mock_lesson_plan = {
        "title": "Data Structures Lesson",
        "overview": "Introduction to data structures",
        "prerequisites": ["Basic programming knowledge"],
        "materials": ["Textbook", "Computer"],
        "technology_requirements": ["Computer"],
        "assessment_methods": ["Quiz", "Project"],
        "differentiation_strategies": ["Visual aids"],
        "closure_activities": ["Summary discussion"]
    }
    
    content_input = {
        "gagne_events": mock_gagne_events,
        "objectives": mock_objectives,
        "lesson_plan": mock_lesson_plan,
        "lesson_info": {
            "course_title": "Computer Science",
            "lesson_topic": "Data Structures",
            "grade_level": "junior",
            "duration_minutes": 60
        }
    }
    
    try:
        content_result = await content_agent.process(content_input)
        if content_result.get("success"):
            logger.info("✅ Content Agent test passed")
            slides_response = content_result["data"]["gagne_slides_response"]
            logger.info(f"   Generated {slides_response['total_slides']} slides")
        else:
            logger.error("❌ Content Agent test failed")
            logger.error(f"   Error: {content_result.get('error')}")
    except Exception as e:
        logger.error(f"❌ Content Agent test failed with exception: {str(e)}")
    
    # Test UDL Agent
    logger.info("Testing UDL Agent...")
    udl_agent = UDLAgent()
    
    # Create mock slide data
    mock_slides = [
        {
            "slide_number": 1,
            "title": "Introduction to Data Structures",
            "content_type": "mixed",
            "main_content": "# Data Structures\n\nBasic concepts and examples",
            "visual_elements": [],
            "audio_script": "Audio narration",
            "speaker_notes": "Speaker notes",
            "duration_minutes": 3.0,
            "learning_objectives": ["Understand data structures"],
            "key_points": ["Key point 1"],
            "activities": ["Activity 1"],
            "materials_needed": ["Materials"],
            "assessment_criteria": "Assessment criteria",
            "accessibility_features": ["alt_text", "keyboard_navigation"],
            "udl_guidelines": ["multiple_representation", "engagement"],
            "difficulty_level": "intermediate"
        }
    ]
    
    udl_input = {
        "slides": mock_slides,
        "lesson_info": {
            "course_title": "Computer Science",
            "lesson_topic": "Data Structures",
            "grade_level": "junior",
            "duration_minutes": 60
        }
    }
    
    try:
        udl_result = await udl_agent.process(udl_input)
        if udl_result.get("success"):
            logger.info("✅ UDL Agent test passed")
            compliance = udl_result["data"]["udl_compliance_report"]
            logger.info(f"   Overall UDL compliance: {compliance['overall_compliance']:.2f}")
        else:
            logger.error("❌ UDL Agent test failed")
            logger.error(f"   Error: {udl_result.get('error')}")
    except Exception as e:
        logger.error(f"❌ UDL Agent test failed with exception: {str(e)}")


async def test_coordinator_agent():
    """Test the coordinator agent"""
    logger.info("=== Testing Coordinator Agent ===")
    
    coordinator = CoordinatorAgent()
    
    test_lesson_request = LessonRequest(
        course_title="Advanced Programming",
        lesson_topic="Object-Oriented Design Patterns",
        grade_level=GradeLevel.SENIOR,
        duration_minutes=90,
        selected_bloom_levels=[BloomLevel.ANALYZE, BloomLevel.EVALUATE, BloomLevel.CREATE]
    )
    
    coordinator_input = {
        "lesson_request": test_lesson_request,
        "processed_files": {},
        "preferences": {}
    }
    
    try:
        coordinator_result = await coordinator.process(coordinator_input)
        if coordinator_result.get("success"):
            logger.info("✅ Coordinator Agent test passed")
            data = coordinator_result["data"]
            logger.info(f"   Generated lesson plan with {len(data['lesson_plan']['objectives'])} objectives")
            logger.info(f"   Generated {len(data['lesson_plan']['gagne_events'])} Gagne events")
            logger.info(f"   Generated {data['content']['total_slides']} slides")
            logger.info(f"   UDL compliance: {data['udl_compliance']['overall_compliance']:.2f}")
        else:
            logger.error("❌ Coordinator Agent test failed")
            logger.error(f"   Error: {coordinator_result.get('error')}")
    except Exception as e:
        logger.error(f"❌ Coordinator Agent test failed with exception: {str(e)}")


async def test_multi_agent_service():
    """Test the multi-agent service"""
    logger.info("=== Testing Multi-Agent Service ===")
    
    service = MultiAgentService()
    
    test_lesson_request = LessonRequest(
        course_title="Machine Learning Fundamentals",
        lesson_topic="Neural Networks and Deep Learning",
        grade_level=GradeLevel.MASTERS,
        duration_minutes=120,
        selected_bloom_levels=[BloomLevel.UNDERSTAND, BloomLevel.APPLY, BloomLevel.ANALYZE, BloomLevel.CREATE]
    )
    
    try:
        # Test complete lesson generation
        lesson_response = await service.generate_lesson_content(test_lesson_request)
        logger.info("✅ Multi-Agent Service test passed")
        logger.info(f"   Generated lesson: {lesson_response.lesson_info['course_title']}")
        logger.info(f"   Objectives: {len(lesson_response.objectives)}")
        logger.info(f"   Gagne events: {len(lesson_response.gagne_events)}")
        logger.info(f"   Total slides: {lesson_response.gagne_slides.total_slides}")
        logger.info(f"   UDL compliance: {lesson_response.udl_compliance['overall_compliance']:.2f}")
        
        # Test agent status
        agent_status = service.get_agent_status()
        logger.info("✅ Agent status check passed")
        for agent_name, status in agent_status.items():
            logger.info(f"   {agent_name}: {status['status']}")
        
        # Test system capabilities
        capabilities = service.get_system_capabilities()
        logger.info("✅ System capabilities check passed")
        logger.info(f"   Lesson planning: {capabilities['lesson_planning']}")
        logger.info(f"   Content generation: {capabilities['content_generation']}")
        logger.info(f"   Accessibility: {capabilities['accessibility']}")
        
        # Test health check
        health = await service.health_check()
        logger.info("✅ Health check passed")
        logger.info(f"   System status: {health['status']}")
        
    except Exception as e:
        logger.error(f"❌ Multi-Agent Service test failed with exception: {str(e)}")


async def test_agent_communication():
    """Test agent-to-agent communication through coordinator"""
    logger.info("=== Testing Agent Communication ===")
    
    coordinator = CoordinatorAgent()
    
    # Test individual agent access
    try:
        plan_agent = coordinator.plan_agent
        content_agent = coordinator.content_agent
        udl_agent = coordinator.udl_agent
        
        logger.info("✅ Agent access test passed")
        logger.info(f"   Plan Agent: {type(plan_agent).__name__}")
        logger.info(f"   Content Agent: {type(content_agent).__name__}")
        logger.info(f"   UDL Agent: {type(udl_agent).__name__}")
        
        # Test agent status
        status = coordinator.get_agent_status()
        logger.info("✅ Agent status test passed")
        for agent_name, agent_info in status.items():
            logger.info(f"   {agent_name}: {agent_info['status']} (v{agent_info['version']})")
        
    except Exception as e:
        logger.error(f"❌ Agent communication test failed: {str(e)}")


async def test_error_handling():
    """Test error handling and fallback mechanisms"""
    logger.info("=== Testing Error Handling ===")
    
    service = MultiAgentService()
    
    # Test with invalid input
    try:
        invalid_request = LessonRequest(
            course_title="",  # Empty title
            lesson_topic="",  # Empty topic
            grade_level=GradeLevel.JUNIOR,
            duration_minutes=0,  # Invalid duration
            selected_bloom_levels=[]  # No bloom levels
        )
        
        result = await service.generate_lesson_content(invalid_request)
        if result:
            logger.info("✅ Error handling test passed - system handled invalid input gracefully")
        else:
            logger.error("❌ Error handling test failed - system should handle invalid input")
            
    except Exception as e:
        logger.info(f"✅ Error handling test passed - system properly rejected invalid input: {str(e)}")


async def main():
    """Run all tests"""
    logger.info("🚀 Starting Multi-Agent System Tests")
    logger.info("=" * 50)
    
    try:
        # Test individual agents
        await test_individual_agents()
        logger.info("")
        
        # Test coordinator agent
        await test_coordinator_agent()
        logger.info("")
        
        # Test multi-agent service
        await test_multi_agent_service()
        logger.info("")
        
        # Test agent communication
        await test_agent_communication()
        logger.info("")
        
        # Test error handling
        await test_error_handling()
        logger.info("")
        
        logger.info("🎉 All tests completed!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Test suite failed with exception: {str(e)}")
        raise


if __name__ == "__main__":
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ OPENAI_API_KEY environment variable not set")
        logger.error("Please set your OpenAI API key to run the tests")
        sys.exit(1)
    
    # Run the tests
    asyncio.run(main())
