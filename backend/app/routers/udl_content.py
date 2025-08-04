from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import io
import logging
import traceback

from ..models.udl_content import CourseContentRequest, CourseContentResponse, ContentRefinementRequest
from ..services.udl_content_service import UDLContentService
from ..services.export_service import ExportService

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/udl-content", tags=["UDL Content"])


# Dependency injection
def get_udl_content_service() -> UDLContentService:
    """Dependency to get UDL content service"""
    logger.info("Creating UDLContentService dependency...")
    try:
        service = UDLContentService()
        logger.info("UDLContentService initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize UDLContentService: {e}")
        raise HTTPException(status_code=500, detail="Service initialization failed")

def get_export_service() -> ExportService:
    """Dependency to get export service"""
    try:
        return ExportService()
    except Exception as e:
        logger.error(f"Failed to initialize ExportService: {e}")
        raise HTTPException(status_code=500, detail="Export service initialization failed")


@router.post("/generate")
async def generate_course_content(
    request: CourseContentRequest,
    udl_service: UDLContentService = Depends(get_udl_content_service)
) -> CourseContentResponse:
    """Generate UDL-compliant course content based on lesson plan"""
    logger.info("=== UDL CONTENT GENERATION START ===")
    try:
        logger.info("Received course content generation request")
        logger.info(f"Request data: lesson_data keys: {list(request.lesson_data.keys())}")
        
        lesson_info = request.lesson_data.get("lesson_info", {})
        logger.info(f"Lesson info: {lesson_info.get('lesson_topic', 'Unknown')}")
        
        objectives = request.lesson_data.get("objectives", [])
        logger.info(f"Objectives count: {len(objectives)}")
        
        gagne_events = request.lesson_data.get("gagne_events", [])
        logger.info(f"Gagne events count: {len(gagne_events)}")
        
        logger.info("Calling UDL service generate_course_content...")
        result = await udl_service.generate_course_content(request)
        logger.info("UDL service returned successfully")
        
        logger.info("Course content generation completed successfully")
        logger.info("=== UDL CONTENT GENERATION END ===")
        
        return result
    except Exception as e:
        logger.error(f"Error in generate_course_content: {str(e)}")
        if hasattr(e, '__traceback__'):
            logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate course content: {str(e)}")

@router.post("/refine")
async def refine_content(
    request: ContentRefinementRequest,
    udl_service: UDLContentService = Depends(get_udl_content_service)
) -> Dict[str, Any]:
    """Refine specific slide content"""
    try:
        result = await udl_service.refine_content(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine content: {str(e)}")

@router.get("/guidelines")
async def get_udl_guidelines() -> Dict[str, Any]:
    """Get UDL guidelines and principles"""
    try:
        service = UDLContentService()
        return service.get_udl_guidelines()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get UDL guidelines: {str(e)}")

@router.get("/modalities")
async def get_content_modalities() -> Dict[str, Any]:
    """Get available content modalities"""
    try:
        service = UDLContentService()
        return service.get_content_modalities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content modalities: {str(e)}")

@router.get("/accessibility")
async def get_accessibility_features() -> Dict[str, Any]:
    """Get available accessibility features"""
    try:
        service = UDLContentService()
        return service.get_accessibility_features()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get accessibility features: {str(e)}")

@router.post("/export/pptx")
async def export_powerpoint(
    request: Dict[str, Any],
    export_service: ExportService = Depends(get_export_service)
):
    """Export course content to PowerPoint format"""
    try:
        logger.info("Starting PowerPoint export")
        
        # Extract course content data
        course_content = request.get("course_content")
        lesson_data = request.get("lesson_data", {})
        
        if not course_content:
            raise HTTPException(status_code=400, detail="Course content is required")
        
        # Generate PowerPoint file
        pptx_buffer = await export_service.export_to_powerpoint(course_content, lesson_data)
        
        # Generate filename
        lesson_info = lesson_data.get("lesson_info", {})
        filename = f"{lesson_info.get('course_title', 'Course')}_{lesson_info.get('lesson_topic', 'Lesson')}.pptx"
        filename = filename.replace(" ", "_").replace("/", "_")
        
        logger.info(f"PowerPoint export completed: {filename}")
        
        return StreamingResponse(
            io.BytesIO(pptx_buffer.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"PowerPoint export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export PowerPoint: {str(e)}")

@router.post("/export/pdf")
async def export_pdf(
    request: Dict[str, Any],
    export_service: ExportService = Depends(get_export_service)
):
    """Export course content to PDF format"""
    try:
        logger.info("Starting PDF export")
        
        # Extract course content data
        course_content = request.get("course_content")
        lesson_data = request.get("lesson_data", {})
        
        if not course_content:
            raise HTTPException(status_code=400, detail="Course content is required")
        
        # Generate PDF file
        pdf_buffer = await export_service.export_to_pdf(course_content, lesson_data)
        
        # Generate filename
        lesson_info = lesson_data.get("lesson_info", {})
        filename = f"{lesson_info.get('course_title', 'Course')}_{lesson_info.get('lesson_topic', 'Lesson')}.pdf"
        filename = filename.replace(" ", "_").replace("/", "_")
        
        logger.info(f"PDF export completed: {filename}")
        
        return StreamingResponse(
            io.BytesIO(pdf_buffer.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"PDF export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export PDF: {str(e)}")

@router.post("/export/html")
async def export_html(
    request: Dict[str, Any],
    export_service: ExportService = Depends(get_export_service)
):
    """Export course content to premium HTML format"""
    try:
        logger.info("Starting HTML export")
        
        # Extract course content data
        course_content = request.get("course_content")
        lesson_data = request.get("lesson_data", {})
        
        if not course_content:
            raise HTTPException(status_code=400, detail="Course content is required")
        
        # Generate HTML content
        html_content = export_service.export_to_html(course_content, lesson_data)
        
        # Generate filename
        lesson_info = lesson_data.get("lesson_info", {})
        filename = f"{lesson_info.get('course_title', 'Course')}_{lesson_info.get('lesson_topic', 'Lesson')}.html"
        filename = filename.replace(" ", "_").replace("/", "_")
        
        logger.info(f"HTML export completed: {filename}")
        
        return StreamingResponse(
            io.StringIO(html_content),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"HTML export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export HTML: {str(e)}") 