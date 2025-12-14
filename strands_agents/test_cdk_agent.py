#!/usr/bin/env python3
"""
Test script for the CDK Agent to verify functionality
"""

import sys
import os
from cdk_agent import CDKAgent, check_prerequisites

def test_cdk_agent():
    """Test the CDK agent with basic functionality."""
    print("🧪 Testing CDK Agent")
    print("=" * 40)
    
    # Check prerequisites first
    if not check_prerequisites():
        print("❌ Prerequisites not met")
        return False
    
    try:
        # Create and initialize agent
        print("\n1. Creating CDK Agent...")
        cdk_agent = CDKAgent()
        
        print("\n2. Initializing agent...")
        if not cdk_agent.initialize():
            print("❌ Failed to initialize agent")
            return False
        
        print("\n3. Testing basic query...")
        response = cdk_agent.chat("What is AWS CDK?")
        
        # Convert response to string if needed
        response_str = str(response) if response else ""
        
        if response_str and not response_str.startswith("❌"):
            print("✅ Basic query successful")
            print(f"Response preview: {response_str[:100]}...")
        else:
            print(f"❌ Query failed: {response_str}")
            return False
        
        print("\n4. Getting available tools...")
        tools = cdk_agent.get_available_tools()
        print(f"✅ Found {len(tools)} tools")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Main test function."""
    success = test_cdk_agent()
    
    if success:
        print("\n🎉 CDK Agent is working correctly!")
        print("You can now run:")
        print("  python cdk_agent.py --interactive  # Interactive mode")
        print("  python cdk_agent.py --demo         # Demo mode")
    else:
        print("\n❌ CDK Agent test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()