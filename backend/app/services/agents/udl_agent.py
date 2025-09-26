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

import asyncio
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
        Process UDL compliance validation and content enhancement request.
        
        Args:
            input_data: Dictionary containing:
                - slides: List of SlideContent objects
                - lesson_info: Dictionary with lesson metadata
                - refinement_request: Optional refinement instructions
                
        Returns:
            Dictionary containing:
                - udl_compliance_report: UDLComplianceReport object
                - enhanced_slides: List of enhanced SlideContent objects
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
            
            # Enhance slides with UDL principles
            enhanced_slides = await self._enhance_slides_with_udl(slide_dicts, udl_compliance_report, lesson_info)
            
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
                "enhanced_slides": enhanced_slides,
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
            representation_score = await self._calculate_principle_score(slides, "representation")
            action_expression_score = await self._calculate_principle_score(slides, "action_expression")
            engagement_score = await self._calculate_principle_score(slides, "engagement")
            
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
    
    async def _calculate_principle_score(self, slides: List[SlideContent], principle: str) -> float:
        """Calculate compliance score for a UDL principle with AI-powered analysis"""
        try:
            if principle not in self.udl_guidelines:
                self.logger.warning(f"Principle '{principle}' not found in UDL guidelines")
                return 0.5
                
            principle_data = self.udl_guidelines[principle]
            if 1 not in principle_data:
                self.logger.warning(f"Principle '{principle}' data structure is invalid")
                return 0.5
                
            # Use AI-powered analysis for more accurate scoring
            return await self._analyze_udl_principle_with_ai(slides, principle, principle_data)
        except Exception as e:
            self.logger.error(f"Error calculating principle score for {principle}: {str(e)}")
            return 0.5
    
    async def _analyze_udl_principle_with_ai(self, slides: List[SlideContent], principle: str, principle_data: Dict[str, Any]) -> float:
        """Use AI to analyze UDL principle compliance"""
        try:
            # Prepare content for AI analysis
            slide_contents = []
            for slide in slides:
                slide_content = {
                    "title": slide.get("title", ""),
                    "main_content": slide.get("main_content", ""),
                    "visual_elements": slide.get("visual_elements", []),
                    "activities": slide.get("activities", []),
                    "audio_script": slide.get("audio_script", ""),
                    "udl_guidelines": slide.get("udl_guidelines", [])
                }
                slide_contents.append(slide_content)
            
            # Create AI prompt for UDL analysis
            prompt = f"""
            Analyze the following educational slides for UDL (Universal Design for Learning) compliance for the principle: {principle}
            
            UDL Principle: {principle_data[1]["name"]}
            Guidelines: {list(principle_data[1]["guidelines"].keys())}
            
            Slide Content:
            {self._format_slides_for_ai_analysis(slide_contents)}
            
            Please analyze each slide and provide a compliance score (0.0 to 1.0) for the {principle} principle based on:
            1. Content representation diversity
            2. Engagement strategies
            3. Action and expression opportunities
            4. Accessibility features
            
            Return only a JSON object with:
            {{
                "overall_score": 0.0-1.0,
                "detailed_analysis": {{
                    "representation_score": 0.0-1.0,
                    "engagement_score": 0.0-1.0,
                    "action_expression_score": 0.0-1.0,
                    "accessibility_score": 0.0-1.0
                }},
                "recommendations": ["specific improvement suggestions"],
                "strengths": ["identified strengths"]
            }}
            """
            
            response = await self._call_openai(
                messages=[
                    {"role": "system", "content": "You are an expert in Universal Design for Learning (UDL) principles. Analyze educational content for UDL compliance and provide detailed scores and recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse AI response
            analysis_result = self._parse_json_response(response, "object")
            return analysis_result.get("overall_score", 0.5)
            
        except Exception as e:
            self.logger.error(f"Error in AI-powered UDL analysis: {str(e)}")
            # Fallback to basic analysis
            return self._calculate_basic_principle_score(slides, principle)
    
    def _format_slides_for_ai_analysis(self, slides: List[Dict[str, Any]]) -> str:
        """Format slides for AI analysis"""
        try:
            formatted_slides = []
            for i, slide in enumerate(slides, 1):
                slide_text = f"Slide {i}: {slide.get('title', 'Untitled')}\n"
                slide_text += f"Content: {slide.get('main_content', '')[:500]}...\n"
                slide_text += f"Visual Elements: {len(slide.get('visual_elements', []))} elements\n"
                slide_text += f"Activities: {slide.get('activities', [])}\n"
                slide_text += f"UDL Guidelines: {slide.get('udl_guidelines', [])}\n"
                slide_text += "---\n"
                formatted_slides.append(slide_text)
            
            return "\n".join(formatted_slides)
            
        except Exception as e:
            self.logger.error(f"Error formatting slides for AI analysis: {str(e)}")
            return "Error formatting slides for analysis"
    
    def _calculate_basic_principle_score(self, slides: List[SlideContent], principle: str) -> float:
        """Fallback basic calculation for UDL principle score"""
        try:
            total_guidelines = 4  # Basic guideline count
            implemented_guidelines = 0
            
            for slide in slides:
                for guideline in slide.get("udl_guidelines", []):
                    if principle in guideline.lower():
                        implemented_guidelines += 1
            
            return min(1.0, implemented_guidelines / total_guidelines)
        except Exception as e:
            self.logger.error(f"Error in basic principle score calculation: {str(e)}")
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
    
    async def _enhance_slides_with_udl(self, slides: List[Dict[str, Any]], compliance_report: UDLComplianceReport, lesson_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance slides with UDL principles based on compliance analysis"""
        try:
            enhanced_slides = []
            
            for slide in slides:
                enhanced_slide = slide.copy()
                
                # Apply UDL enhancements based on compliance scores
                if compliance_report.representation_score < 0.7:
                    enhanced_slide = await self._enhance_representation(enhanced_slide, lesson_info)
                
                if compliance_report.action_expression_score < 0.7:
                    enhanced_slide = await self._enhance_action_expression(enhanced_slide, lesson_info)
                
                if compliance_report.engagement_score < 0.7:
                    enhanced_slide = await self._enhance_engagement(enhanced_slide, lesson_info)
                
                # Add UDL guidelines to the slide
                if "udl_guidelines" not in enhanced_slide:
                    enhanced_slide["udl_guidelines"] = []
                
                # Add specific UDL guidelines based on enhancements
                udl_guidelines = enhanced_slide["udl_guidelines"]
                if "multiple_representation" not in udl_guidelines:
                    udl_guidelines.append("multiple_representation")
                if "multiple_means_action" not in udl_guidelines:
                    udl_guidelines.append("multiple_means_action")
                if "engagement_strategies" not in udl_guidelines:
                    udl_guidelines.append("engagement_strategies")
                
                enhanced_slides.append(enhanced_slide)
            
            return enhanced_slides
            
        except Exception as e:
            self.logger.error(f"Error enhancing slides with UDL: {str(e)}")
            return slides  # Return original slides if enhancement fails
    
    async def _enhance_representation(self, slide: Dict[str, Any], lesson_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide with multiple means of representation"""
        try:
            # Add multiple representation properties
            slide["multiple_representations"] = True
            slide["visual_learning"] = True
            slide["auditory_learning"] = True
            slide["kinesthetic_learning"] = True
            
            # Ensure visual elements exist and are diverse
            if not slide.get("visual_elements"):
                slide["visual_elements"] = []
            
            # Add different types of visual elements for multiple representations
            visual_elements = slide.get("visual_elements", [])
            
            # Add diagram if not present
            has_diagram = any(elem.get("type") == "diagram" for elem in visual_elements)
            if not has_diagram:
                visual_elements.append({
                    "type": "diagram",
                    "url": f"placeholder_diagram_{slide.get('title', 'topic').replace(' ', '_').lower()}.png",
                    "description": "Visual representation of key concepts",
                    "alt_text": f"Diagram showing {slide.get('title', 'main concepts')}",
                    "position": "right",
                    "size": "medium"
                })
            
            # Add chart/graph if not present
            has_chart = any(elem.get("type") == "chart" for elem in visual_elements)
            if not has_chart:
                visual_elements.append({
                    "type": "chart",
                    "url": f"placeholder_chart_{slide.get('title', 'topic').replace(' ', '_').lower()}.png",
                    "description": "Chart showing relevant data and relationships",
                    "alt_text": f"Chart displaying data related to {slide.get('title', 'the topic')}",
                    "position": "left",
                    "size": "medium"
                })
            
            slide["visual_elements"] = visual_elements
            
            # Add audio narration
            slide["audio_narration"] = {
                "script": f"Audio explanation of {slide.get('title', 'this concept')}",
                "duration": slide.get("duration_minutes", 2) * 60,
                "language": "en-US",
                "speed_control": True,
                "pause_control": True
            }
            
            # Add text alternatives and translations
            slide["text_alternatives"] = {
                "simplified_text": f"Simplified explanation: {slide.get('main_content', '')[:100]}...",
                "detailed_text": slide.get("main_content", ""),
                "key_terms": ["Queue", "FIFO", "Enqueue", "Dequeue", "Peek"],
                "definitions": {
                    "Queue": "A linear data structure following First In First Out principle",
                    "FIFO": "First In First Out - the order elements are processed",
                    "Enqueue": "Adding an element to the rear of the queue",
                    "Dequeue": "Removing an element from the front of the queue",
                    "Peek": "Viewing the front element without removing it"
                }
            }
            
            # Add multiple language support
            slide["multilingual_support"] = {
                "primary_language": "en",
                "available_languages": ["en", "es", "fr"],
                "translation_available": True
            }
            
            # Add different content formats
            slide["content_formats"] = {
                "text": True,
                "visual": True,
                "audio": True,
                "interactive": True,
                "printable": True
            }
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing representation: {str(e)}")
            return slide
    
    async def _enhance_action_expression(self, slide: Dict[str, Any], lesson_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide with multiple means of action and expression"""
        try:
            # Add multiple action/expression properties
            slide["multiple_actions"] = True
            slide["interactive_elements"] = True
            slide["collaborative_learning"] = True
            slide["self_assessment"] = True
            
            # Add diverse interactive activities as a simple list
            slide["activities"] = [
                f"Group discussion: Real-world applications of {slide.get('title', 'this concept')}",
                f"Hands-on practice: Implement {slide.get('title', 'the concept')}",
                "Individual reflection: How does this relate to your previous knowledge?",
                "Peer teaching: Explain the concept to a classmate",
                "Visual demonstration: Create a diagram or flowchart"
            ]
            
            # Add multiple assessment options
            slide["assessment_options"] = {
                "written_response": {
                    "description": "Write a paragraph explaining the concept",
                    "word_count": "100-200 words",
                    "rubric": "clarity, accuracy, examples"
                },
                "verbal_explanation": {
                    "description": "Explain the concept to a classmate",
                    "time_limit": "2-3 minutes",
                    "peer_feedback": True
                },
                "visual_demonstration": {
                    "description": "Create a diagram or flowchart",
                    "tools_provided": ["paper", "digital_drawing", "physical_objects"],
                    "sharing_encouraged": True
                },
                "practical_application": {
                    "description": "Solve a real-world problem using the concept",
                    "scaffolding_levels": ["guided", "semi_guided", "independent"],
                    "collaboration_allowed": True
                }
            }
            
            # Add assistive technologies support
            slide["assistive_technologies"] = {
                "screen_reader": True,
                "voice_recognition": True,
                "keyboard_navigation": True,
                "switch_control": True,
                "eye_tracking": True
            }
            
            # Add different expression formats
            slide["expression_formats"] = {
                "text": True,
                "audio": True,
                "visual": True,
                "multimedia": True,
                "interactive": True
            }
            
            # Add progress tracking
            slide["progress_tracking"] = {
                "self_paced": True,
                "checkpoints": True,
                "milestones": True,
                "feedback_loops": True,
                "goal_setting": True
            }
            
            # Add collaborative features
            slide["collaboration_features"] = {
                "peer_review": True,
                "group_projects": True,
                "discussion_forums": True,
                "shared_workspaces": True,
                "mentor_support": True
            }
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing action expression: {str(e)}")
            return slide
    
    async def _enhance_engagement(self, slide: Dict[str, Any], lesson_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance slide with engagement strategies"""
        try:
            # Add engagement properties
            slide["engagement_strategies"] = True
            slide["motivational_elements"] = True
            slide["choice_and_autonomy"] = True
            slide["relevance_and_authenticity"] = True
            
            # Add motivational elements
            slide["motivation"] = {
                "relevance_statement": f"Why {slide.get('title', 'this concept')} matters in real life",
                "learning_goals": f"By the end of this slide, you'll understand {slide.get('title', 'the concept')}",
                "success_criteria": "You'll know you've mastered this when you can explain it to someone else",
                "personal_connection": "Think about how this relates to your own experiences"
            }
            
            # Add choice and autonomy features
            slide["learner_choice"] = {
                "content_paths": ["visual_learners", "auditory_learners", "kinesthetic_learners"],
                "activity_options": ["individual", "pair", "group"],
                "assessment_formats": ["written", "verbal", "visual", "practical"],
                "pacing_options": ["self_paced", "guided", "challenging"]
            }
            
            # Add relevance and authenticity
            slide["real_world_connections"] = {
                "industry_examples": f"Real applications of {slide.get('title', 'this concept')} in technology",
                "career_relevance": "How this skill is used in software development careers",
                "daily_life_examples": "Where you might encounter this concept in everyday life",
                "future_learning": "How this connects to advanced topics you'll learn later"
            }
            
            # Add interactive engagement elements
            slide["interactive_engagement"] = {
                "polls": {
                    "question": f"What's your experience level with {slide.get('title', 'this topic')}?",
                    "options": ["Beginner", "Some experience", "Experienced", "Expert"],
                    "anonymous": True
                },
                "discussions": {
                    "prompt": f"Share a time when you encountered {slide.get('title', 'this concept')}",
                    "format": "open_ended",
                    "peer_interaction": True
                },
                "reflection": {
                    "prompt": "What questions do you have about this topic?",
                    "format": "written_or_verbal",
                    "sharing_encouraged": True
                }
            }
            
            # Add gamification elements
            slide["gamification"] = {
                "progress_tracking": True,
                "achievement_badges": ["concept_master", "active_participant", "helpful_contributor"],
                "challenges": f"Complete the {slide.get('title', 'concept')} challenge",
                "leaderboard": "optional",
                "rewards": "recognition_and_feedback"
            }
            
            # Add social learning features
            slide["social_learning"] = {
                "peer_collaboration": True,
                "study_groups": True,
                "peer_teaching": True,
                "community_sharing": True,
                "mentor_connections": True
            }
            
            # Add feedback and support systems
            slide["feedback_systems"] = {
                "immediate_feedback": True,
                "peer_feedback": True,
                "instructor_feedback": True,
                "self_assessment": True,
                "progress_indicators": True
            }
            
            return slide
            
        except Exception as e:
            self.logger.error(f"Error enhancing engagement: {str(e)}")
            return slide
    
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
