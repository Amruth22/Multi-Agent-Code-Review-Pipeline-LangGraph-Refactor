import ast
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("complexity_analyzer")

def analyze_code_complexity(code: str, filename: str) -> Dict[str, Any]:
    """Analyze code complexity and maintainability"""
    try:
        tree = ast.parse(code)
        
        # Count various complexity metrics
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        
        # Calculate complexity score (starting from perfect 10.0)
        complexity_score = 10.0
        code_smells = []
        
        # Check for long functions
        for func in functions:
            func_lines = func.end_lineno - func.lineno if hasattr(func, 'end_lineno') else 0
            if func_lines > 50:
                complexity_score -= 1.0
                code_smells.append(f"Function '{func.name}' is too long ({func_lines} lines)")
            elif func_lines > 30:
                complexity_score -= 0.5
                code_smells.append(f"Function '{func.name}' is getting long ({func_lines} lines)")
        
        # Check for too many parameters
        for func in functions:
            param_count = len(func.args.args) - (1 if func.args.args and func.args.args[0].arg == 'self' else 0)
            if param_count > 7:
                complexity_score -= 0.5
                code_smells.append(f"Function '{func.name}' has too many parameters ({param_count})")
            elif param_count > 5:
                complexity_score -= 0.2
                code_smells.append(f"Function '{func.name}' has many parameters ({param_count})")
        
        # Check for large classes
        for cls in classes:
            methods = [node for node in ast.walk(cls) if isinstance(node, ast.FunctionDef)]
            if len(methods) > 20:
                complexity_score -= 1.0
                code_smells.append(f"Class '{cls.name}' has too many methods ({len(methods)})")
            elif len(methods) > 10:
                complexity_score -= 0.5
                code_smells.append(f"Class '{cls.name}' has many methods ({len(methods)})")
        
        # Check for deep nesting
        max_nesting = calculate_max_nesting(tree)
        if max_nesting > 5:
            complexity_score -= 1.0
            code_smells.append(f"Code contains deep nesting (depth {max_nesting})")
        elif max_nesting > 3:
            complexity_score -= 0.5
            code_smells.append(f"Code contains moderate nesting (depth {max_nesting})")
        
        # Check for too many imports
        if len(imports) > 20:
            complexity_score -= 0.5
            code_smells.append(f"File has too many imports ({len(imports)})")
        
        # Check for large modules
        lines_count = code.count('\n') + 1
        if lines_count > 500:
            complexity_score -= 1.0
            code_smells.append(f"Module is too large ({lines_count} lines)")
        elif lines_count > 300:
            complexity_score -= 0.5
            code_smells.append(f"Module is getting large ({lines_count} lines)")
        
        # Calculate maintainability index (simplified version, 0-100 scale)
        # Higher is better
        maintainability_index = max(0, min(100, 100 - (
            lines_count / 10 +  # size factor
            len(functions) * 2 +  # function count factor
            max_nesting * 5 +  # nesting factor
            (10 - complexity_score) * 10  # complexity factor
        )))
        
        # Calculate technical debt (in days, based on code smells)
        technical_debt = len(code_smells) * 0.5
        
        return {
            'complexity_score': max(0.0, complexity_score),
            'maintainability_index': maintainability_index,
            'code_smells': code_smells,
            'technical_debt': technical_debt
        }
        
    except Exception as e:
        logger.error(f"Error analyzing code complexity: {e}")
        return {
            'complexity_score': 5.0,  # Neutral score for error cases
            'maintainability_index': 50.0,
            'code_smells': ['Unable to analyze code complexity'],
            'technical_debt': 1.0
        }

def calculate_max_nesting(tree: ast.AST) -> int:
    """Calculate the maximum nesting level in the AST"""
    max_nesting = 0
    
    def traverse_node(node, current_nesting=0):
        nonlocal max_nesting
        max_nesting = max(max_nesting, current_nesting)
        
        # Check for control structures that increase nesting
        if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            current_nesting += 1
        
        # Recursively traverse child nodes
        for child in ast.iter_child_nodes(node):
            traverse_node(child, current_nesting)
    
    traverse_node(tree)
    return max_nesting