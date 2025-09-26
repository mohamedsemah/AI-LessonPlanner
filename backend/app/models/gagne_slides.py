from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class SlideContentType(str, Enum):
    """Types of slide content"""
    INTRODUCTION = "introduction"
    CONCEPT_EXPLANATION = "concept_explanation"
    ACTIVITY_GUIDE = "activity_guide"
    ASSESSMENT = "assessment"
    REFLECTION = "reflection"
    MIXED = "mixed"


class VisualElementType(str, Enum):
    """Types of visual elements"""
    IMAGE = "image"
    DIAGRAM = "diagram"
    CHART = "chart"
    VIDEO = "video"
    ANIMATION = "animation"
    INTERACTIVE = "interactive"
    CODE_SNIPPET = "code_snippet"


class VisualElement(BaseModel):
    """Visual element for slides"""
    type: VisualElementType
    url: str
    alt_text: str
    description: str
    position: Optional[str] = "center"  # "left", "center", "right", "background"
    size: Optional[str] = "medium"  # "small", "medium", "large", "full"
    caption: Optional[str] = None


class SlideContent(BaseModel):
    """Individual slide content with educational materials"""
    slide_number: int
    title: str
    content_type: SlideContentType
    main_content: str  # Markdown formatted content
    visual_elements: List[VisualElement] = Field(default_factory=list)
    audio_script: Optional[str] = None
    speaker_notes: Optional[str] = None
    duration_minutes: float
    learning_objectives: List[str] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)
    materials_needed: List[str] = Field(default_factory=list)
    assessment_criteria: Optional[str] = None
    accessibility_features: List[str] = Field(default_factory=list)
    udl_guidelines: List[str] = Field(default_factory=list)
    difficulty_level: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    estimated_reading_time: Optional[int] = None  # in minutes
    
    # Enhancement properties
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    heading_color: Optional[str] = None
    accent_color: Optional[str] = None
    font_family: Optional[str] = None
    font_size: Optional[str] = None
    heading_font_size: Optional[str] = None
    line_height: Optional[str] = None
    text_align: Optional[str] = None
    heading_align: Optional[str] = None
    content_align: Optional[str] = None
    padding: Optional[str] = None
    margin_top: Optional[str] = None
    margin_bottom: Optional[str] = None
    margin_left: Optional[str] = None
    margin_right: Optional[str] = None
    section_spacing: Optional[str] = None
    paragraph_spacing: Optional[str] = None
    element_grouping: Optional[bool] = None
    white_space_ratio: Optional[float] = None
    grid_columns: Optional[str] = None
    grid_gap: Optional[str] = None
    bullet_style: Optional[str] = None
    numbering_style: Optional[str] = None
    margin_between_sections: Optional[str] = None
    margin_between_elements: Optional[str] = None
    padding_around_groups: Optional[str] = None
    content_padding: Optional[str] = None
    element_spacing: Optional[str] = None


class GagneEventSlides(BaseModel):
    """Slides for a specific Gagne event"""
    event_number: int
    event_name: str
    event_description: str
    total_slides: int
    estimated_duration: float  # Total duration for all slides in this event
    slides: List[SlideContent]
    teaching_strategies: List[str] = Field(default_factory=list)
    learning_outcomes: List[str] = Field(default_factory=list)
    materials_summary: List[str] = Field(default_factory=list)
    assessment_notes: Optional[str] = None


class GagneSlidesResponse(BaseModel):
    """Complete response with slides for all Gagne events"""
    lesson_info: Dict[str, Any]
    total_events: int
    total_slides: int
    total_duration: float
    events: List[GagneEventSlides]
    generation_metadata: Dict[str, Any]
    created_at: str


class SlideGenerationRequest(BaseModel):
    """Request for generating slides for a specific event"""
    event_number: int
    event_name: str
    event_description: str
    activities: List[str]
    duration_minutes: int
    materials_needed: List[str]
    assessment_strategy: Optional[str]
    lesson_context: Dict[str, Any]  # Course title, topic, grade level, etc.
    objectives: List[Dict[str, Any]]
    slide_preferences: Optional[Dict[str, Any]] = None


class SlideRefinementRequest(BaseModel):
    """Request for refining specific slide content"""
    event_number: int
    slide_number: int
    refinement_type: Literal["content", "visuals", "activities", "assessment", "accessibility"]
    refinement_instructions: str
    current_slide: SlideContent


class SlideExportRequest(BaseModel):
    """Request for exporting slides"""
    event_numbers: List[int]  # Which events to export
    format: Literal["pdf", "pptx", "html"]
    include_notes: bool = True
    include_visuals: bool = True
    custom_styling: Optional[Dict[str, Any]] = None
