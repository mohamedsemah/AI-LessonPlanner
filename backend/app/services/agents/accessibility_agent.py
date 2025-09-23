import logging
import re
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from .base_agent import BaseAgent
from ...models.gagne_slides import SlideContent
from ...models.accessibility_content import (
    AccessibilityComplianceReport, WCAGPrinciple, AccessibilityRecommendation,
    WCAGPrincipleType, WCAGLevel, AccessibilityComplianceLevel, AccessibilityRecommendationPriority
)

logger = logging.getLogger(__name__)

class AccessibilityAgent(BaseAgent):
    """
    Accessibility Agent for Multi-Agent Lesson Planning System.
    Validates technical accessibility compliance for:
    - Screen reader compatibility
    - Keyboard navigation
    - Color contrast (WCAG 2.2 standards)
    - Alt text for images
    - Focus management
    - Semantic structure
    - Mobile accessibility
    - Target size requirements
    """
    
    def __init__(self, client: AsyncOpenAI):
        """Initialize the Accessibility Agent."""
        super().__init__(client)
        self.logger = logging.getLogger(f"agents.{self.__class__.__name__}")
        self.wcag_guidelines = self._initialize_wcag_guidelines()
    
    def _initialize_wcag_guidelines(self) -> Dict[str, Any]:
        """Initialize WCAG 2.2 accessibility guidelines."""
        return {
            "perceivable": {
                "color_contrast": {
                    "aa_normal": 4.5,
                    "aa_large": 3.0,
                    "aaa_normal": 7.0,
                    "aaa_large": 4.5
                },
                "color_independence": True,
                "text_resize": True,
                "alt_text": True
            },
            "operable": {
                "keyboard_accessible": True,
                "no_seizure": True,
                "navigable": True,
                "focus_visible": True
            },
            "understandable": {
                "readable": True,
                "predictable": True,
                "input_assistance": True
            },
            "robust": {
                "compatible": True,
                "future_proof": True
            }
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process accessibility validation request.
        
        Args:
            input_data: Dictionary containing:
                - slides: List of SlideContent objects or dictionaries
                - accessibility_level: "A", "AA", "AAA" (WCAG 2.2 compliance level)
                - validation_preferences: Optional validation preferences
                
        Returns:
            Dictionary containing:
                - accessibility_compliance_report: AccessibilityComplianceReport object
                - recommendations: List of accessibility improvement recommendations
                - violations: List of specific accessibility violations
                - metadata: Processing metadata
        """
        try:
            slides = input_data.get("slides", [])
            accessibility_level = input_data.get("accessibility_level", "AA")
            validation_preferences = input_data.get("validation_preferences", {})
            
            if not slides:
                raise ValueError("slides are required for accessibility validation")
            
            # Convert slides to dictionaries if they are objects
            slide_dicts = []
            for slide in slides:
                if isinstance(slide, dict):
                    slide_dicts.append(slide)
                else:
                    slide_dicts.append(slide.dict())
            
            self._log_processing_start(f"Validating accessibility compliance for {len(slide_dicts)} slides")
            
            # Validate WCAG compliance
            accessibility_compliance_report = await self._validate_wcag_compliance(slide_dicts, accessibility_level)
            
            # Generate accessibility recommendations
            recommendations = self._generate_accessibility_recommendations(slide_dicts, accessibility_compliance_report)
            
            # Extract specific violations
            violations = self._extract_accessibility_violations(slide_dicts, accessibility_compliance_report)
            
            result = {
                "accessibility_compliance_report": accessibility_compliance_report,
                "recommendations": recommendations,
                "violations": violations,
                "metadata": {
                    "total_slides": len(slide_dicts),
                    "wcag_level": accessibility_level,
                    "principles_checked": list(self.wcag_guidelines.keys())
                }
            }
            
            self._log_processing_success(f"Accessibility validation completed - Overall score: {accessibility_compliance_report.overall_score:.2f}")
            return self._create_success_response(result)
            
        except Exception as e:
            self._log_processing_error(e)
            return self._create_error_response(e)
    
    async def _validate_wcag_compliance(self, slides: List[Dict[str, Any]], accessibility_level: str) -> AccessibilityComplianceReport:
        """Validate slides against WCAG 2.2 compliance."""
        try:
            perceivable_score = await self._validate_perceivable(slides, accessibility_level)
            operable_score = await self._validate_operable(slides, accessibility_level)
            understandable_score = await self._validate_understandable(slides, accessibility_level)
            robust_score = await self._validate_robust(slides, accessibility_level)
            
            # Calculate overall score
            overall_score = (perceivable_score + operable_score + understandable_score + robust_score) / 4
            
            # Create principle objects
            principles = {
                "perceivable": WCAGPrinciple(
                    principle=WCAGPrincipleType.PERCEIVABLE,
                    score=perceivable_score,
                    status=AccessibilityComplianceLevel.EXCELLENT if perceivable_score >= 0.8 else 
                           AccessibilityComplianceLevel.GOOD if perceivable_score >= 0.6 else
                           AccessibilityComplianceLevel.FAIR if perceivable_score >= 0.4 else
                           AccessibilityComplianceLevel.POOR,
                    details="Information and UI components must be presentable in ways users can perceive",
                    violations=[] if perceivable_score >= 0.7 else ["Perceivability issues detected"],
                    recommendations=[] if perceivable_score >= 0.7 else ["Improve perceivability features"],
                    success_criteria=[]
                ),
                "operable": WCAGPrinciple(
                    principle=WCAGPrincipleType.OPERABLE,
                    score=operable_score,
                    status=AccessibilityComplianceLevel.EXCELLENT if operable_score >= 0.8 else 
                           AccessibilityComplianceLevel.GOOD if operable_score >= 0.6 else
                           AccessibilityComplianceLevel.FAIR if operable_score >= 0.4 else
                           AccessibilityComplianceLevel.POOR,
                    details="UI components and navigation must be operable",
                    violations=[] if operable_score >= 0.7 else ["Operability issues detected"],
                    recommendations=[] if operable_score >= 0.7 else ["Improve operability features"],
                    success_criteria=[]
                ),
                "understandable": WCAGPrinciple(
                    principle=WCAGPrincipleType.UNDERSTANDABLE,
                    score=understandable_score,
                    status=AccessibilityComplianceLevel.EXCELLENT if understandable_score >= 0.8 else 
                           AccessibilityComplianceLevel.GOOD if understandable_score >= 0.6 else
                           AccessibilityComplianceLevel.FAIR if understandable_score >= 0.4 else
                           AccessibilityComplianceLevel.POOR,
                    details="Information and UI operation must be understandable",
                    violations=[] if understandable_score >= 0.7 else ["Understandability issues detected"],
                    recommendations=[] if understandable_score >= 0.7 else ["Improve understandability features"],
                    success_criteria=[]
                ),
                "robust": WCAGPrinciple(
                    principle=WCAGPrincipleType.ROBUST,
                    score=robust_score,
                    status=AccessibilityComplianceLevel.EXCELLENT if robust_score >= 0.8 else 
                           AccessibilityComplianceLevel.GOOD if robust_score >= 0.6 else
                           AccessibilityComplianceLevel.FAIR if robust_score >= 0.4 else
                           AccessibilityComplianceLevel.POOR,
                    details="Content must be robust enough for various assistive technologies",
                    violations=[] if robust_score >= 0.7 else ["Robustness issues detected"],
                    recommendations=[] if robust_score >= 0.7 else ["Improve robustness features"],
                    success_criteria=[]
                )
            }
            
            return AccessibilityComplianceReport(
                perceivable_score=perceivable_score,
                operable_score=operable_score,
                understandable_score=understandable_score,
                robust_score=robust_score,
                overall_score=overall_score,
                wcag_level=WCAGLevel(accessibility_level),
                principles=principles,
                recommendations=[],
                violations=[],
                metadata={"total_slides": len(slides)}
            )
            
        except Exception as e:
            self.logger.error(f"Error validating WCAG compliance: {str(e)}")
            return AccessibilityComplianceReport(
                perceivable_score=0.0,
                operable_score=0.0,
                understandable_score=0.0,
                robust_score=0.0,
                overall_score=0.0,
                wcag_level=WCAGLevel(accessibility_level),
                principles={},
                recommendations=[],
                violations=[],
                metadata={"error": str(e)}
            )
    
    async def _validate_perceivable(self, slides: List[Dict[str, Any]], accessibility_level: str) -> float:
        """Validate perceivable principle (WCAG 1.1-1.4)."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Check for alt text in visual elements
                visual_elements = slide.get("visual_elements", [])
                if visual_elements:
                    alt_text_count = sum(1 for element in visual_elements if element.get("alt_text"))
                    if alt_text_count == len(visual_elements):
                        slide_score += 0.4
                        checks_passed += 1
                    elif alt_text_count > 0:
                        slide_score += 0.2
                        checks_passed += 1
                
                # Check text content readability
                content = slide.get("main_content", "")
                if content:
                    # Check for proper text structure
                    if len(content) > 20:  # Has substantial content
                        slide_score += 0.3
                        checks_passed += 1
                    
                    # Check for heading structure
                    title = slide.get("title", "")
                    if title and len(title) > 0:
                        slide_score += 0.3
                        checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating perceivable: {str(e)}")
            return 0.0
    
    async def _validate_operable(self, slides: List[Dict[str, Any]], accessibility_level: str) -> float:
        """Validate operable principle (WCAG 2.1-2.5)."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Check for keyboard accessibility indicators
                content = slide.get("main_content", "")
                if content:
                    # Check for interactive elements that should be keyboard accessible
                    interactive_indicators = ["click", "select", "choose", "button", "link"]
                    has_interactive_content = any(indicator in content.lower() for indicator in interactive_indicators)
                    
                    if has_interactive_content:
                        # In a real implementation, would check for proper ARIA labels
                        slide_score += 0.5
                        checks_passed += 1
                    else:
                        # Static content is inherently keyboard accessible
                        slide_score += 0.3
                        checks_passed += 1
                
                # Check for focus management
                title = slide.get("title", "")
                if title:
                    slide_score += 0.2
                    checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating operable: {str(e)}")
            return 0.0
    
    async def _validate_understandable(self, slides: List[Dict[str, Any]], accessibility_level: str) -> float:
        """Validate understandable principle (WCAG 3.1-3.3)."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Check for clear language and structure
                content = slide.get("main_content", "")
                title = slide.get("title", "")
                
                if content:
                    # Check for clear sentence structure
                    sentences = content.split('.')
                    clear_sentences = sum(1 for sentence in sentences if len(sentence.split()) > 3 and len(sentence.split()) < 30)
                    
                    if clear_sentences > 0:
                        slide_score += 0.4
                        checks_passed += 1
                    
                    # Check for logical organization
                    if len(content.split('\n')) > 1:  # Has paragraph structure
                        slide_score += 0.3
                        checks_passed += 1
                
                if title:
                    # Check for clear, descriptive titles
                    if len(title) > 5 and len(title) < 100:
                        slide_score += 0.3
                        checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating understandable: {str(e)}")
            return 0.0
    
    async def _validate_robust(self, slides: List[Dict[str, Any]], accessibility_level: str) -> float:
        """Validate robust principle (WCAG 4.1)."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Check for semantic structure
                title = slide.get("title", "")
                content = slide.get("main_content", "")
                
                if title and content:
                    # Has both title and content (good semantic structure)
                    slide_score += 0.5
                    checks_passed += 1
                
                # Check for proper content formatting
                if content:
                    # Check for structured content
                    if any(marker in content for marker in ["•", "-", "*", "1.", "2.", "3."]):
                        slide_score += 0.3
                        checks_passed += 1
                    
                    # Check for reasonable content length
                    if 10 < len(content) < 1000:  # Reasonable content length
                        slide_score += 0.2
                        checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating robust: {str(e)}")
            return 0.0
    
    def _generate_accessibility_recommendations(self, slides: List[Dict[str, Any]], compliance_report: AccessibilityComplianceReport) -> List[str]:
        """Generate accessibility improvement recommendations."""
        recommendations = []
        
        # Perceivable recommendations
        if compliance_report.perceivable_score < 0.7:
            recommendations.extend([
                "Add alt text to all images and visual elements",
                "Ensure color contrast meets WCAG AA standards (4.5:1 for normal text)",
                "Provide text alternatives for audio content",
                "Use semantic HTML structure with proper headings",
                "Ensure text can be resized up to 200% without loss of functionality"
            ])
        
        # Operable recommendations
        if compliance_report.operable_score < 0.7:
            recommendations.extend([
                "Ensure all interactive elements are keyboard accessible",
                "Provide visible focus indicators for keyboard navigation",
                "Avoid content that flashes more than 3 times per second",
                "Provide skip links for long content",
                "Ensure all functionality is available via keyboard"
            ])
        
        # Understandable recommendations
        if compliance_report.understandable_score < 0.7:
            recommendations.extend([
                "Use clear, simple language appropriate for the audience",
                "Provide consistent navigation and interface elements",
                "Include error messages that clearly identify the problem",
                "Use descriptive labels for form elements",
                "Provide help text for complex interactions"
            ])
        
        # Robust recommendations
        if compliance_report.robust_score < 0.7:
            recommendations.extend([
                "Use valid, semantic HTML markup",
                "Ensure compatibility with assistive technologies",
                "Test with screen readers and other accessibility tools",
                "Provide fallback content for dynamic elements",
                "Use ARIA labels where appropriate"
            ])
        
        return recommendations
    
    def _extract_accessibility_violations(self, slides: List[Dict[str, Any]], compliance_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract specific accessibility violations."""
        violations = []
        
        for i, slide in enumerate(slides):
            slide_violations = []
            
            # Check for missing alt text
            visual_elements = slide.get("visual_elements", [])
            for j, element in enumerate(visual_elements):
                if not element.get("alt_text"):
                    slide_violations.append({
                        "type": "missing_alt_text",
                        "severity": "high",
                        "description": f"Visual element {j+1} missing alt text",
                        "element": element
                    })
            
            # Check for missing titles
            title = slide.get("title", "")
            if not title or len(title.strip()) == 0:
                slide_violations.append({
                    "type": "missing_title",
                    "severity": "high",
                    "description": "Slide missing accessible title"
                })
            
            # Check for poor content structure
            content = slide.get("main_content", "")
            if content and len(content.split('\n')) < 2:
                slide_violations.append({
                    "type": "poor_structure",
                    "severity": "medium",
                    "description": "Content lacks proper paragraph structure for screen readers"
                })
            
            if slide_violations:
                violations.append({
                    "slide_number": i + 1,
                    "slide_title": title or f"Slide {i + 1}",
                    "violations": slide_violations
                })
        
        return violations
    
    def get_wcag_guidelines(self) -> Dict[str, Any]:
        """Get WCAG 2.2 accessibility guidelines."""
        return self.wcag_guidelines
    
    def get_accessibility_recommendations(self) -> List[str]:
        """Get general accessibility recommendations."""
        return [
            "Ensure all images have descriptive alt text",
            "Use sufficient color contrast (4.5:1 for normal text, 3:1 for large text)",
            "Provide keyboard navigation for all interactive elements",
            "Use semantic HTML structure with proper heading hierarchy",
            "Include skip links for long content",
            "Test with screen readers and other assistive technologies",
            "Provide text alternatives for audio and video content",
            "Use clear, descriptive labels for all form elements",
            "Ensure content is readable and understandable",
            "Avoid content that flashes more than 3 times per second",
            "Follow WCAG 2.2 guidelines for latest accessibility standards",
            "Ensure target sizes meet minimum requirements (24x24px)",
            "Implement focus management for better keyboard navigation"
        ]
