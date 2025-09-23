"""
UDL Agent for Multi-Agent Lesson Planning System

This agent is responsible for Universal Design for Learning (UDL) compliance validation:
- UDL principle compliance scoring
- Accessibility feature validation
- Content modality analysis
- UDL guideline recommendations
- Compliance report generation

The agent ensures that all generated content adheres to UDL principles and
provides comprehensive accessibility for diverse learners.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ...models.udl_content import (
    UDLComplianceReport, UDLPrinciple, ContentModality
)
from ...models.gagne_slides import SlideContent

logger = logging.getLogger(__name__)


class UDLAgent(BaseAgent):
    """
    Agent responsible for UDL compliance validation and accessibility assessment.
    
    This agent handles:
    - UDL principle compliance scoring
    - Accessibility feature validation
    - Content modality analysis
    - UDL guideline recommendations
    - Compliance report generation
    """
    
    def __init__(self, client=None):
        """Initialize the UDL Agent."""
        super().__init__(client)
        self.logger = logging.getLogger(f"agents.{self.__class__.__name__}")
        self.udl_guidelines = self._initialize_udl_guidelines()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process UDL compliance validation request.
        
        Args:
            input_data: Dictionary containing:
                - slides: List of SlideContent objects
                - lesson_info: Dictionary with lesson metadata
                - refinement_request: Optional refinement instructions
                
        Returns:
            Dictionary containing:
                - udl_compliance_report: UDLComplianceReport object
                - recommendations: List of improvement recommendations
                - accessibility_features: List of implemented features
                - metadata: Processing metadata
        """
        try:
            slides = input_data.get("slides", [])
            lesson_info = input_data.get("lesson_info", {})
            refinement_request = input_data.get("refinement_request")
            
            if not slides:
                raise ValueError("slides are required for UDL validation")
            
            # Convert slides to dictionaries if they are objects
            slide_dicts = []
            for slide in slides:
                if isinstance(slide, dict):
                    slide_dicts.append(slide)
                else:
                    slide_dicts.append(slide.dict())
            
            self._log_processing_start(f"Validating UDL compliance for {len(slide_dicts)} slides")
            
            # Calculate UDL compliance
            udl_compliance_report = await self._calculate_udl_compliance(slide_dicts, lesson_info)
            
            # Generate recommendations
            recommendations = self._generate_udl_recommendations(slide_dicts, udl_compliance_report.missing_guidelines)
            
            # Extract accessibility features
            accessibility_features = self._extract_accessibility_features(slide_dicts)
            
            # Handle refinement request if provided
            refined_content = None
            if refinement_request:
                refined_content = await self._refine_content_for_udl(refinement_request, slide_dicts)
            
            result = {
                "udl_compliance_report": udl_compliance_report.dict(),
                "recommendations": recommendations,
                "accessibility_features": accessibility_features
            }
            
            if refined_content:
                result["refined_content"] = refined_content
            
            metadata = {
                "total_slides": len(slides),
                "overall_compliance": udl_compliance_report.overall_compliance,
                "representation_score": udl_compliance_report.representation_score,
                "action_expression_score": udl_compliance_report.action_expression_score,
                "engagement_score": udl_compliance_report.engagement_score,
                "missing_guidelines_count": len(udl_compliance_report.missing_guidelines)
            }
            
            self._log_processing_success(f"UDL compliance validation completed - Overall score: {udl_compliance_report.overall_compliance:.2f}")
            
            return self._create_success_response(result, metadata)
            
        except Exception as e:
            self._log_processing_error(e)
            return self._create_error_response(e)
    
    def _initialize_udl_guidelines(self) -> Dict[str, Any]:
        """Initialize UDL guidelines with implementation strategies"""
        return {
            "representation": {
                1: {
                    "name": "Provide Multiple Means of Representation",
                    "guidelines": {
                        "perception": {
                            "name": "Perception",
                            "strategies": ["Customize display", "Provide alternatives for auditory info", "Provide alternatives for visual info"],
                            "modalities": ["visual", "auditory", "textual"]
                        },
                        "language": {
                            "name": "Language & Symbols",
                            "strategies": ["Clarify vocabulary", "Clarify syntax", "Support decoding", "Promote understanding across languages"],
                            "modalities": ["textual", "visual", "interactive"]
                        },
                        "comprehension": {
                            "name": "Comprehension",
                            "strategies": ["Activate background knowledge", "Highlight patterns", "Guide information processing", "Maximize transfer"],
                            "modalities": ["textual", "visual", "interactive", "kinesthetic"]
                        }
                    }
                }
            },
            "action_expression": {
                1: {
                    "name": "Provide Multiple Means of Action & Expression",
                    "guidelines": {
                        "physical_action": {
                            "name": "Physical Action",
                            "strategies": ["Vary methods for response", "Optimize access to tools"],
                            "modalities": ["kinesthetic", "interactive"]
                        },
                        "expression": {
                            "name": "Expression & Communication",
                            "strategies": ["Use multiple media", "Build fluencies", "Practice with graduated support"],
                            "modalities": ["textual", "visual", "auditory", "interactive"]
                        },
                        "executive_functions": {
                            "name": "Executive Functions",
                            "strategies": ["Guide goal setting", "Support planning", "Manage resources", "Enhance capacity for monitoring"],
                            "modalities": ["textual", "visual", "interactive"]
                        }
                    }
                }
            },
            "engagement": {
                1: {
                    "name": "Provide Multiple Means of Engagement",
                    "guidelines": {
                        "recruiting_interest": {
                            "name": "Recruiting Interest",
                            "strategies": ["Optimize individual choice", "Optimize relevance", "Minimize threats"],
                            "modalities": ["visual", "interactive", "kinesthetic"]
                        },
                        "sustaining_effort": {
                            "name": "Sustaining Effort & Persistence",
                            "strategies": ["Heighten salience of goals", "Vary demands", "Foster collaboration", "Increase mastery-oriented feedback"],
                            "modalities": ["interactive", "visual", "textual"]
                        },
                        "self_regulation": {
                            "name": "Self-Regulation",
                            "strategies": ["Guide personal coping skills", "Develop self-assessment", "Promote expectations and beliefs"],
                            "modalities": ["textual", "interactive", "visual"]
                        }
                    }
                }
            }
        }
    
    async def _calculate_udl_compliance(self, slides: List[SlideContent], lesson_info: Dict[str, Any]) -> UDLComplianceReport:
        """Calculate UDL compliance score and provide recommendations"""
        try:
            # Analyze representation
            representation_score = self._calculate_principle_score(slides, "representation")
            action_expression_score = self._calculate_principle_score(slides, "action_expression")
            engagement_score = self._calculate_principle_score(slides, "engagement")
            
            overall_compliance = (representation_score + action_expression_score + engagement_score) / 3
            
            # Identify missing guidelines
            missing_guidelines = self._identify_missing_guidelines(slides)
            
            # Generate recommendations
            recommendations = self._generate_udl_recommendations(slides, missing_guidelines)
            
            return UDLComplianceReport(
                representation_score=representation_score,
                action_expression_score=action_expression_score,
                engagement_score=engagement_score,
                overall_compliance=overall_compliance,
                missing_guidelines=missing_guidelines,
                recommendations=recommendations,
                accessibility_features_implemented=self._extract_accessibility_features(slides)
            )
        except Exception as e:
            self.logger.error(f"Error in _calculate_udl_compliance: {str(e)}")
            # Return default compliance report
            return UDLComplianceReport(
                representation_score=0.5,
                action_expression_score=0.5,
                engagement_score=0.5,
                overall_compliance=0.5,
                missing_guidelines=[],
                recommendations=["Unable to calculate compliance due to error"],
                accessibility_features_implemented=[]
            )
    
    def _calculate_principle_score(self, slides: List[SlideContent], principle: str) -> float:
        """Calculate compliance score for a UDL principle"""
        try:
            if principle not in self.udl_guidelines:
                self.logger.warning(f"Principle '{principle}' not found in UDL guidelines")
                return 0.5
                
            principle_data = self.udl_guidelines[principle]
            if 1 not in principle_data:
                self.logger.warning(f"Principle '{principle}' data structure is invalid")
                return 0.5
                
            total_guidelines = len(principle_data[1]["guidelines"])
            if total_guidelines == 0:
                self.logger.warning(f"No guidelines found for principle '{principle}'")
                return 0.5
                
            implemented_guidelines = 0
            
            for slide in slides:
                for guideline in slide.get("udl_guidelines", []):
                    if principle in guideline.lower():
                        implemented_guidelines += 1
            
            return min(1.0, implemented_guidelines / total_guidelines)
        except Exception as e:
            self.logger.error(f"Error calculating principle score for {principle}: {str(e)}")
            return 0.5
    
    def _identify_missing_guidelines(self, slides: List[SlideContent]) -> List[str]:
        """Identify UDL guidelines that are not implemented"""
        try:
            implemented = set()
            for slide in slides:
                implemented.update(slide.get("udl_guidelines", []))
            
            all_guidelines = set()
            for principle_name, principle_data in self.udl_guidelines.items():
                if 1 in principle_data and "guidelines" in principle_data[1]:
                    for guideline_group in principle_data[1]["guidelines"].values():
                        if "name" in guideline_group:
                            all_guidelines.add(guideline_group["name"])
            
            return list(all_guidelines - implemented)
        except Exception as e:
            self.logger.error(f"Error identifying missing guidelines: {str(e)}")
            return []
    
    def _generate_udl_recommendations(self, slides: List[SlideContent], missing_guidelines: List[str]) -> List[str]:
        """Generate specific recommendations for improving UDL compliance"""
        try:
            recommendations = []
            
            if "Perception" in missing_guidelines:
                recommendations.append("Add audio descriptions and visual alternatives for all content")
            
            if "Language & Symbols" in missing_guidelines:
                recommendations.append("Include vocabulary definitions and multiple language support")
            
            if "Physical Action" in missing_guidelines:
                recommendations.append("Provide alternative response methods and optimize tool access")
            
            if "Recruiting Interest" in missing_guidelines:
                recommendations.append("Add choice-based activities and relevant real-world examples")
            
            # Additional recommendations based on content analysis
            if not any("multiple_representation" in slide.get("udl_guidelines", []) for slide in slides):
                recommendations.append("Implement multiple means of representation across all slides")
            
            if not any("engagement" in slide.get("udl_guidelines", []) for slide in slides):
                recommendations.append("Add engagement strategies to increase student motivation")
            
            if not any("action_expression" in slide.get("udl_guidelines", []) for slide in slides):
                recommendations.append("Provide multiple means of action and expression for student responses")
            
            return recommendations
        except Exception as e:
            self.logger.error(f"Error generating UDL recommendations: {str(e)}")
            return ["Ensure all UDL principles are properly implemented"]
    
    def _extract_accessibility_features(self, slides: List[Any]) -> List[str]:
        """Extract all accessibility features from slides"""
        try:
            features = set()
            for slide in slides:
                # Handle both dictionary and object inputs
                if isinstance(slide, dict):
                    slide_features = slide.get("accessibility_features", [])
                else:
                    slide_features = getattr(slide, "accessibility_features", [])
                
                if slide_features:
                    features.update(slide_features)
            return list(features)
        except Exception as e:
            self.logger.error(f"Error extracting accessibility features: {str(e)}")
            return []
    
    async def _refine_content_for_udl(self, refinement_request: Dict[str, Any], slides: List[SlideContent]) -> Dict[str, Any]:
        """Refine content based on UDL principles using AI"""
        try:
            slide_id = refinement_request.get("slide_id")
            refinement_type = refinement_request.get("refinement_type")
            instructions = refinement_request.get("refinement_instructions")
            current_content = refinement_request.get("current_content", {})
            
            # Find the specific slide if slide_id is provided
            target_slide = None
            if slide_id:
                target_slide = next((slide for slide in slides if slide.slide_number == slide_id), None)
            
            if not target_slide:
                target_slide = slides[0] if slides else None
            
            if not target_slide:
                return {"error": "No slides available for refinement"}
            
            prompt = f"""
Refine the following slide content to improve {refinement_type} and enhance UDL compliance:

CURRENT SLIDE CONTENT:
Title: {target_slide.title}
Content: {target_slide.main_content}
Current UDL Guidelines: {', '.join(target_slide.get("udl_guidelines", []))}
Current Accessibility Features: {', '.join(target_slide.get("accessibility_features", []))}

REFINEMENT INSTRUCTIONS:
{instructions}

UDL PRINCIPLES TO APPLY:
- Representation: Multiple means of presenting information (visual, auditory, textual)
- Action & Expression: Multiple ways for students to respond and demonstrate learning
- Engagement: Multiple ways to motivate and engage learners

ACCESSIBILITY REQUIREMENTS:
- Ensure all visual content has alt text
- Provide keyboard navigation support
- Include screen reader compatibility
- Use high contrast and readable fonts
- Provide multiple content modalities

Return the refined content in JSON format with:
- title: Updated slide title
- main_content: Enhanced markdown content
- udl_guidelines: Array of UDL guidelines implemented
- accessibility_features: Array of accessibility features
- visual_elements: Array of visual elements with proper accessibility
- audio_script: Enhanced audio narration
- speaker_notes: Updated teaching notes

Focus on making the content more accessible, engaging, and compliant with UDL principles.
"""
            
            response = await self._call_openai(
                messages=[
                    {"role": "system", "content": "You are an expert in UDL principles and accessible content creation. Return only valid JSON with no additional text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            try:
                refined_content = self._parse_json_response(response, "object")
                return {"refined_content": refined_content}
            except Exception as e:
                self.logger.warning(f"Failed to parse refined content: {str(e)}")
                return {"refined_content": current_content}
                
        except Exception as e:
            self.logger.error(f"Error in _refine_content_for_udl: {str(e)}")
            return {"refined_content": refinement_request.get("current_content", {})}
    
    def get_udl_guidelines(self) -> Dict[str, Any]:
        """Get UDL guidelines and implementation strategies"""
        return {"udl_guidelines": self.udl_guidelines}
    
    def get_content_modalities(self) -> Dict[str, Any]:
        """Get available content modalities for multimodal learning"""
        modalities = {
            "visual": {
                "name": "Visual",
                "description": "Content that can be seen and processed visually",
                "examples": ["Images", "Diagrams", "Charts", "Videos", "Animations"],
                "accessibility_features": ["Alt text", "High contrast", "Large fonts", "Color coding"]
            },
            "auditory": {
                "name": "Auditory",
                "description": "Content that can be heard and processed aurally",
                "examples": ["Audio narration", "Podcasts", "Music", "Sound effects"],
                "accessibility_features": ["Transcripts", "Captions", "Audio descriptions", "Volume control"]
            },
            "textual": {
                "name": "Textual",
                "description": "Written content that can be read",
                "examples": ["Text", "Documents", "Articles", "Notes"],
                "accessibility_features": ["Screen readers", "Text-to-speech", "Font size adjustment", "Line spacing"]
            },
            "kinesthetic": {
                "name": "Kinesthetic",
                "description": "Content that involves physical movement and interaction",
                "examples": ["Hands-on activities", "Simulations", "Interactive exercises"],
                "accessibility_features": ["Alternative input methods", "Assistive technologies", "Physical accommodations"]
            },
            "interactive": {
                "name": "Interactive",
                "description": "Content that responds to user input and engagement",
                "examples": ["Quizzes", "Games", "Simulations", "Virtual labs"],
                "accessibility_features": ["Keyboard navigation", "Voice control", "Alternative input devices"]
            }
        }
        return {"content_modalities": modalities}
    
    def get_accessibility_features(self) -> Dict[str, Any]:
        """Get available accessibility features for course content"""
        features = {
            "visual_accessibility": [
                "Alt text for images",
                "High contrast mode",
                "Large font options",
                "Color-blind friendly palettes",
                "Screen reader compatibility"
            ],
            "auditory_accessibility": [
                "Closed captions",
                "Audio transcripts",
                "Audio descriptions",
                "Volume controls",
                "Background noise reduction"
            ],
            "cognitive_accessibility": [
                "Clear navigation",
                "Consistent layout",
                "Simple language",
                "Step-by-step instructions",
                "Progress indicators"
            ],
            "physical_accessibility": [
                "Keyboard navigation",
                "Voice control support",
                "Alternative input devices",
                "Adjustable timing",
                "Physical accommodation options"
            ]
        }
        return {"accessibility_features": features}
    
    async def validate_slide_udl_compliance(self, slide: SlideContent) -> Dict[str, Any]:
        """Validate UDL compliance for a single slide"""
        try:
            compliance_issues = []
            recommendations = []
            
            # Check representation
            if not slide.visual_elements:
                compliance_issues.append("No visual elements for multiple representation")
                recommendations.append("Add visual elements with alt text")
            
            if not slide.audio_script:
                compliance_issues.append("No audio script for auditory representation")
                recommendations.append("Add audio narration script")
            
            # Check action and expression
            if not slide.activities:
                compliance_issues.append("No interactive activities for action/expression")
                recommendations.append("Add hands-on activities or interactive elements")
            
            # Check engagement
            if not any("engagement" in guideline for guideline in slide.get("udl_guidelines", [])):
                compliance_issues.append("Missing engagement strategies")
                recommendations.append("Add engagement-focused UDL guidelines")
            
            # Check accessibility
            if not slide.accessibility_features:
                compliance_issues.append("No accessibility features implemented")
                recommendations.append("Add basic accessibility features like alt text and keyboard navigation")
            
            compliance_score = max(0, 1.0 - (len(compliance_issues) * 0.2))
            
            return {
                "slide_number": slide.slide_number,
                "compliance_score": compliance_score,
                "issues": compliance_issues,
                "recommendations": recommendations,
                "udl_guidelines_implemented": slide.get("udl_guidelines", []),
                "accessibility_features_implemented": slide.get("accessibility_features", [])
            }
            
        except Exception as e:
            self.logger.error(f"Error validating slide UDL compliance: {str(e)}")
            return {
                "slide_number": slide.slide_number,
                "compliance_score": 0.0,
                "issues": ["Error during validation"],
                "recommendations": ["Contact support for assistance"],
                "udl_guidelines_implemented": [],
                "accessibility_features_implemented": []
            }
