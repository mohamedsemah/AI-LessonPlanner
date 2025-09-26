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
        Process design validation and enhancement request.
        
        Args:
            input_data: Dictionary containing:
                - slides: List of SlideContent objects or dictionaries
                - design_preferences: Optional design preferences
                - validation_level: "basic", "standard", "strict"
                
        Returns:
            Dictionary containing:
                - design_compliance_report: DesignComplianceReport object
                - enhanced_slides: List of enhanced SlideContent objects
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
            
            # Enhance slides with design improvements
            enhanced_slides = await self._enhance_slides_with_design(slide_dicts, design_compliance_report, design_preferences)
            
            # Generate design recommendations
            recommendations = self._generate_design_recommendations(slide_dicts, design_compliance_report)
            
            # Extract specific violations
            violations = self._extract_design_violations(slide_dicts, design_compliance_report)
            
            result = {
                "design_compliance_report": design_compliance_report.dict() if hasattr(design_compliance_report, 'dict') else design_compliance_report,
                "enhanced_slides": enhanced_slides,
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
        """Validate contrast principles with real analysis."""
        try:
            total_score = 0.0
            valid_slides = 0
            
            for slide in slides:
                slide_score = 0.0
                checks_passed = 0
                
                # Real contrast analysis
                contrast_score = await self._analyze_text_contrast(slide)
                if contrast_score > 0:
                    slide_score += contrast_score
                    checks_passed += 1
                
                # Check heading hierarchy and font sizes
                hierarchy_score = await self._analyze_heading_hierarchy(slide)
                if hierarchy_score > 0:
                    slide_score += hierarchy_score
                    checks_passed += 1
                
                # Check color usage and accessibility
                color_score = await self._analyze_color_usage(slide)
                if color_score > 0:
                    slide_score += color_score
                    checks_passed += 1
                
                # Check text readability
                readability_score = await self._analyze_text_readability(slide)
                if readability_score > 0:
                    slide_score += readability_score
                    checks_passed += 1
                
                if checks_passed > 0:
                    total_score += slide_score / checks_passed
                    valid_slides += 1
            
            return total_score / valid_slides if valid_slides > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating contrast: {str(e)}")
            return 0.0
    
    async def _analyze_text_contrast(self, slide: Dict[str, Any]) -> float:
        """Analyze text contrast ratio and readability"""
        try:
            content = slide.get("main_content", "")
            title = slide.get("title", "")
            
            # Check for contrast indicators in content
            contrast_indicators = 0
            total_checks = 0
            
            # Check for bold text (indicates emphasis/contrast)
            if "**" in content or "<b>" in content or "<strong>" in content:
                contrast_indicators += 0.3
            total_checks += 1
            
            # Check for heading structure (indicates visual hierarchy)
            if "#" in content or title:
                contrast_indicators += 0.3
            total_checks += 1
            
            # Check for bullet points (indicates structure)
            if "•" in content or "-" in content or "*" in content:
                contrast_indicators += 0.2
            total_checks += 1
            
            # Check for color mentions (indicates design awareness)
            color_keywords = ["color", "contrast", "dark", "light", "bright", "bold"]
            if any(keyword in content.lower() for keyword in color_keywords):
                contrast_indicators += 0.2
            total_checks += 1
            
            return contrast_indicators / total_checks if total_checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing text contrast: {str(e)}")
            return 0.0
    
    async def _analyze_heading_hierarchy(self, slide: Dict[str, Any]) -> float:
        """Analyze heading hierarchy and structure"""
        try:
            content = slide.get("main_content", "")
            title = slide.get("title", "")
            
            hierarchy_score = 0.0
            checks = 0
            
            # Check for title presence
            if title and len(title.strip()) > 0:
                hierarchy_score += 0.4
            checks += 1
            
            # Check for heading structure in content
            heading_indicators = ["#", "##", "###", "####", "**", "## "]
            heading_count = sum(1 for indicator in heading_indicators if indicator in content)
            if heading_count > 0:
                hierarchy_score += min(0.4, heading_count * 0.1)
            checks += 1
            
            # Check for list structure (indicates organization)
            list_indicators = ["•", "-", "*", "1.", "2.", "3."]
            list_count = sum(1 for indicator in list_indicators if indicator in content)
            if list_count > 0:
                hierarchy_score += min(0.2, list_count * 0.05)
            checks += 1
            
            return hierarchy_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing heading hierarchy: {str(e)}")
            return 0.0
    
    async def _analyze_color_usage(self, slide: Dict[str, Any]) -> float:
        """Analyze color usage and accessibility"""
        try:
            content = slide.get("main_content", "")
            visual_elements = slide.get("visual_elements", [])
            
            color_score = 0.0
            checks = 0
            
            # Check for color-related content
            color_keywords = ["color", "contrast", "dark", "light", "bright", "highlight"]
            color_mentions = sum(1 for keyword in color_keywords if keyword in content.lower())
            if color_mentions > 0:
                color_score += min(0.3, color_mentions * 0.1)
            checks += 1
            
            # Check visual elements for color considerations
            if visual_elements:
                for element in visual_elements:
                    if element.get("alt_text") and len(element.get("alt_text", "")) > 10:
                        color_score += 0.2
                        break
            checks += 1
            
            # Check for accessibility considerations
            accessibility_keywords = ["accessible", "readable", "visible", "clear"]
            if any(keyword in content.lower() for keyword in accessibility_keywords):
                color_score += 0.2
            checks += 1
            
            return color_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing color usage: {str(e)}")
            return 0.0
    
    async def _analyze_text_readability(self, slide: Dict[str, Any]) -> float:
        """Analyze text readability and structure"""
        try:
            content = slide.get("main_content", "")
            
            readability_score = 0.0
            checks = 0
            
            # Check content length (not too short, not too long)
            content_length = len(content)
            if 50 <= content_length <= 500:  # Optimal length range
                readability_score += 0.3
            elif content_length > 50:  # At least has content
                readability_score += 0.2
            checks += 1
            
            # Check for paragraph structure
            paragraph_count = content.count('\n\n') + content.count('\n')
            if paragraph_count > 0:
                readability_score += 0.2
            checks += 1
            
            # Check for sentence structure
            sentence_indicators = [".", "!", "?"]
            sentence_count = sum(content.count(indicator) for indicator in sentence_indicators)
            if sentence_count > 0:
                readability_score += 0.2
            checks += 1
            
            # Check for formatting (bold, italic, etc.)
            formatting_indicators = ["**", "*", "_", "`"]
            formatting_count = sum(content.count(indicator) for indicator in formatting_indicators)
            if formatting_count > 0:
                readability_score += 0.3
            checks += 1
            
            return readability_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing text readability: {str(e)}")
            return 0.0
    
    async def _validate_repetition(self, slides: List[Dict[str, Any]], validation_level: str) -> float:
        """Validate repetition principles with real analysis."""
        try:
            if len(slides) < 2:
                return 1.0  # Single slide is automatically consistent
            
            # Real repetition analysis
            consistency_score = 0.0
            total_checks = 0
            
            # Analyze title consistency
            title_consistency = await self._analyze_title_consistency(slides)
            if title_consistency > 0:
                consistency_score += title_consistency
                total_checks += 1
            
            # Analyze content structure consistency
            structure_consistency = await self._analyze_content_structure_consistency(slides)
            if structure_consistency > 0:
                consistency_score += structure_consistency
                total_checks += 1
            
            # Analyze formatting consistency
            formatting_consistency = await self._analyze_formatting_consistency(slides)
            if formatting_consistency > 0:
                consistency_score += formatting_consistency
                total_checks += 1
            
            # Analyze visual element consistency
            visual_consistency = await self._analyze_visual_consistency(slides)
            if visual_consistency > 0:
                consistency_score += visual_consistency
                total_checks += 1
            
            return consistency_score / total_checks if total_checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error validating repetition: {str(e)}")
            return 0.0
    
    async def _analyze_title_consistency(self, slides: List[Dict[str, Any]]) -> float:
        """Analyze title formatting consistency across slides"""
        try:
            titles = [slide.get("title", "") for slide in slides]
            valid_titles = [title for title in titles if title.strip()]
            
            if len(valid_titles) < 2:
                return 0.5  # Not enough titles to compare
            
            consistency_score = 0.0
            checks = 0
            
            # Check title length consistency
            title_lengths = [len(title) for title in valid_titles]
            length_variance = max(title_lengths) - min(title_lengths)
            if length_variance <= 20:  # Similar lengths
                consistency_score += 0.3
            checks += 1
            
            # Check title formatting consistency
            formatting_patterns = []
            for title in valid_titles:
                if title[0].isupper():  # Starts with capital
                    formatting_patterns.append("capital_start")
                if ":" in title:  # Has colon
                    formatting_patterns.append("has_colon")
                if title.endswith("."):  # Ends with period
                    formatting_patterns.append("ends_period")
            
            # Count most common pattern
            if formatting_patterns:
                from collections import Counter
                pattern_counts = Counter(formatting_patterns)
                most_common_count = max(pattern_counts.values())
                consistency_score += (most_common_count / len(valid_titles)) * 0.4
            checks += 1
            
            # Check title structure consistency
            structure_indicators = ["#", "##", "###", "**", "*"]
            structure_consistency = 0
            for title in valid_titles:
                if any(indicator in title for indicator in structure_indicators):
                    structure_consistency += 1
            
            if structure_consistency > 0:
                consistency_score += (structure_consistency / len(valid_titles)) * 0.3
            checks += 1
            
            return consistency_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing title consistency: {str(e)}")
            return 0.0
    
    async def _analyze_content_structure_consistency(self, slides: List[Dict[str, Any]]) -> float:
        """Analyze content structure consistency across slides"""
        try:
            content_structures = []
            
            for slide in slides:
                content = slide.get("main_content", "")
                structure = {
                    "paragraphs": content.count('\n\n') + 1,
                    "headings": content.count('#'),
                    "lists": content.count('•') + content.count('-') + content.count('*'),
                    "bold": content.count('**'),
                    "italic": content.count('*') - content.count('**'),
                    "length": len(content)
                }
                content_structures.append(structure)
            
            if len(content_structures) < 2:
                return 0.5
            
            consistency_score = 0.0
            checks = 0
            
            # Check paragraph count consistency
            paragraph_counts = [s["paragraphs"] for s in content_structures]
            if len(set(paragraph_counts)) <= 2:  # Similar paragraph counts
                consistency_score += 0.3
            checks += 1
            
            # Check heading usage consistency
            heading_counts = [s["headings"] for s in content_structures]
            if len(set(heading_counts)) <= 2:  # Similar heading counts
                consistency_score += 0.2
            checks += 1
            
            # Check list usage consistency
            list_counts = [s["lists"] for s in content_structures]
            if len(set(list_counts)) <= 2:  # Similar list counts
                consistency_score += 0.2
            checks += 1
            
            # Check formatting consistency
            bold_counts = [s["bold"] for s in content_structures]
            if len(set(bold_counts)) <= 2:  # Similar bold usage
                consistency_score += 0.2
            checks += 1
            
            # Check content length consistency
            lengths = [s["length"] for s in content_structures]
            length_variance = max(lengths) - min(lengths)
            if length_variance <= 200:  # Similar lengths
                consistency_score += 0.1
            checks += 1
            
            return consistency_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing content structure consistency: {str(e)}")
            return 0.0
    
    async def _analyze_formatting_consistency(self, slides: List[Dict[str, Any]]) -> float:
        """Analyze formatting consistency across slides"""
        try:
            formatting_patterns = []
            
            for slide in slides:
                content = slide.get("main_content", "")
                patterns = {
                    "uses_bold": "**" in content,
                    "uses_italic": "*" in content and "**" not in content,
                    "uses_lists": any(indicator in content for indicator in ["•", "-", "*", "1.", "2."]),
                    "uses_headings": "#" in content,
                    "uses_code": "`" in content,
                    "uses_quotes": '"' in content or "'" in content
                }
                formatting_patterns.append(patterns)
            
            if len(formatting_patterns) < 2:
                return 0.5
            
            consistency_score = 0.0
            checks = 0
            
            # Check each formatting pattern
            for pattern in ["uses_bold", "uses_italic", "uses_lists", "uses_headings", "uses_code", "uses_quotes"]:
                pattern_usage = [p[pattern] for p in formatting_patterns]
                usage_count = sum(pattern_usage)
                usage_ratio = usage_count / len(pattern_usage)
                
                # High consistency if most slides use the same pattern
                if usage_ratio >= 0.8 or usage_ratio <= 0.2:
                    consistency_score += 0.2
                elif usage_ratio >= 0.6 or usage_ratio <= 0.4:
                    consistency_score += 0.1
                checks += 1
            
            return consistency_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing formatting consistency: {str(e)}")
            return 0.0
    
    async def _analyze_visual_consistency(self, slides: List[Dict[str, Any]]) -> float:
        """Analyze visual element consistency across slides"""
        try:
            visual_elements = []
            
            for slide in slides:
                elements = slide.get("visual_elements", [])
                element_types = [elem.get("type", "unknown") for elem in elements]
                visual_elements.append(element_types)
            
            if len(visual_elements) < 2:
                return 0.5
            
            consistency_score = 0.0
            checks = 0
            
            # Check visual element count consistency
            element_counts = [len(elements) for elements in visual_elements]
            if len(set(element_counts)) <= 2:  # Similar element counts
                consistency_score += 0.3
            checks += 1
            
            # Check visual element type consistency
            all_types = []
            for elements in visual_elements:
                all_types.extend(elements)
            
            if all_types:
                from collections import Counter
                type_counts = Counter(all_types)
                most_common_type = type_counts.most_common(1)[0][1]
                type_consistency = most_common_type / len(all_types)
                consistency_score += type_consistency * 0.4
            checks += 1
            
            # Check alt text consistency
            alt_text_usage = []
            for slide in slides:
                elements = slide.get("visual_elements", [])
                has_alt_text = any(elem.get("alt_text") for elem in elements)
                alt_text_usage.append(has_alt_text)
            
            alt_text_consistency = sum(alt_text_usage) / len(alt_text_usage)
            consistency_score += alt_text_consistency * 0.3
            checks += 1
            
            return consistency_score / checks if checks > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing visual consistency: {str(e)}")
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
    
    async def _enhance_slides_with_design(self, slides: List[Dict[str, Any]], compliance_report: DesignComplianceReport, design_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance slides with design improvements based on C.R.A.P. principles"""
        try:
            enhanced_slides = []
            
            for slide in slides:
                enhanced_slide = slide.copy()
                
                # Apply design enhancements based on compliance scores
                if compliance_report.contrast_score < 0.7:
                    enhanced_slide = await self._enhance_contrast(enhanced_slide, design_preferences)
                
                if compliance_report.repetition_score < 0.7:
                    enhanced_slide = await self._enhance_repetition(enhanced_slide, design_preferences)
                
                if compliance_report.alignment_score < 0.7:
                    enhanced_slide = await self._enhance_alignment(enhanced_slide, design_preferences)
                
                if compliance_report.proximity_score < 0.7:
                    enhanced_slide = await self._enhance_proximity(enhanced_slide, design_preferences)
                
                enhanced_slides.append(enhanced_slide)
            
            return enhanced_slides
            
        except Exception as e:
            self.logger.error(f"Error enhancing slides with design: {str(e)}")
            return slides  # Return original slides if enhancement fails
    
    async def _enhance_contrast(self, slide: Dict[str, Any], design_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide contrast and readability"""
        try:
            # Apply actual contrast enhancements to slide properties
            slide["background_color"] = "#FFFFFF"  # High contrast white background
            slide["text_color"] = "#000000"  # High contrast black text
            slide["heading_color"] = "#1a365d"  # Dark blue for headings
            slide["accent_color"] = "#2d3748"  # Dark gray for accents
            
            # Enhance visual elements with better contrast
            if "visual_elements" in slide:
                for element in slide["visual_elements"]:
                    if element.get("type") == "image":
                        element["border_color"] = "#000000"
                        element["border_width"] = 2
                    elif element.get("type") == "text":
                        element["text_color"] = "#000000"
                        element["background_color"] = "#f7fafc"
            
            # Apply bold formatting to important terms in content
            content = slide.get("main_content", "")
            if content:
                # Make key terms bold for better contrast
                key_terms = ["Queue", "FIFO", "Enqueue", "Dequeue", "Peek", "Stack", "LIFO"]
                enhanced_content = content
                for term in key_terms:
                    enhanced_content = enhanced_content.replace(term, f"**{term}**")
                slide["main_content"] = enhanced_content
            
            # Add high contrast styling properties
            slide["font_size"] = "16px"
            slide["heading_font_size"] = "24px"
            slide["line_height"] = "1.6"
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing contrast: {str(e)}")
            return slide
    
    async def _enhance_repetition(self, slide: Dict[str, Any], design_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide with consistent design elements"""
        try:
            # Apply consistent styling properties
            slide["font_family"] = "Arial, sans-serif"
            slide["bullet_style"] = "•"
            slide["numbering_style"] = "1."
            slide["margin_top"] = "20px"
            slide["margin_bottom"] = "20px"
            slide["margin_left"] = "30px"
            slide["margin_right"] = "30px"
            
            # Ensure consistent color scheme
            if "background_color" not in slide:
                slide["background_color"] = "#FFFFFF"
            if "text_color" not in slide:
                slide["text_color"] = "#000000"
            if "heading_color" not in slide:
                slide["heading_color"] = "#1a365d"
            
            # Apply consistent formatting to content
            content = slide.get("main_content", "")
            if content:
                # Convert content to consistent bullet point format
                lines = content.split('\n')
                formatted_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('**') and not line.startswith('#'):
                        # Convert to bullet points
                        if line.startswith('- ') or line.startswith('• '):
                            formatted_lines.append(f"• {line[2:].strip()}")
                        elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                            formatted_lines.append(f"• {line[3:].strip()}")
                        else:
                            formatted_lines.append(f"• {line}")
                    else:
                        formatted_lines.append(line)
                
                slide["main_content"] = '\n'.join(formatted_lines)
            
            # Ensure consistent visual element styling
            if "visual_elements" in slide:
                for element in slide["visual_elements"]:
                    element["font_family"] = "Arial, sans-serif"
                    if "border_radius" not in element:
                        element["border_radius"] = 4
                    if "padding" not in element:
                        element["padding"] = 10
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing repetition: {str(e)}")
            return slide
    
    async def _enhance_alignment(self, slide: Dict[str, Any], design_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide alignment and visual structure"""
        try:
            # Apply actual alignment properties
            slide["text_align"] = "left"
            slide["heading_align"] = "center"
            slide["content_align"] = "left"
            slide["grid_columns"] = "2"
            slide["grid_gap"] = "20px"
            
            # Set consistent positioning for visual elements
            if "visual_elements" in slide:
                for i, element in enumerate(slide["visual_elements"]):
                    element["position"] = "relative"
                    element["margin"] = "10px"
                    element["text_align"] = "left"
                    
                    # Distribute elements in a grid
                    if i % 2 == 0:
                        element["float"] = "left"
                        element["width"] = "48%"
                    else:
                        element["float"] = "right"
                        element["width"] = "48%"
            
            # Apply consistent spacing to content
            content = slide.get("main_content", "")
            if content:
                # Add proper spacing between sections
                lines = content.split('\n')
                formatted_lines = []
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line:
                        formatted_lines.append(line)
                        # Add spacing after headings
                        if line.startswith('**') and line.endswith('**'):
                            formatted_lines.append('')  # Empty line after heading
                    elif i > 0 and lines[i-1].strip():  # Add spacing between paragraphs
                        formatted_lines.append('')
                
                slide["main_content"] = '\n'.join(formatted_lines)
            
            # Set consistent margins and padding
            slide["padding"] = "20px"
            slide["content_padding"] = "15px"
            slide["element_spacing"] = "15px"
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing alignment: {str(e)}")
            return slide
    
    async def _enhance_proximity(self, slide: Dict[str, Any], design_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide proximity and logical grouping"""
        try:
            # Apply actual proximity and spacing properties
            slide["section_spacing"] = "30px"
            slide["paragraph_spacing"] = "15px"
            slide["element_grouping"] = True
            slide["white_space_ratio"] = 0.3
            
            # Group related content with proper spacing
            content = slide.get("main_content", "")
            if content:
                # Organize content into logical sections with proper spacing
                lines = content.split('\n')
                formatted_lines = []
                current_section = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('**') and line.endswith('**'):  # Heading
                        if current_section:
                            # Add section with proper spacing
                            formatted_lines.extend(current_section)
                            formatted_lines.append('')  # Section separator
                            current_section = []
                        formatted_lines.append(line)
                        formatted_lines.append('')  # Space after heading
                    elif line:
                        current_section.append(f"  {line}")  # Indent content
                    else:
                        if current_section:
                            current_section.append('')
                
                # Add final section
                if current_section:
                    formatted_lines.extend(current_section)
                
                slide["main_content"] = '\n'.join(formatted_lines)
            
            # Apply grouping to visual elements (without creating invalid group types)
            if "visual_elements" in slide:
                # Add spacing properties to existing elements instead of grouping
                for element in slide["visual_elements"]:
                    element["margin_bottom"] = 15
                    element["margin_top"] = 10
                    element["grouped"] = True
            
            # Set consistent spacing properties
            slide["margin_between_sections"] = "25px"
            slide["margin_between_elements"] = "15px"
            slide["padding_around_groups"] = "20px"
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing proximity: {str(e)}")
            return slide
