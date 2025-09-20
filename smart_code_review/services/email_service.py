import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional, Union
from ..core.config import get_config_value
from ..utils.error_handling import log_and_raise
from ..utils.formatters import format_list_items, format_score, format_percentage

logger = logging.getLogger("email_service")

class EmailService:
    """Email notification service for code review"""
    
    def __init__(self):
        self.email_from = get_config_value("EMAIL_FROM", "")
        self.email_password = get_config_value("EMAIL_PASSWORD", "")
        self.email_to = get_config_value("EMAIL_TO", "")
        self.smtp_server = get_config_value("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(get_config_value("SMTP_PORT", 587))
        
        if not all([self.email_from, self.email_password, self.email_to]):
            logger.warning("Email configuration incomplete. Email notifications will not be sent.")
    
    def send_email(self, subject: str, content: str) -> bool:
        """Send an email with the given subject and content"""
        if not all([self.email_from, self.email_password, self.email_to]):
            logger.warning("Email configuration incomplete. Skipping email notification.")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject
            
            # Add content
            msg.attach(MIMEText(content, 'plain'))
            
            # Connect to server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            logger.info(f" Email sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f" Error sending email: {e}")
            return False
    
    def send_review_started_email(self, pr_details: Dict[str, Any], files_count: int) -> bool:
        """Send email notification for review initiation"""
        pr_number = pr_details.get('pr_number', 'unknown')
        pr_title = pr_details.get('title', 'unknown')
        pr_author = pr_details.get('author', 'unknown')
        
        subject = f" Code Review Started: PR #{pr_number} - {pr_title}"
        
        content = f"""
REVIEW STARTED - PR #{pr_number}
============================

PR Title: {pr_title}
Author: {pr_author}
Files to Review: {files_count} Python files

The Smart Code Review Pipeline has started analyzing this PR.
You will receive updates as the analysis progresses.

This is an automated notification from the Smart Code Review Pipeline.
        """
        
        return self.send_email(subject, content)
    
    def send_analysis_complete_email(self, pr_details: Dict[str, Any], 
                                  pylint_results: List[Dict[str, Any]],
                                  coverage_results: List[Dict[str, Any]]) -> bool:
        """Send email notification for static analysis completion"""
        pr_number = pr_details.get('pr_number', 'unknown')
        pr_title = pr_details.get('title', 'unknown')
        
        # Calculate average metrics
        avg_pylint_score = sum(r.get('score', 0) for r in pylint_results) / len(pylint_results) if pylint_results else 0
        avg_coverage = sum(r.get('coverage_percent', 0) for r in coverage_results) / len(coverage_results) if coverage_results else 0
        
        subject = f" Code Analysis Complete: PR #{pr_number} - {pr_title}"
        
        content = f"""
CODE ANALYSIS COMPLETE - PR #{pr_number}
===================================

PR Title: {pr_title}

ANALYSIS RESULTS:
---------------
Files Analyzed: {len(pylint_results)}
PyLint Score: {avg_pylint_score:.2f}/10.0
Test Coverage: {avg_coverage:.1f}%

PyLint Breakdown:
{self._format_pylint_summary(pylint_results)}

Coverage Breakdown:
{self._format_coverage_summary(coverage_results)}

The AI-powered review is now in progress.
You will receive the final report once it is complete.

This is an automated notification from the Smart Code Review Pipeline.
        """
        
        return self.send_email(subject, content)
    
    def send_ai_review_complete_email(self, pr_details: Dict[str, Any], 
                                   ai_reviews: List[Dict[str, Any]]) -> bool:
        """Send email notification for AI review completion"""
        pr_number = pr_details.get('pr_number', 'unknown')
        pr_title = pr_details.get('title', 'unknown')
        
        # Format AI review summary
        ai_summary = self.format_ai_reviews_summary(ai_reviews)
        
        subject = f" AI Review Complete: PR #{pr_number} - {pr_title}"
        
        content = f"""
AI REVIEW COMPLETE - PR #{pr_number}
===============================

PR Title: {pr_title}

AI REVIEW SUMMARY:
---------------
{ai_summary}

The final decision is being made based on all analysis results.
You will receive the final report shortly.

This is an automated notification from the Smart Code Review Pipeline.
        """
        
        return self.send_email(subject, content)
    
    def send_final_report_email(self, pr_details: Dict[str, Any], 
                             report: Dict[str, Any], 
                             is_critical: bool) -> bool:
        """Send email notification with final review report"""
        pr_number = pr_details.get('pr_number', 'unknown')
        pr_title = pr_details.get('title', 'unknown')
        
        # Determine status prefix based on criticality
        status_prefix = " CRITICAL ISSUES" if is_critical else " REVIEW COMPLETE"
        decision = report.get('decision', 'NEEDS_REVIEW').upper()
        
        subject = f"{status_prefix}: PR #{pr_number} - {pr_title}"
        
        content = f"""
{status_prefix} - PR #{pr_number}
===============================

PR Title: {pr_title}
Author: {pr_details.get('author', 'unknown')}

FINAL STATUS: {decision}

{self._format_final_report(report)}

This is an automated notification from the Smart Code Review Pipeline.
        """
        
        return self.send_email(subject, content)
    
    def send_error_notification(self, pr_details: Dict[str, Any], error_message: str) -> bool:
        """Send email notification for workflow errors"""
        pr_number = pr_details.get('pr_number', 'unknown')
        pr_title = pr_details.get('title', 'unknown')
        
        subject = f" Review Error: PR #{pr_number} - {pr_title}"
        
        content = f"""
REVIEW ERROR - PR #{pr_number}
=========================

PR Title: {pr_title}

An error occurred during the review process:
{error_message}

Please check the logs for more details and restart the review process.

This is an automated notification from the Smart Code Review Pipeline.
        """
        
        return self.send_email(subject, content)
    
    def _format_pylint_summary(self, pylint_results: List[Dict[str, Any]]) -> str:
        """Format PyLint results summary for email"""
        if not pylint_results:
            return "No PyLint results available."
        
        total_issues = sum(r.get('total_issues', 0) for r in pylint_results)
        avg_score = sum(r.get('score', 0) for r in pylint_results) / len(pylint_results)
        
        summary = []
        summary.append(f"Overall Score: {avg_score:.2f}/10.0")
        summary.append(f"Total Issues: {total_issues}")
        
        # Add file breakdown for low scores
        low_score_files = [r for r in pylint_results if r.get('score', 10) < 7.0]
        if low_score_files:
            summary.append("\nFiles needing attention:")
            for result in low_score_files:
                filename = result.get('filename', 'Unknown')
                score = result.get('score', 0.0)
                issues = result.get('total_issues', 0)
                summary.append(f"- {filename}: Score {score:.2f} ({issues} issues)")
        
        return "\n".join(summary)
    
    def _format_coverage_summary(self, coverage_results: List[Dict[str, Any]]) -> str:
        """Format coverage results summary for email"""
        if not coverage_results:
            return "No coverage results available."
        
        avg_coverage = sum(r.get('coverage_percent', 0) for r in coverage_results) / len(coverage_results)
        
        summary = []
        summary.append(f"Average Coverage: {avg_coverage:.1f}%")
        
        # Add file breakdown for low coverage
        low_coverage_files = [r for r in coverage_results if r.get('coverage_percent', 100) < 80.0]
        if low_coverage_files:
            summary.append("\nFiles with low coverage:")
            for result in low_coverage_files:
                filename = result.get('filename', 'Unknown')
                coverage = result.get('coverage_percent', 0.0)
                summary.append(f"- {filename}: {coverage:.1f}% coverage")
        
        return "\n".join(summary)
    
    def format_ai_reviews_summary(self, ai_reviews: List[Dict[str, Any]]) -> str:
        """Format AI review summary for email"""
        if not ai_reviews:
            return "No AI review results available."
        
        avg_score = sum(r.get('overall_score', 0) for r in ai_reviews) / len(ai_reviews) if ai_reviews else 0
        avg_confidence = sum(r.get('confidence', 0) for r in ai_reviews) / len(ai_reviews) if ai_reviews else 0
        
        summary = []
        summary.append(f"AI Review Score: {avg_score:.2f}/1.0")
        summary.append(f"Confidence: {avg_confidence:.2f}/1.0")
        summary.append(f"Files Reviewed: {len(ai_reviews)}")
        
        # Collect all issues and recommendations
        all_issues = []
        all_recommendations = []
        
        for review in ai_reviews:
            issues = review.get('issues', [])
            recommendations = review.get('recommendations', [])
            filename = review.get('filename', 'Unknown file')
            
            for issue in issues:
                all_issues.append(f"{filename}: {issue}")
            
            for recommendation in recommendations:
                all_recommendations.append(f"{filename}: {recommendation}")
        
        # Add top issues
        if all_issues:
            summary.append("\nTop Issues:")
            for issue in all_issues[:5]:  # Show only top 5
                summary.append(f"- {issue}")
            
            if len(all_issues) > 5:
                summary.append(f"... and {len(all_issues) - 5} more issues.")
        
        # Add top recommendations
        if all_recommendations:
            summary.append("\nTop Recommendations:")
            for rec in all_recommendations[:5]:  # Show only top 5
                summary.append(f"- {rec}")
            
            if len(all_recommendations) > 5:
                summary.append(f"... and {len(all_recommendations) - 5} more recommendations.")
        
        return "\n".join(summary)
    
    def _format_final_report(self, report: Dict[str, Any]) -> str:
        """Format final report for email"""
        sections = []
        
        # Add recommendation and priority
        recommendation = report.get('recommendation', 'NEEDS_REVIEW').upper()
        priority = report.get('priority', 'MEDIUM').upper()
        
        sections.append(f"RECOMMENDATION: {recommendation}")
        sections.append(f"PRIORITY: {priority}")
        
        # Add metrics if available
        metrics = report.get('metrics', {})
        if metrics:
            sections.append("\nMETRICS:")
            sections.append(f"PyLint Score: {format_score(metrics.get('pylint_score', 0), 10.0)}")
            sections.append(f"Test Coverage: {format_percentage(metrics.get('coverage', 0))}")
            sections.append(f"AI Quality Score: {format_score(metrics.get('ai_score', 0), 1.0)}")
            sections.append(f"Security Score: {format_score(metrics.get('security_score', 0), 10.0)}")
            sections.append(f"Documentation Coverage: {format_percentage(metrics.get('documentation_coverage', 0))}")
        
        # Add key findings
        key_findings = report.get('key_findings', [])
        if key_findings:
            sections.append("\nKEY FINDINGS:")
            sections.append(format_list_items(key_findings, bullet="- "))
        
        # Add action items
        action_items = report.get('action_items', [])
        if action_items:
            sections.append("\nACTION ITEMS:")
            sections.append(format_list_items(action_items, bullet="- "))
        
        # Add approval criteria
        approval_criteria = report.get('approval_criteria', [])
        if approval_criteria:
            sections.append("\nAPPROVAL CRITERIA:")
            sections.append(format_list_items(approval_criteria, bullet="- "))
        
        return "\n".join(sections)