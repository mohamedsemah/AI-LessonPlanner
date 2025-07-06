import os
import json
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
from ..models.lesson import LessonRequest, LessonResponse, LessonObjective, LessonPlan, GagneEvent, BloomLevel, \
    RefineRequest


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate_lesson_content(self, request: LessonRequest) -> LessonResponse:
        """Generate complete lesson content including objectives, lesson plan, and Gagne events"""

        # Generate objectives and lesson plan concurrently
        objectives_task = self._generate_objectives(request)
        lesson_plan_task = self._generate_lesson_plan(request)

        objectives, lesson_plan = await asyncio.gather(objectives_task, lesson_plan_task)

        # Generate Gagne events with context from objectives and lesson plan
        gagne_events = await self._generate_gagne_events(request, objectives, lesson_plan)

        return LessonResponse(
            lesson_info={
                "course_title": request.course_title,
                "lesson_topic": request.lesson_topic,
                "grade_level": request.grade_level,
                "duration_minutes": request.duration_minutes,
                "preliminary_objectives": request.preliminary_objectives,
                "selected_bloom_levels": request.selected_bloom_levels
            },
            objectives=objectives,
            lesson_plan=lesson_plan,
            gagne_events=gagne_events,
            total_duration=request.duration_minutes,
            created_at=str(asyncio.get_event_loop().time())
        )

    async def _generate_objectives(self, request: LessonRequest) -> List[LessonObjective]:
        """Generate detailed learning objectives based on Bloom's taxonomy"""

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
Preliminary Goals: {request.preliminary_objectives}

PEDAGOGICAL REQUIREMENTS:
Create exactly {total_objectives} learning objectives following these research-based principles:

1. COGNITIVE LOAD THEORY: Limit to {total_objectives} objectives for optimal retention
2. BLOOM'S HIERARCHY: Ensure foundational levels support higher-order thinking
3. SCAFFOLDING: Build complexity progressively
4. CONTEXT APPROPRIATENESS: Match cognitive demand to student level

OBJECTIVE DISTRIBUTION:
{self._format_distribution_guidance(objectives_distribution, selected_levels)}

QUALITY STANDARDS:
- Each objective must be specific, measurable, and achievable in {request.duration_minutes} minutes
- Use appropriate cognitive verbs for each Bloom's level
- Include realistic conditions and criteria
- Focus on depth over breadth (Bloom's emphasis on mastery)

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

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You are an expert instructional designer specializing in Bloom's taxonomy. You must generate the exact number of objectives requested. Return only valid JSON with no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )

        try:
            raw_content = response.choices[0].message.content.strip()
            print(f"=== RAW AI RESPONSE FOR OBJECTIVES ===")
            print(raw_content)
            print(f"=== END RAW RESPONSE ===")

            # Try to clean the response if it has extra text
            if raw_content.startswith('```json'):
                raw_content = raw_content.replace('```json', '').replace('```', '').strip()
            elif raw_content.startswith('```'):
                raw_content = raw_content.replace('```', '').strip()

            # Find JSON array in the response
            start_idx = raw_content.find('[')
            end_idx = raw_content.rfind(']') + 1

            if start_idx != -1 and end_idx != -1:
                json_content = raw_content[start_idx:end_idx]
                print(f"=== EXTRACTED JSON ===")
                print(json_content)
                print(f"=== END EXTRACTED JSON ===")

                objectives_data = json.loads(json_content)

                # Fix case sensitivity issue - convert bloom_level to lowercase
                for obj in objectives_data:
                    if 'bloom_level' in obj:
                        obj['bloom_level'] = obj['bloom_level'].lower()

            else:
                print("ERROR: No JSON array found in response")
                raise json.JSONDecodeError("No JSON array found", raw_content, 0)

            print(f"Successfully parsed {len(objectives_data)} objectives from AI")

            # Validate we have appropriate number of objectives
            optimal_count = self._calculate_optimal_objectives_count(request)
            if len(objectives_data) < optimal_count * 0.8:  # Allow 20% tolerance
                print(f"Warning: Only {len(objectives_data)} objectives generated, expected around {optimal_count}")
                print("Using comprehensive fallback system...")
                return self._create_comprehensive_fallback_objectives(request)

            # Validate objective structure (case already fixed above)
            for i, obj in enumerate(objectives_data):
                if not all(key in obj for key in ['bloom_level', 'objective', 'action_verb', 'content']):
                    print(f"Error: Objective {i} missing required fields: {obj}")
                    print("Using comprehensive fallback system...")
                    return self._create_comprehensive_fallback_objectives(request)

            print("AI objectives validation passed - using AI generated content")
            return [LessonObjective(**obj) for obj in objectives_data]

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Failed to parse response, using comprehensive fallback")
            return self._create_comprehensive_fallback_objectives(request)
        except Exception as e:
            print(f"Unexpected error processing AI response: {e}")
            print(f"Using comprehensive fallback")
            return self._create_comprehensive_fallback_objectives(request)

    def _calculate_optimal_objectives_count(self, request: LessonRequest) -> int:
        """
        Calculate optimal number of objectives based on Bloom's philosophy and modern research

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
        else:
            base_objectives = 5  # Long sessions: max for cognitive load

        # Bloom's hierarchical complexity adjustment
        complexity_weight = self._calculate_cognitive_complexity(selected_levels)

        # Higher complexity = fewer objectives (need more time per objective)
        if complexity_weight > 0.7:  # High complexity (Create, Evaluate dominant)
            base_objectives = max(2, base_objectives - 1)
        elif complexity_weight < 0.3:  # Low complexity (Remember, Understand dominant)
            base_objectives = min(base_objectives + 1, 5)

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
        max_objectives = 5  # Cognitive load limit

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

    async def _generate_lesson_plan(self, request: LessonRequest) -> LessonPlan:
        """Generate a comprehensive lesson plan"""

        prompt = f"""
        Create a comprehensive lesson plan for a {request.grade_level} level course titled "{request.course_title}" 
        for a lesson on "{request.lesson_topic}" lasting {request.duration_minutes} minutes.

        Preliminary objectives: {request.preliminary_objectives}

        Generate a detailed lesson plan including:
        1. Clear lesson overview
        2. Prerequisites students should have
        3. Materials and resources needed
        4. Technology requirements
        5. Assessment methods
        6. Differentiation strategies for diverse learners
        7. Closure activities

        Make it practical and actionable for college instructors.

        Return as JSON with this structure:
        {{
            "title": "Lesson title",
            "overview": "Brief description of the lesson",
            "prerequisites": ["prerequisite 1", "prerequisite 2"],
            "materials": ["material 1", "material 2"],
            "technology_requirements": ["tech 1", "tech 2"],
            "assessment_methods": ["method 1", "method 2"],
            "differentiation_strategies": ["strategy 1", "strategy 2"],
            "closure_activities": ["activity 1", "activity 2"]
        }}
        """

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert instructional designer. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        try:
            lesson_data = json.loads(response.choices[0].message.content)
            return LessonPlan(**lesson_data)
        except json.JSONDecodeError:
            return self._create_fallback_lesson_plan(request)

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
            8: 0.04  # Assess Performance
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
        """Generate Gagne's Nine Events of Instruction"""

    async def _generate_gagne_events(self, request: LessonRequest, objectives: List[LessonObjective],
                                     lesson_plan: LessonPlan) -> List[GagneEvent]:
        """Generate Gagne's Nine Events of Instruction with pedagogically-based time distribution"""

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

        Learning Objectives:
        {objectives_text}

        {time_guidance}

        PEDAGOGICAL PRINCIPLES:
        - Events 1-4: Information delivery and preparation (~40-50% of time)
        - Events 5-6: Active learning and practice (~40-45% of time)  
        - Events 7-9: Assessment and closure (~10-15% of time)

        For EACH of the 9 events, provide:
        1. 2-4 specific, detailed activities appropriate for the time allocated
        2. EXACT duration as specified above (non-negotiable)
        3. Required materials and resources
        4. Assessment strategy (where applicable)

        CONTENT ADAPTATION:
        {"- Focus on hands-on practice, problem-solving, and skill demonstration" if is_practical_focused else "- Focus on knowledge delivery, comprehension, and conceptual understanding"}
        {"- Longer practice sessions (Events 5-6) with immediate feedback" if is_practical_focused else "- Detailed content presentation (Event 4) with scaffolded learning"}
        {"- Performance-based assessment throughout" if is_practical_focused else "- Knowledge-based assessment and retention activities"}

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

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system",
                 "content": "You are an expert in Gagne's Nine Events of Instruction. You must generate exactly 9 events. Return only valid JSON with no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=5000  # Increased from 4000 to handle all 9 events
        )

        try:
            raw_content = response.choices[0].message.content.strip()
            print(f"AI Response for Gagne events: {len(raw_content)} characters")
            print(f"Raw Gagne response preview: {raw_content[:200]}...")

            # Clean the response - remove markdown formatting
            if raw_content.startswith('```json'):
                clean_content = raw_content.replace('```json', '').replace('```', '').strip()
            elif raw_content.startswith('```'):
                clean_content = raw_content.replace('```', '').strip()
            else:
                clean_content = raw_content

            # Find JSON array in the response
            start_idx = clean_content.find('[')
            end_idx = clean_content.rfind(']') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_content = clean_content[start_idx:end_idx]
                print(f"Extracted Gagne JSON length: {len(json_content)} characters")

                # Try to parse the JSON
                events_data = json.loads(json_content)
                print(f"Successfully parsed {len(events_data)} Gagne events from AI")

            else:
                print("ERROR: No complete JSON array found in Gagne events response")
                print(f"Start index: {start_idx}, End index: {end_idx}")
                raise json.JSONDecodeError("No complete JSON array found", clean_content, 0)

            # Ensure we have all 9 events
            if len(events_data) < 9:
                print(f"Warning: Only {len(events_data)} events generated, expected 9. Using fallback.")
                return self._create_fallback_gagne_events(request)

            return [GagneEvent(**event) for event in events_data]

        except json.JSONDecodeError as e:
            print(f"JSON parsing error for Gagne events: {e}")
            print(f"Raw response length: {len(response.choices[0].message.content)}")
            print(f"Raw response preview: {response.choices[0].message.content[:300]}...")
            print("Using fallback Gagne events")
            return self._create_fallback_gagne_events(request)
        except Exception as e:
            print(f"Unexpected error parsing Gagne events: {e}")
            print("Using fallback Gagne events")
            return self._create_fallback_gagne_events(request)

    async def refine_content(self, request: RefineRequest) -> Dict[str, Any]:
        """Refine specific sections of the lesson content"""

        prompt = f"""
        You are an expert instructional designer. Refine the following {request.section_type} content based on the user's instructions.

        SECTION TYPE: {request.section_type}

        CURRENT CONTENT:
        {request.section_content}

        REFINEMENT INSTRUCTIONS:
        {request.refinement_instructions}

        LESSON CONTEXT:
        Course: {request.lesson_context.get('course_title', 'N/A')}
        Topic: {request.lesson_context.get('lesson_topic', 'N/A')}
        Level: {request.lesson_context.get('grade_level', 'N/A')}
        Duration: {request.lesson_context.get('duration_minutes', 'N/A')} minutes

        INSTRUCTIONS:
        1. Keep the same JSON structure and format as the original
        2. Apply the requested refinements while maintaining educational quality
        3. Ensure all required fields are present
        4. For objectives: maintain proper Bloom's taxonomy alignment
        5. For Gagne events: preserve the nine-event structure and time allocation
        6. For lesson plans: keep all essential components

        Return ONLY the refined JSON content with no additional text or formatting.
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system",
                     "content": "You are an expert instructional designer. Return only valid JSON that matches the original structure exactly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )

            raw_content = response.choices[0].message.content.strip()

            # Clean the response - remove markdown formatting
            if raw_content.startswith('```json'):
                clean_content = raw_content.replace('```json', '').replace('```', '').strip()
            elif raw_content.startswith('```'):
                clean_content = raw_content.replace('```', '').strip()
            else:
                clean_content = raw_content

            # Try to parse as JSON to validate
            try:
                parsed_content = json.loads(clean_content)
                return {"refined_content": clean_content}
            except json.JSONDecodeError:
                # If JSON parsing fails, return the content as-is but log the issue
                print(f"Warning: Refined content is not valid JSON for {request.section_type}")
                return {"refined_content": clean_content}

        except Exception as e:
            print(f"Error in content refinement: {e}")
            # Return original content if refinement fails
            return {"refined_content": request.section_content}

    def _create_fallback_lesson_plan(self, request: LessonRequest) -> LessonPlan:
        """Create fallback lesson plan if AI generation fails"""
        return LessonPlan(
            title=f"{request.lesson_topic} - {request.course_title}",
            overview=f"This lesson covers {request.lesson_topic} for {request.grade_level} students.",
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