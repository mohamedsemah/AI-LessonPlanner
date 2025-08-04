#!/usr/bin/env python3

import sys
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_udl_api():
    try:
        from app.services.udl_content_service import UDLContentService
        from app.models.udl_content import CourseContentRequest
        
        print("✅ UDLContentService imported successfully")
        
        # Create service
        service = UDLContentService()
        print("✅ UDLContentService instantiated successfully")
        
        # Create a sample request (similar to what the frontend sends)
        sample_lesson_data = {
            "lesson_info": {
                "course_title": "Computer Science",
                "lesson_topic": "Data Structures",
                "grade_level": "College",
                "duration_minutes": 60
            },
            "objectives": [
                {
                    "bloom_level": "understand",
                    "objective": "Students will understand basic data structures",
                    "action_verb": "understand",
                    "content": "basic data structures",
                    "condition": "through examples",
                    "criteria": "by explaining concepts"
                }
            ],
            "gagne_events": [
                {
                    "event_number": 1,
                    "event_name": "Gain Attention",
                    "description": "Capture student interest",
                    "activities": ["Show real-world example"],
                    "duration_minutes": 5
                },
                {
                    "event_number": 2,
                    "event_name": "Inform Learners of Objectives",
                    "description": "Tell students what they will learn",
                    "activities": ["Present learning objectives"],
                    "duration_minutes": 5
                }
            ]
        }
        
        request = CourseContentRequest(
            lesson_data=sample_lesson_data,
            presentation_preferences={},
            accessibility_requirements=["alt_text", "keyboard_navigation"],
            target_audience_needs=[],
            technology_constraints=None,
            slide_duration_preference="balanced"
        )
        
        print("✅ Sample request created successfully")
        print(f"✅ Request contains {len(sample_lesson_data['gagne_events'])} Gagne events")
        
        # Test the actual generation method
        print("🔄 Starting course content generation...")
        result = await service.generate_course_content(request)
        
        print("✅ Course content generation completed successfully!")
        print(f"✅ Generated {result.total_slides} slides")
        print(f"✅ Estimated duration: {result.estimated_duration} minutes")
        print(f"✅ UDL compliance: {result.udl_compliance_report['overall_compliance']:.2%}")
        
    except Exception as e:
        print(f"❌ Error during API test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_udl_api()) 