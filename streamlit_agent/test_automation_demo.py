#!/usr/bin/env python3
"""
TestAutomation Demo Script

Demonstrates the TestAutomation component functionality and provides
a way to test the browser automation capabilities independently.

Usage:
    python streamlit_agent/test_automation_demo.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from streamlit_agent.components.test_automation import TestAutomation, create_test_automation, run_quick_validation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_basic_functionality():
    """Demonstrate basic TestAutomation functionality"""
    print("=== TestAutomation Basic Functionality Demo ===\n")
    
    # Create TestAutomation instance
    print("1. Creating TestAutomation instance...")
    test_automation = create_test_automation("http://localhost:8501")
    print(f"   ✓ Created for URL: {test_automation.app_url}")
    print(f"   ✓ Timeout: {test_automation.timeout}s")
    print(f"   ✓ Screenshots directory: {test_automation.screenshots_dir}")
    
    # Check MCP client creation (without actually connecting)
    print("\n2. Testing MCP client creation...")
    try:
        mcp_client = test_automation._create_mcp_client()
        if mcp_client:
            print("   ✓ MCP client created successfully")
        else:
            print("   ⚠ MCP client creation failed (dependencies may not be available)")
    except Exception as e:
        print(f"   ⚠ MCP client creation error: {e}")
    
    # Test configuration
    print("\n3. Testing configuration...")
    print(f"   ✓ Test queries configured: {len(test_automation.test_queries)}")
    for i, query in enumerate(test_automation.test_queries, 1):
        print(f"      {i}. {query[:60]}...")
    
    print("\n4. Testing utility functions...")
    
    # Test get_test_summary with no results
    summary = test_automation.get_test_summary()
    print(f"   ✓ Empty test summary: {summary}")
    
    # Test save_test_report with no results
    try:
        report_path = test_automation.save_test_report("demo_empty_report.json")
        print(f"   ✓ Empty report saved to: {report_path}")
    except Exception as e:
        print(f"   ⚠ Report save error: {e}")
    
    print("\n=== Basic Functionality Demo Complete ===\n")

async def demo_quick_validation():
    """Demonstrate quick validation functionality"""
    print("=== Quick Validation Demo ===\n")
    
    print("Testing quick validation (this will attempt to connect to the app)...")
    print("Note: This requires the Streamlit app to be running on localhost:8501")
    
    try:
        # Run quick validation with a short timeout
        is_valid = await run_quick_validation("http://localhost:8501")
        
        if is_valid:
            print("   ✅ Quick validation PASSED - Application is accessible and working")
        else:
            print("   ❌ Quick validation FAILED - Application may not be running or accessible")
            
    except Exception as e:
        print(f"   ⚠ Quick validation error: {e}")
        print("   This is expected if the Streamlit app is not running")
    
    print("\n=== Quick Validation Demo Complete ===\n")

async def demo_comprehensive_tests():
    """Demonstrate comprehensive testing (requires running app)"""
    print("=== Comprehensive Tests Demo ===\n")
    
    print("This demo will attempt to run comprehensive browser automation tests.")
    print("Requirements:")
    print("- Streamlit app running on localhost:8501")
    print("- Chrome DevTools MCP server available")
    print("- uvx command available for MCP server execution")
    print()
    
    # Ask user if they want to proceed
    try:
        response = input("Do you want to proceed with comprehensive tests? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Skipping comprehensive tests.")
            return
    except KeyboardInterrupt:
        print("\nSkipping comprehensive tests.")
        return
    
    print("\nRunning comprehensive tests...")
    
    try:
        test_automation = create_test_automation("http://localhost:8501")
        results = await test_automation.run_comprehensive_tests()
        
        print("\n=== Test Results ===")
        for result in results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"{status} {result.test_name}")
            print(f"   Message: {result.message}")
            print(f"   Duration: {result.duration:.2f}s")
            if result.screenshot_path:
                print(f"   Screenshot: {result.screenshot_path}")
            if result.details:
                print(f"   Details: {result.details}")
            print()
        
        # Print summary
        summary = test_automation.get_test_summary()
        print(f"Summary: {summary['passed']}/{summary['total_tests']} tests passed ({summary['success_rate']:.1f}%)")
        if 'total_duration' in summary:
            print(f"Total duration: {summary['total_duration']:.2f}s")
        
        # Save report
        report_path = test_automation.save_test_report()
        print(f"Detailed report saved to: {report_path}")
        
    except Exception as e:
        print(f"   ❌ Comprehensive tests failed: {e}")
        logger.exception("Comprehensive tests error")
    
    print("\n=== Comprehensive Tests Demo Complete ===\n")

async def main():
    """Main demo function"""
    print("TestAutomation Component Demo")
    print("=" * 50)
    print()
    
    # Run basic functionality demo
    await demo_basic_functionality()
    
    # Run quick validation demo
    await demo_quick_validation()
    
    # Run comprehensive tests demo (optional)
    await demo_comprehensive_tests()
    
    print("Demo complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"Demo failed: {e}")
        logger.exception("Demo error")