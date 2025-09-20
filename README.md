# 🔍 Smart Code Review Pipeline - Parallel Multi-Agent System

Automated code review system using **LangGraph Multi-Agent Orchestration** + **Gemini 2.0 Flash** + **GitHub API** + **Gmail** for comprehensive Python code analysis with specialized agents working in parallel.

## 📋 Overview

The Smart Code Review Pipeline is an advanced automated code review system that leverages multiple specialized AI agents working in parallel to analyze and evaluate Python code. It can analyze both GitHub pull requests and local Python files, providing comprehensive feedback on security vulnerabilities, code quality, test coverage, documentation, and AI-powered suggestions.

### Key Features:

- **True Parallel Execution**: All agents run simultaneously for maximum efficiency
- **GitHub Integration**: Real PR analysis via GitHub API
- **Static Analysis**: PyLint code quality scoring and complexity analysis
- **Test Coverage**: Coverage analysis and missing test identification
- **AI Code Review**: Gemini 2.0 Flash intelligent analysis
- **Email Reports**: Comprehensive notifications and reports

## 🤖 Parallel Multi-Agent Architecture

This system implements a true parallel multi-agent architecture with 5 specialized agents:

1. **🔒 Security Analysis Agent** → Vulnerability detection and security scoring
2. **📊 Quality Analysis Agent** → PyLint + complexity metrics + code smells
3. **🧪 Coverage Analysis Agent** → Test coverage + missing test identification
4. **🤖 AI Review Agent** → Gemini 2.0 Flash with cross-agent context
5. **📚 Documentation Agent** → Docstring coverage + API documentation

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Run in interactive mode
python main.py

# Review GitHub PR
python main.py pr https://github.com/user/repo 123

# Review local files
python main.py files path/to/file1.py path/to/file2.py

# Run demo
python main.py demo
```

## ⚙️ Configuration

Create a `.env` file with your credentials:

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

## 📊 Quality Thresholds

The system enforces the following quality thresholds:

- **PyLint Score**: ≥ 7.0/10.0
- **Test Coverage**: ≥ 80%
- **AI Confidence**: ≥ 0.8
- **Security Score**: ≥ 8.0/10.0
- **Documentation Coverage**: ≥ 70%

## 📁 Project Structure

The project has been structured for improved modularity and maintainability:

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
│   ├── gemini/                     # Gemini AI service module
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
├── visualization/                  # Visualization components
├── __init__.py                     # Package initialization
└── main.py                         # Application entry point
```

## 🚀 Testing

To verify the installation, run the test script:

```bash
python tests.py
```

## 📄 Advanced Documentation

For more detailed information, see the documentation in the `smart_code_review/README.md` file.

## 📧 Email Notifications

The system sends the following email notifications:

- **Review Started**: PR analysis initiated
- **Analysis Complete**: PyLint + coverage results
- **AI Review Complete**: Gemini recommendations
- **Final Report**: Approval or escalation decision

## 📝 Requirements

- Python 3.8+
- LangGraph >= 0.0.10
- Langchain-core >= 0.0.10
- Google Generative AI SDK >= 0.3.0
- PyLint >= 2.8.0
- Pytest >= 6.0.0
- Pytest-cov >= 2.12.0
- Python-dotenv >= 0.15.0