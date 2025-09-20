import re
import ast
import logging
from typing import Dict, Any, List

logger = logging.getLogger("test_analyzer")

def analyze_test_quality(code: str, filename: str) -> Dict[str, Any]:
    """Analyze test quality and coverage gaps"""
    test_quality_score = 5.0  # Start with a neutral score
    missing_test_types = []
    
    # Check if this is a test file
    is_test_file = 'test' in filename.lower() or 'tests' in filename.lower()
    
    if is_test_file:
        test_quality_score = 8.0  # Start higher for test files
        
        # Check for different types of tests
        if 'unittest' not in code and 'pytest' not in code:
            missing_test_types.append('Unit tests')
            test_quality_score -= 1.0
            
        if 'mock' not in code.lower() and 'Mock' not in code:
            missing_test_types.append('Mock tests')
            test_quality_score -= 0.5
            
        if 'integration' not in code.lower() and 'functional' not in code.lower():
            missing_test_types.append('Integration tests')
            test_quality_score -= 0.5
            
        # Check for assertions
        try:
            tree = ast.parse(code)
            assertions = [
                node for node in ast.walk(tree) 
                if (isinstance(node, ast.Assert) or 
                    (isinstance(node, ast.Call) and 
                     hasattr(node.func, 'attr') and 
                     'assert' in getattr(node.func, 'attr', '').lower()))
            ]
            
            if len(assertions) < 1:
                missing_test_types.append('Assertions')
                test_quality_score -= 2.0
            
            # Check test structure
            test_functions = [
                node for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and 
                   (node.name.startswith('test_') or node.name.endswith('_test'))
            ]
            
            if not test_functions:
                missing_test_types.append('Proper test functions')
                test_quality_score -= 1.5
                
            # Check for test fixtures/setup/teardown
            has_setup = any('setup' in node.name.lower() or 'fixture' in node.name.lower() 
                            for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            
            if not has_setup and len(test_functions) > 3:
                missing_test_types.append('Test fixtures or setup')
                test_quality_score -= 0.5
                
        except Exception as e:
            logger.error(f"Error parsing test code: {e}")
    else:
        # Non-test file - check if it has testable elements
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            # Check if file has testable elements but no tests
            if functions or classes:
                missing_test_types = ['Unit tests', 'Integration tests', 'Mock tests']
                test_quality_score = 3.0  # Lower score for non-test files
        except Exception as e:
            logger.error(f"Error parsing source code: {e}")
            missing_test_types = ['Unable to analyze test quality']
    
    # Calculate testability score
    testability_score = 10.0 - len(missing_test_types) * 2.0
    
    # Ensure scores are in valid ranges
    test_quality_score = max(0.0, min(10.0, test_quality_score))
    testability_score = max(0.0, min(10.0, testability_score))
    
    return {
        'test_quality_score': test_quality_score,
        'missing_test_types': missing_test_types,
        'testability_score': testability_score
    }