import os
import tempfile
import json
import logging
import re
import ast
from typing import Dict, Any, List, Optional, Set
import subprocess
from ..utils.error_handling import safe_execute

logger = logging.getLogger("coverage_service")

class CoverageService:
    """Service for test coverage analysis"""
    
    def __init__(self):
        self._check_pytest_installed()
    
    def _check_pytest_installed(self):
        """Check if pytest and pytest-cov are installed"""
        try:
            subprocess.run(["pytest", "--version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE,
                          check=True)
            logger.debug("pytest is installed and working")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("pytest is not installed or not working properly")
    
    def analyze_test_coverage(self, files_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze test coverage for multiple files"""
        results = []
        
        for file_data in files_data:
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")
            
            if content:
                logger.info(f" Analyzing test coverage for {filename}...")
                result = self._analyze_file_coverage(filename, content)
                results.append(result)
            else:
                logger.warning(f" No content for {filename}, skipping coverage analysis...")
                results.append(self._create_empty_coverage_result(filename))
        
        return results
    
    def _analyze_file_coverage(self, filename: str, content: str) -> Dict[str, Any]:
        """Analyze coverage for a single file"""
        # For a real implementation, this would run pytest with coverage
        # Here, we'll simulate coverage analysis based on the file content
        
        try:
            # Parse the file to get functions and classes
            tree = ast.parse(content)
            
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            # Check if it's a test file
            is_test_file = "test_" in filename or "tests" in filename
            
            # Simulate coverage calculation
            if is_test_file:
                coverage_percent = 90.0  # Higher coverage for test files
            else:
                # Calculate based on function and class complexity
                total_items = len(functions) + len(classes)
                if total_items == 0:
                    coverage_percent = 100.0  # Empty files are "fully covered"
                else:
                    # Simulate coverage - more complex files have lower coverage
                    complexity = self._calculate_complexity(functions, classes)
                    coverage_percent = max(10.0, min(95.0, 100.0 - complexity * 5.0))
            
            # Generate simulated coverage data
            covered_lines = self._simulate_covered_lines(content, coverage_percent)
            uncovered_lines = self._simulate_uncovered_lines(content, covered_lines)
            
            return {
                "filename": filename,
                "coverage_percent": coverage_percent,
                "covered_lines": covered_lines,
                "uncovered_lines": uncovered_lines,
                "is_test_file": is_test_file
            }
            
        except Exception as e:
            logger.error(f"Error analyzing coverage for {filename}: {e}")
            return self._create_empty_coverage_result(filename)
    
    def _calculate_complexity(self, functions: List[ast.FunctionDef], classes: List[ast.ClassDef]) -> float:
        """Calculate a complexity score based on code structure"""
        complexity = 0.0
        
        # Add complexity for functions
        for func in functions:
            # More parameters = more complex
            complexity += len(func.args.args) * 0.2
            
            # More lines = more complex
            func_lines = func.end_lineno - func.lineno if hasattr(func, 'end_lineno') else 10
            complexity += func_lines * 0.05
        
        # Add complexity for classes
        for cls in classes:
            # More methods = more complex
            methods = [node for node in ast.walk(cls) if isinstance(node, ast.FunctionDef)]
            complexity += len(methods) * 0.3
            
            # Inheritance adds complexity
            complexity += len(cls.bases) * 0.5
        
        return complexity
    
    def _simulate_covered_lines(self, content: str, coverage_percent: float) -> List[int]:
        """Simulate covered lines based on coverage percentage"""
        lines = content.split("\n")
        total_lines = len(lines)
        
        # Calculate number of covered lines
        num_covered = int(total_lines * coverage_percent / 100)
        
        # Simulate covered lines (evenly distributed)
        covered_lines = []
        step = max(1, total_lines // num_covered)
        
        for i in range(0, total_lines, step):
            if len(covered_lines) < num_covered:
                covered_lines.append(i + 1)  # Line numbers are 1-indexed
        
        return covered_lines
    
    def _simulate_uncovered_lines(self, content: str, covered_lines: List[int]) -> List[int]:
        """Simulate uncovered lines based on covered lines"""
        lines = content.split("\n")
        total_lines = len(lines)
        
        # Create set of all lines and remove covered ones
        all_lines = set(range(1, total_lines + 1))  # Line numbers are 1-indexed
        covered_set = set(covered_lines)
        
        return sorted(list(all_lines - covered_set))
    
    def _create_empty_coverage_result(self, filename: str) -> Dict[str, Any]:
        """Create an empty coverage result"""
        return {
            "filename": filename,
            "coverage_percent": 0.0,
            "covered_lines": [],
            "uncovered_lines": [],
            "is_test_file": False
        }
    
    def analyze_missing_tests(self, files_data: List[Dict[str, Any]], 
                           coverage_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify missing tests based on coverage results"""
        missing_tests = []
        
        for i, file_data in enumerate(files_data):
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")
            
            # Skip test files
            if "test_" in filename or "tests" in filename:
                continue
            
            # Get corresponding coverage result
            coverage_result = None
            for result in coverage_results:
                if result.get("filename") == filename:
                    coverage_result = result
                    break
            
            if coverage_result and content:
                # Find functions and classes that need tests
                uncovered_lines = set(coverage_result.get("uncovered_lines", []))
                missing = self._identify_missing_tests(content, uncovered_lines)
                
                if missing["untested_functions"] or missing["untested_classes"]:
                    missing_tests.append({
                        "filename": filename,
                        "untested_functions": missing["untested_functions"],
                        "untested_classes": missing["untested_classes"]
                    })
        
        return missing_tests
    
    def _identify_missing_tests(self, content: str, uncovered_lines: Set[int]) -> Dict[str, List[str]]:
        """Identify functions and classes without tests"""
        try:
            tree = ast.parse(content)
            
            untested_functions = []
            untested_classes = []
            
            # Check functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    line_num = node.lineno
                    # If first line of function is uncovered, consider it untested
                    if line_num in uncovered_lines:
                        untested_functions.append(node.name)
                
                elif isinstance(node, ast.ClassDef):
                    line_num = node.lineno
                    # If first line of class is uncovered, consider it untested
                    if line_num in uncovered_lines:
                        untested_classes.append(node.name)
            
            return {
                "untested_functions": untested_functions,
                "untested_classes": untested_classes
            }
            
        except Exception as e:
            logger.error(f"Error identifying missing tests: {e}")
            return {
                "untested_functions": [],
                "untested_classes": []
            }
    
    def format_coverage_summary(self, coverage_results: List[Dict[str, Any]]) -> str:
        """Format coverage results as readable summary"""
        if not coverage_results:
            return "No coverage results available."
        
        summary = []
        summary.append("Coverage Analysis Summary")
        summary.append("=" * 30)
        
        # Calculate overall coverage
        total_coverage = sum(r.get('coverage_percent', 0) for r in coverage_results) / len(coverage_results)
        summary.append(f"\nOverall Coverage: {total_coverage:.1f}%")
        
        # Add file breakdown
        summary.append("\nFile breakdown:")
        for result in coverage_results:
            filename = result.get('filename', 'Unknown file')
            coverage = result.get('coverage_percent', 0)
            is_test = result.get('is_test_file', False)
            file_type = "Test file" if is_test else "Source file"
            
            summary.append(f"- {filename}: {coverage:.1f}% ({file_type})")
        
        return "\n".join(summary)