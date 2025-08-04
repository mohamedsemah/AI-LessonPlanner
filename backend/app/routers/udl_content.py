from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import io
import logging
import traceback

from ..models.udl_content import CourseContentRequest, CourseContentResponse, ContentRefinementRequest
from ..services.udl_content_service import UDLContentService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/udl-content", tags=["udl-content"])


# Dependency injection
def get_udl_content_service() -> UDLContentService:
    try:
        logger.info("Creating UDLContentService dependency...")
        service = UDLContentService()
        logger.info("UDLContentService dependency created successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to create UDLContentService dependency: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Service initialization failed: {str(e)}")


@router.post("/generate", response_model=CourseContentResponse)
async def generate_course_content(
    request: CourseContentRequest,
    udl_service: UDLContentService = Depends(get_udl_content_service)
) -> CourseContentResponse:
    """Generate multimodal course content based on lesson plan with UDL compliance"""
    try:
        logger.info("=== UDL CONTENT GENERATION START ===")
        logger.info("Received course content generation request")
        logger.info(f"Request data: lesson_data keys: {list(request.lesson_data.keys()) if request.lesson_data else 'None'}")
        
        # Log the request structure for debugging
        if request.lesson_data:
            lesson_info = request.lesson_data.get("lesson_info", {})
            objectives = request.lesson_data.get("objectives", [])
            gagne_events = request.lesson_data.get("gagne_events", [])
            
            logger.info(f"Lesson info: {lesson_info.get('course_title', 'Unknown')}")
            logger.info(f"Objectives count: {len(objectives)}")
            logger.info(f"Gagne events count: {len(gagne_events)}")
        
        logger.info("Calling UDL service generate_course_content...")
        course_content = await udl_service.generate_course_content(request)
        logger.info("UDL service returned successfully")
        logger.info("Course content generation completed successfully")
        logger.info("=== UDL CONTENT GENERATION END ===")
        return course_content
    except Exception as e:
        logger.error("=== UDL CONTENT GENERATION ERROR ===")
        logger.error(f"Failed to generate course content: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error args: {e.args}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error("=== UDL CONTENT GENERATION ERROR END ===")
        
        # Return a more detailed error message
        error_detail = f"Failed to generate course content: {str(e)}"
        if hasattr(e, '__traceback__'):
            error_detail += f"\nTraceback: {traceback.format_exc()}"
        
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/refine")
async def refine_content(
    request: ContentRefinementRequest,
    udl_service: UDLContentService = Depends(get_udl_content_service)
) -> Dict[str, Any]:
    """Refine specific slide content based on UDL principles"""
    try:
        logger.info(f"Received content refinement request for slide {request.slide_id}")
        refined_content = await udl_service.refine_content(request.dict())
        logger.info("Content refinement completed successfully")
        return refined_content
    except Exception as e:
        logger.error(f"Failed to refine content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to refine content: {str(e)}")


@router.get("/udl-guidelines")
async def get_udl_guidelines() -> Dict[str, Any]:
    """Get UDL guidelines and implementation strategies"""
    udl_guidelines = {
        "representation": {
            "name": "Provide Multiple Means of Representation",
            "guidelines": {
                "perception": {
                    "name": "Perception",
                    "description": "Offer ways of customizing the display of information",
                    "strategies": [
                        "Provide alternatives for auditory information",
                        "Provide alternatives for visual information",
                        "Customize the display of information"
                    ]
                },
                "language": {
                    "name": "Language & Symbols",
                    "description": "Clarify vocabulary, syntax, and structure",
                    "strategies": [
                        "Clarify vocabulary and symbols",
                        "Clarify syntax and structure",
                        "Support decoding of text and mathematical notation",
                        "Promote understanding across languages"
                    ]
                },
                "comprehension": {
                    "name": "Comprehension",
                    "description": "Help learners make sense of information",
                    "strategies": [
                        "Activate or supply background knowledge",
                        "Highlight patterns, critical features, big ideas, and relationships",
                        "Guide information processing and visualization",
                        "Maximize transfer and generalization"
                    ]
                }
            }
        },
        "action_expression": {
            "name": "Provide Multiple Means of Action & Expression",
            "guidelines": {
                "physical_action": {
                    "name": "Physical Action",
                    "description": "Vary the methods for response and navigation",
                    "strategies": [
                        "Vary the methods for response and navigation",
                        "Optimize access to tools and assistive technologies"
                    ]
                },
                "expression": {
                    "name": "Expression & Communication",
                    "description": "Use multiple media for communication",
                    "strategies": [
                        "Use multiple media for communication",
                        "Build fluencies with graduated levels of support",
                        "Practice with graduated levels of support"
                    ]
                },
                "executive_functions": {
                    "name": "Executive Functions",
                    "description": "Guide appropriate goal-setting and strategy development",
                    "strategies": [
                        "Guide appropriate goal-setting",
                        "Support planning and strategy development",
                        "Facilitate managing information and resources",
                        "Enhance capacity for monitoring progress"
                    ]
                }
            }
        },
        "engagement": {
            "name": "Provide Multiple Means of Engagement",
            "guidelines": {
                "recruiting_interest": {
                    "name": "Recruiting Interest",
                    "description": "Optimize individual choice and autonomy",
                    "strategies": [
                        "Optimize individual choice and autonomy",
                        "Optimize relevance, value, and authenticity",
                        "Minimize threats and distractions"
                    ]
                },
                "sustaining_effort": {
                    "name": "Sustaining Effort & Persistence",
                    "description": "Help learners maintain effort and motivation",
                    "strategies": [
                        "Heighten salience of goals and objectives",
                        "Vary demands and resources to optimize challenge",
                        "Foster collaboration and community",
                        "Increase mastery-oriented feedback"
                    ]
                },
                "self_regulation": {
                    "name": "Self-Regulation",
                    "description": "Help learners develop self-assessment and reflection",
                    "strategies": [
                        "Guide personal goal-setting and expectations",
                        "Scaffold coping skills and strategies",
                        "Develop self-assessment and reflection"
                    ]
                }
            }
        }
    }
    return {"udl_guidelines": udl_guidelines}


@router.get("/content-modalities")
async def get_content_modalities() -> Dict[str, Any]:
    """Get available content modalities for multimodal learning"""
    modalities = {
        "visual": {
            "name": "Visual",
            "description": "Content that can be seen and processed visually",
            "examples": ["Images", "Diagrams", "Charts", "Videos", "Animations"],
            "accessibility_features": ["Alt text", "High contrast", "Large fonts", "Color coding"]
        },
        "auditory": {
            "name": "Auditory",
            "description": "Content that can be heard and processed aurally",
            "examples": ["Audio narration", "Podcasts", "Music", "Sound effects"],
            "accessibility_features": ["Transcripts", "Captions", "Audio descriptions", "Volume control"]
        },
        "textual": {
            "name": "Textual",
            "description": "Written content that can be read",
            "examples": ["Text", "Documents", "Articles", "Notes"],
            "accessibility_features": ["Screen readers", "Text-to-speech", "Font size adjustment", "Line spacing"]
        },
        "kinesthetic": {
            "name": "Kinesthetic",
            "description": "Content that involves physical movement and interaction",
            "examples": ["Hands-on activities", "Simulations", "Interactive exercises"],
            "accessibility_features": ["Alternative input methods", "Assistive technologies", "Physical accommodations"]
        },
        "interactive": {
            "name": "Interactive",
            "description": "Content that responds to user input and engagement",
            "examples": ["Quizzes", "Games", "Simulations", "Virtual labs"],
            "accessibility_features": ["Keyboard navigation", "Voice control", "Alternative input devices"]
        }
    }
    return {"content_modalities": modalities}


@router.get("/accessibility-features")
async def get_accessibility_features() -> Dict[str, Any]:
    """Get available accessibility features for course content"""
    features = {
        "visual_accessibility": [
            "Alt text for images",
            "High contrast mode",
            "Large font options",
            "Color-blind friendly palettes",
            "Screen reader compatibility"
        ],
        "auditory_accessibility": [
            "Closed captions",
            "Audio transcripts",
            "Audio descriptions",
            "Volume controls",
            "Background noise reduction"
        ],
        "cognitive_accessibility": [
            "Clear navigation",
            "Consistent layout",
            "Simple language",
            "Step-by-step instructions",
            "Progress indicators"
        ],
        "physical_accessibility": [
            "Keyboard navigation",
            "Voice control support",
            "Alternative input devices",
            "Adjustable timing",
            "Physical accommodation options"
        ]
    }
    return {"accessibility_features": features}


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for UDL content service"""
    return {"status": "healthy", "service": "udl-content-service"} 