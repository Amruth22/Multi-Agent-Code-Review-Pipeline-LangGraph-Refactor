#!/usr/bin/env python3
"""
Smart Code Review Pipeline
Parallel Multi-Agent implementation with LangGraph + Gemini 2.0 Flash + GitHub API + Gmail
Specialized agents working in parallel for comprehensive code analysis
"""

import sys
import os
import argparse
import logging
from typing import List, Optional
import tempfile

from .utils.logging_utils import setup_logging
from .utils.validation import parse_repo_url, validate_file_paths
from .workflows.parallel_workflow import ParallelMultiAgentWorkflow
from .core.config import validate_config, get_config_value

def main():
    """Main application entry point"""
    # Setup logging
    log_file = get_config_value("LOG_FILE", "logs/code_review.log")
    log_level = get_config_value("LOG_LEVEL", "INFO")
    setup_logging(log_level, log_file)
    
    # Create logger
    logger = logging.getLogger("main")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Smart Code Review Pipeline - Parallel Multi-Agent System")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # PR review command
    pr_parser = subparsers.add_parser("pr", help="Review GitHub pull request")
    pr_parser.add_argument("repo_url", help="GitHub repository URL")
    pr_parser.add_argument("pr_number", type=int, help="Pull request number")
    
    # Local files review command
    files_parser = subparsers.add_parser("files", help="Review local Python files")
    files_parser.add_argument("file_paths", nargs="+", help="Python file paths to review")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run demo scenarios")
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Validate configuration
        validate_config()
        
        # Handle command
        if args.command == "pr":
            review_github_pr(args.repo_url, args.pr_number)
        elif args.command == "files":
            review_local_files(args.file_paths)
        elif args.command == "demo":
            run_demo()
        else:
            # Interactive mode
            interactive_mode()
            
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def review_github_pr(repo_url: str, pr_number: int):
    """Review a GitHub pull request"""
    logger = logging.getLogger("main.pr")
    
    # Parse repository URL
    repo_owner, repo_name = parse_repo_url(repo_url)
    if not repo_owner or not repo_name:
        logger.error("Invalid repository URL format")
        print("Invalid repository URL format")
        return
    
    logger.info(f"Reviewing PR #{pr_number} from {repo_owner}/{repo_name}")
    print(f"Reviewing PR #{pr_number} from {repo_owner}/{repo_name}")
    
    # Create and execute workflow
    workflow = ParallelMultiAgentWorkflow()
    workflow.execute(repo_owner, repo_name, pr_number)

def review_local_files(file_paths: List[str]):
    """Review local Python files"""
    logger = logging.getLogger("main.files")
    
    # Validate file paths
    valid_files = validate_file_paths(file_paths)
    if not valid_files:
        logger.error("No valid Python files to review")
        print("No valid Python files to review")
        return
    
    logger.info(f"Reviewing {len(valid_files)} local Python files")
    print(f"Reviewing {len(valid_files)} local Python files")
    
    # For local files, we need to create a simulated PR structure
    # (In a real implementation, this would need to be enhanced)
    from .services.github.models import PullRequest
    
    # Create temporary PR data
    pr_details = {
        "pr_number": 0,
        "title": "Local Files Review",
        "author": "local-user",
        "head_branch": "local",
        "base_branch": "main",
        "state": "open",
        "created_at": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Read file contents
    files_data = []
    for file_path in valid_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                files_data.append({
                    "filename": os.path.basename(file_path),
                    "status": "modified",
                    "additions": content.count('\n'),
                    "deletions": 0,
                    "changes": content.count('\n'),
                    "content": content
                })
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
    
    if not files_data:
        logger.error("Could not read any files")
        print("Could not read any files")
        return
    
    # Create a modified workflow for local files
    # (In a real implementation, this would be a separate workflow class)
    # For now, we'll use a similar approach to the main workflow
    from .core.state import StateManager
    
    # Create initial state
    state = StateManager.create_initial_state("local", "files", 0)
    state["pr_details"] = pr_details
    state["files_data"] = files_data
    
    # Execute individual agents
    from .agents.security_agent import SecurityAnalysisAgent
    from .agents.quality_agent import QualityAnalysisAgent
    from .agents.coverage_agent import CoverageAnalysisAgent
    from .agents.ai_review_agent import AIReviewAgent
    from .agents.documentation_agent import DocumentationAgent
    
    # Run security analysis
    security_agent = SecurityAnalysisAgent()
    security_results = security_agent.execute(state)
    
    # Run quality analysis
    quality_agent = QualityAnalysisAgent()
    quality_results = quality_agent.execute(state)
    
    # Run coverage analysis
    coverage_agent = CoverageAnalysisAgent()
    coverage_results = coverage_agent.execute(state)
    
    # Run AI review
    ai_review_agent = AIReviewAgent()
    ai_results = ai_review_agent.execute(state)
    
    # Run documentation analysis
    documentation_agent = DocumentationAgent()
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
    
    # Generate report
    report_result = workflow.report_generator_node(combined_state)
    combined_state.update(report_result)
    
    # Display results
    logger.info("=" * 70)
    logger.info("ANALYSIS COMPLETED")
    
    if combined_state.get("has_critical_issues"):
        logger.info(f"Critical Issues: {combined_state.get('critical_reason', 'Unknown')}")
        print(f"Critical Issues: {combined_state.get('critical_reason', 'Unknown')}")
    else:
        logger.info("No critical issues found")
        print("No critical issues found")
    
    # Display detailed metrics
    if "decision_metrics" in combined_state:
        metrics = combined_state["decision_metrics"]
        print("\n" + "=" * 70)
        print("QUALITY METRICS SUMMARY")
        print(f"Security Score: {metrics.get('security_score', 0):.2f}/10.0")
        print(f"PyLint Score: {metrics.get('pylint_score', 0):.2f}/10.0")
        print(f"Test Coverage: {metrics.get('coverage', 0):.1f}%")
        print(f"AI Review Score: {metrics.get('ai_score', 0):.2f}/1.0")
        print(f"Documentation: {metrics.get('documentation_coverage', 0):.1f}%")

def run_demo():
    """Run demo with sample scenarios"""
    logger = logging.getLogger("main.demo")
    
    print("DEMO MODE - Smart Code Review Pipeline")
    print("=" * 50)
    
    # Demo scenarios
    print("Available Demo Scenarios:")
    print("1. Sample Python Function Review")
    print("2. GitHub PR Review")
    
    choice = input("\nSelect demo scenario (1-2): ")
    
    try:
        choice_num = int(choice)
        
        if choice_num == 1:
            run_sample_code_demo()
        elif choice_num == 2:
            run_github_pr_demo()
        else:
            print("Invalid choice")
    
    except ValueError:
        print("Invalid input")

def run_sample_code_demo():
    """Demo with sample Python code"""
    print("\nRunning Sample Code Demo...")
    
    # Sample code with intentional issues
    sample_code = '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total

def process_order(order_data):
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
        result = process_order(order)
        if result:
            self.processed_orders.append(result)
        return result
'''
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(sample_code)
        temp_file_path = temp_file.name
    
    try:
        print(f"Analyzing sample code: {temp_file_path}")
        review_local_files([temp_file_path])
    finally:
        # Clean up
        os.unlink(temp_file_path)

def run_github_pr_demo():
    """Demo with GitHub PR"""
    print("\nRunning GitHub PR Demo...")
    print("Note: This requires a valid GitHub repository and PR number")
    
    # Example repositories
    print("\nExample repositories:")
    print("  - https://github.com/Amruth22/lung-disease-prediction-yolov10 (Demo PR with flawed code)")
    print("  - https://github.com/python/cpython")
    print("  - https://github.com/django/django")
    print("  - https://github.com/pallets/flask")
    
    repo_url = input("\nEnter repository URL: ").strip()
    pr_number_str = input("Enter PR number: ").strip()
    
    if repo_url and pr_number_str:
        try:
            pr_number = int(pr_number_str)
            review_github_pr(repo_url, pr_number)
        except ValueError:
            print("Invalid PR number")
    else:
        print("Repository URL and PR number required")

def interactive_mode():
    """Interactive mode for code review"""
    print("Smart Code Review Pipeline - Parallel Multi-Agent Mode")
    print("=" * 60)
    print("1. Review GitHub PR (Parallel Multi-Agent)")
    print("2. Review Local Files")
    print("3. Run Demo")
    print("0. Exit")
    
    choice = input("\nSelect option (0-3): ")
    
    if choice == "0":
        print("Goodbye!")
        return
    
    elif choice == "1":
        repo_url = input("Enter GitHub repository URL: ").strip()
        pr_number_str = input("Enter PR number: ").strip()
        
        try:
            pr_number = int(pr_number_str)
            review_github_pr(repo_url, pr_number)
        except ValueError:
            print("Invalid PR number")
    
    elif choice == "2":
        file_paths_str = input("Enter Python file paths (space-separated): ").strip()
        if file_paths_str:
            file_paths = file_paths_str.split()
            review_local_files(file_paths)
        else:
            print("No files specified")
    
    elif choice == "3":
        run_demo()
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()