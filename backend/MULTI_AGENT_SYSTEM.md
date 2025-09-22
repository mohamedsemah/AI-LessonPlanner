# Multi-Agent Lesson Planning System

## Overview

The Multi-Agent Lesson Planning System is a sophisticated AI-powered platform that generates comprehensive, pedagogically sound lesson plans and multimodal teaching content. The system uses a coordinated approach with specialized agents, each responsible for different aspects of lesson planning and content generation.

## Architecture

### Core Agents

#### 1. **Plan Agent** (`PlanAgent`)
- **Purpose**: Generates core lesson planning components
- **Responsibilities**:
  - Learning objectives based on Bloom's Taxonomy
  - Comprehensive lesson plans
  - Gagne's Nine Events of Instruction with pedagogically-based time distribution
- **Key Features**:
  - Cognitive load theory optimization
  - Pedagogical principle adherence
  - Grade-level appropriate content generation

#### 2. **Content Agent** (`ContentAgent`)
- **Purpose**: Creates multimodal teaching content
- **Responsibilities**:
  - Slide generation for Gagne's Nine Events
  - Visual elements and multimedia content
  - Audio scripts and speaker notes
  - Interactive activities and assessments
- **Key Features**:
  - UDL-compliant content design
  - Multiple content modalities
  - Professional presentation quality

#### 3. **UDL Agent** (`UDLAgent`)
- **Purpose**: Validates Universal Design for Learning compliance
- **Responsibilities**:
  - UDL principle compliance scoring
  - Accessibility feature validation
  - Content modality analysis
  - UDL guideline recommendations
- **Key Features**:
  - Comprehensive accessibility assessment
  - Real-time compliance validation
  - Improvement recommendations

#### 4. **Coordinator Agent** (`CoordinatorAgent`)
- **Purpose**: Orchestrates all agents and manages the lesson planning process
- **Responsibilities**:
  - Agent coordination and communication
  - Data flow between agents
  - Error handling and fallback strategies
  - Result aggregation and validation
- **Key Features**:
  - Seamless agent integration
  - Robust error handling
  - Fallback content generation

## System Features

### Educational Frameworks
- **Bloom's Taxonomy**: Complete integration with all six cognitive levels
- **Gagne's Nine Events**: Pedagogically-based time distribution
- **Universal Design for Learning (UDL)**: Comprehensive compliance validation
- **Cognitive Load Theory**: Optimized content complexity

### Content Generation
- **Multimodal Content**: Visual, auditory, textual, kinesthetic, and interactive
- **Professional Quality**: Ready-to-use teaching materials
- **Accessibility**: WCAG-compliant content design
- **Personalization**: Grade-level and subject-specific adaptation

### Technical Capabilities
- **AI-Powered**: Advanced language models for content generation
- **Real-time Processing**: Concurrent agent execution
- **Error Resilience**: Fallback mechanisms for reliability
- **Scalable Architecture**: Modular design for easy extension

## API Endpoints

### Core Lesson Planning
- `POST /api/lesson/generate` - Generate complete lesson plan
- `POST /api/lesson/refine` - Refine specific lesson components

### Multi-Agent System
- `GET /api/lesson/agents/status` - Get agent status
- `GET /api/lesson/agents/capabilities` - Get system capabilities
- `GET /api/lesson/health/agents` - Health check for all agents

### UDL and Accessibility
- `GET /api/lesson/udl/guidelines` - Get UDL guidelines
- `GET /api/lesson/udl/modalities` - Get content modalities
- `GET /api/lesson/udl/accessibility` - Get accessibility features

## Usage Examples

### Basic Lesson Generation

```python
from app.services.multi_agent_service import MultiAgentService
from app.models.lesson import LessonRequest, BloomLevel, GradeLevel

# Initialize the service
service = MultiAgentService()

# Create lesson request
request = LessonRequest(
    course_title="Introduction to Computer Science",
    lesson_topic="Data Structures and Algorithms",
    grade_level=GradeLevel.JUNIOR,
    duration_minutes=60,
    selected_bloom_levels=[BloomLevel.UNDERSTAND, BloomLevel.APPLY, BloomLevel.ANALYZE]
)

# Generate complete lesson
lesson_response = await service.generate_lesson_content(request)

# Access results
print(f"Generated {len(lesson_response.objectives)} objectives")
print(f"Created {lesson_response.gagne_slides.total_slides} slides")
print(f"UDL compliance: {lesson_response.udl_compliance['overall_compliance']:.2f}")
```

### Individual Agent Usage

```python
from app.services.agents.plan_agent import PlanAgent
from app.services.agents.content_agent import ContentAgent
from app.services.agents.udl_agent import UDLAgent

# Use Plan Agent directly
plan_agent = PlanAgent()
plan_result = await plan_agent.process({
    "lesson_request": request,
    "processed_files": {}
})

# Use Content Agent directly
content_agent = ContentAgent()
content_result = await content_agent.process({
    "gagne_events": gagne_events,
    "objectives": objectives,
    "lesson_plan": lesson_plan,
    "lesson_info": lesson_info
})

# Use UDL Agent directly
udl_agent = UDLAgent()
udl_result = await udl_agent.process({
    "slides": slides,
    "lesson_info": lesson_info
})
```

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DEBUG=False
PORT=8000
```

### Agent Configuration
Each agent can be configured with custom parameters:

```python
# Custom OpenAI client
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key="your_key", base_url="custom_endpoint")

# Initialize agents with custom client
plan_agent = PlanAgent(client=client)
content_agent = ContentAgent(client=client)
udl_agent = UDLAgent(client=client)
coordinator = CoordinatorAgent(client=client)
```

## Testing

### Run the Test Suite
```bash
cd backend
python test_multi_agent_system.py
```

### Test Coverage
- Individual agent functionality
- Coordinator agent orchestration
- Multi-agent service integration
- Error handling and fallback mechanisms
- Agent communication and data flow

## Performance Considerations

### Optimization Features
- **Concurrent Processing**: Agents run in parallel where possible
- **Caching**: Intelligent caching of common responses
- **Fallback Systems**: Graceful degradation on failures
- **Resource Management**: Efficient memory and CPU usage

### Scalability
- **Modular Design**: Easy to add new agents
- **Stateless Agents**: Horizontal scaling capability
- **Async Processing**: Non-blocking operations
- **Error Isolation**: Failures don't cascade

## Error Handling

### Fallback Mechanisms
1. **Agent-Level Fallbacks**: Each agent has built-in fallback content
2. **Service-Level Fallbacks**: Multi-agent service provides backup content
3. **Graceful Degradation**: System continues with reduced functionality
4. **Error Reporting**: Comprehensive error logging and reporting

### Error Types
- **API Failures**: OpenAI service unavailability
- **Validation Errors**: Invalid input data
- **Processing Errors**: Content generation failures
- **Network Errors**: Connectivity issues

## Future Enhancements

### Planned Features
- **Additional Agents**: Image, Video, and Chart agents
- **Advanced UDL**: Real-time compliance monitoring
- **Personalization**: User preference learning
- **Analytics**: Usage and performance metrics

### Extension Points
- **Custom Agents**: Easy integration of new agent types
- **Plugin System**: Modular functionality additions
- **API Extensions**: Additional endpoints and capabilities
- **Integration Hooks**: Third-party service connections

## Troubleshooting

### Common Issues

#### 1. Agent Initialization Failures
```python
# Check OpenAI API key
import os
print(f"API Key set: {bool(os.getenv('OPENAI_API_KEY'))}")

# Test individual agent
from app.services.agents.plan_agent import PlanAgent
agent = PlanAgent()
print(f"Agent initialized: {agent is not None}")
```

#### 2. Content Generation Failures
```python
# Check agent status
service = MultiAgentService()
status = service.get_agent_status()
print(f"Agent status: {status}")

# Test health check
health = await service.health_check()
print(f"System health: {health}")
```

#### 3. UDL Compliance Issues
```python
# Get UDL guidelines
guidelines = service.get_udl_guidelines()
print(f"Available guidelines: {list(guidelines.keys())}")

# Check accessibility features
features = service.get_accessibility_features()
print(f"Accessibility features: {features}")
```

## Support

### Documentation
- API Documentation: `/docs` endpoint
- Agent Documentation: Individual agent docstrings
- Code Examples: Test files and usage examples

### Monitoring
- Health Checks: `/api/lesson/health/agents`
- Agent Status: `/api/lesson/agents/status`
- System Capabilities: `/api/lesson/agents/capabilities`

### Logging
- Structured logging with different levels
- Error tracking and reporting
- Performance metrics collection

## License

This multi-agent system is part of the AI Lesson Planning Tool and follows the same licensing terms as the main project.
