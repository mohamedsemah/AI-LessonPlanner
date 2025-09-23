"""
Design Content Models for Multi-Agent Lesson Planning System

This module contains Pydantic models for design-related data structures:
- DesignComplianceReport: Comprehensive design compliance assessment
- DesignPrinciple: Individual C.R.A.P. principle validation
- DesignRecommendation: Specific design improvement recommendations
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class DesignPrincipleType(str, Enum):
    """Types of design principles"""
    CONTRAST = "contrast"
    REPETITION = "repetition"
    ALIGNMENT = "alignment"
    PROXIMITY = "proximity"


class DesignComplianceLevel(str, Enum):
    """Design compliance levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class DesignRecommendationPriority(str, Enum):
    """Priority levels for design recommendations"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"


class DesignPrinciple(BaseModel):
    """Individual design principle validation result"""
    principle: DesignPrincipleType
    score: float = Field(..., ge=0.0, le=1.0, description="Score from 0.0 to 1.0")
    status: DesignComplianceLevel
    details: str
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class DesignRecommendation(BaseModel):
    """Specific design improvement recommendation"""
    principle: DesignPrincipleType
    recommendation: str
    priority: DesignRecommendationPriority
    impact: str = Field(..., description="Expected impact of implementing this recommendation")
    effort: Literal["low", "medium", "high"] = Field(..., description="Implementation effort required")
    examples: List[str] = Field(default_factory=list, description="Specific examples or suggestions")


class DesignComplianceReport(BaseModel):
    """Comprehensive design compliance assessment report"""
    contrast_score: float = Field(..., ge=0.0, le=1.0)
    repetition_score: float = Field(..., ge=0.0, le=1.0)
    alignment_score: float = Field(..., ge=0.0, le=1.0)
    proximity_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    validation_level: Literal["basic", "standard", "strict"] = "standard"
    principles: Dict[str, DesignPrinciple] = Field(default_factory=dict)
    recommendations: List[DesignRecommendation] = Field(default_factory=list)
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DesignValidationRequest(BaseModel):
    """Request for design validation"""
    slides: List[Dict[str, Any]] = Field(..., description="Slides to validate")
    design_preferences: Dict[str, Any] = Field(default_factory=dict)
    validation_level: Literal["basic", "standard", "strict"] = "standard"
    target_audience: Optional[str] = None
    brand_guidelines: Optional[Dict[str, Any]] = None


class DesignValidationResponse(BaseModel):
    """Response from design validation"""
    compliance_report: DesignComplianceReport
    recommendations: List[DesignRecommendation]
    violations: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time: Optional[float] = None
    agent_version: str = "1.0.0"
