from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class UDLPrinciple(str, Enum):
    REPRESENTATION = "representation"
    ACTION_EXPRESSION = "action_expression"
    ENGAGEMENT = "engagement"


class ContentModality(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    TEXTUAL = "textual"
    INTERACTIVE = "interactive"


class SlideContent(BaseModel):
    slide_number: int
    title: str
    content: str  # Changed from main_content
    gagne_event: int = 0
    gagne_event_name: str = "Unknown"
    duration_minutes: float = 5.0
    content_modality: str = "mixed"  # Changed from content_type
    visual_elements: List[Dict[str, Any]] = Field(default_factory=list)
    audio_script: Optional[str] = None
    speaker_notes: Optional[str] = None  # Added new field
    udl_guidelines: List[str] = Field(default_factory=list)
    accessibility_features: List[str] = Field(default_factory=list)
    generated_image: Optional[str] = None  # Added for AI-generated images


class UDLGuideline(BaseModel):
    principle: UDLPrinciple
    guideline_number: int
    guideline_name: str
    description: str
    implementation_strategies: List[str]
    content_modalities: List[ContentModality]


class CourseContentRequest(BaseModel):
    lesson_data: Dict[str, Any]  # The generated lesson plan
    presentation_preferences: Dict[str, Any] = Field(default_factory=dict)
    accessibility_requirements: List[str] = Field(default_factory=list)
    target_audience_needs: List[str] = Field(default_factory=list)
    technology_constraints: Optional[str] = None
    slide_duration_preference: Literal["detailed", "concise", "balanced"] = "balanced"


class CourseContentResponse(BaseModel):
    presentation_title: str
    total_slides: int
    estimated_duration: int
    slides: List[SlideContent]
    udl_compliance_report: Dict[str, Any]
    accessibility_features: List[str]
    export_formats: List[str]
    created_at: str


class ContentRefinementRequest(BaseModel):
    slide_id: int
    refinement_type: Literal["content", "accessibility", "modality", "udl_guidelines"]
    refinement_instructions: str
    current_content: Dict[str, Any]


class UDLComplianceReport(BaseModel):
    representation_score: float
    action_expression_score: float
    engagement_score: float
    overall_compliance: float
    missing_guidelines: List[str]
    recommendations: List[str]
    accessibility_features_implemented: List[str] 