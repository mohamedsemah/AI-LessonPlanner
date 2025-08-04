#!/usr/bin/env python3

import sys
import os
import asyncio
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_frontend_request():
    try:
        # Simulate the exact request that the frontend sends
        request_data = {
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
        
        print("🔄 Testing UDL content generation endpoint...")
        print(f"📤 Request data keys: {list(request_data.keys())}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/udl-content/generate",
                json=request_data,
                timeout=120.0
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ UDL content generation successful!")
                print(f"✅ Generated {result.get('total_slides', 0)} slides")
                print(f"✅ Estimated duration: {result.get('estimated_duration', 0)} minutes")
            else:
                print(f"❌ UDL content generation failed: {response.status_code}")
                print(f"❌ Error details: {response.text}")
                
    except Exception as e:
        print(f"❌ Error testing frontend request: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_frontend_request()) 