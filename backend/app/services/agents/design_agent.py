import logging
import re
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from .base_agent import BaseAgent
from ...models.gagne_slides import SlideContent
from ...models.design_content import (
    DesignComplianceReport, DesignPrinciple, DesignRecommendation,
    DesignPrincipleType, DesignComplianceLevel, DesignRecommendationPriority
)

logger = logging.getLogger(__name__)

class DesignAgent(BaseAgent):
    """
    Design Agent for Multi-Agent Lesson Planning System.
    Validates slide designs against C.R.A.P. principles:
    - Contrast: Color contrast, text readability
    - Repetition: Consistent design elements
    - Alignment: Visual alignment and structure
    - Proximity: Logical grouping of related elements
    """
    
    def __init__(self, client: AsyncOpenAI):
        """Initialize the Design Agent."""
        super().__init__(client)
        self.logger = logging.getLogger(f"agents.{self.__class__.__name__}")
        self.crap_guidelines = self._initialize_crap_guidelines()
    
    def _initialize_crap_guidelines(self) -> Dict[str, Any]:
        """Initialize C.R.A.P. design principles guidelines."""
        return {
            "contrast": {
                "color_contrast_ratio": 4.5,  # WCAG AA standard
                "large_text_ratio": 3.0,     # WCAG AA for large text
                "color_combinations": {
                    "good": [
                        ("#000000", "#FFFFFF"),  # Black on white
                        ("#000000", "#FFFF00"),  # Black on yellow
                        ("#FFFFFF", "#0000FF"),  # White on blue
                        ("#000000", "#00FF00"),  # Black on green
                    ],
                    "bad": [
                        ("#808080", "#FFFFFF"),  # Gray on white
                        ("#FF0000", "#0000FF"),  # Red on blue
                        ("#FFFF00", "#FFFFFF"),  # Yellow on white
                    ]
                },
                "font_size_minimum": 12,
                "heading_hierarchy": ["h1", "h2", "h3", "h4", "h5", "h6"]
            },
            "repetition": {
                "consistent_elements": [
                    "font_family", "font_size", "color_scheme", 
                    "spacing", "bullet_style", "heading_style"
                ],
                "brand_consistency": True,
                "template_usage": True
            },
            "alignment": {
                "text_alignment": "left",  # or "center", "right", "justify"
                "element_alignment": "grid",
                "margin_consistency": True,
                "visual_hierarchy": True
            },
            "proximity": {
                "related_elements_grouped": True,
                "white_space_usage": "appropriate",
                "logical_grouping": True,
                "content_flow": "natural"
            }
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process design validation request.
        
        Args:
            input_data: Dictionary containing:
                - slides: List of SlideContent objects or dictionaries
                - design_preferences: Optional design preferences
                - validation_level: "basic", "standard", "strict"
                
        Returns:
            Dictionary containing:
                - design_compliance_report: DesignComplianceReport object
                - recommendations: List of design improvement recommendations
                - violations: List of specific design violations
                - metadata: Processing metadata
        """
        try:
            slides = input_data.get("slides", [])
            design_preferences = input_data.get("design_preferences", {})
            validation_level = input_data.get("validation_level", "standard")
            
            if not slides:
                raise ValueError("slides are required for design validation")
            
            # Convert slides to dictionaries if they are objects
            slide_dicts = []
            for slide in slides:
                if isinstance(slide, dict):
                    slide_dicts.append(slide)
                else:
                    slide_dicts.append(slide.dict())
            
            self._log_processing_start(f"Validating design compliance for {len(slide_dicts)} slides")
            
            # Validate C.R.A.P. principles
            design_compliance_report = await self._validate_crap_principles(slide_dicts, validation_level)
            
            # Generate design recommendations
            recommendations = self._generate_design_recommendations(slide_dicts, design_compliance_report)
            
            # Extract specific violations
            violations = self._extract_design_violations(slide_dicts, design_compliance_report)
            
            result = {
                "design_compliance_report": design_compliance_report,
                "recommendations": recommendations,
                "violations": violations,
                "metadata": {
                    "total_slides": len(slide_dicts),
                    "validation_level": validation_level,
                    "principles_checked": list(self.crap_guidelines.keys())
                }
            }
            
            self._log_processing_success(f"Design validation completed - Overall score: {design_compliance_report.overall_score:.2f}")
            return self._create_success_response(result)
            
        except Exception as e:
            self._log_processing_error(e)
            return self._create_error_response(e)
    
    async def _validate_crap_principles(self, slides: List[Dict[str, Any]], validation_level: str) -> DesignComplianceReport:
        """Validate slides against C.R.A.P. principles."""
        try:
            contrast_score = await self._validate_contrast(slides, validation_level)
            repetition_score = await self._validate_repetition(slides, validation_level)
            alignment_score = await self._validate_alignment(slides, validation_level)
            proximity_score = await self._validate_proximity(slides, validation_level)
            
            # Calculate overall score
            overall_score = (contrast_score + repetition_score + alignment_score + proximity_score) / 4
            
            # Create principle objects
            principles = {
                "contrast": DesignPrinciple(
                    principle=DesignPrincipleType.CONTRAST,
                    score=contrast_score,
                    status=DesignComplianceLevel.EXCELLENT if contrast_score >= 0.8 else 
                           DesignComplianceLevel.GOOD if contrast_score >= 0.6 else
                           DesignComplianceLevel.FAIR if contrast_score >= 0.4 else
                           DesignComplianceLevel.POOR,
                    details="Color contrast and readability validation",
                    violations=[] if contrast_score >= 0.7 else ["Insufficient color contrast"],
                    recommendations=[] if contrast_score >= 0.7 else ["Improve color contrast ratios"]
                ),
                "repetition": DesignPrinciple(
                    principle=DesignPrincipleType.REPETITION,
                    score=repetition_score,
                    status=DesignComplianceLevel.EXCELLENT if repetition_score >= 0.8 else 
                           DesignComplianceLevel.GOOD if repetition_score >= 0.6 else
                           DesignComplianceLevel.FAIR if repetition_score >= 0.4 else
                           DesignComplianceLevel.POOR,
                    details="Consistent design elements validation",
                    violations=[] if repetition_score >= 0.7 else ["Inconsistent design elements"],
                    recommendations=[] if repetition_score >= 0.7 else ["Establish consistent design patterns"]
                ),
                "alignment": DesignPrinciple(
                    principle=DesignPrincipleType.ALIGNMENT,
                    score=alignment_score,
                    status=DesignComplianceLevel.EXCELLENT if alignment_score >= 0.8 else 
                           DesignComplianceLevel.GOOD if alignment_score >= 0.6 else
                           DesignComplianceLevel.FAIR if alignment_score >= 0.4 else
                           DesignComplianceLevel.POOR,
                    details="Visual alignment and structure validation",
                    violations=[] if alignment_score >= 0.7 else ["Poor visual alignment"],
                    recommendations=[] if alignment_score >= 0.7 else ["Improve element alignment"]
                ),
                "proximity": DesignPrinciple(
                    principle=DesignPrincipleType.PROXIMITY,
                    score=proximity_score,
                    status=DesignComplianceLevel.EXCELLENT if proximity_score >= 0.8 else 
                           DesignComplianceLevel.GOOD if proximity_score >= 0.6 else
                           DesignComplianceLevel.FAIR if proximity_score >= 0.4 else
                           DesignComplianceLevel.POOR,
                    details="Logical grouping and spacing validation",
                    violations=[] if proximity_score >= 0.7 else ["Poor content grouping"],
                    recommendations=[] if proximity_score >= 0.7 else ["Improve content proximity and grouping"]
                )
            }
            
            return DesignComplianceReport(
                contrast_score=contrast_score,
                repetition_score=repetition_score,
                alignment_score=alignment_score,
                proximity_score=proximity_score,
                overall_score=overall_score,
                validation_level=validation_level,
                principles=principles,
                recommendations=[],
                violations=[],
                metadata={"total_slides": len(slides)}
            )
            
        except Exception as e:
            self.logger.error(f"Error validating C.R.A.P. principles: {str(e)}")
            return DesignComplianceReport(
                contrast_score=0.0,
                repetition_score=0.0,
                alignment_score=0.0,
                proximity_score=0.0,
                overall_score=0.0,
                validation_level=validation_level,
                principles={},
                recommendations=[],
                violations=[],
                metadata={"error": str(e)}
            )
    
    async def _validate_contrast(self, slides: List[Dict[str, Any]], validation_level: str) -> float:
        """Validate contrast principles."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Check text contrast
                main_content = slide.get("main_content", "")
                if main_content:
                    # Simulate contrast check (in real implementation, would analyze actual colors)
                    if len(main_content) > 50:  # Has substantial content
                        slide_score += 0.5
                        checks_passed += 1
                
                # Check font size
                if "font" in str(slide).lower() or "size" in str(slide).lower():
                    slide_score += 0.3
                    checks_passed += 1
                
                # Check heading hierarchy
                title = slide.get("title", "")
                if title and len(title) > 0:
                    slide_score += 0.2
                    checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating contrast: {str(e)}")
            return 0.0
    
    async def _validate_repetition(self, slides: List[Dict[str, Any]], validation_level: str) -> float:
        """Validate repetition principles."""
        try:
            if len(slides) < 2:
                return 1.0  # Single slide is automatically consistent
            
            # Check for consistent elements across slides
            consistency_score = 0.0
            total_checks = 0
            
            # Check title formatting consistency
            title_lengths = [len(slide.get("title", "")) for slide in slides]
            if len(set(title_lengths)) <= 2:  # Similar title lengths
                consistency_score += 0.3
            total_checks += 1
            
            # Check content structure consistency
            content_structures = []
            for slide in slides:
                content = slide.get("main_content", "")
                structure = len(content.split('\n'))  # Number of paragraphs
                content_structures.append(structure)
            
            if len(set(content_structures)) <= 3:  # Similar content structures
                consistency_score += 0.4
            total_checks += 1
            
            # Check for consistent bullet points or formatting
            bullet_consistency = 0
            for slide in slides:
                content = slide.get("main_content", "")
                if "•" in content or "-" in content or "*" in content:
                    bullet_consistency += 1
            
            if bullet_consistency >= len(slides) * 0.7:  # 70% of slides have bullets
                consistency_score += 0.3
            total_checks += 1
            
            return consistency_score / total_checks if total_checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating repetition: {str(e)}")
            return 0.0
    
    async def _validate_alignment(self, slides: List[Dict[str, Any]], validation_level: str) -> float:
        """Validate alignment principles."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Check title alignment (should be consistent)
                title = slide.get("title", "")
                if title:
                    slide_score += 0.4
                    checks_passed += 1
                
                # Check content structure alignment
                content = slide.get("main_content", "")
                if content:
                    # Check if content has proper structure
                    lines = content.split('\n')
                    if len(lines) > 1:  # Has multiple lines
                        slide_score += 0.3
                        checks_passed += 1
                    
                    # Check for proper spacing
                    if content.count('\n\n') > 0:  # Has paragraph breaks
                        slide_score += 0.3
                        checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating alignment: {str(e)}")
            return 0.0
    
    async def _validate_proximity(self, slides: List[Dict[str, Any]], validation_level: str) -> float:
        """Validate proximity principles."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Check if related content is grouped together
                content = slide.get("main_content", "")
                if content:
                    # Check for logical content grouping
                    if len(content.split('\n\n')) > 1:  # Has paragraph grouping
                        slide_score += 0.4
                        checks_passed += 1
                    
                    # Check for list formatting (indicates grouping)
                    if any(marker in content for marker in ["•", "-", "*", "1.", "2.", "3."]):
                        slide_score += 0.3
                        checks_passed += 1
                    
                    # Check for proper white space usage
                    if content.count(' ') > len(content) * 0.1:  # Reasonable spacing
                        slide_score += 0.3
                        checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating proximity: {str(e)}")
            return 0.0
    
    def _generate_design_recommendations(self, slides: List[Dict[str, Any]], compliance_report: DesignComplianceReport) -> List[str]:
        """Generate design improvement recommendations."""
        recommendations = []
        
        # Contrast recommendations
        if compliance_report.contrast_score < 0.7:
            recommendations.extend([
                "Improve color contrast between text and background",
                "Ensure minimum font size of 12pt for body text",
                "Use high contrast color combinations (black on white, dark blue on light blue)",
                "Avoid red-green color combinations for colorblind accessibility"
            ])
        
        # Repetition recommendations
        if compliance_report.repetition_score < 0.7:
            recommendations.extend([
                "Maintain consistent font family across all slides",
                "Use consistent heading styles and sizes",
                "Apply uniform spacing and margins",
                "Keep bullet point styles consistent throughout"
            ])
        
        # Alignment recommendations
        if compliance_report.alignment_score < 0.7:
            recommendations.extend([
                "Align all text elements consistently (left, center, or right)",
                "Use a grid system for element placement",
                "Maintain consistent margins and padding",
                "Create clear visual hierarchy with headings"
            ])
        
        # Proximity recommendations
        if compliance_report.proximity_score < 0.7:
            recommendations.extend([
                "Group related content elements together",
                "Use white space to separate different sections",
                "Ensure logical flow of information",
                "Group similar items in lists or sections"
            ])
        
        return recommendations
    
    def _extract_design_violations(self, slides: List[Dict[str, Any]], compliance_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract specific design violations."""
        violations = []
        
        for i, slide in enumerate(slides):
            slide_violations = []
            
            # Check for common violations
            content = slide.get("main_content", "")
            title = slide.get("title", "")
            
            if not title or len(title.strip()) == 0:
                slide_violations.append({
                    "type": "missing_title",
                    "severity": "high",
                    "description": "Slide missing a clear title"
                })
            
            if not content or len(content.strip()) < 10:
                slide_violations.append({
                    "type": "insufficient_content",
                    "severity": "medium",
                    "description": "Slide has insufficient content"
                })
            
            if content and content.count('\n') < 2:
                slide_violations.append({
                    "type": "poor_structure",
                    "severity": "low",
                    "description": "Content lacks proper paragraph structure"
                })
            
            if slide_violations:
                violations.append({
                    "slide_number": i + 1,
                    "slide_title": title or f"Slide {i + 1}",
                    "violations": slide_violations
                })
        
        return violations
    
    def get_crap_guidelines(self) -> Dict[str, Any]:
        """Get C.R.A.P. design guidelines."""
        return self.crap_guidelines
    
    def get_design_recommendations(self) -> List[str]:
        """Get general design recommendations."""
        return [
            "Use high contrast colors for better readability",
            "Maintain consistent fonts and sizes throughout",
            "Align elements on a grid for visual harmony",
            "Group related content with appropriate spacing",
            "Use bullet points and lists for better organization",
            "Ensure adequate white space between sections",
            "Create clear visual hierarchy with headings",
            "Test designs on different screen sizes"
        ]
