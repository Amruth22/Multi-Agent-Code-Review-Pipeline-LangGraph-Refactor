#!/usr/bin/env python3
"""
Comprehensive test suite for the Smart Code Review Pipeline.
Tests all major components and services.

Run with: python tests.py
"""

import os
import sys
import unittest
import logging
import tempfile
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("tests")

# Import the required modules
try:
    from smart_code_review.core.config import get_config, get_config_value, validate_config
    from smart_code_review.core.state import StateManager
    from smart_code_review.models.review_state import ReviewState
    from smart_code_review.services.github.client import GitHubClient
    from smart_code_review.services.pylint_service import PylintService
    from smart_code_review.services.coverage_service import CoverageService
    from smart_code_review.services.gemini_service import GeminiService
    from smart_code_review.analyzers.security_analyzer import detect_security_vulnerabilities
    from smart_code_review.analyzers.documentation_analyzer import analyze_documentation_quality
    from smart_code_review.agents.security_agent import SecurityAnalysisAgent
    from smart_code_review.agents.quality_agent import QualityAnalysisAgent
    from smart_code_review.agents.coverage_agent import CoverageAnalysisAgent
    from smart_code_review.agents.ai_review_agent import AIReviewAgent
    from smart_code_review.agents.documentation_agent import DocumentationAgent
    from smart_code_review.workflows.parallel_workflow import ParallelMultiAgentWorkflow
    from smart_code_review.utils.validation import validate_file_paths
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you're running this test from the project root directory")
    sys.exit(1)

class TestSmartCodeReview(unittest.TestCase):
    """Test suite for Smart Code Review Pipeline"""
    
    SAMPLE_CODE = '''
def calculate_total(items):
    """Calculate the total price of items"""
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total

def process_order(order_data):
    """Process an order and calculate totals with discounts"""
    if not order_data:
        return None
    
    items = order_data.get('items', [])
    total = calculate_total(items)
    
    # Apply discount
    discount = order_data.get('discount', 0)
    final_total = total - (total * discount / 100)
    
    # Security issue - evaluate expression from input
    if 'custom_calculation' in order_data:
        expression = order_data['custom_calculation']
        final_total = eval(expression)  # Security vulnerability!
    
    return {
        'order_id': order_data.get('id'),
        'total': final_total,
        'items_count': len(items)
    }

class OrderProcessor:
    def __init__(self):
        self.processed_orders = []
        self.api_key = "sk_test_123456789abcdef"  # Security issue - hardcoded API key
    
    def add_order(self, order):
        """Add an order to the processor"""
        result = process_order(order)
        if result:
            self.processed_orders.append(result)
        return result
        
    def get_orders(self):
        """Return all processed orders"""
        return self.processed_orders
    '''

    def setUp(self):
        """Setup test environment"""
        # Create a temporary file with the sample code
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write(self.SAMPLE_CODE)
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """Clean up test environment"""
        # Remove the temporary file
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_configuration(self):
        """Test configuration management"""
        logger.info("Testing configuration management...")
        
        # Test getting configuration
        config = get_config()
        self.assertIsNotNone(config, "Config should not be None")
        
        # Test getting specific values with defaults
        github_token = get_config_value("GITHUB_TOKEN", "default")
        self.assertIsNotNone(github_token, "GITHUB_TOKEN should not be None")
        
        # Test default value
        test_value = get_config_value("NON_EXISTENT_VALUE", "default_value")
        self.assertEqual(test_value, "default_value", "Default value should be returned for missing keys")
        
        # Test thresholds
        pylint_threshold = get_config_value("PYLINT_THRESHOLD", 0.0)
        self.assertGreaterEqual(pylint_threshold, 0.0, "PYLINT_THRESHOLD should be >= 0.0")
        
        coverage_threshold = get_config_value("COVERAGE_THRESHOLD", 0.0)
        self.assertGreaterEqual(coverage_threshold, 0.0, "COVERAGE_THRESHOLD should be >= 0.0")

        logger.info("✓ Configuration tests passed")
    
    def test_state_management(self):
        """Test state management"""
        logger.info("Testing state management...")
        
        # Test creating initial state
        state = StateManager.create_initial_state("owner", "repo", 123)
        self.assertIsNotNone(state, "State should not be None")
        self.assertEqual(state["repo_owner"], "owner", "Repo owner should be set correctly")
        self.assertEqual(state["repo_name"], "repo", "Repo name should be set correctly")
        self.assertEqual(state["pr_number"], 123, "PR number should be set correctly")
        
        # Test review ID format
        self.assertTrue("review_id" in state, "State should contain review_id")
        self.assertTrue(state["review_id"].startswith("REV-"), "Review ID should start with REV-")
        
        # Test timestamp format
        self.assertTrue("timestamp" in state, "State should contain timestamp")
        
        logger.info("✓ State management tests passed")
    
    def test_security_analysis(self):
        """Test security analysis functionality"""
        logger.info("Testing security analysis...")
        
        # Test direct analyzer
        with open(self.temp_file_path, 'r') as f:
            content = f.read()
        
        results = detect_security_vulnerabilities(content, self.temp_file_path)
        self.assertIsNotNone(results, "Security analysis results should not be None")
        self.assertTrue("vulnerabilities" in results, "Results should contain vulnerabilities")
        self.assertTrue(len(results["vulnerabilities"]) > 0, "Should find vulnerabilities in sample code")
        
        # Test security agent
        agent = SecurityAnalysisAgent()
        state = {
            "review_id": "TEST-REVIEW",
            "files_data": [{"filename": os.path.basename(self.temp_file_path), "content": content}]
        }
        result = agent.execute(state)
        self.assertIsNotNone(result, "Security agent result should not be None")
        self.assertTrue("security_results" in result, "Result should contain security_results")
        
        logger.info("✓ Security analysis tests passed")
    
    def test_documentation_analysis(self):
        """Test documentation analysis functionality"""
        logger.info("Testing documentation analysis...")
        
        # Test direct analyzer
        with open(self.temp_file_path, 'r') as f:
            content = f.read()
        
        results = analyze_documentation_quality(content, self.temp_file_path)
        self.assertIsNotNone(results, "Documentation analysis results should not be None")
        self.assertTrue("documentation_coverage" in results, "Results should contain documentation_coverage")
        
        # Test documentation agent
        agent = DocumentationAgent()
        state = {
            "review_id": "TEST-REVIEW",
            "files_data": [{"filename": os.path.basename(self.temp_file_path), "content": content}]
        }
        result = agent.execute(state)
        self.assertIsNotNone(result, "Documentation agent result should not be None")
        self.assertTrue("documentation_results" in result, "Result should contain documentation_results")
        
        logger.info("✓ Documentation analysis tests passed")
    
    def test_coverage_analysis(self):
        """Test coverage analysis functionality"""
        logger.info("Testing coverage analysis...")
        
        # Test coverage service
        coverage_service = CoverageService()
        
        with open(self.temp_file_path, 'r') as f:
            content = f.read()
        
        files_data = [{"filename": os.path.basename(self.temp_file_path), "content": content}]
        results = coverage_service.analyze_test_coverage(files_data)
        
        self.assertIsNotNone(results, "Coverage analysis results should not be None")
        self.assertTrue(len(results) > 0, "Should have at least one result")
        self.assertTrue("coverage_percent" in results[0], "Result should contain coverage_percent")
        
        # Test coverage agent
        agent = CoverageAnalysisAgent()
        state = {
            "review_id": "TEST-REVIEW",
            "files_data": files_data
        }
        result = agent.execute(state)
        self.assertIsNotNone(result, "Coverage agent result should not be None")
        self.assertTrue("coverage_results" in result, "Result should contain coverage_results")
        
        logger.info("✓ Coverage analysis tests passed")
    
    def test_quality_analysis(self):
        """Test quality (pylint) analysis functionality"""
        logger.info("Testing quality analysis...")
        
        # Test pylint service
        pylint_service = PylintService()
        
        with open(self.temp_file_path, 'r') as f:
            content = f.read()
        
        # The service should gracefully handle missing pylint installation
        result = pylint_service.analyze_file(os.path.basename(self.temp_file_path), content)
        self.assertIsNotNone(result, "PyLint analysis result should not be None")
        self.assertTrue("score" in result, "Result should contain score")
        
        # Test quality agent
        agent = QualityAnalysisAgent()
        state = {
            "review_id": "TEST-REVIEW",
            "files_data": [{"filename": os.path.basename(self.temp_file_path), "content": content}]
        }
        result = agent.execute(state)
        self.assertIsNotNone(result, "Quality agent result should not be None")
        self.assertTrue("pylint_results" in result, "Result should contain pylint_results")
        
        logger.info("✓ Quality analysis tests passed")
    
    def test_workflow_structure(self):
        """Test workflow structure and node setup"""
        logger.info("Testing workflow structure...")
        
        workflow = ParallelMultiAgentWorkflow()
        compiled_workflow = workflow.create_workflow()
        
        self.assertIsNotNone(compiled_workflow, "Compiled workflow should not be None")
        
        # We can't directly test the graph structure, but we can verify workflow methods
        self.assertTrue(hasattr(workflow, "decision_maker_node"), "Workflow should have decision_maker_node method")
        self.assertTrue(hasattr(workflow, "report_generator_node"), "Workflow should have report_generator_node method")
        self.assertTrue(hasattr(workflow, "error_handler_node"), "Workflow should have error_handler_node method")
        
        logger.info("✓ Workflow structure tests passed")
    
    def test_github_service(self):
        """Test GitHub service functionality if token is available"""
        logger.info("Testing GitHub service...")
        
        github_token = get_config_value("GITHUB_TOKEN", "")
        if not github_token or github_token == "your_github_token_here":
            logger.warning("Skipping GitHub service test - No valid GitHub token configured")
            return
        
        try:
            # Test GitHub client
            github_client = GitHubClient(github_token)
            self.assertIsNotNone(github_client, "GitHub client should not be None")
            
            # Test a public repository that should exist
            repo_details = github_client.get_repo_details("microsoft", "TypeScript")
            self.assertIsNotNone(repo_details, "Should retrieve Microsoft/TypeScript repo details")
            
            logger.info("✓ GitHub service tests passed")
        except Exception as e:
            self.fail(f"GitHub service test failed: {e}")
    
    def test_gemini_service(self):
        """Test Gemini service functionality if API key is available"""
        logger.info("Testing Gemini service...")
        
        gemini_api_key = get_config_value("GEMINI_API_KEY", "")
        if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
            logger.warning("Skipping Gemini service test - No valid Gemini API key configured")
            return
        
        try:
            # Test Gemini client
            gemini_service = GeminiService()
            self.assertIsNotNone(gemini_service, "Gemini service should not be None")
            
            # Test AI review agent
            agent = AIReviewAgent()
            with open(self.temp_file_path, 'r') as f:
                content = f.read()
                
            state = {
                "review_id": "TEST-REVIEW",
                "files_data": [{"filename": os.path.basename(self.temp_file_path), "content": content}]
            }
            
            result = agent.execute(state)
            self.assertIsNotNone(result, "AI review result should not be None")
            self.assertTrue("ai_reviews" in result, "Result should contain ai_reviews")
            
            logger.info("✓ Gemini service tests passed")
        except Exception as e:
            self.fail(f"Gemini service test failed: {e}")
    
    def test_full_pipeline(self):
        """Test the full pipeline on a sample file"""
        logger.info("Testing full pipeline execution...")
        
        # Read sample file
        with open(self.temp_file_path, 'r') as f:
            content = f.read()
        
        files_data = [{"filename": os.path.basename(self.temp_file_path), "content": content}]
        
        # Create state
        state = StateManager.create_initial_state("test", "repo", 0)
        state["files_data"] = files_data
        state["pr_details"] = {
            "pr_number": 0,
            "title": "Test PR",
            "author": "test-user",
            "head_branch": "test-branch",
            "base_branch": "main",
            "state": "open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Execute agents
        security_agent = SecurityAnalysisAgent()
        quality_agent = QualityAnalysisAgent()
        coverage_agent = CoverageAnalysisAgent()
        ai_review_agent = AIReviewAgent()
        documentation_agent = DocumentationAgent()
        
        # Execute agents
        security_results = security_agent.execute(state)
        quality_results = quality_agent.execute(state)
        coverage_results = coverage_agent.execute(state)
        ai_results = ai_review_agent.execute(state)
        documentation_results = documentation_agent.execute(state)
        
        # Combine results
        combined_state = {**state}
        for key in ["security_results", "pylint_results", "coverage_results", "ai_reviews", "documentation_results"]:
            if key in security_results:
                combined_state[key] = security_results[key]
            if key in quality_results:
                combined_state[key] = quality_results[key]
            if key in coverage_results:
                combined_state[key] = coverage_results[key]
            if key in ai_results:
                combined_state[key] = ai_results[key]
            if key in documentation_results:
                combined_state[key] = documentation_results[key]
        
        # Create decision
        workflow = ParallelMultiAgentWorkflow()
        decision_result = workflow.decision_maker_node(combined_state)
        combined_state.update(decision_result)
        
        self.assertIsNotNone(decision_result, "Decision result should not be None")
        self.assertTrue("decision" in decision_result, "Decision result should contain decision")
        
        # Skip report generation as it requires email configuration
        
        logger.info(f"Pipeline decision: {decision_result.get('decision', 'unknown')}")
        logger.info("✓ Full pipeline tests passed")

    def test_file_validation(self):
        """Test file validation functionality"""
        logger.info("Testing file validation...")
        
        # Test with existing file
        valid_files = validate_file_paths([self.temp_file_path])
        self.assertEqual(len(valid_files), 1, "Should validate one file")
        
        # Test with non-existent file
        invalid_files = validate_file_paths(["non_existent_file.py"])
        self.assertEqual(len(invalid_files), 0, "Should not validate non-existent files")
        
        # Test with non-Python file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            txt_path = f.name
        try:
            non_py_files = validate_file_paths([txt_path])
            self.assertEqual(len(non_py_files), 0, "Should not validate non-Python files")
        finally:
            os.unlink(txt_path)
        
        logger.info("✓ File validation tests passed")

def run_tests():
    """Run all tests"""
    logger.info("=" * 70)
    logger.info("Smart Code Review Pipeline - Test Suite")
    logger.info("=" * 70)
    
    # Check if the project is properly installed
    try:
        import smart_code_review
    except ImportError:
        logger.error("smart_code_review module not found!")
        logger.error("Make sure you run this test from the project root directory")
        logger.error("Try: pip install -e .")
        return
    
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    run_tests()