# Smart Code Review - Optimized Parallel Multi-Agent System

A modular, optimized implementation of the Smart Code Review Pipeline using **LangGraph Multi-Agent Orchestration**, **Gemini 2.0 Flash**, **GitHub API**, and **Gmail** for comprehensive Python code analysis with specialized agents working in parallel.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Run the CLI tool
code-review

# Review GitHub PR (Parallel Multi-Agent)
code-review pr https://github.com/user/repo 123

# Review local files (Multi-Agent Analysis)
code-review files app.py utils.py models.py

# Run demo (Parallel Multi-Agent Demo)
code-review demo
```

## Optimized Architecture

The project has been completely restructured for improved modularity, maintainability, and extensibility:

```
smart_code_review/
├── core/                           # Core application framework
│   ├── config.py                   # Configuration management
│   └── state.py                    # State management abstraction
├── agents/                         # Agent implementations
│   ├── base_agent.py               # Abstract base agent class
│   ├── pr_detector.py              # PR detection agent
│   ├── security_agent.py           # Security analysis agent
│   ├── quality_agent.py            # Quality analysis agent  
│   ├── coverage_agent.py           # Coverage analysis agent
│   ├── ai_review_agent.py          # AI review agent
│   ├── documentation_agent.py      # Documentation agent
│   └── agent_coordinator.py        # Agent coordination logic
├── services/                       # External service integrations
│   ├── github/                     # GitHub service module
│   │   ├── client.py               # GitHub API client
│   │   └── models.py               # GitHub data models
│   ├── gemini/                     # Gemini AI service module
│   │   ├── client.py               # Gemini API client
│   │   ├── parser.py               # Response parsing utilities
│   │   └── prompts.py              # Prompt templates
│   ├── pylint_service.py           # PyLint integration
│   ├── coverage_service.py         # Test coverage analysis
│   └── email_service.py            # Email notifications
├── analyzers/                      # Analysis components
│   ├── security_analyzer.py        # Security vulnerability detection
│   ├── code_complexity.py          # Code complexity analysis
│   ├── test_quality.py             # Test quality analysis
│   └── documentation_analyzer.py   # Documentation analysis
├── workflows/                      # Workflow implementations
│   └── parallel_workflow.py        # Parallel multi-agent workflow
├── utils/                          # Utility modules
│   ├── logging_utils.py            # Logging utilities
│   ├── validation.py               # Input validation
│   ├── formatters.py               # Output formatting utilities
│   └── error_handling.py           # Error handling utilities
├── models/                         # Data models and schemas
│   └── review_state.py             # Review state model
├── __init__.py                     # Package initialization
└── main.py                         # Application entry point
```

## Parallel Multi-Agent Workflow

1. **PR Detector Agent** → Fetch PR details and extract Python files
2. **Parallel Agent Execution** → 5 specialized agents working simultaneously:
   - **Security Analysis Agent** → Vulnerability detection and security scoring
   - **Quality Analysis Agent** → PyLint + complexity metrics + code smells
   - **Coverage Analysis Agent** → Test coverage + missing test identification
   - **AI Review Agent** → Gemini 2.0 Flash with cross-agent context
   - **Documentation Agent** → Docstring coverage + API documentation
3. **Agent Coordinator** → Aggregate and correlate all agent results
4. **Decision Maker** → Multi-dimensional threshold evaluation
5. **Report Generator** → Comprehensive email report with all agent findings

## Email Notifications

- **Review Started**: PR analysis initiated
- **Analysis Complete**: PyLint + coverage results
- **AI Review Complete**: Gemini recommendations
- **Final Report**: Approval or escalation decision

## Enhanced Quality Thresholds

- **PyLint Score**: ≥ 7.0/10.0
- **Test Coverage**: ≥ 80%
- **AI Confidence**: ≥ 0.8
- **Security Score**: ≥ 8.0/10.0
- **Documentation Coverage**: ≥ 70%

## Configuration

The application uses environment variables for secure credential management. Configuration is loaded from a `.env` file:

```bash
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

## Key Improvements

1. **Enhanced Modularity**:
   - Clean separation of concerns with specialized modules
   - Well-defined component interfaces
   - Improved code organization

2. **Improved Maintainability**:
   - Base agent class with standardized execution flow
   - Consistent error handling across all components
   - Proper logging infrastructure

3. **Better Testability**:
   - Service abstractions with clean interfaces
   - Dependency injection for easier testing
   - Separate analyzers from agents

4. **Type Safety**:
   - Comprehensive type annotations throughout
   - Well-defined data models
   - Clear state management

5. **Error Handling**:
   - Standardized error handling patterns
   - Custom exception hierarchy
   - Proper logging and reporting

6. **Configuration Management**:
   - Centralized configuration management
   - Environment variable support
   - Default configuration values

## Features

### **GitHub Integration**
- Real PR analysis via GitHub API
- Changed files detection
- Python file filtering
- Content extraction

### **Static Analysis**
- PyLint code quality scoring
- Code smell detection
- Complexity analysis
- Best practices validation

### **Test Coverage**
- pytest coverage analysis
- Missing test identification
- Function/class coverage mapping
- Coverage percentage calculation

### **AI Code Review**
- Gemini 2.0 Flash intelligent analysis
- Code improvement suggestions
- Security vulnerability detection
- Refactoring recommendations
- Confidence scoring

### **Email Reports**
- Gmail SMTP integration
- Stage-by-stage notifications
- Comprehensive final reports
- Critical issue alerts