from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class GradeLevel(str, Enum):
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"
    MASTERS = "masters"
    POSTGRAD = "postgrad"


class BloomLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class LessonObjective(BaseModel):
    bloom_level: BloomLevel
    objective: str
    action_verb: str
    content: str
    condition: Optional[str] = None
    criteria: Optional[str] = None


class GagneEvent(BaseModel):
    event_number: int
    event_name: str
    description: str
    activities: List[str]
    duration_minutes: int
    materials_needed: List[str]
    assessment_strategy: Optional[str] = None


class LessonRequest(BaseModel):
    course_title: str = Field(..., min_length=1, max_length=200)
    lesson_topic: str = Field(..., min_length=1, max_length=200)
    grade_level: GradeLevel
    duration_minutes: int = Field(..., gt=0, le=480)  # Max 8 hours
    uploaded_files: List[Dict[str, Any]] = Field(..., min_items=1, max_items=5)  # File data from frontend
    selected_bloom_levels: List[BloomLevel] = Field(..., min_items=1)
    additional_requirements: Optional[str] = Field(None, max_length=500)


class RefineRequest(BaseModel):
    section_type: str = Field(..., pattern="^(objectives|lesson_plan|gagne_events|duration_change)$")
    section_content: str = Field(..., min_length=1)
    refinement_instructions: str = Field(..., min_length=1, max_length=500)
    lesson_context: Dict[str, Any]


class LessonPlan(BaseModel):
    title: str
    overview: str
    prerequisites: List[str]
    materials: List[str]
    technology_requirements: List[str]
    assessment_methods: List[str]
    differentiation_strategies: List[str]
    closure_activities: List[str]


class LessonResponse(BaseModel):
    lesson_info: Dict[str, Any]
    objectives: List[LessonObjective]
    lesson_plan: LessonPlan
    gagne_events: List[GagneEvent]
    total_duration: int
    created_at: str


class PDFRequest(BaseModel):
    lesson_data: LessonResponse
    include_cover_page: bool = True
    include_appendices: bool = True


class DurationChangeRequest(BaseModel):
    """Model for duration change requests"""
    current_duration: int = Field(..., gt=0, le=480)
    new_duration: int = Field(..., gt=0, le=480)
    gagne_events: List[GagneEvent]
    lesson_plan: LessonPlan