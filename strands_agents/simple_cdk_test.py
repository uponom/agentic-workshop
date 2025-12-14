#!/usr/bin/env python3
"""
Simple test for CDK Agent to isolate issues
"""

from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

def simple_test():
    """Simple test of CDK MCP connection."""
    print("🧪 Simple CDK MCP Test")
    
    try:
        # Create MCP client
        print("1. Creating MCP client...")
        mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.cdk-mcp-server@latest"]
            )
        ))
        print("✅ MCP client created")
        
        # Test connection and get tools
        print("2. Testing MCP connection...")
        with mcp_client:
            tools = mcp_client.list_tools_sync()
            print(f"✅ Found {len(tools)} tools")
            
            # Show tool details
            for i, tool in enumerate(tools[:3], 1):
                print(f"   Tool {i}: {type(tool)} - {getattr(tool, 'name', 'no name')}")
        
        print("3. Creating simple agent...")
        model = BedrockModel(
            model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            temperature=0.3,
            max_tokens=1000,
        )
        
        with mcp_client:
            tools = mcp_client.list_tools_sync()
            agent = Agent(
                model=model,
                tools=tools,
                system_prompt="You are a helpful CDK assistant."
            )
            
            print("4. Testing simple query...")
            response = agent("Hello, what can you help me with?")
            print(f"✅ Response type: {type(response)}")
            print(f"✅ Response: {str(response)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n🎉 Simple test passed!")
    else:
        print("\n❌ Simple test failed!")