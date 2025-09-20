import ast
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("documentation_analyzer")

def analyze_documentation_quality(code: str, filename: str) -> Dict[str, Any]:
    """Analyze documentation quality"""
    try:
        tree = ast.parse(code)
        
        # Extract documentable items
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        total_items = len(functions) + len(classes)
        documented_items = 0
        
        # Check for module docstring
        module_docstring = ast.get_docstring(tree)
        has_module_docstring = module_docstring is not None
        
        if has_module_docstring:
            documented_items += 1
            total_items += 1
        
        # Check for docstrings in functions and classes
        missing_docs = []
        
        for func in functions:
            if ast.get_docstring(func) is not None:
                documented_items += 1
            else:
                missing_docs.append(f"Function '{func.name}' missing docstring")
        
        for cls in classes:
            if ast.get_docstring(cls) is not None:
                documented_items += 1
            else:
                missing_docs.append(f"Class '{cls.name}' missing docstring")
        
        # Check for class methods
        for cls in classes:
            methods = [node for node in ast.walk(cls) if isinstance(node, ast.FunctionDef)]
            for method in methods:
                # Skip __methods__ as they don't always need docs
                if method.name.startswith('__') and method.name.endswith('__'):
                    continue
                
                if ast.get_docstring(method) is not None:
                    documented_items += 1
                else:
                    missing_docs.append(f"Method '{cls.name}.{method.name}' missing docstring")
                
                total_items += 1
        
        # Calculate documentation coverage percentage
        documentation_coverage = (documented_items / total_items * 100) if total_items > 0 else 100
        
        # Evaluate docstring quality for documented items
        docstring_quality = evaluate_docstring_quality(tree)
        
        return {
            'filename': filename,
            'documentation_coverage': documentation_coverage,
            'missing_documentation': missing_docs,
            'total_items': total_items,
            'documented_items': documented_items,
            'has_module_docstring': has_module_docstring,
            'docstring_quality': docstring_quality
        }
        
    except Exception as e:
        logger.error(f"Error analyzing documentation for {filename}: {e}")
        return {
            'filename': filename,
            'documentation_coverage': 0,
            'missing_documentation': ['Unable to analyze documentation'],
            'total_items': 0,
            'documented_items': 0,
            'has_module_docstring': False,
            'docstring_quality': {}
        }

def evaluate_docstring_quality(tree: ast.AST) -> Dict[str, Any]:
    """Evaluate the quality of docstrings in the AST"""
    quality_metrics = {
        'has_param_docs': False,
        'has_return_docs': False,
        'has_exception_docs': False,
        'avg_docstring_length': 0,
        'quality_score': 5.0  # Default neutral score
    }
    
    docstrings = []
    
    # Check module docstring
    module_docstring = ast.get_docstring(tree)
    if module_docstring:
        docstrings.append(module_docstring)
    
    # Check all docstrings in the tree
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings.append(docstring)
                
                # Check for param documentation
                if isinstance(node, ast.FunctionDef) and ':param' in docstring:
                    quality_metrics['has_param_docs'] = True
                
                # Check for return documentation
                if isinstance(node, ast.FunctionDef) and ':return' in docstring:
                    quality_metrics['has_return_docs'] = True
                
                # Check for exception documentation
                if ':raise' in docstring or ':except' in docstring:
                    quality_metrics['has_exception_docs'] = True
    
    # Calculate average docstring length
    if docstrings:
        quality_metrics['avg_docstring_length'] = sum(len(ds) for ds in docstrings) / len(docstrings)
    
    # Calculate quality score
    quality_score = 5.0  # Start with neutral score
    
    # Adjust score based on metrics
    if quality_metrics['has_param_docs']:
        quality_score += 1.0
    
    if quality_metrics['has_return_docs']:
        quality_score += 1.0
    
    if quality_metrics['has_exception_docs']:
        quality_score += 0.5
    
    # Adjust for docstring length
    avg_length = quality_metrics['avg_docstring_length']
    if avg_length > 100:
        quality_score += 1.0
    elif avg_length > 50:
        quality_score += 0.5
    elif avg_length < 10:
        quality_score -= 1.0
    
    quality_metrics['quality_score'] = max(0.0, min(10.0, quality_score))
    
    return quality_metrics