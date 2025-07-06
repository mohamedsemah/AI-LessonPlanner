from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import asyncio
import json
import io

from ..models.lesson import LessonRequest, LessonResponse, RefineRequest, PDFRequest
from ..services.openai_service import OpenAIService
from ..services.pdf_service import PDFService

router = APIRouter(prefix="/api/lesson", tags=["lesson"])


# Dependency injection
def get_openai_service() -> OpenAIService:
    return OpenAIService()


def get_pdf_service() -> PDFService:
    return PDFService()


@router.post("/generate", response_model=LessonResponse)
async def generate_lesson(
        request: LessonRequest,
        openai_service: OpenAIService = Depends(get_openai_service)
) -> LessonResponse:
    """Generate a complete lesson plan with objectives and Gagne events"""
    try:
        lesson_response = await openai_service.generate_lesson_content(request)
        return lesson_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate lesson: {str(e)}")


@router.post("/refine")
async def refine_content(
        request: RefineRequest,
        openai_service: OpenAIService = Depends(get_openai_service)
) -> Dict[str, Any]:
    """Refine specific sections of the lesson content"""
    try:
        refined_content = await openai_service.refine_content(request)
        return refined_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine content: {str(e)}")


@router.post("/export/pdf")
async def export_pdf(
        request: PDFRequest,
        pdf_service: PDFService = Depends(get_pdf_service)
):
    """Export lesson plan to PDF format"""
    try:
        pdf_buffer = pdf_service.generate_pdf(request)

        # Generate filename based on lesson info
        lesson_info = request.lesson_data.lesson_info
        filename = f"{lesson_info['course_title']}_{lesson_info['lesson_topic']}.pdf"
        filename = filename.replace(" ", "_").replace("/", "_")

        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.get("/bloom-levels")
async def get_bloom_levels() -> Dict[str, Any]:
    """Get available Bloom's taxonomy levels with descriptions"""
    bloom_levels = {
        "remember": {
            "name": "Remember",
            "description": "Recall facts, basic concepts, and answers",
            "verbs": ["define", "list", "recall", "identify", "describe", "retrieve"]
        },
        "understand": {
            "name": "Understand",
            "description": "Explain ideas or concepts and interpret information",
            "verbs": ["explain", "interpret", "summarize", "classify", "compare", "discuss"]
        },
        "apply": {
            "name": "Apply",
            "description": "Use information in new situations and solve problems",
            "verbs": ["use", "demonstrate", "implement", "solve", "execute", "carry out"]
        },
        "analyze": {
            "name": "Analyze",
            "description": "Draw connections and distinguish between different parts",
            "verbs": ["analyze", "break down", "examine", "compare", "contrast", "investigate"]
        },
        "evaluate": {
            "name": "Evaluate",
            "description": "Justify decisions and critique work or ideas",
            "verbs": ["evaluate", "critique", "judge", "assess", "defend", "justify"]
        },
        "create": {
            "name": "Create",
            "description": "Produce new or original work and combine ideas",
            "verbs": ["create", "design", "construct", "develop", "formulate", "produce"]
        }
    }
    return {"bloom_levels": bloom_levels}


@router.get("/gagne-events")
async def get_gagne_events() -> Dict[str, Any]:
    """Get information about Gagne's Nine Events of Instruction"""
    gagne_events = {
        1: {
            "name": "Gain Attention",
            "description": "Capture student interest and focus attention on the lesson",
            "strategies": ["Ask thought-provoking questions", "Share interesting facts", "Use multimedia",
                           "Tell a story"]
        },
        2: {
            "name": "Inform Learners of Objectives",
            "description": "Share learning goals and explain their relevance",
            "strategies": ["Present clear objectives", "Explain benefits", "Connect to student goals",
                           "Provide learning roadmap"]
        },
        3: {
            "name": "Stimulate Recall of Prior Learning",
            "description": "Connect new content to existing knowledge",
            "strategies": ["Review prerequisites", "Ask about experiences", "Use analogies", "Activate schema"]
        },
        4: {
            "name": "Present the Content",
            "description": "Deliver new information and concepts",
            "strategies": ["Structured presentation", "Multiple examples", "Visual aids", "Clear organization"]
        },
        5: {
            "name": "Provide Learning Guidance",
            "description": "Guide students through the learning process",
            "strategies": ["Provide hints", "Model procedures", "Use mnemonics", "Offer coaching"]
        },
        6: {
            "name": "Elicit Performance",
            "description": "Have students practice and demonstrate learning",
            "strategies": ["Practice exercises", "Problem solving", "Simulations", "Hands-on activities"]
        },
        7: {
            "name": "Provide Feedback",
            "description": "Give informative feedback on performance",
            "strategies": ["Immediate feedback", "Corrective guidance", "Positive reinforcement", "Specific comments"]
        },
        8: {
            "name": "Assess Performance",
            "description": "Evaluate student learning and understanding",
            "strategies": ["Formal tests", "Observations", "Portfolios", "Self-assessment"]
        },
        9: {
            "name": "Enhance Retention and Transfer",
            "description": "Promote long-term retention and application",
            "strategies": ["Real-world applications", "Summary activities", "Reflection", "Future connections"]
        }
    }
    return {"gagne_events": gagne_events}


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "lesson-planning-api"}