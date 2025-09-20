import os
import tempfile
import json
import logging
import re
from typing import Dict, Any, List, Optional
import subprocess
from ..utils.error_handling import safe_execute

logger = logging.getLogger("pylint_service")

class PylintService:
    """Service for Python code quality analysis using PyLint"""
    
    def __init__(self):
        self._check_pylint_installed()
    
    def _check_pylint_installed(self):
        """Check if PyLint is installed"""
        try:
            subprocess.run(["pylint", "--version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE,
                          check=True)
            logger.debug("PyLint is installed and working")
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("PyLint is not installed or not working properly")
    
    def analyze_file(self, filename: str, content: str) -> Dict[str, Any]:
        """Analyze a single Python file with PyLint"""
        # Write content to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Run PyLint on the temporary file
            return self._run_pylint_on_file(temp_file_path, filename)
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def _run_pylint_on_file(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """Run PyLint on a file and parse the results"""
        try:
            # Run PyLint with JSON output format
            command = ["pylint", "--output-format=json", file_path]
            result = subprocess.run(command, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True,
                                   check=False)
            
            # Parse JSON output
            if result.stdout:
                try:
                    pylint_data = json.loads(result.stdout)
                    return self._parse_pylint_result(pylint_data, original_filename)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse PyLint output as JSON: {result.stdout}")
            
            # Handle PyLint errors
            if result.returncode != 0 and not result.stdout:
                logger.warning(f"PyLint returned error: {result.stderr}")
            
            # Return empty result if no data
            return self._create_empty_pylint_result(original_filename)
            
        except Exception as e:
            logger.error(f"Error running PyLint: {e}")
            return self._create_empty_pylint_result(original_filename)
    
    def _parse_pylint_result(self, pylint_data: List[Dict[str, Any]], original_filename: str) -> Dict[str, Any]:
        """Parse PyLint JSON result"""
        # Calculate score (PyLint uses a scale of 0-10)
        score = self._calculate_pylint_score(pylint_data)
        
        # Extract issues
        issues = []
        for item in pylint_data:
            issues.append({
                'line': item.get('line', 0),
                'column': item.get('column', 0),
                'type': item.get('type', ''),
                'symbol': item.get('symbol', ''),
                'message': item.get('message', ''),
                'message_id': item.get('message-id', '')
            })
        
        # Group issues by type
        issue_counts = {
            'convention': 0,
            'refactor': 0,
            'warning': 0,
            'error': 0,
            'fatal': 0
        }
        
        for issue in issues:
            issue_type = issue.get('type', '').lower()
            if issue_type in issue_counts:
                issue_counts[issue_type] += 1
        
        return {
            'filename': original_filename,
            'score': score,
            'total_issues': len(issues),
            'issue_counts': issue_counts,
            'issues': issues
        }
    
    def _calculate_pylint_score(self, pylint_data: List[Dict[str, Any]]) -> float:
        """Calculate PyLint score (0-10 scale)"""
        # Default score if no issues
        if not pylint_data:
            return 10.0
        
        # Calculate weighted score based on issue types
        weights = {
            'convention': 0.1,
            'refactor': 0.2,
            'warning': 0.4,
            'error': 1.0,
            'fatal': 2.0
        }
        
        # Count issues by type
        counts = {issue_type: 0 for issue_type in weights}
        for item in pylint_data:
            issue_type = item.get('type', '').lower()
            if issue_type in counts:
                counts[issue_type] += 1
        
        # Calculate penalty
        penalty = sum(counts[issue_type] * weights[issue_type] for issue_type in weights)
        
        # Calculate score (10 - penalty, minimum 0)
        return max(0.0, min(10.0, 10.0 - penalty / 2.0))
    
    def _create_empty_pylint_result(self, filename: str) -> Dict[str, Any]:
        """Create an empty PyLint result"""
        return {
            'filename': filename,
            'score': 10.0,  # Perfect score for empty result
            'total_issues': 0,
            'issue_counts': {
                'convention': 0,
                'refactor': 0,
                'warning': 0,
                'error': 0,
                'fatal': 0
            },
            'issues': []
        }
    
    def analyze_multiple_files(self, files_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple files with PyLint"""
        results = []
        
        for file_data in files_data:
            filename = file_data.get("filename", "")
            content = file_data.get("content", "")
            
            if content:
                logger.info(f" PyLint analyzing {filename}...")
                result = self.analyze_file(filename, content)
                results.append(result)
            else:
                logger.warning(f" No content for {filename}, skipping PyLint analysis...")
                results.append(self._create_empty_pylint_result(filename))
        
        return results
    
    def format_pylint_summary(self, pylint_results: List[Dict[str, Any]]) -> str:
        """Format PyLint results as readable summary"""
        if not pylint_results:
            return "No PyLint results available."
        
        summary = []
        summary.append("PyLint Analysis Summary")
        summary.append("=" * 30)
        
        for result in pylint_results:
            filename = result.get('filename', 'Unknown file')
            score = result.get('score', 0.0)
            total_issues = result.get('total_issues', 0)
            issue_counts = result.get('issue_counts', {})
            
            summary.append(f"\nFile: {filename}")
            summary.append(f"Score: {score:.2f}/10.0")
            summary.append(f"Issues: {total_issues} total")
            
            if issue_counts:
                summary.append("Issue breakdown:")
                for issue_type, count in issue_counts.items():
                    if count > 0:
                        summary.append(f"  - {issue_type.capitalize()}: {count}")
            
            # Add top issues
            issues = result.get('issues', [])
            if issues:
                top_issues = issues[:5]  # Show top 5 issues
                summary.append("\nTop issues:")
                for issue in top_issues:
                    line = issue.get('line', 0)
                    message = issue.get('message', '')
                    symbol = issue.get('symbol', '')
                    summary.append(f"  - Line {line}: {message} ({symbol})")
                
                if len(issues) > 5:
                    summary.append(f"  ... and {len(issues) - 5} more issues.")
        
        return "\n".join(summary)