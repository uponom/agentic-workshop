#!/usr/bin/env python3
"""
AWS CDK Strands Agent - A specialized agent for AWS CDK operations

This agent connects to the AWS CDK MCP server to provide comprehensive
CDK assistance including project initialization, stack management, 
deployment operations, and best practices guidance.
"""

import os
import sys
from typing import Optional, List
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient


class CDKAgent:
    """
    A specialized Strands Agent for AWS CDK operations.
    
    This agent provides comprehensive CDK assistance through the AWS CDK MCP server,
    including project management, stack operations, and deployment guidance.
    """
    
    def __init__(self, model_id: str = "us.anthropic.claude-3-5-haiku-20241022-v1:0"):
        """
        Initialize the CDK Agent.
        
        Args:
            model_id: The Bedrock model ID to use for the agent
        """
        self.model_id = model_id
        self.agent: Optional[Agent] = None
        self.mcp_client: Optional[MCPClient] = None
        self._setup_model()
        self._setup_mcp_client()
    
    def _setup_model(self) -> None:
        """Setup the Bedrock model for the agent."""
        try:
            self.model = BedrockModel(
                model_id=self.model_id,
                temperature=0.3,  # Lower temperature for more precise CDK guidance
                max_tokens=4096,
            )
            print(f"✅ Model configured: {self.model_id}")
        except Exception as e:
            print(f"❌ Error setting up model: {e}")
            raise
    
    def _setup_mcp_client(self) -> None:
        """Setup the MCP client for AWS CDK server."""
        try:
            self.mcp_client = MCPClient(
                lambda: stdio_client(
                    StdioServerParameters(
                        command="uvx",
                        args=["awslabs.cdk-mcp-server@latest"]
                    )
                )
            )
            print("✅ CDK MCP client configured")
        except Exception as e:
            print(f"❌ Error setting up MCP client: {e}")
            raise
    
    def initialize(self) -> bool:
        """
        Initialize the agent with CDK MCP tools.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            print("🔗 Connecting to AWS CDK MCP server...")
            
            with self.mcp_client:
                # Get available tools from CDK MCP server
                tools = self.mcp_client.list_tools_sync()
                
                if not tools:
                    print("❌ No tools available from CDK MCP server")
                    return False
                
                print(f"📋 Found {len(tools)} CDK tools:")
                for i, tool in enumerate(tools, 1):
                    tool_name = getattr(tool, 'name', f'tool_{i}')
                    tool_desc = getattr(tool, 'description', 'No description available')
                    print(f"  {i}. {tool_name}")
                    print(f"     {tool_desc[:80]}...")
                
                # Create the agent with CDK-specific system prompt
                self.agent = Agent(
                    model=self.model,
                    tools=tools,
                    system_prompt=self._get_system_prompt()
                )
                
                print("✅ CDK Agent initialized successfully!")
                return True
                
        except Exception as e:
            print(f"❌ Error initializing CDK agent: {e}")
            return False
    
    def _get_system_prompt(self) -> str:
        """Get the specialized system prompt for CDK operations."""
        return """You are an expert AWS CDK (Cloud Development Kit) assistant with access to comprehensive CDK tools and operations.

Your capabilities include:
- CDK project initialization and setup
- Stack creation, modification, and management
- Deployment and destruction operations
- CDK best practices and troubleshooting
- Infrastructure as Code guidance
- AWS service integration with CDK

Guidelines for assistance:
1. Always use the available CDK tools to perform operations and gather information
2. Provide clear, step-by-step instructions for CDK operations
3. Include relevant code examples and best practices
4. Explain the implications of CDK operations before executing them
5. Help users understand CDK concepts and AWS service integrations
6. Suggest appropriate CDK patterns and constructs for different use cases
7. Always consider security, cost optimization, and maintainability

When helping with CDK operations:
- Verify prerequisites before suggesting operations
- Explain what each CDK command or operation will do
- Provide context about AWS resources being created or modified
- Suggest testing and validation approaches
- Recommend appropriate CDK construct libraries

You have access to real CDK tools, so use them to provide accurate, up-to-date information and perform actual CDK operations when requested."""
    
    def chat(self, message: str) -> str:
        """
        Send a message to the CDK agent and get a response.
        
        Args:
            message: The user's message/question
            
        Returns:
            str: The agent's response
        """
        if not self.agent:
            return "❌ Agent not initialized. Please call initialize() first."
        
        try:
            with self.mcp_client:
                response = self.agent(message)
                # AgentResult objects can be converted to string directly
                return str(response)
        except Exception as e:
            return f"❌ Error processing message: {e}"
    
    def get_available_tools(self) -> List[str]:
        """
        Get a list of available CDK tools.
        
        Returns:
            List[str]: List of tool names and descriptions
        """
        if not self.mcp_client:
            return ["❌ MCP client not initialized"]
        
        try:
            with self.mcp_client:
                tools = self.mcp_client.list_tools_sync()
                tool_list = []
                for tool in tools:
                    tool_name = getattr(tool, 'name', 'Unknown')
                    tool_desc = getattr(tool, 'description', 'No description')
                    tool_list.append(f"{tool_name}: {tool_desc}")
                return tool_list
        except Exception as e:
            return [f"❌ Error getting tools: {e}"]


def check_prerequisites() -> bool:
    """Check if all prerequisites are met for running the CDK agent."""
    print("🔍 Checking prerequisites...")
    
    # Check AWS credentials
    has_bedrock_key = bool(os.getenv("AWS_BEDROCK_API_KEY"))
    has_aws_creds = bool(os.getenv("AWS_ACCESS_KEY_ID"))
    
    if not (has_bedrock_key or has_aws_creds):
        print("⚠️  Warning: No AWS credentials found")
        print("   Set one of the following:")
        print("   export AWS_BEDROCK_API_KEY=your_key")
        print("   or configure AWS credentials: aws configure")
        return False
    else:
        print("✅ AWS credentials found")
    
    # Check uvx availability
    try:
        import subprocess
        result = subprocess.run(["uvx", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ uvx is available")
        else:
            print("❌ uvx not working correctly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ uvx not found. Install with: pip install uv")
        return False
    except Exception as e:
        print(f"❌ Error checking uvx: {e}")
        return False
    
    return True


def interactive_mode(cdk_agent: CDKAgent) -> None:
    """Run the CDK agent in interactive mode."""
    print("\n🎯 CDK Agent Interactive Mode")
    print("Ask questions about AWS CDK, request operations, or get guidance!")
    print("Type 'quit', 'exit', or press Ctrl+C to exit")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("🤔 CDK Agent is thinking...")
            response = cdk_agent.chat(user_input)
            print(f"🤖 CDK Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def demo_mode(cdk_agent: CDKAgent) -> None:
    """Run the CDK agent in demo mode with predefined questions."""
    print("\n🧪 CDK Agent Demo Mode")
    print("Testing with common CDK questions...")
    
    demo_questions = [
        "What is AWS CDK and how does it work?",
        "How do I initialize a new CDK project?",
        "What are the main CDK constructs I should know about?",
        "How do I deploy a simple Lambda function with CDK?",
        "What are CDK best practices for production environments?",
        "How do I manage different environments (dev, staging, prod) with CDK?"
    ]
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n📝 Demo Question {i}: {question}")
        print("🤔 CDK Agent is processing...")
        
        try:
            response = cdk_agent.chat(question)
            
            # Truncate long responses for demo readability
            if len(response) > 500:
                display_response = response[:500] + "\n... (response truncated for demo)"
            else:
                display_response = response
            
            print(f"💬 CDK Agent Response:\n{display_response}")
            
        except Exception as e:
            print(f"❌ Error processing question: {e}")
        
        # Pause between questions in demo mode
        input("\nPress Enter to continue to next question...")
    
    print("\n✅ Demo completed!")


def main():
    """Main function to run the CDK Agent."""
    print("=" * 70)
    print("🚀 AWS CDK Strands Agent")
    print("   Specialized agent for AWS CDK operations and guidance")
    print("=" * 70)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install dependencies and configure credentials.")
        sys.exit(1)
    
    # Initialize CDK agent
    print("\n🤖 Initializing CDK Agent...")
    try:
        cdk_agent = CDKAgent()
        
        if not cdk_agent.initialize():
            print("❌ Failed to initialize CDK agent")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error creating CDK agent: {e}")
        sys.exit(1)
    
    # Show available tools
    print("\n📋 Available CDK Tools:")
    tools = cdk_agent.get_available_tools()
    for tool in tools[:5]:  # Show first 5 tools
        print(f"  • {tool}")
    if len(tools) > 5:
        print(f"  ... and {len(tools) - 5} more tools")
    
    # Determine run mode
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "--demo":
            demo_mode(cdk_agent)
        elif mode == "--interactive":
            interactive_mode(cdk_agent)
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: --demo, --interactive")
    else:
        # Default to interactive mode
        interactive_mode(cdk_agent)


if __name__ == "__main__":
    main()