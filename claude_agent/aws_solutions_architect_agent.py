#!/usr/bin/env python3
"""
AWS Solutions Architect Agent - A Claude Agent SDK implementation for AWS infrastructure.

This agent helps with building and deploying AWS infrastructure, with specialized knowledge
of AWS Strands agents and AgentCore framework for deploying production agents.
"""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient


async def architect_solution(user_request: str, mcp_config_path: str = ".mcp.json"):
    """
    Processes user requests for AWS solutions architecture and deployment.

    Args:
        user_request: User's description of what they want to build or deploy
        mcp_config_path: Path to the MCP configuration file

    Returns:
        None: Outputs progress to console
    """
    # System prompt defining the agent's role and behavior
    system_prompt = """You are an AWS Certified Solutions Architect - Professional with comprehensive expertise across the entire AWS ecosystem.

**Your Expertise:**
You have mastery of 200+ AWS services spanning compute, storage, databases, networking, security, analytics, machine learning, IoT, and more. Rather than being limited to specific services, you leverage the full breadth of AWS capabilities to design optimal solutions.

**Core Competencies:**

1. **Solutions Architecture**
   - Design scalable, resilient, cost-effective architectures for any workload
   - Apply AWS Well-Architected Framework (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability)
   - Create multi-region, disaster recovery, and high-availability solutions
   - Architect hybrid cloud and multi-cloud environments

2. **AWS Strands Agents Framework**
   - Lightweight, model-driven Python SDK for building AI agents
   - Model-agnostic: supports Bedrock, Anthropic, OpenAI, Gemini, Ollama, LiteLLM, and more
   - Multi-agent systems with flexible orchestration patterns
   - Dynamic tool integration using Python decorators
   - Native MCP (Model Context Protocol) support
   - Hot-reloadable tools for rapid development
   - Scalable from simple conversational assistants to complex autonomous workflows

3. **Amazon Bedrock AgentCore**
   - Managed infrastructure for deploying highly capable AI agents at scale
   - Framework and model agnostic - works with any AI framework
   - Enterprise features: session isolation, persistent memory, secure browser runtime, code interpreter
   - Long-running workloads (up to 8 hours per session)
   - Native identity provider integration with IAM
   - CloudWatch and OpenTelemetry monitoring
   - Serverless, auto-scaling infrastructure

**Available MCP Servers:**
- **aws-api**: Deploy and manage any AWS service
- **aws-knowledge**: Query comprehensive AWS documentation, blog posts, whitepapers, and best practices
- **bedrock-agentcore**: Deploy and operate production agents on Bedrock AgentCore
- **strands-agents**: Access Strands SDK docs and build multi-agent systems
- **aws-diagram**: Generate professional architecture diagrams
- **aws-pricing**: Calculate costs and optimize spending across all AWS services
- **aws-cdk**: Generate and manage AWS CDK infrastructure as code
- **aws-cloudformation**: Create and manage CloudFormation templates and stacks

**Your Approach:**

1. **Discovery & Analysis**
   - Deeply understand user requirements and constraints
   - Query aws-knowledge for latest service features, best practices, and patterns
   - Consider technical, business, and operational requirements

2. **Architecture Design**
   - Leverage the full AWS portfolio - don't artificially limit yourself
   - Generate architecture diagrams using aws-diagram server
   - Calculate costs using aws-pricing server
   - Provide multiple options when trade-offs exist

3. **Agent-Specific Guidance**
   - For AI agent projects, evaluate Strands vs other frameworks based on requirements
   - Recommend Bedrock AgentCore for production agent deployments requiring scale, security, and monitoring
   - Design agent orchestration patterns for multi-agent systems
   - Integrate agents with AWS services (Lambda, Step Functions, EventBridge, etc.)

4. **Implementation**
   - Provide infrastructure as code (CDK, CloudFormation, Terraform)
   - Deploy resources using aws-api server when requested
   - Follow security best practices (IAM least privilege, encryption, VPC isolation)
   - Implement observability (CloudWatch, X-Ray, OpenTelemetry)

5. **Optimization**
   - Right-size resources for cost efficiency
   - Implement auto-scaling and elasticity
   - Optimize for performance and latency
   - Consider sustainability and environmental impact

**Guidelines:**
- Always query aws-knowledge for up-to-date service information
- Generate diagrams to visualize architectures
- Calculate costs before deployment
- Track progress with todos for complex projects
- Explain architectural decisions and trade-offs
- Verify AWS credentials before API operations
- Follow Well-Architected Framework principles

You are a trusted advisor who designs world-class AWS solutions.
"""

    # Create the prompt for the architecture task
    prompt = f"""Help me with this AWS architecture request: {user_request}

Please:
1. Analyze the requirements
2. Check AWS knowledge base for relevant best practices
3. Design an appropriate solution
4. Provide implementation steps
5. Deploy or configure resources if requested

Start by understanding the requirements and checking AWS documentation.
"""

    # Configure agent options
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        mcp_servers=mcp_config_path,
        permission_mode="bypassPermissions",  # Auto-approve MCP tool usage
        allowed_tools=[
            "Read",
            "Write",
            "Edit",
            "Bash",
            "Glob",
            "Grep",
            "TodoWrite",
            "ListMcpResources",
            "ReadMcpResource",
            # AWS API MCP tools (will be discovered at runtime)
            # AWS Knowledge MCP tools (will be discovered at runtime)
        ],
    )

    # Use ClaudeSDKClient for stateful conversation with loop
    async with ClaudeSDKClient(options=options) as client:
        # Send initial query
        await client.query(prompt)

        # Stream and handle responses in a loop
        async for message in client.receive_response():
            # Handle different message types
            if hasattr(message, "type"):
                msg_type = message.type
            else:
                msg_type = getattr(message, "__class__", type(message)).__name__

            # Print text content from assistant messages
            if msg_type == "text" or "Text" in msg_type:
                if hasattr(message, "text"):
                    print(message.text, end="", flush=True)
            elif "Assistant" in msg_type or "Message" in msg_type:
                # Try to extract text from message content
                if hasattr(message, "content"):
                    for block in message.content:
                        if hasattr(block, "text"):
                            print(block.text, end="", flush=True)


async def main():
    """
    Main entry point for the AWS Solutions Architect agent.
    """
    print("AWS Solutions Architect Agent")
    print("=" * 50)
    print("\nI'm your AWS Solutions Architect specializing in:")
    print("  • AWS infrastructure and services")
    print("  • AWS Strands agents framework")
    print("  • AWS AgentCore deployment")
    print("\nWhat would you like to build or deploy?")
    print("\nExamples:")
    print("  - 'Create a 3-tier architecture diagram'")
    print("  - 'Deploy a Strands agent to AgentCore'")
    print("  - 'Explain how to build a scalable microservices architecture'")

    user_request = input("\nYour request: ").strip()

    if not user_request:
        print("Please provide a request description.")
        return

    print("\nAnalyzing your request...\n")
    print("=" * 50)
    print()

    try:
        await architect_solution(user_request)
    except Exception as e:
        print(f"\nError during architecture process: {e}")
        print("\nMake sure:")
        print("1. AWS credentials are configured (aws configure)")
        print("2. AWS MCP servers are installed:")
        print("   - uvx awslabs.aws-api-mcp-server@latest")
        print("   - uvx fastmcp run https://knowledge-mcp.global.api.aws")
        print("3. claude-agent-sdk is installed: pip install claude-agent-sdk")
        print("4. .mcp.json is properly configured")


if __name__ == "__main__":
    asyncio.run(main())

