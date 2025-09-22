"""
Plan Agent for Multi-Agent Lesson Planning System

This agent is responsible for generating the core lesson planning components:
- Learning objectives based on Bloom's Taxonomy
- Comprehensive lesson plans
- Gagne's Nine Events of Instruction with pedagogically-based time distribution

The agent uses advanced pedagogical principles and cognitive load theory to create
educationally sound lesson plans that are appropriate for different grade levels
and lesson durations.
"""

import json
import logging
from typing import Dict, Any, List
from ..base_agent import BaseAgent
from ...models.lesson import (
    LessonRequest, LessonObjective, LessonPlan, GagneEvent, 
    BloomLevel, GradeLevel
)

logger = logging.getLogger(__name__)


class PlanAgent(BaseAgent):
    """
    Agent responsible for generating lesson planning components.
    
    This agent handles:
    - Learning objective generation using Bloom's Taxonomy
    - Lesson plan creation with comprehensive details
    - Gagne's Nine Events with intelligent time distribution
    - Pedagogical optimization based on cognitive load theory
    """
    
    def __init__(self, client=None):
        """Initialize the Plan Agent."""
        super().__init__(client)
        self.logger = logging.getLogger(f"agents.{self.__class__.__name__}")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process lesson planning request and generate all planning components.
        
        Args:
            input_data: Dictionary containing:
                - lesson_request: LessonRequest object
                - processed_files: Dictionary with file processing results
                
        Returns:
            Dictionary containing:
                - objectives: List of LessonObjective objects
                - lesson_plan: LessonPlan object
                - gagne_events: List of GagneEvent objects
                - metadata: Processing metadata
        """
        try:
            lesson_request = input_data.get("lesson_request")
            processed_files = input_data.get("processed_files", {})
            
            if not lesson_request:
                raise ValueError("lesson_request is required")
            
            self._log_processing_start(f"Course: {lesson_request.course_title}, Topic: {lesson_request.lesson_topic}")
            
            # Generate all planning components
            objectives = await self._generate_objectives(lesson_request, processed_files)
            lesson_plan = await self._generate_lesson_plan(lesson_request, processed_files)
            gagne_events = await self._generate_gagne_events(lesson_request, objectives, lesson_plan, processed_files)
            
            result = {
                "objectives": [obj.dict() for obj in objectives],
                "lesson_plan": lesson_plan.dict(),
                "gagne_events": [event.dict() for event in gagne_events]
            }
            
            metadata = {
                "objectives_count": len(objectives),
                "events_count": len(gagne_events),
                "total_duration": lesson_request.duration_minutes,
                "grade_level": lesson_request.grade_level,
                "bloom_levels": [level.value for level in lesson_request.selected_bloom_levels]
            }
            
            self._log_processing_success(f"Generated {len(objectives)} objectives, 1 lesson plan, {len(gagne_events)} Gagne events")
            
            return self._create_success_response(result, metadata)
            
        except Exception as e:
            self._log_processing_error(e)
            return self._create_error_response(e)
    
    async def _generate_objectives(self, request: LessonRequest, processed_files: Dict[str, Any]) -> List[LessonObjective]:
        """Generate detailed learning objectives based on Bloom's taxonomy."""
        
        selected_levels = [level.value for level in request.selected_bloom_levels]
        
        # Calculate appropriate number of objectives based on pedagogical principles
        total_objectives = self._calculate_optimal_objectives_count(request)
        objectives_distribution = self._distribute_objectives_pedagogically(request, total_objectives)
        
        # Create pedagogically informed prompt
        prompt = f"""
You are an expert instructional designer following Bloom's Taxonomy principles and modern educational research.

LESSON CONTEXT:
Course: {request.course_title}
Topic: {request.lesson_topic}
Level: {request.grade_level}
Duration: {request.duration_minutes} minutes

UPLOADED MATERIALS CONTEXT:
{processed_files.get("ai_context", "No additional materials provided")}

IMPORTANT: Use the uploaded materials to understand the course context and student knowledge level. 
- If this is an early lesson in a course, avoid referencing concepts that haven't been taught yet
- If specific materials, images, or data are provided, incorporate them appropriately
- Ensure objectives align with the course progression and prerequisites shown in the materials

PEDAGOGICAL REQUIREMENTS:
Create exactly {total_objectives} learning objectives following these research-based principles:

1. COGNITIVE LOAD THEORY: Limit to {total_objectives} objectives for optimal retention
2. BLOOM'S HIERARCHY: Ensure foundational levels support higher-order thinking
3. SCAFFOLDING: Build complexity progressively
4. CONTEXT APPROPRIATENESS: Match cognitive demand to student level based on uploaded materials

OBJECTIVE DISTRIBUTION:
{self._format_distribution_guidance(objectives_distribution, selected_levels)}

QUALITY STANDARDS:
- Each objective must be specific, measurable, and achievable in {request.duration_minutes} minutes
- Use appropriate cognitive verbs for each Bloom's level
- Include realistic conditions and criteria
- Focus on depth over breadth (Bloom's emphasis on mastery)
- Ensure objectives are contextually appropriate based on uploaded course materials

COGNITIVE VERBS BY LEVEL:
- Remember: recall, recognize, identify, define, list, name
- Understand: explain, interpret, summarize, classify, compare, discuss
- Apply: implement, demonstrate, solve, use, execute, apply
- Analyze: analyze, examine, compare, differentiate, organize, deconstruct
- Evaluate: evaluate, critique, judge, defend, justify, assess
- Create: create, design, construct, develop, formulate, compose

Return ONLY a JSON array with exactly {total_objectives} objectives (use lowercase for bloom_level):
[{{"bloom_level": "remember", "objective": "Students will be able to...", "action_verb": "verb", "content": "specific content", "condition": "realistic condition", "criteria": "measurable criteria"}}]
"""
        
        try:
            response = await self._call_openai(
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer specializing in Bloom's taxonomy. You must generate the exact number of objectives requested. Return only valid JSON with no additional text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            # Parse and validate response
            objectives_data = self._parse_json_response(response, "array")
            
            # Fix case sensitivity issue - convert bloom_level to lowercase
            for obj in objectives_data:
                if 'bloom_level' in obj:
                    obj['bloom_level'] = obj['bloom_level'].lower()
            
            # Validate we have appropriate number of objectives
            optimal_count = self._calculate_optimal_objectives_count(request)
            if len(objectives_data) < optimal_count * 0.8:  # Allow 20% tolerance
                self.logger.warning(f"Only {len(objectives_data)} objectives generated, expected around {optimal_count}. Using fallback.")
                return self._create_comprehensive_fallback_objectives(request)
            
            # Validate objective structure
            for i, obj in enumerate(objectives_data):
                if not all(key in obj for key in ['bloom_level', 'objective', 'action_verb', 'content']):
                    self.logger.warning(f"Objective {i} missing required fields: {obj}. Using fallback.")
                    return self._create_comprehensive_fallback_objectives(request)
            
            self.logger.info(f"Successfully generated {len(objectives_data)} objectives from AI")
            return [LessonObjective(**obj) for obj in objectives_data]
            
        except Exception as e:
            self.logger.warning(f"AI objective generation failed: {str(e)}. Using fallback.")
            return self._create_comprehensive_fallback_objectives(request)
    
    async def _generate_lesson_plan(self, request: LessonRequest, processed_files: Dict[str, Any]) -> LessonPlan:
        """Generate a comprehensive lesson plan."""
        
        # Format grade level properly for the prompt
        grade_level_display = {
            "freshman": "freshman",
            "sophomore": "sophomore", 
            "junior": "junior",
            "senior": "senior",
            "masters": "master's",
            "postgrad": "postgraduate"
        }.get(request.grade_level, request.grade_level)
        
        prompt = f"""
Create a comprehensive lesson plan for {grade_level_display} students in a course titled "{request.course_title}" 
for a lesson on "{request.lesson_topic}" lasting {request.duration_minutes} minutes.

UPLOADED MATERIALS CONTEXT:
{processed_files.get("ai_context", "No additional materials provided")}

IMPORTANT: Use the uploaded materials to understand the course context and student knowledge level.
- If this is an early lesson in a course, avoid referencing concepts that haven't been taught yet
- If specific materials, images, or data are provided, incorporate them appropriately
- Ensure the lesson plan aligns with the course progression and prerequisites shown in the materials

IMPORTANT FORMATTING GUIDELINES:
- Write the overview in complete, professional sentences
- Use "{grade_level_display}" when referring to the student level
- Make the overview engaging and descriptive (2-3 sentences)
- Focus on what students will learn and how they will learn it
- Include the learning approach and key activities
- DO NOT use template variables like "GradeLevel.MASTERS"
- Incorporate relevant content from uploaded materials when appropriate

Generate a detailed lesson plan including:
1. Clear, engaging lesson overview that describes what students will learn and how
2. Prerequisites students should have (based on uploaded materials)
3. Materials and resources needed (including any from uploaded files)
4. Technology requirements
5. Assessment methods
6. Differentiation strategies for diverse learners
7. Closure activities

Make it practical and actionable for college instructors.

Return as JSON with this structure:
{{
    "title": "Engaging lesson title",
    "overview": "This comprehensive lesson introduces {grade_level_display} students to [specific topic concepts], focusing on [key learning goals]. Students will explore [main concepts] through [teaching methods such as interactive discussions, hands-on activities, case studies]. The lesson combines theoretical understanding with practical application to ensure deep comprehension of [core topic elements].",
    "prerequisites": ["prerequisite 1", "prerequisite 2"],
    "materials": ["material 1", "material 2"],
    "technology_requirements": ["tech 1", "tech 2"],
    "assessment_methods": ["method 1", "method 2"],
    "differentiation_strategies": ["strategy 1", "strategy 2"],
    "closure_activities": ["activity 1", "activity 2"]
}}
"""
        
        try:
            response = await self._call_openai(
                messages=[
                    {"role": "system", "content": "You are an expert instructional designer. Create engaging, professional lesson overviews. Never use template variables like 'GradeLevel.MASTERS' - always use proper, natural language formatting. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            lesson_data = self._parse_json_response(response, "object")
            
            # Post-process the overview to ensure proper formatting
            if 'overview' in lesson_data:
                overview = lesson_data['overview']
                # Clean up any remaining template variables
                overview = overview.replace('GradeLevel.MASTERS', 'master\'s')
                overview = overview.replace('GradeLevel.FRESHMAN', 'freshman')
                overview = overview.replace('GradeLevel.SOPHOMORE', 'sophomore')
                overview = overview.replace('GradeLevel.JUNIOR', 'junior')
                overview = overview.replace('GradeLevel.SENIOR', 'senior')
                overview = overview.replace('GradeLevel.POSTGRAD', 'postgraduate')
                overview = overview.replace('GradeLevel.', '')
                lesson_data['overview'] = overview
            
            return LessonPlan(**lesson_data)
            
        except Exception as e:
            self.logger.warning(f"AI lesson plan generation failed: {str(e)}. Using fallback.")
            return self._create_fallback_lesson_plan(request)
    
    async def _generate_gagne_events(self, request: LessonRequest, objectives: List[LessonObjective], 
                                   lesson_plan: LessonPlan, processed_files: Dict[str, Any]) -> List[GagneEvent]:
        """Generate Gagne's Nine Events of Instruction with pedagogically-based time distribution."""
        
        objectives_text = "\n".join([obj.objective for obj in objectives])
        
        # Calculate pedagogically-based time distribution
        time_distribution = self._calculate_gagne_time_distribution(request)
        time_guidance = self._format_time_distribution_guidance(time_distribution, request.duration_minutes)
        
        # Determine lesson focus for content guidance
        selected_levels = [level.value for level in request.selected_bloom_levels]
        practical_levels = {"apply", "analyze", "evaluate", "create"}
        is_practical_focused = len([l for l in selected_levels if l in practical_levels]) >= len(selected_levels) / 2
        
        focus_guidance = "PRACTICAL/SKILLS-FOCUSED lesson" if is_practical_focused else "THEORETICAL/KNOWLEDGE-FOCUSED lesson"
        
        prompt = f"""
Design specific activities for ALL NINE of Gagne's Events of Instruction for this {focus_guidance}:

Course: {request.course_title}
Topic: {request.lesson_topic}
Level: {request.grade_level}
Duration: {request.duration_minutes} minutes
Focus: {focus_guidance}

UPLOADED MATERIALS CONTEXT:
{processed_files.get("ai_context", "No additional materials provided")}

Learning Objectives:
{objectives_text}

{time_guidance}

IMPORTANT: Use the uploaded materials to create contextually appropriate activities.
- If this is an early lesson in a course, avoid referencing concepts that haven't been taught yet
- If specific materials, images, or data are provided, incorporate them into relevant activities
- Ensure activities align with the course progression and prerequisites shown in the materials

PEDAGOGICAL PRINCIPLES:
- Events 1-4: Information delivery and preparation (~40-50% of time)
- Events 5-6: Active learning and practice (~40-45% of time)  
- Events 7-9: Assessment and closure (~10-15% of time)

For EACH of the 9 events, provide:
1. 2-4 specific, detailed activities appropriate for the time allocated
2. EXACT duration as specified above (non-negotiable)
3. Required materials and resources (including any from uploaded files)
4. Assessment strategy (where applicable)

CONTENT ADAPTATION:
{("- Focus on hands-on practice, problem-solving, and skill demonstration" if is_practical_focused else "- Focus on knowledge delivery, comprehension, and conceptual understanding")}
{("- Longer practice sessions (Events 5-6) with immediate feedback" if is_practical_focused else "- Detailed content presentation (Event 4) with scaffolded learning")}
{("- Performance-based assessment throughout" if is_practical_focused else "- Knowledge-based assessment and retention activities")}

The 9 Events you MUST include:
1. Gain Attention ({time_distribution[1]} min) - Capture student interest and focus
2. Inform Learners of Objectives ({time_distribution[2]} min) - Share learning goals clearly
3. Stimulate Recall of Prior Learning ({time_distribution[3]} min) - Connect to previous knowledge
4. Present the Content ({time_distribution[4]} min) - Deliver new information systematically
5. Provide Learning Guidance ({time_distribution[5]} min) - Guide the learning process
6. Elicit Performance ({time_distribution[6]} min) - Have students practice and demonstrate
7. Provide Feedback ({time_distribution[7]} min) - Give constructive feedback on performance
8. Assess Performance ({time_distribution[8]} min) - Evaluate student learning
9. Enhance Retention and Transfer ({time_distribution[9]} min) - Promote long-term retention

IMPORTANT: Return ONLY a valid JSON array with exactly 9 events. Use the EXACT duration specified for each event.

Format:
[
    {{
        "event_number": 1,
        "event_name": "Gain Attention",
        "description": "Capture student interest and focus attention on the lesson",
        "activities": ["Specific activity for {request.lesson_topic}", "Another engaging activity", "Third attention-grabbing technique"],
        "duration_minutes": {time_distribution[1]},
        "materials_needed": ["Required materials", "Additional resources"],
        "assessment_strategy": null
    }}
]

Continue this pattern for all 9 events with pedagogically-appropriate time distribution.
"""
        
        try:
            response = await self._call_openai(
                messages=[
                    {"role": "system", "content": "You are an expert in Gagne's Nine Events of Instruction. You must generate exactly 9 events. Return only valid JSON with no additional text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=5000
            )
            
            events_data = self._parse_json_response(response, "array")
            
            # Ensure we have all 9 events
            if len(events_data) < 9:
                self.logger.warning(f"Only {len(events_data)} events generated, expected 9. Using fallback.")
                return self._create_fallback_gagne_events(request)
            
            self.logger.info(f"Successfully generated {len(events_data)} Gagne events from AI")
            return [GagneEvent(**event) for event in events_data]
            
        except Exception as e:
            self.logger.warning(f"AI Gagne events generation failed: {str(e)}. Using fallback.")
            return self._create_fallback_gagne_events(request)
    
    def _calculate_optimal_objectives_count(self, request: LessonRequest) -> int:
        """
        Calculate optimal number of objectives based on Bloom's philosophy and modern research.
        
        Key principles:
        - Cognitive load theory (Miller's 7±2 rule)
        - Bloom's hierarchical progression
        - Quality over quantity
        - Context-dependent complexity
        """
        duration = request.duration_minutes
        num_levels = len(request.selected_bloom_levels)
        selected_levels = [level.value for level in request.selected_bloom_levels]
        
        # Research-based base calculation
        # Cognitive load theory: 3-5 objectives optimal for retention
        # Duration factor: Deeper learning needs more time per objective
        if duration <= 30:
            base_objectives = 2  # Short sessions: focus deeply
        elif duration <= 60:
            base_objectives = 3  # Standard: manageable cognitive load
        elif duration <= 90:
            base_objectives = 4  # Extended: can handle more complexity
        elif duration <= 120:
            base_objectives = 5  # Long sessions: can handle more
        else:
            base_objectives = 6  # Very long sessions: max for cognitive load
        
        # Bloom's hierarchical complexity adjustment
        complexity_weight = self._calculate_cognitive_complexity(selected_levels)
        
        # Higher complexity = fewer objectives (need more time per objective)
        if complexity_weight > 0.7:  # High complexity (Create, Evaluate dominant)
            base_objectives = max(2, base_objectives - 1)
        elif complexity_weight < 0.3:  # Low complexity (Remember, Understand dominant)
            base_objectives = min(base_objectives + 1, 6)
        
        # Academic level adjustment (scaffolding principle)
        level_adjustments = {
            "freshman": -1,  # Need more time for foundational skills
            "sophomore": 0,  # Standard
            "junior": 0,  # Standard
            "senior": 1,  # Can handle slightly more complexity
            "masters": 1,  # Graduate-level cognitive capacity
            "postgrad": 1  # Advanced analytical skills
        }
        
        adjustment = level_adjustments.get(request.grade_level, 0)
        adjusted_objectives = base_objectives + adjustment
        
        # Pedagogical constraints
        min_objectives = max(2, min(num_levels, 3))  # At least 2, max 3 for focus
        max_objectives = 6  # Updated cognitive load limit for longer sessions
        
        optimal_count = max(min_objectives, min(adjusted_objectives, max_objectives))
        
        return optimal_count
    
    def _calculate_cognitive_complexity(self, selected_levels: list) -> float:
        """
        Calculate cognitive complexity based on Bloom's hierarchy
        Returns 0.0 (simple) to 1.0 (complex)
        """
        complexity_weights = {
            "remember": 0.1,
            "understand": 0.2,
            "apply": 0.4,
            "analyze": 0.6,
            "evaluate": 0.8,
            "create": 1.0
        }
        
        if not selected_levels:
            return 0.5
        
        total_weight = sum(complexity_weights.get(level, 0.5) for level in selected_levels)
        return total_weight / len(selected_levels)
    
    def _distribute_objectives_pedagogically(self, request: LessonRequest, total_objectives: int) -> dict:
        """
        Distribute objectives across Bloom's levels following pedagogical principles
        
        Principles:
        - Foundation first (Remember/Understand before higher levels)
        - Scaffolding (lower levels support higher levels)
        - Context appropriateness
        """
        selected_levels = [level.value for level in request.selected_bloom_levels]
        distribution = {}
        
        # Categorize levels by cognitive demand
        foundational = [l for l in selected_levels if l in ["remember", "understand"]]
        application = [l for l in selected_levels if l in ["apply", "analyze"]]
        synthesis = [l for l in selected_levels if l in ["evaluate", "create"]]
        
        remaining_objectives = total_objectives
        
        # Bloom's principle: Ensure foundational understanding first
        if foundational and remaining_objectives > 0:
            foundation_count = max(1, min(len(foundational), remaining_objectives // 2))
            for level in foundational:
                if remaining_objectives > 0:
                    distribution[level] = 1 if foundation_count == 1 else foundation_count // len(foundational)
                    remaining_objectives -= distribution[level]
        
        # Application levels: Bridge between foundation and synthesis
        if application and remaining_objectives > 0:
            app_count = max(1, remaining_objectives // 2) if synthesis else remaining_objectives
            for level in application:
                if remaining_objectives > 0:
                    distribution[level] = 1 if len(application) == 1 else max(1, app_count // len(application))
                    remaining_objectives -= distribution[level]
        
        # Synthesis levels: Culminating activities
        if synthesis and remaining_objectives > 0:
            for level in synthesis:
                if remaining_objectives > 0:
                    distribution[level] = 1
                    remaining_objectives -= 1
        
        # Distribute any remaining objectives to most appropriate levels
        priority_order = ["understand", "apply", "analyze", "remember", "evaluate", "create"]
        for level in priority_order:
            if level in selected_levels and remaining_objectives > 0:
                distribution[level] = distribution.get(level, 0) + 1
                remaining_objectives -= 1
        
        return distribution
    
    def _format_distribution_guidance(self, distribution: dict, selected_levels: list) -> str:
        """Format the distribution guidance for the AI prompt"""
        guidance_lines = []
        
        for level in selected_levels:
            count = distribution.get(level, 0)
            if count > 0:
                level_desc = {
                    "remember": "foundational knowledge",
                    "understand": "conceptual understanding",
                    "apply": "practical application",
                    "analyze": "analytical thinking",
                    "evaluate": "critical evaluation",
                    "create": "synthesis and creation"
                }
                
                desc = level_desc.get(level, "learning")
                guidance_lines.append(f"- {count} objective(s) for {level.title()} level ({desc})")
        
        return "\n".join(guidance_lines)
    
    def _calculate_gagne_time_distribution(self, request: LessonRequest) -> dict:
        """
        Calculate pedagogically-based time distribution for Gagne's Nine Events
        
        Based on:
        - Content type (theoretical vs practical)
        - Bloom's cognitive levels selected
        - Grade level (scaffolding needs)
        - Lesson duration
        """
        selected_levels = [level.value for level in request.selected_bloom_levels]
        duration = request.duration_minutes
        
        # Determine lesson focus based on Bloom's levels
        practical_levels = {"apply", "analyze", "evaluate", "create"}
        theoretical_levels = {"remember", "understand"}
        
        practical_count = len([l for l in selected_levels if l in practical_levels])
        theoretical_count = len([l for l in selected_levels if l in theoretical_levels])
        
        # Calculate focus ratio (0.0 = pure theory, 1.0 = pure practical)
        if practical_count + theoretical_count == 0:
            focus_ratio = 0.5  # Default balanced
        else:
            focus_ratio = practical_count / (practical_count + theoretical_count)
        
        # Base distributions for different lesson types
        theoretical_distribution = {
            1: 0.05,  # Gain Attention
            2: 0.05,  # Inform Objectives
            3: 0.12,  # Stimulate Recall (more for theory)
            4: 0.35,  # Present Content (largest for theory)
            5: 0.15,  # Provide Guidance
            6: 0.15,  # Elicit Performance
            7: 0.08,  # Provide Feedback
            8: 0.05,  # Assess Performance
            9: 0.06  # Enhance Retention
        }
        
        practical_distribution = {
            1: 0.05,  # Gain Attention
            2: 0.03,  # Inform Objectives (shorter for practical)
            3: 0.08,  # Stimulate Recall
            4: 0.25,  # Present Content (reduced for practical)
            5: 0.20,  # Provide Guidance (more coaching needed)
            6: 0.25,  # Elicit Performance (largest for practical)
            7: 0.10,  # Provide Feedback (more important for skills)
            8: 0.04,  # Assess Performance
            9: 0.06  # Enhance Retention
        }
        
        # Interpolate between theoretical and practical based on focus ratio
        base_distribution = {}
        for event in range(1, 10):
            if event in practical_distribution:
                theoretical_weight = theoretical_distribution[event]
                practical_weight = practical_distribution[event]
                
                # Linear interpolation
                base_distribution[event] = (
                    theoretical_weight * (1 - focus_ratio) +
                    practical_weight * focus_ratio
                )
            else:
                base_distribution[event] = theoretical_distribution[event]
        
        # Adjust for grade level (scaffolding needs)
        grade_adjustments = {
            "freshman": {2: 1.2, 3: 1.3, 5: 1.2},  # More objectives, recall, guidance
            "sophomore": {2: 1.1, 3: 1.1, 5: 1.1},  # Slight increase
            "junior": {},  # No adjustment (baseline)
            "senior": {6: 1.1, 8: 1.1},  # More practice and assessment
            "masters": {6: 1.2, 7: 1.1, 8: 1.2},  # More practice, feedback, assessment
            "postgrad": {4: 0.9, 6: 1.3, 8: 1.3}  # Less content, much more practice/assessment
        }
        
        level_adj = grade_adjustments.get(request.grade_level, {})
        
        # Apply grade level adjustments
        for event, multiplier in level_adj.items():
            if event in base_distribution:
                base_distribution[event] *= multiplier
        
        # Normalize to ensure total = 1.0
        total_weight = sum(base_distribution.values())
        normalized_distribution = {
            event: weight / total_weight
            for event, weight in base_distribution.items()
        }
        
        # Convert to actual minutes and ensure total equals lesson duration
        time_distribution = {}
        total_allocated = 0
        
        for event in range(1, 9):  # Events 1-8
            minutes = round(normalized_distribution[event] * duration)
            time_distribution[event] = max(1, minutes)  # Minimum 1 minute per event
            total_allocated += time_distribution[event]
        
        # Event 9 gets remaining time
        time_distribution[9] = max(1, duration - total_allocated)
        
        return time_distribution
    
    def _format_time_distribution_guidance(self, time_dist: dict, total_duration: int) -> str:
        """Format time distribution for the AI prompt"""
        guidance = f"CRITICAL: Distribute the total {total_duration} minutes as follows:\n"
        
        event_names = {
            1: "Gain Attention",
            2: "Inform Objectives",
            3: "Stimulate Recall",
            4: "Present Content",
            5: "Provide Guidance",
            6: "Elicit Performance",
            7: "Provide Feedback",
            8: "Assess Performance",
            9: "Enhance Retention"
        }
        
        for event_num in range(1, 10):
            minutes = time_dist[event_num]
            percentage = (minutes / total_duration) * 100
            guidance += f"- Event {event_num} ({event_names[event_num]}): {minutes} minutes ({percentage:.1f}%)\n"
        
        guidance += f"\nTotal must equal exactly {total_duration} minutes."
        return guidance
    
    def _create_comprehensive_fallback_objectives(self, request: LessonRequest) -> List[LessonObjective]:
        """Create pedagogically sound fallback objectives"""
        total_objectives = self._calculate_optimal_objectives_count(request)
        distribution = self._distribute_objectives_pedagogically(request, total_objectives)
        
        objectives = []
        
        # Template objectives following pedagogical principles
        templates = {
            "remember": [
                "Students will be able to recall fundamental concepts of {topic}",
                "Students will be able to identify key components in {topic}",
                "Students will be able to define essential terminology for {topic}"
            ],
            "understand": [
                "Students will be able to explain the core principles of {topic}",
                "Students will be able to interpret the significance of {topic}",
                "Students will be able to summarize the main ideas in {topic}"
            ],
            "apply": [
                "Students will be able to implement {topic} techniques in practical situations",
                "Students will be able to demonstrate {topic} procedures accurately",
                "Students will be able to solve problems using {topic} methods"
            ],
            "analyze": [
                "Students will be able to examine the relationships within {topic}",
                "Students will be able to compare different approaches to {topic}",
                "Students will be able to analyze the components of {topic} systems"
            ],
            "evaluate": [
                "Students will be able to assess the effectiveness of {topic} strategies",
                "Students will be able to critique {topic} methodologies",
                "Students will be able to justify decisions regarding {topic}"
            ],
            "create": [
                "Students will be able to design innovative {topic} solutions",
                "Students will be able to develop original {topic} approaches",
                "Students will be able to construct new {topic} frameworks"
            ]
        }
        
        action_verbs = {
            "remember": ["recall", "identify", "define"],
            "understand": ["explain", "interpret", "summarize"],
            "apply": ["implement", "demonstrate", "solve"],
            "analyze": ["examine", "compare", "analyze"],
            "evaluate": ["assess", "critique", "justify"],
            "create": ["design", "develop", "construct"]
        }
        
        # Generate objectives according to pedagogical distribution
        for level_str, count in distribution.items():
            level_enum = next((l for l in request.selected_bloom_levels if l.value == level_str), None)
            if not level_enum:
                continue
            
            level_templates = templates.get(level_str, templates["understand"])
            level_verbs = action_verbs.get(level_str, ["understand"])
            
            for i in range(count):
                template = level_templates[i % len(level_templates)]
                verb = level_verbs[i % len(level_verbs)]
                
                objectives.append(LessonObjective(
                    bloom_level=level_enum,
                    objective=template.format(topic=request.lesson_topic),
                    action_verb=verb,
                    content=f"core concepts of {request.lesson_topic}",
                    condition="following instruction",
                    criteria="with understanding and accuracy"
                ))
        
        return objectives
    
    def _create_fallback_lesson_plan(self, request: LessonRequest) -> LessonPlan:
        """Create fallback lesson plan if AI generation fails"""
        
        # Format grade level properly
        grade_level_display = {
            "freshman": "freshman",
            "sophomore": "sophomore",
            "junior": "junior",
            "senior": "senior",
            "masters": "master's",
            "postgrad": "postgraduate"
        }.get(request.grade_level, request.grade_level)
        
        # Create a more engaging overview
        overview = f"This comprehensive lesson introduces {grade_level_display} students to {request.lesson_topic}, providing both theoretical understanding and practical application. Students will explore key concepts through interactive discussions, hands-on activities, and real-world examples to ensure deep comprehension and retention."
        
        return LessonPlan(
            title=f"{request.lesson_topic} - {request.course_title}",
            overview=overview,
            prerequisites=[f"Basic understanding of {request.course_title} fundamentals"],
            materials=["Textbook", "Handouts", "Writing materials"],
            technology_requirements=["Computer/tablet", "Internet access"],
            assessment_methods=["Formative assessment", "Exit ticket"],
            differentiation_strategies=["Visual aids", "Multiple learning modalities"],
            closure_activities=["Summary discussion", "Q&A session"]
        )
    
    def _create_fallback_gagne_events(self, request: LessonRequest) -> List[GagneEvent]:
        """Create fallback Gagne events with pedagogically-based time distribution"""
        
        # Use the same smart time distribution for fallbacks
        time_distribution = self._calculate_gagne_time_distribution(request)
        
        events_data = [
            {
                "event_number": 1,
                "event_name": "Gain Attention",
                "description": "Capture student interest and focus attention on the lesson",
                "activities": [f"Opening question about {request.lesson_topic}", "Share interesting fact or story",
                               "Use multimedia presentation"],
                "duration_minutes": time_distribution[1],
                "materials_needed": ["Presentation slides", "Multimedia equipment"],
                "assessment_strategy": None
            },
            {
                "event_number": 2,
                "event_name": "Inform Learners of Objectives",
                "description": "Share learning goals and explain their relevance",
                "activities": ["Present lesson objectives", "Explain relevance to students", "Connect to course goals"],
                "duration_minutes": time_distribution[2],
                "materials_needed": ["Objective slides", "Course syllabus"],
                "assessment_strategy": None
            },
            {
                "event_number": 3,
                "event_name": "Stimulate Recall of Prior Learning",
                "description": "Connect new content to existing knowledge",
                "activities": ["Review previous concepts", "Ask about related experiences", "Use analogies"],
                "duration_minutes": time_distribution[3],
                "materials_needed": ["Review materials", "Whiteboard"],
                "assessment_strategy": "Quick verbal quiz"
            },
            {
                "event_number": 4,
                "event_name": "Present the Content",
                "description": "Deliver new information and concepts systematically",
                "activities": ["Structured lecture", "Provide multiple examples", "Use visual aids"],
                "duration_minutes": time_distribution[4],
                "materials_needed": ["Lecture slides", "Visual aids", "Handouts"],
                "assessment_strategy": None
            },
            {
                "event_number": 5,
                "event_name": "Provide Learning Guidance",
                "description": "Guide students through the learning process",
                "activities": ["Provide hints and prompts", "Model procedures", "Offer coaching"],
                "duration_minutes": time_distribution[5],
                "materials_needed": ["Examples", "Step-by-step guides"],
                "assessment_strategy": "Guided practice observation"
            },
            {
                "event_number": 6,
                "event_name": "Elicit Performance",
                "description": "Have students practice and demonstrate learning",
                "activities": ["Practice exercises", "Problem-solving tasks", "Hands-on activities"],
                "duration_minutes": time_distribution[6],
                "materials_needed": ["Practice worksheets", "Equipment for activities"],
                "assessment_strategy": "Performance observation"
            },
            {
                "event_number": 7,
                "event_name": "Provide Feedback",
                "description": "Give constructive feedback on student performance",
                "activities": ["Individual feedback", "Group discussion of solutions", "Peer feedback"],
                "duration_minutes": time_distribution[7],
                "materials_needed": ["Feedback forms", "Answer keys"],
                "assessment_strategy": "Feedback quality assessment"
            },
            {
                "event_number": 8,
                "event_name": "Assess Performance",
                "description": "Evaluate student learning and understanding",
                "activities": ["Formative assessment", "Quiz or test", "Project evaluation"],
                "duration_minutes": time_distribution[8],
                "materials_needed": ["Assessment tools", "Rubrics"],
                "assessment_strategy": "Formal assessment"
            },
            {
                "event_number": 9,
                "event_name": "Enhance Retention and Transfer",
                "description": "Promote long-term retention and real-world application",
                "activities": ["Summary and reflection", "Real-world applications", "Future learning connections"],
                "duration_minutes": time_distribution[9],
                "materials_needed": ["Summary materials", "Application examples"],
                "assessment_strategy": "Reflection assessment"
            }
        ]
        
        return [GagneEvent(**event) for event in events_data]
