# Smart Code Review Pipeline - Student Project Template

**Learning Project**: Build an automated code review system using **LangGraph Multi-Agent Orchestration** + **Gemini 2.0 Flash** + **GitHub API** + **Gmail** for comprehensive Python code analysis with specialized agents working in parallel.

## Project Overview

**What You Will Build**: An advanced automated code review system that leverages multiple specialized AI agents working in parallel to analyze and evaluate Python code. Your system will analyze both GitHub pull requests and local Python files, providing comprehensive feedback on security vulnerabilities, code quality, test coverage, documentation, and AI-powered suggestions.

### Features You Will Implement:

- **True Parallel Execution**: Design agents that run simultaneously for maximum efficiency
- **GitHub Integration**: Build real PR analysis via GitHub API
- **Static Analysis**: Implement PyLint code quality scoring and complexity analysis
- **Test Coverage**: Create coverage analysis and missing test identification
- **AI Code Review**: Integrate Gemini 2.0 Flash intelligent analysis
- **Email Reports**: Build comprehensive notification and reporting system

## Multi-Agent Architecture You Will Build

**Your Task**: Implement a true parallel multi-agent architecture with 5 specialized agents:

1. **Security Analysis Agent** → You will build vulnerability detection and security scoring
2. **Quality Analysis Agent** → You will implement PyLint + complexity metrics + code smells
3. **Coverage Analysis Agent** → You will create test coverage + missing test identification
4. **AI Review Agent** → You will integrate Gemini 2.0 Flash with cross-agent context
5. **Documentation Agent** → You will build docstring coverage + API documentation analysis

## Getting Started

### Prerequisites
- Python 3.8+
- GitHub account and personal access token
- Google AI Studio account and API key
- Gmail account with app password

### Setup Instructions
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create your `.env` file with required credentials (see Configuration section)
4. Start implementing the empty template files following the instructions below

### Testing Your Implementation
- Run tests: `python tests.py`
- Test with demo: `python main.py demo`
- Test with local files: `python main.py files path/to/file.py`
- Test with GitHub PR: `python main.py pr https://github.com/user/repo 123`

## Configuration Setup

**Your Task**: Create a `.env` file in the root directory with your credentials:

```
# GitHub API Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_API_URL=https://api.github.com

# Email Configuration
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
EMAIL_TO=recipient@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Quality Thresholds
PYLINT_THRESHOLD=7.0
COVERAGE_THRESHOLD=80.0
AI_CONFIDENCE_THRESHOLD=0.8
SECURITY_THRESHOLD=8.0
DOCUMENTATION_THRESHOLD=70.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/code_review.log
```

## Quality Thresholds to Implement

**Your Task**: Implement decision logic that enforces these quality thresholds:

- **PyLint Score**: ≥ 7.0/10.0 (implement in Quality Agent)
- **Test Coverage**: ≥ 80% (implement in Coverage Agent)
- **AI Confidence**: ≥ 0.8 (implement in AI Review Agent)
- **Security Score**: ≥ 8.0/10.0 (implement in Security Agent)
- **Documentation Coverage**: ≥ 70% (implement in Documentation Agent)

## Project Structure & Implementation Guide

**Your Task**: Implement the functionality in each of these files. The structure is provided, but the files contain only templates and TODOs.

```
Multi-Agent-Code-Review-Pipeline-LangGraph-Refactor/
├── smart_code_review/              # Main package (implement all files below)
│   ├── __init__.py                # Package initialization
│   ├── main.py                    # IMPLEMENT: Application entry point & CLI
│   ├── README.md                  # Package documentation
│   │
│   ├── core/                      # Core system components
│   │   ├── __init__.py           # Package initialization
│   │   ├── config.py             # IMPLEMENT: Configuration management
│   │   └── state.py              # IMPLEMENT: State management functions
│   │
│   ├── agents/                    # Specialized agent implementations
│   │   ├── __init__.py           # Package exports
│   │   ├── base_agent.py         # IMPLEMENT: Abstract base agent class
│   │   ├── pr_detector.py        # IMPLEMENT: PR detection and parsing
│   │   ├── security_agent.py     # IMPLEMENT: Security vulnerability analysis
│   │   ├── quality_agent.py      # IMPLEMENT: PyLint code quality analysis
│   │   ├── coverage_agent.py     # IMPLEMENT: Test coverage analysis
│   │   ├── ai_review_agent.py    # IMPLEMENT: Gemini AI-powered review
│   │   ├── documentation_agent.py # IMPLEMENT: Documentation analysis
│   │   └── agent_coordinator.py  # IMPLEMENT: Result aggregation logic
│   │
│   ├── services/                  # External service integrations
│   │   ├── __init__.py           # Package initialization
│   │   ├── gemini/               # Gemini AI service
│   │   │   ├── __init__.py       # Service exports
│   │   │   ├── client.py         # IMPLEMENT: AI client implementation
│   │   │   ├── prompts.py        # IMPLEMENT: AI prompts and templates
│   │   │   └── parser.py         # IMPLEMENT: Response parsing logic
│   │   ├── github/               # GitHub API service
│   │   │   ├── __init__.py       # Service exports
│   │   │   ├── client.py         # IMPLEMENT: GitHub API client
│   │   │   └── models.py         # IMPLEMENT: GitHub data models
│   │   ├── email_service.py      # IMPLEMENT: Email notification service
│   │   ├── pylint_service.py     # IMPLEMENT: PyLint integration service
│   │   ├── coverage_service.py   # IMPLEMENT: Coverage analysis service
│   │   └── gemini_service.py     # IMPLEMENT: Legacy Gemini service wrapper
│   │
│   ├── workflows/                 # LangGraph workflow definitions
│   │   ├── __init__.py           # Package exports
│   │   └── parallel_workflow.py  # IMPLEMENT: Main workflow orchestration
│   │
│   ├── analyzers/                 # Analysis components
│   │   ├── __init__.py           # Package exports
│   │   ├── security_analyzer.py  # IMPLEMENT: Security vulnerability detection
│   │   ├── code_complexity.py    # IMPLEMENT: Code complexity analysis
│   │   ├── test_quality.py       # IMPLEMENT: Test quality analysis
│   │   └── documentation_analyzer.py # IMPLEMENT: Documentation analysis
│   │
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py           # Package exports
│   │   ├── logging_utils.py      # IMPLEMENT: Logging configuration
│   │   ├── validation.py         # IMPLEMENT: Input validation
│   │   ├── formatters.py         # IMPLEMENT: Output formatting utilities
│   │   └── error_handling.py     # IMPLEMENT: Error handling utilities
│   │
│   ├── models/                    # Data models and schemas
│   │   ├── __init__.py           # Package exports
│   │   └── review_state.py       # IMPLEMENT: Review state model
│   │
│   └── visualization/             # Visualization components (future)
│       └── __init__.py           # Package placeholder
│
├── logs/                          # Log files (created at runtime)
├── main.py                        # IMPLEMENT: Wrapper entry point
├── demo_sample.py                # Sample code for testing
├── tests.py                      # IMPLEMENT: Comprehensive test suite
├── requirements.txt              # Python dependencies
├── setup.py                     # IMPLEMENT: Package setup configuration
├── .env                         # CREATE: Environment configuration
├── README.md                    # This file
└── ARCHITECTURE.md              # System architecture documentation
```

## Implementation Instructions by File

### Core Components

#### `smart_code_review/core/config.py`
**Implement**: Configuration management system
- Create `ConfigManager` class with singleton pattern
- Load settings from environment variables and .env file
- Validate required credentials (GitHub token, Gemini API key, email credentials)
- Provide default values for quality thresholds
- Handle type conversion for numeric values

#### `smart_code_review/core/state.py`
**Implement**: State management functions
- Create `StateManager` class with static methods
- Implement `create_initial_state()` function
- Generate unique review IDs with timestamp
- Provide state validation and update helpers

### Agent Implementations

#### `smart_code_review/agents/base_agent.py`
**Implement**: Abstract base class for all agents
- Create `BaseAgent` abstract class
- Implement standardized `execute()` method with error handling
- Add completion tracking to `agents_completed` list
- Provide consistent logging patterns
- Define abstract `process()` method for subclasses

#### `smart_code_review/agents/pr_detector.py`
**Implement**: PR detection and parsing agent
- Parse GitHub PR details using GitHub service
- Extract file changes and content
- Send initial alert email
- Populate state with PR information and file data
- Handle both GitHub PRs and local file analysis

#### `smart_code_review/agents/security_agent.py`
**Implement**: Security vulnerability analysis
- Use security analyzer to detect vulnerabilities
- Calculate security scores (0-10 scale)
- Classify severity levels (HIGH, MEDIUM, LOW)
- Generate security recommendations
- Return structured security results

#### `smart_code_review/agents/quality_agent.py`
**Implement**: Code quality analysis using PyLint
- Integrate with PyLint service for static analysis
- Calculate code quality scores
- Categorize issues by type
- Generate quality improvement recommendations
- Handle PyLint execution errors gracefully

#### `smart_code_review/agents/coverage_agent.py`
**Implement**: Test coverage analysis
- Use coverage service to analyze test coverage
- Identify missing test coverage areas
- Calculate coverage percentages
- Generate test recommendations
- Handle missing test files

#### `smart_code_review/agents/ai_review_agent.py`
**Implement**: AI-powered code review using Gemini
- Integrate with Gemini service for AI analysis
- Use context from other agents for enhanced analysis
- Generate code suggestions and improvements
- Calculate AI confidence scores
- Create comprehensive PR summaries

#### `smart_code_review/agents/documentation_agent.py`
**Implement**: Documentation quality analysis
- Analyze docstring coverage and quality
- Identify missing documentation
- Calculate documentation coverage percentages
- Generate documentation improvement suggestions
- Assess API documentation completeness

#### `smart_code_review/agents/agent_coordinator.py`
**Implement**: Result aggregation and coordination
- Wait for all agents to complete
- Aggregate results from all 5 agents
- Prepare combined state for decision making
- Handle partial results from failed agents
- Coordinate email notifications

### Service Implementations

#### `smart_code_review/services/github/client.py`
**Implement**: GitHub API integration
- Create `GitHubClient` class with authentication
- Implement PR details retrieval
- Get file contents and changes
- Handle GitHub API rate limiting
- Provide error handling for API failures

#### `smart_code_review/services/gemini/client.py`
**Implement**: Gemini AI service integration
- Create `GeminiClient` class with API key authentication
- Implement code review generation
- Create PR summary generation
- Handle streaming responses
- Provide fallback responses for failures

#### `smart_code_review/services/gemini/prompts.py`
**Implement**: AI prompt templates
- Create structured prompts for code review
- Design PR summary prompt templates
- Include context integration prompts
- Provide security enhancement prompts
- Create documentation improvement prompts

#### `smart_code_review/services/email_service.py`
**Implement**: Email notification system
- Create `EmailService` class with SMTP integration
- Implement HTML email templates
- Send notifications for different workflow stages
- Handle email authentication and TLS
- Provide error handling for email failures

#### `smart_code_review/services/pylint_service.py`
**Implement**: PyLint integration service
- Create `PylintService` class
- Execute PyLint analysis on code files
- Parse PyLint output and scores
- Handle PyLint configuration
- Provide graceful degradation if PyLint unavailable

#### `smart_code_review/services/coverage_service.py`
**Implement**: Test coverage analysis service
- Create `CoverageService` class
- Integrate with coverage.py library
- Analyze test coverage for Python files
- Identify missing test coverage
- Generate coverage reports and metrics

### Analyzer Implementations

#### `smart_code_review/analyzers/security_analyzer.py`
**Implement**: Security vulnerability detection
- Create `detect_security_vulnerabilities()` function
- Define 17+ security vulnerability patterns
- Implement pattern matching with regex
- Calculate security scores based on findings
- Generate specific security recommendations

#### `smart_code_review/analyzers/documentation_analyzer.py`
**Implement**: Documentation quality analysis
- Create `analyze_documentation_quality()` function
- Parse Python AST to find functions and classes
- Check for missing docstrings
- Calculate documentation coverage percentages
- Assess docstring quality and completeness

### Workflow Implementation

#### `smart_code_review/workflows/parallel_workflow.py`
**Implement**: LangGraph workflow orchestration
- Create `ParallelMultiAgentWorkflow` class
- Build LangGraph StateGraph with all agents
- Implement TRUE parallel agent execution
- Create decision maker with quality thresholds
- Implement report generator
- Add comprehensive error handling

### Utility Implementations

#### `smart_code_review/utils/logging_utils.py`
**Implement**: Logging configuration
- Create `setup_logging()` function
- Configure structured logging with levels
- Implement file and console logging
- Provide agent-specific logger creation

#### `smart_code_review/utils/validation.py`
**Implement**: Input validation utilities
- Create `validate_file_paths()` function
- Implement `parse_repo_url()` function
- Add input sanitization functions
- Provide validation error handling

#### `smart_code_review/utils/error_handling.py`
**Implement**: Error handling utilities
- Create custom exception classes
- Implement `safe_execute()` decorator
- Add detailed error information capture
- Provide graceful degradation helpers

### Model Implementations

#### `smart_code_review/models/review_state.py`
**Implement**: Review state data model
- Define `ReviewState` TypedDict or dataclass
- Specify all state fields and types
- Add state validation methods
- Provide state serialization helpers

### Testing Implementation

#### `tests.py`
**Implement**: Comprehensive test suite
- Test all agent implementations
- Test service integrations with mocks
- Test workflow execution
- Test error handling scenarios
- Test configuration management
- Provide sample data for testing

## Learning Objectives

By completing this project, you will learn:

### **Technical Skills**
- **Multi-Agent System Design**: Build systems with specialized, parallel components
- **LangGraph Workflow Orchestration**: Modern AI workflow management
- **API Integration**: GitHub API, Gemini AI API, SMTP email services
- **Parallel Processing**: TRUE concurrent execution vs sequential processing
- **State Management**: Complex state transitions in distributed systems
- **Error Handling**: Graceful degradation and resilience patterns
- **Testing Strategies**: Unit, integration, and system testing

### **Software Engineering Practices**
- **Clean Architecture**: Separation of concerns and dependency injection
- **Configuration Management**: Environment-based configuration
- **Logging and Monitoring**: Structured logging and error tracking
- **Security Best Practices**: Vulnerability detection and secure coding
- **Documentation**: Comprehensive code and system documentation

### **AI/ML Integration**
- **Large Language Model Integration**: Working with Gemini 2.0 Flash
- **Prompt Engineering**: Designing effective AI prompts
- **Context-Aware AI**: Using multi-agent context for better AI responses
- **AI Decision Making**: Confidence-based automated decisions

## Email Notification System You Will Build

**Your Task**: Implement an email notification system that sends:

- **Review Started**: PR analysis initiated notification
- **Agent Complete**: Individual agent completion notifications
- **Analysis Complete**: Combined analysis results
- **AI Review Complete**: Gemini AI recommendations
- **Final Report**: Approval, escalation, or review decision
- **Error Notifications**: System failure alerts

## Additional Resources

- **Architecture Documentation**: See `ARCHITECTURE.md` for detailed system design
- **LangGraph Documentation**: [LangGraph Official Docs](https://langchain-ai.github.io/langgraph/)
- **Gemini AI Documentation**: [Google AI Studio](https://ai.google.dev/)
- **GitHub API Documentation**: [GitHub REST API](https://docs.github.com/en/rest)

## Submission Guidelines

### **Implementation Requirements**
1. All files marked with 🔨 IMPLEMENT must be completed
2. All tests in `tests.py` must pass
3. System must handle both GitHub PRs and local files
4. All 5 agents must execute in TRUE parallel (not sequential)
5. Email notifications must work for all workflow stages
6. Error handling must be comprehensive with graceful degradation

### **Code Quality Standards**
- Follow PEP 8 Python style guidelines
- Include type hints for all functions
- Add docstrings for all classes and methods
- Implement comprehensive error handling
- Write unit tests for all major components

### **Testing Requirements**
- All unit tests must pass: `python tests.py`
- Demo mode must work: `python main.py demo`
- Local file analysis must work: `python main.py files demo_sample.py`
- GitHub PR analysis must work (with valid credentials)

## Dependencies

**Required Python Packages** (already in requirements.txt):
- Python 3.8+
- LangGraph >= 0.0.10
- Langchain-core >= 0.0.10
- Google Generative AI SDK >= 0.3.0
- PyLint >= 2.8.0
- Pytest >= 6.0.0
- Pytest-cov >= 2.12.0
- Python-dotenv >= 0.15.0
- Requests >= 2.25.0

**External Services Required**:
- GitHub Personal Access Token
- Google AI Studio API Key (Gemini)
- Gmail Account with App Password

---

**Good luck building your Multi-Agent Code Review System!**