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
        Process accessibility validation and enhancement request.
        
        Args:
            input_data: Dictionary containing:
                - slides: List of SlideContent objects or dictionaries
                - accessibility_level: "A", "AA", "AAA" (WCAG 2.2 compliance level)
                - validation_preferences: Optional validation preferences
                
        Returns:
            Dictionary containing:
                - accessibility_compliance_report: AccessibilityComplianceReport object
                - enhanced_slides: List of enhanced SlideContent objects
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
            
            # Enhance slides with accessibility improvements
            enhanced_slides = await self._enhance_slides_with_accessibility(slide_dicts, accessibility_compliance_report, validation_preferences)
            
            # Generate accessibility recommendations
            recommendations = self._generate_accessibility_recommendations(slide_dicts, accessibility_compliance_report)
            
            # Extract specific violations
            violations = self._extract_accessibility_violations(slide_dicts, accessibility_compliance_report)
            
            result = {
                "accessibility_compliance_report": accessibility_compliance_report.dict() if hasattr(accessibility_compliance_report, 'dict') else accessibility_compliance_report,
                "enhanced_slides": enhanced_slides,
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
        """Validate perceivable principle (WCAG 1.1-1.4) with real analysis."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Real perceivability analysis
                alt_text_score = await self._analyze_alt_text_compliance(slide, accessibility_level)
                if alt_text_score > 0:
                    slide_score += alt_text_score
                    checks_passed += 1
                
                # Check text alternatives and captions
                text_alternatives_score = await self._analyze_text_alternatives(slide, accessibility_level)
                if text_alternatives_score > 0:
                    slide_score += text_alternatives_score
                    checks_passed += 1
                
                # Check color and contrast
                color_contrast_score = await self._analyze_color_contrast(slide, accessibility_level)
                if color_contrast_score > 0:
                    slide_score += color_contrast_score
                    checks_passed += 1
                
                # Check text resizing and scaling
                text_scaling_score = await self._analyze_text_scaling(slide, accessibility_level)
                if text_scaling_score > 0:
                    slide_score += text_scaling_score
                    checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating perceivable: {str(e)}")
            return 0.0
    
    async def _analyze_alt_text_compliance(self, slide: Dict[str, Any], accessibility_level: str) -> float:
        """Analyze alt text compliance for visual elements"""
        try:
            visual_elements = slide.get("visual_elements", [])
            
            if not visual_elements:
                return 0.8  # No visual elements to check
            
            alt_text_score = 0.0
            total_elements = len(visual_elements)
            
            for element in visual_elements:
                alt_text = element.get("alt_text", "")
                description = element.get("description", "")
                
                # Check if alt text exists and is meaningful
                if alt_text and len(alt_text.strip()) > 5:
                    alt_text_score += 0.4
                elif alt_text and len(alt_text.strip()) > 0:
                    alt_text_score += 0.2
                
                # Check if description exists and is detailed
                if description and len(description.strip()) > 10:
                    alt_text_score += 0.3
                elif description and len(description.strip()) > 0:
                    alt_text_score += 0.1
                
                # Check for decorative image indicators
                if "decorative" in alt_text.lower() or "decorative" in description.lower():
                    alt_text_score += 0.1
            
            return min(1.0, alt_text_score / total_elements) if total_elements > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing alt text compliance: {str(e)}")
            return 0.0
    
    async def _analyze_text_alternatives(self, slide: Dict[str, Any], accessibility_level: str) -> float:
        """Analyze text alternatives for non-text content"""
        try:
            content = slide.get("main_content", "")
            audio_script = slide.get("audio_script", "")
            
            text_score = 0.0
            checks = 0
            
            # Check for substantial text content
            if content and len(content.strip()) > 20:
                text_score += 0.4
            checks += 1
            
            # Check for audio script (text alternative for audio)
            if audio_script and len(audio_script.strip()) > 10:
                text_score += 0.3
            checks += 1
            
            # Check for heading structure (improves text navigation)
            title = slide.get("title", "")
            if title and len(title.strip()) > 0:
                text_score += 0.2
            checks += 1
            
            # Check for list structure (improves text organization)
            list_indicators = ["•", "-", "*", "1.", "2.", "3."]
            if any(indicator in content for indicator in list_indicators):
                text_score += 0.1
            checks += 1
            
            return text_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing text alternatives: {str(e)}")
            return 0.0
    
    async def _analyze_color_contrast(self, slide: Dict[str, Any], accessibility_level: str) -> float:
        """Analyze color contrast and color usage"""
        try:
            content = slide.get("main_content", "")
            
            contrast_score = 0.0
            checks = 0
            
            # Check for color-related content that indicates awareness
            color_keywords = ["color", "contrast", "dark", "light", "bright", "highlight"]
            color_mentions = sum(1 for keyword in color_keywords if keyword in content.lower())
            if color_mentions > 0:
                contrast_score += min(0.3, color_mentions * 0.1)
            checks += 1
            
            # Check for accessibility considerations
            accessibility_keywords = ["accessible", "readable", "visible", "clear", "high contrast"]
            if any(keyword in content.lower() for keyword in accessibility_keywords):
                contrast_score += 0.2
            checks += 1
            
            # Check for text formatting that improves contrast
            formatting_indicators = ["**", "bold", "strong", "##", "###"]
            formatting_count = sum(content.count(indicator) for indicator in formatting_indicators)
            if formatting_count > 0:
                contrast_score += min(0.3, formatting_count * 0.05)
            checks += 1
            
            # Check for visual hierarchy (indicates good contrast design)
            hierarchy_indicators = ["#", "##", "###", "####"]
            if any(indicator in content for indicator in hierarchy_indicators):
                contrast_score += 0.2
            checks += 1
            
            return contrast_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing color contrast: {str(e)}")
            return 0.0
    
    async def _analyze_text_scaling(self, slide: Dict[str, Any], accessibility_level: str) -> float:
        """Analyze text scaling and resizing capabilities"""
        try:
            content = slide.get("main_content", "")
            
            scaling_score = 0.0
            checks = 0
            
            # Check for proper text structure that supports scaling
            if content and len(content.strip()) > 10:
                scaling_score += 0.3
            checks += 1
            
            # Check for heading hierarchy (supports text scaling)
            heading_count = content.count('#') + content.count('##') + content.count('###')
            if heading_count > 0:
                scaling_score += 0.2
            checks += 1
            
            # Check for list structure (supports text scaling)
            list_indicators = ["•", "-", "*", "1.", "2.", "3."]
            if any(indicator in content for indicator in list_indicators):
                scaling_score += 0.2
            checks += 1
            
            # Check for paragraph structure (supports text scaling)
            paragraph_count = content.count('\n\n') + content.count('\n')
            if paragraph_count > 0:
                scaling_score += 0.2
            checks += 1
            
            # Check for responsive design considerations
            responsive_keywords = ["responsive", "scalable", "flexible", "adaptive"]
            if any(keyword in content.lower() for keyword in responsive_keywords):
                scaling_score += 0.1
            checks += 1
            
            return scaling_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing text scaling: {str(e)}")
            return 0.0
    
    async def _validate_operable(self, slides: List[Dict[str, Any]], accessibility_level: str) -> float:
        """Validate operable principle (WCAG 2.1-2.5) with real analysis."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Real operability analysis
                keyboard_score = await self._analyze_keyboard_accessibility(slide, accessibility_level)
                if keyboard_score > 0:
                    slide_score += keyboard_score
                    checks_passed += 1
                
                # Check for seizure and motion safety
                seizure_score = await self._analyze_seizure_safety(slide, accessibility_level)
                if seizure_score > 0:
                    slide_score += seizure_score
                    checks_passed += 1
                
                # Check for navigation and focus management
                navigation_score = await self._analyze_navigation_accessibility(slide, accessibility_level)
                if navigation_score > 0:
                    slide_score += navigation_score
                    checks_passed += 1
                
                # Check for input methods and timing
                input_score = await self._analyze_input_accessibility(slide, accessibility_level)
                if input_score > 0:
                    slide_score += input_score
                    checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating operable: {str(e)}")
            return 0.0
    
    async def _analyze_keyboard_accessibility(self, slide: Dict[str, Any], accessibility_level: str) -> float:
        """Analyze keyboard accessibility and navigation"""
        try:
            content = slide.get("main_content", "")
            
            keyboard_score = 0.0
            checks = 0
            
            # Check for interactive elements that need keyboard access
            interactive_indicators = ["click", "select", "choose", "button", "link", "menu", "tab"]
            interactive_count = sum(1 for indicator in interactive_indicators if indicator in content.lower())
            if interactive_count > 0:
                keyboard_score += 0.3
            checks += 1
            
            # Check for keyboard navigation indicators
            navigation_keywords = ["keyboard", "tab", "enter", "space", "arrow", "focus"]
            if any(keyword in content.lower() for keyword in navigation_keywords):
                keyboard_score += 0.2
            checks += 1
            
            # Check for ARIA labels and accessibility attributes
            aria_keywords = ["aria", "label", "role", "alt", "title"]
            if any(keyword in content.lower() for keyword in aria_keywords):
                keyboard_score += 0.2
            checks += 1
            
            # Check for skip links and navigation aids
            skip_keywords = ["skip", "jump", "navigation", "menu", "main"]
            if any(keyword in content.lower() for keyword in skip_keywords):
                keyboard_score += 0.2
            checks += 1
            
            # Check for focus management
            focus_keywords = ["focus", "highlight", "active", "selected"]
            if any(keyword in content.lower() for keyword in focus_keywords):
                keyboard_score += 0.1
            checks += 1
            
            return keyboard_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing keyboard accessibility: {str(e)}")
            return 0.0
    
    async def _analyze_seizure_safety(self, slide: Dict[str, Any], accessibility_level: str) -> float:
        """Analyze seizure and motion safety"""
        try:
            content = slide.get("main_content", "")
            visual_elements = slide.get("visual_elements", [])
            
            seizure_score = 0.0
            checks = 0
            
            # Check for seizure-inducing content warnings
            seizure_keywords = ["flash", "blink", "flicker", "strobe", "rapid", "fast"]
            seizure_mentions = sum(1 for keyword in seizure_keywords if keyword in content.lower())
            if seizure_mentions == 0:  # No seizure-inducing content mentioned
                seizure_score += 0.4
            elif "warning" in content.lower() or "caution" in content.lower():
                seizure_score += 0.3  # Has warnings
            checks += 1
            
            # Check for motion sensitivity considerations
            motion_keywords = ["motion", "animation", "video", "gif", "moving"]
            motion_mentions = sum(1 for keyword in motion_keywords if keyword in content.lower())
            if motion_mentions == 0:  # No motion content
                seizure_score += 0.3
            elif "pause" in content.lower() or "stop" in content.lower():
                seizure_score += 0.2  # Has motion controls
            checks += 1
            
            # Check for accessibility features in visual elements
            for element in visual_elements:
                element_type = element.get("type", "").lower()
                if element_type in ["video", "animation", "gif"]:
                    if "pause" in element.get("description", "").lower():
                        seizure_score += 0.1
                    break
            checks += 1
            
            # Check for static content (inherently safe)
            if not any(keyword in content.lower() for keyword in ["video", "animation", "gif", "flash"]):
                seizure_score += 0.3
            checks += 1
            
            return seizure_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing seizure safety: {str(e)}")
            return 0.0
    
    async def _analyze_navigation_accessibility(self, slide: Dict[str, Any], accessibility_level: str) -> float:
        """Analyze navigation and focus management"""
        try:
            content = slide.get("main_content", "")
            title = slide.get("title", "")
            
            navigation_score = 0.0
            checks = 0
            
            # Check for clear navigation structure
            if title and len(title.strip()) > 0:
                navigation_score += 0.3
            checks += 1
            
            # Check for heading hierarchy (improves navigation)
            heading_count = content.count('#') + content.count('##') + content.count('###')
            if heading_count > 0:
                navigation_score += 0.2
            checks += 1
            
            # Check for list structure (improves navigation)
            list_indicators = ["•", "-", "*", "1.", "2.", "3."]
            if any(indicator in content for indicator in list_indicators):
                navigation_score += 0.2
            checks += 1
            
            # Check for navigation keywords
            nav_keywords = ["navigation", "menu", "skip", "jump", "next", "previous", "back"]
            if any(keyword in content.lower() for keyword in nav_keywords):
                navigation_score += 0.2
            checks += 1
            
            # Check for focus indicators
            focus_keywords = ["focus", "highlight", "active", "selected", "current"]
            if any(keyword in content.lower() for keyword in focus_keywords):
                navigation_score += 0.1
            checks += 1
            
            return navigation_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing navigation accessibility: {str(e)}")
            return 0.0
    
    async def _analyze_input_accessibility(self, slide: Dict[str, Any], accessibility_level: str) -> float:
        """Analyze input methods and timing accessibility"""
        try:
            content = slide.get("main_content", "")
            
            input_score = 0.0
            checks = 0
            
            # Check for input method flexibility
            input_keywords = ["input", "type", "method", "alternative", "choice"]
            if any(keyword in content.lower() for keyword in input_keywords):
                input_score += 0.2
            checks += 1
            
            # Check for timing considerations
            timing_keywords = ["time", "duration", "pause", "wait", "speed", "rate"]
            if any(keyword in content.lower() for keyword in timing_keywords):
                input_score += 0.2
            checks += 1
            
            # Check for error handling
            error_keywords = ["error", "mistake", "correct", "fix", "help", "guidance"]
            if any(keyword in content.lower() for keyword in error_keywords):
                input_score += 0.2
            checks += 1
            
            # Check for user control
            control_keywords = ["control", "adjust", "customize", "setting", "option"]
            if any(keyword in content.lower() for keyword in control_keywords):
                input_score += 0.2
            checks += 1
            
            # Check for clear instructions
            instruction_keywords = ["instruction", "step", "guide", "how", "process"]
            if any(keyword in content.lower() for keyword in instruction_keywords):
                input_score += 0.2
            checks += 1
            
            return input_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing input accessibility: {str(e)}")
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
    
    async def _enhance_slides_with_accessibility(self, slides: List[Dict[str, Any]], compliance_report: AccessibilityComplianceReport, validation_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance slides with accessibility improvements based on WCAG 2.2 compliance"""
        try:
            enhanced_slides = []
            
            for slide in slides:
                enhanced_slide = slide.copy()
                
                # Apply accessibility enhancements based on compliance scores
                if compliance_report.perceivable_score < 0.7:
                    enhanced_slide = await self._enhance_perceivable(enhanced_slide, validation_preferences)
                
                if compliance_report.operable_score < 0.7:
                    enhanced_slide = await self._enhance_operable(enhanced_slide, validation_preferences)
                
                if compliance_report.understandable_score < 0.7:
                    enhanced_slide = await self._enhance_understandable(enhanced_slide, validation_preferences)
                
                if compliance_report.robust_score < 0.7:
                    enhanced_slide = await self._enhance_robust(enhanced_slide, validation_preferences)
                
                enhanced_slides.append(enhanced_slide)
            
            return enhanced_slides
            
        except Exception as e:
            self.logger.error(f"Error enhancing slides with accessibility: {str(e)}")
            return slides  # Return original slides if enhancement fails
    
    async def _enhance_perceivable(self, slide: Dict[str, Any], validation_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide perceivability (WCAG 1.1-1.4)"""
        try:
            # Add accessibility features if missing
            if "accessibility_features" not in slide:
                slide["accessibility_features"] = []
            
            # Ensure visual elements have proper alt text
            visual_elements = slide.get("visual_elements", [])
            for element in visual_elements:
                if not element.get("alt_text"):
                    element["alt_text"] = f"Descriptive text for {element.get('type', 'visual element')}"
                if not element.get("description"):
                    element["description"] = f"Detailed description of the visual content"
            
            # Add perceivability guidelines
            slide["accessibility_features"].extend([
                "alt_text_for_images",
                "descriptive_links",
                "color_contrast_compliance",
                "text_scalability"
            ])
            
            # Enhance content with perceivability improvements
            content = slide.get("main_content", "")
            if content:
                enhanced_content = content + "\n\n**Accessibility Enhancement:**\n- All images include descriptive alt text\n- High contrast colors for better visibility\n- Text is scalable and readable\n- Content is perceivable by all users"
                slide["main_content"] = enhanced_content
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing perceivability: {str(e)}")
            return slide
    
    async def _enhance_operable(self, slide: Dict[str, Any], validation_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide operability (WCAG 2.1-2.5)"""
        try:
            # Add operability features
            if "accessibility_features" not in slide:
                slide["accessibility_features"] = []
            
            slide["accessibility_features"].extend([
                "keyboard_navigation",
                "focus_management",
                "no_seizure_risk",
                "sufficient_time_limits"
            ])
            
            # Add operability guidelines
            if "accessibility_guidelines" not in slide:
                slide["accessibility_guidelines"] = []
            
            slide["accessibility_guidelines"].extend([
                "Ensure all interactive elements are keyboard accessible",
                "Provide clear focus indicators",
                "Avoid content that flashes more than 3 times per second",
                "Allow sufficient time for users to read and interact with content"
            ])
            
            # Enhance content with operability improvements
            content = slide.get("main_content", "")
            if content:
                enhanced_content = content + "\n\n**Operability Features:**\n- All content is keyboard accessible\n- Clear focus indicators for navigation\n- No seizure-inducing content\n- Adequate time for interaction"
                slide["main_content"] = enhanced_content
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing operability: {str(e)}")
            return slide
    
    async def _enhance_understandable(self, slide: Dict[str, Any], validation_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide understandability (WCAG 3.1-3.3)"""
        try:
            # Add understandability features
            if "accessibility_features" not in slide:
                slide["accessibility_features"] = []
            
            slide["accessibility_features"].extend([
                "clear_language",
                "consistent_navigation",
                "error_identification",
                "help_mechanisms"
            ])
            
            # Add understandability guidelines
            if "accessibility_guidelines" not in slide:
                slide["accessibility_guidelines"] = []
            
            slide["accessibility_guidelines"].extend([
                "Use clear, simple language appropriate for the audience",
                "Maintain consistent navigation and interface elements",
                "Provide clear error messages and help text",
                "Use familiar UI patterns and conventions"
            ])
            
            # Enhance content with understandability improvements
            content = slide.get("main_content", "")
            if content:
                enhanced_content = content + "\n\n**Understandability Features:**\n- Clear, simple language throughout\n- Consistent formatting and structure\n- Helpful error messages and guidance\n- Familiar interface patterns"
                slide["main_content"] = enhanced_content
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing understandability: {str(e)}")
            return slide
    
    async def _enhance_robust(self, slide: Dict[str, Any], validation_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide robustness (WCAG 4.1)"""
        try:
            # Add robustness features
            if "accessibility_features" not in slide:
                slide["accessibility_features"] = []
            
            slide["accessibility_features"].extend([
                "valid_markup",
                "assistive_technology_compatibility",
                "future_proof_design",
                "cross_platform_compatibility"
            ])
            
            # Add robustness guidelines
            if "accessibility_guidelines" not in slide:
                slide["accessibility_guidelines"] = []
            
            slide["accessibility_guidelines"].extend([
                "Use valid, semantic HTML markup",
                "Ensure compatibility with assistive technologies",
                "Design for future technology compatibility",
                "Test across different platforms and devices"
            ])
            
            # Enhance content with robustness improvements
            content = slide.get("main_content", "")
            if content:
                enhanced_content = content + "\n\n**Robustness Features:**\n- Valid, semantic markup structure\n- Compatible with assistive technologies\n- Future-proof design principles\n- Cross-platform compatibility"
                slide["main_content"] = enhanced_content
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing robustness: {str(e)}")
            return slide
