"""
Multi-Agent System for Lesson Planning and Content Generation

This module contains the core agents responsible for different aspects of lesson planning:
- PlanAgent: Generates learning objectives, lesson plans, and Gagne events
- ContentAgent: Creates teaching slides and multimodal content
- UDLAgent: Validates Universal Design for Learning compliance
- DesignAgent: Validates C.R.A.P. design principles (Contrast, Repetition, Alignment, Proximity)
- AccessibilityAgent: Validates technical accessibility compliance (WCAG 2.2 standards)
- CoordinatorAgent: Orchestrates all agents in the lesson generation process

The agents work together to create comprehensive, pedagogically sound lesson plans
with multimodal content that adheres to educational best practices and design standards.
"""

from .base_agent import BaseAgent
from .coordinator_agent import CoordinatorAgent
from .plan_agent import PlanAgent
from .content_agent import ContentAgent
from .udl_agent import UDLAgent
from .design_agent import DesignAgent
from .accessibility_agent import AccessibilityAgent

__all__ = [
    'BaseAgent',
    'CoordinatorAgent', 
    'PlanAgent',
    'ContentAgent',
    'UDLAgent',
    'DesignAgent',
    'AccessibilityAgent'
]

__version__ = '1.0.0'
