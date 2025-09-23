"""
Accessibility Content Models for Multi-Agent Lesson Planning System

This module contains Pydantic models for accessibility-related data structures:
- AccessibilityComplianceReport: Comprehensive WCAG 2.2 compliance assessment
- WCAGPrinciple: Individual WCAG principle validation
- AccessibilityRecommendation: Specific accessibility improvement recommendations
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class WCAGPrincipleType(str, Enum):
    """WCAG 2.2 principle types"""
    PERCEIVABLE = "perceivable"
    OPERABLE = "operable"
    UNDERSTANDABLE = "understandable"
    ROBUST = "robust"


class WCAGLevel(str, Enum):
    """WCAG compliance levels"""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class AccessibilityComplianceLevel(str, Enum):
    """Accessibility compliance levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class AccessibilityRecommendationPriority(str, Enum):
    """Priority levels for accessibility recommendations"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"


class WCAGPrinciple(BaseModel):
    """Individual WCAG principle validation result"""
    principle: WCAGPrincipleType
    score: float = Field(..., ge=0.0, le=1.0, description="Score from 0.0 to 1.0")
    status: AccessibilityComplianceLevel
    details: str
    violations: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    success_criteria: List[Dict[str, Any]] = Field(default_factory=list)


class AccessibilityRecommendation(BaseModel):
    """Specific accessibility improvement recommendation"""
    principle: WCAGPrincipleType
    recommendation: str
    priority: AccessibilityRecommendationPriority
    wcag_level: WCAGLevel
    impact: str = Field(..., description="Expected impact of implementing this recommendation")
    effort: Literal["low", "medium", "high"] = Field(..., description="Implementation effort required")
    examples: List[str] = Field(default_factory=list, description="Specific examples or suggestions")
    success_criteria: List[str] = Field(default_factory=list, description="Related WCAG success criteria")


class AccessibilityComplianceReport(BaseModel):
    """Comprehensive WCAG 2.2 accessibility compliance assessment report"""
    perceivable_score: float = Field(..., ge=0.0, le=1.0)
    operable_score: float = Field(..., ge=0.0, le=1.0)
    understandable_score: float = Field(..., ge=0.0, le=1.0)
    robust_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    wcag_level: WCAGLevel = WCAGLevel.AA
    principles: Dict[str, WCAGPrinciple] = Field(default_factory=dict)
    recommendations: List[AccessibilityRecommendation] = Field(default_factory=list)
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessibilityValidationRequest(BaseModel):
    """Request for accessibility validation"""
    slides: List[Dict[str, Any]] = Field(..., description="Slides to validate")
    accessibility_level: WCAGLevel = WCAGLevel.AA
    validation_preferences: Dict[str, Any] = Field(default_factory=dict)
    target_audience: Optional[str] = None
    assistive_technologies: List[str] = Field(default_factory=list)


class AccessibilityValidationResponse(BaseModel):
    """Response from accessibility validation"""
    compliance_report: AccessibilityComplianceReport
    recommendations: List[AccessibilityRecommendation]
    violations: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time: Optional[float] = None
    agent_version: str = "1.0.0"
