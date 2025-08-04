#!/usr/bin/env python3

import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_real_request():
    try:
        from app.models.udl_content import CourseContentRequest
        from app.services.udl_content_service import UDLContentService
        
        print("✅ Models imported successfully")
        
        # Simulate the exact request structure from frontend
        # This is what the frontend sends based on the CourseContent.jsx code
        frontend_request = {
            "lesson_data": {
                "lesson_info": {
                    "course_title": "Computer Science",
                    "lesson_topic": "Data Structures",
                    "grade_level": "College",
                    "duration_minutes": 60,
                    "selected_bloom_levels": ["remember", "understand", "apply"]
                },
                "objectives": [
                    {
                        "bloom_level": "remember",
                        "objective": "Students will be able to define the concept of a queue in data structures.",
                        "action_verb": "define",
                        "content": "the concept of a queue",
                        "condition": "when prompted during a class discussion",
                        "criteria": "by accurately stating the core characteristics of a queue"
                    },
                    {
                        "bloom_level": "understand",
                        "objective": "Students will be able to explain how a queue operates using real-world examples.",
                        "action_verb": "explain",
                        "content": "how a queue operates",
                        "condition": "using real-world examples in a group activity",
                        "criteria": "by providing at least two examples illustrating queue operations"
                    }
                ],
                "gagne_events": [
                    {
                        "event_number": 1,
                        "event_name": "Gain Attention",
                        "description": "Capture student interest and focus attention on the lesson",
                        "activities": ["Show real-world example of queue"],
                        "duration_minutes": 5
                    },
                    {
                        "event_number": 2,
                        "event_name": "Inform Learners of Objectives",
                        "description": "Tell students what they will learn",
                        "activities": ["Present learning objectives"],
                        "duration_minutes": 5
                    }
                ],
                "lesson_plan": {
                    "title": "Introduction to Queues",
                    "overview": "This lesson introduces the concept of queues in data structures."
                }
            },
            "presentation_preferences": {
                "style": "balanced",
                "slide_duration": "balanced"
            },
            "accessibility_requirements": ["alt_text", "keyboard_navigation"],
            "target_audience_needs": [],
            "technology_constraints": None,
            "slide_duration_preference": "balanced"
        }
        
        print("✅ Frontend request structure created")
        print(f"✅ Lesson data keys: {list(frontend_request['lesson_data'].keys())}")
        
        # Test Pydantic validation
        try:
            request = CourseContentRequest(**frontend_request)
            print("✅ Pydantic validation passed")
        except Exception as e:
            print(f"❌ Pydantic validation failed: {e}")
            return
        
        # Test service with validated request
        service = UDLContentService()
        print("✅ UDLContentService created")
        
        print("🔄 Starting course content generation...")
        result = await service.generate_course_content(request)
        
        print("✅ Course content generation completed successfully!")
        print(f"✅ Generated {result.total_slides} slides")
        print(f"✅ Estimated duration: {result.estimated_duration} minutes")
        print(f"✅ UDL compliance: {result.udl_compliance_report['overall_compliance']:.2%}")
        
    except Exception as e:
        print(f"❌ Error during real request test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_request()) 