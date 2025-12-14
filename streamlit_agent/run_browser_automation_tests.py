#!/usr/bin/env python3
"""
Standalone Browser Automation Test Runner

This script provides a standalone way to run comprehensive browser automation tests
for the Streamlit Agent application. It can be used when the Chrome DevTools MCP server
is available and the Streamlit application is running.

Usage:
    python streamlit_agent/run_browser_automation_tests.py [options]

Options:
    --app-url URL       URL of the Streamlit application (default: http://localhost:8501)
    --timeout SECONDS   Timeout for operations in seconds (default: 30)
    --verbose           Enable verbose logging
    --save-report PATH  Save detailed test report to specified path
    --skip-mcp-check    Skip MCP server availability check

Requirements:
    - Streamlit application running on specified URL
    - Chrome DevTools MCP server available via uvx
    - uvx command available in PATH

Example:
    python streamlit_agent/run_browser_automation_tests.py --verbose --save-report test_results.json
"""

import asyncio
import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from streamlit_agent.components.test_automation import (
    TestAutomation, TestResult, create_test_automation, run_quick_validation
)

# Configure logging
def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)

class BrowserAutomationTestRunner:
    """
    Standalone test runner for browser automation tests
    
    Provides a comprehensive test suite that can be run independently
    when the proper environment is available.
    """
    
    def __init__(self, app_url: str = "http://localhost:8501", timeout: int = 30):
        """
        Initialize the test runner
        
        Args:
            app_url: URL of the Streamlit application to test
            timeout: Default timeout for operations in seconds
        """
        self.app_url = app_url
        self.timeout = timeout
        self.test_automation = create_test_automation(app_url)
        self.results: List[TestResult] = []
        
        # Test queries for workflow testing
        self.test_queries = [
            "Design a serverless web application with user authentication using AWS Lambda and Cognito",
            "Create a microservices architecture with API Gateway, Lambda, and DynamoDB",
            "Build a real-time data processing pipeline with Kinesis, Lambda, and S3"
        ]
    
    async def check_prerequisites(self) -> Dict[str, bool]:
        """
        Check if all prerequisites are met for running browser automation tests
        
        Returns:
            Dict with prerequisite check results
        """
        logger.info("Checking prerequisites for browser automation tests...")
        
        prerequisites = {
            "mcp_server_available": False,
            "app_accessible": False,
            "test_framework_ready": False
        }
        
        # Check MCP server availability
        try:
            mcp_client = self.test_automation._create_mcp_client()
            prerequisites["mcp_server_available"] = mcp_client is not None
        except Exception as e:
            logger.warning(f"MCP server check failed: {e}")
        
        # Check application accessibility
        try:
            app_accessible = await run_quick_validation(self.app_url)
            prerequisites["app_accessible"] = app_accessible
        except Exception as e:
            logger.warning(f"Application accessibility check failed: {e}")
        
        # Check test framework readiness
        try:
            prerequisites["test_framework_ready"] = (
                self.test_automation is not None and
                len(self.test_automation.test_queries) > 0 and
                self.test_automation.screenshots_dir.exists()
            )
        except Exception as e:
            logger.warning(f"Test framework check failed: {e}")
        
        return prerequisites
    
    async def run_application_startup_test(self) -> TestResult:
        """Run application startup and accessibility test"""
        logger.info("Running application startup and accessibility test...")
        
        setup_success = await self.test_automation.setup_browser()
        if not setup_success:
            return TestResult(
                test_name="Application Startup Test",
                success=False,
                message="Failed to setup browser automation environment",
                duration=0.0,
                timestamp=time.time()
            )
        
        try:
            result = await self.test_automation.validate_application_startup()
            return result
        finally:
            await self.test_automation.teardown_browser()
    
    async def run_query_workflow_test(self, query: str = None) -> TestResult:
        """Run complete query-to-results workflow test"""
        test_query = query or self.test_queries[0]
        logger.info(f"Running query workflow test with query: {test_query[:50]}...")
        
        setup_success = await self.test_automation.setup_browser()
        if not setup_success:
            return TestResult(
                test_name="Query Workflow Test",
                success=False,
                message="Failed to setup browser automation environment",
                duration=0.0,
                timestamp=time.time()
            )
        
        try:
            result = await self.test_automation.validate_query_submission_workflow(test_query)
            return result
        finally:
            await self.test_automation.teardown_browser()
    
    async def run_diagram_display_test(self) -> TestResult:
        """Run diagram generation and display test"""
        logger.info("Running diagram generation and display test...")
        
        setup_success = await self.test_automation.setup_browser()
        if not setup_success:
            return TestResult(
                test_name="Diagram Display Test",
                success=False,
                message="Failed to setup browser automation environment",
                duration=0.0,
                timestamp=time.time()
            )
        
        try:
            # First run a query that should generate a diagram
            diagram_query = "Create an AWS architecture diagram for a serverless web application"
            workflow_result = await self.test_automation.validate_query_submission_workflow(diagram_query)
            
            if workflow_result.success:
                # Wait for diagram generation
                await asyncio.sleep(5)
            
            # Test diagram display
            result = await self.test_automation.validate_diagram_display()
            return result
        finally:
            await self.test_automation.teardown_browser()
    
    async def run_ui_elements_test(self) -> TestResult:
        """Run UI elements presence and functionality test"""
        logger.info("Running UI elements presence and functionality test...")
        
        setup_success = await self.test_automation.setup_browser()
        if not setup_success:
            return TestResult(
                test_name="UI Elements Test",
                success=False,
                message="Failed to setup browser automation environment",
                duration=0.0,
                timestamp=time.time()
            )
        
        try:
            start_time = time.time()
            
            # Get page snapshot and find UI elements
            snapshot = await self.test_automation.get_page_snapshot()
            if not snapshot:
                return TestResult(
                    test_name="UI Elements Test",
                    success=False,
                    message="Failed to get page snapshot",
                    duration=time.time() - start_time,
                    timestamp=time.time()
                )
            
            # Find UI elements
            ui_elements = await self.test_automation.find_ui_elements(['input', 'button', 'submit'])
            
            if len(ui_elements) == 0:
                return TestResult(
                    test_name="UI Elements Test",
                    success=False,
                    message="No UI elements found on the page",
                    duration=time.time() - start_time,
                    timestamp=time.time()
                )
            
            # Test basic UI interactions
            input_elements = [elem for elem in ui_elements if elem.element_type == 'input']
            button_elements = [elem for elem in ui_elements if elem.element_type in ['button', 'submit']]
            
            interactions_successful = 0
            total_interactions = 0
            
            # Test input filling
            if input_elements:
                total_interactions += 1
                fill_success = await self.test_automation.fill_element(
                    input_elements[0].uid, 
                    "Test UI functionality"
                )
                if fill_success:
                    interactions_successful += 1
            
            # Test button clicking
            if button_elements:
                total_interactions += 1
                click_success = await self.test_automation.click_element(button_elements[0].uid)
                if click_success:
                    interactions_successful += 1
            
            success_rate = interactions_successful / total_interactions if total_interactions > 0 else 0
            
            return TestResult(
                test_name="UI Elements Test",
                success=success_rate > 0.5,  # At least 50% of interactions should succeed
                message=f"UI elements test completed: {interactions_successful}/{total_interactions} interactions successful",
                duration=time.time() - start_time,
                timestamp=time.time(),
                details={
                    "elements_found": len(ui_elements),
                    "input_elements": len(input_elements),
                    "button_elements": len(button_elements),
                    "interactions_successful": interactions_successful,
                    "total_interactions": total_interactions,
                    "success_rate": success_rate
                }
            )
            
        finally:
            await self.test_automation.teardown_browser()
    
    async def run_comprehensive_tests(self) -> List[TestResult]:
        """
        Run all comprehensive browser automation tests
        
        Returns:
            List of TestResult objects for all tests performed
        """
        logger.info("Starting comprehensive browser automation tests...")
        
        # Use the existing comprehensive test method
        results = await self.test_automation.run_comprehensive_tests()
        self.results.extend(results)
        
        return results
    
    async def run_individual_tests(self) -> List[TestResult]:
        """
        Run individual tests one by one
        
        Returns:
            List of TestResult objects for all tests performed
        """
        logger.info("Running individual browser automation tests...")
        
        tests = [
            ("Application Startup", self.run_application_startup_test),
            ("Query Workflow", self.run_query_workflow_test),
            ("Diagram Display", self.run_diagram_display_test),
            ("UI Elements", self.run_ui_elements_test)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            logger.info(f"Running {test_name} test...")
            try:
                result = await test_func()
                results.append(result)
                self.results.append(result)
                
                status = "✅ PASS" if result.success else "❌ FAIL"
                logger.info(f"{status} {test_name}: {result.message}")
                
            except Exception as e:
                error_result = TestResult(
                    test_name=f"{test_name} Test",
                    success=False,
                    message=f"Test failed with exception: {str(e)}",
                    duration=0.0,
                    timestamp=time.time()
                )
                results.append(error_result)
                self.results.append(error_result)
                logger.error(f"❌ FAIL {test_name}: {str(e)}")
        
        return results
    
    def generate_report(self, save_path: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive test report
        
        Args:
            save_path: Optional path to save the report as JSON
            
        Returns:
            Dict containing the test report
        """
        if not self.results:
            logger.warning("No test results available for report generation")
            return {}
        
        # Use the test automation's report generation
        summary = self.test_automation.get_test_summary()
        
        if save_path:
            report_path = self.test_automation.save_test_report(save_path)
            logger.info(f"Detailed report saved to: {report_path}")
        
        return summary
    
    def print_summary(self):
        """Print a summary of test results to console"""
        if not self.results:
            print("No test results available")
            return
        
        print("\n" + "=" * 60)
        print("BROWSER AUTOMATION TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.results if result.success)
        total = len(self.results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{status} {result.test_name} ({result.duration:.2f}s)")
            if not result.success:
                print(f"    Error: {result.message}")
        
        print(f"\nOverall: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! The application is working correctly.")
        elif passed > 0:
            print("⚠️  Some tests failed. Check the details above.")
        else:
            print("❌ All tests failed. Check your environment setup.")

async def main():
    """Main function for the standalone test runner"""
    parser = argparse.ArgumentParser(
        description="Run comprehensive browser automation tests for Streamlit Agent"
    )
    parser.add_argument(
        "--app-url", 
        default="http://localhost:8501",
        help="URL of the Streamlit application (default: http://localhost:8501)"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=30,
        help="Timeout for operations in seconds (default: 30)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--save-report", 
        help="Save detailed test report to specified path"
    )
    parser.add_argument(
        "--skip-mcp-check", 
        action="store_true",
        help="Skip MCP server availability check"
    )
    parser.add_argument(
        "--individual-tests", 
        action="store_true",
        help="Run individual tests instead of comprehensive test suite"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    logger.info("Starting Browser Automation Test Runner")
    logger.info(f"Target application: {args.app_url}")
    logger.info(f"Timeout: {args.timeout} seconds")
    
    # Create test runner
    test_runner = BrowserAutomationTestRunner(args.app_url, args.timeout)
    
    # Check prerequisites
    if not args.skip_mcp_check:
        logger.info("Checking prerequisites...")
        prerequisites = await test_runner.check_prerequisites()
        
        print("\nPrerequisite Check Results:")
        for check, result in prerequisites.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {check.replace('_', ' ').title()}")
        
        if not all(prerequisites.values()):
            print("\n⚠️  Some prerequisites are not met. Tests may fail.")
            print("Make sure:")
            print("  - Streamlit application is running on the specified URL")
            print("  - Chrome DevTools MCP server is available (uvx mcp-chrome-devtools@latest)")
            print("  - uvx command is available in PATH")
            
            response = input("\nDo you want to continue anyway? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Exiting...")
                return
    
    # Run tests
    try:
        if args.individual_tests:
            logger.info("Running individual tests...")
            results = await test_runner.run_individual_tests()
        else:
            logger.info("Running comprehensive test suite...")
            results = await test_runner.run_comprehensive_tests()
        
        # Generate and display results
        test_runner.print_summary()
        
        # Save report if requested
        if args.save_report:
            report = test_runner.generate_report(args.save_report)
            print(f"\nDetailed report saved to: {args.save_report}")
        
        # Exit with appropriate code
        passed = sum(1 for result in results if result.success)
        total = len(results)
        
        if passed == total:
            sys.exit(0)  # All tests passed
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        logger.info("Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test run failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())