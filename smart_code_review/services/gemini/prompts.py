# Code review prompt template
CODE_REVIEW_PROMPT = """
You are an expert Python code reviewer. Analyze this code and provide a comprehensive review.

CONTEXT:
{context}

CODE TO REVIEW:
```python
{code}
```

Please provide your review in this exact format:

OVERALL_SCORE: [0.0 to 1.0]
CONFIDENCE: [0.0 to 1.0]

STRENGTHS:
• [List 2-3 positive aspects]

ISSUES:
• [List 2-4 specific issues or improvements needed]

RECOMMENDATIONS:
• [List 2-4 specific actionable recommendations]

REFACTORING_SUGGESTIONS:
• [List 1-3 refactoring ideas if applicable]

SECURITY_CONCERNS:
• [List any security issues or "None identified"]

Focus on code quality, maintainability, performance, and best practices.
"""

# PR summary prompt template
PR_SUMMARY_PROMPT = """
Generate a comprehensive PR review summary based on the analysis results.

PR DETAILS:
Title: {title}
Author: {author}
Files Changed: {files_count}

ANALYSIS RESULTS:
PyLint Score: {pylint_score}/10
Test Coverage: {coverage}%
AI Quality Score: {ai_score}/1.0

Provide a summary in this format:

OVERALL_RECOMMENDATION: [APPROVE/NEEDS_WORK/REJECT]
PRIORITY: [HIGH/MEDIUM/LOW]

KEY_FINDINGS:
• [2-3 most important findings]

ACTION_ITEMS:
• [2-4 specific actions needed]

APPROVAL_CRITERIA:
• [What needs to be fixed before approval]
"""

# Security enhancement prompt
SECURITY_ENHANCEMENT_PROMPT = """
Analyze this Python code for security vulnerabilities and provide specific improvements.

CODE:
```python
{code}
```

CURRENT VULNERABILITIES:
{vulnerabilities}

Please provide security enhancements in this format:

SECURITY_SCORE: [0.0 to 10.0]
SEVERITY: [HIGH/MEDIUM/LOW]

RECOMMENDED_FIXES:
• [List 2-4 specific fixes with code examples]

SECURE_ALTERNATIVES:
• [List secure alternatives to vulnerable patterns]

SECURITY_BEST_PRACTICES:
• [List relevant security best practices]

Focus on addressing the specific vulnerabilities while maintaining code functionality.
"""

# Documentation improvement prompt
DOCUMENTATION_IMPROVEMENT_PROMPT = """
Generate improved documentation for this Python code.

CODE:
```python
{code}
```

CURRENT DOCUMENTATION COVERAGE: {coverage}%

Please provide documentation improvements in this format:

MODULE_DOCSTRING:
\"\"\"
[Comprehensive module description]
\"\"\"

CLASS_DOCSTRINGS:
```python
class ClassName:
    \"\"\"
    [Class description]
    
    Attributes:
        attr1: Description of attribute 1
        attr2: Description of attribute 2
    \"\"\"
```

FUNCTION_DOCSTRINGS:
```python
def function_name(param1, param2):
    \"\"\"
    [Function description]
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception is raised
    \"\"\"
```

Follow PEP 257 docstring conventions and maintain existing code functionality.
"""