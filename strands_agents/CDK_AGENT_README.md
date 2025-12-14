# AWS CDK Strands Agent

A specialized Strands Agent that connects to the AWS CDK MCP server to provide comprehensive CDK assistance, including project initialization, stack management, deployment operations, and best practices guidance.

## Features

- **CDK Project Management**: Initialize, configure, and manage CDK projects
- **Stack Operations**: Create, modify, deploy, and destroy CDK stacks
- **Best Practices Guidance**: Get expert advice on CDK patterns and AWS integrations
- **Real-time CDK Operations**: Execute actual CDK commands through MCP tools
- **Interactive & Demo Modes**: Choose between hands-on interaction or guided demonstrations

## Prerequisites

### 1. Install Dependencies
```bash
pip install strands-agents strands-agents-tools mcp uv
```

### 2. Configure AWS Credentials
Choose one of the following options:

**Option A: Bedrock API Key (Recommended for development)**
```bash
export AWS_BEDROCK_API_KEY=your_bedrock_api_key
```

**Option B: AWS Credentials**
```bash
aws configure
# OR
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2
```

### 3. Verify Installation
```bash
python test_cdk_agent.py
```

## Usage

### Interactive Mode (Default)
```bash
python cdk_agent.py
# OR
python cdk_agent.py --interactive
```

This starts an interactive session where you can:
- Ask questions about CDK concepts
- Request CDK operations
- Get guidance on best practices
- Troubleshoot CDK issues

### Demo Mode
```bash
python cdk_agent.py --demo
```

Runs through predefined CDK questions to demonstrate capabilities.

## Example Interactions

### Getting Started
```
👤 You: How do I create a new CDK project for a Python Lambda function?

🤖 CDK Agent: I'll help you create a new CDK project for a Python Lambda function. Let me walk you through the process...

[Agent uses CDK MCP tools to provide step-by-step guidance]
```

### Stack Management
```
👤 You: How do I deploy my CDK stack to a specific AWS region?

🤖 CDK Agent: To deploy your CDK stack to a specific region, you have several options...

[Agent provides detailed deployment instructions using CDK tools]
```

### Best Practices
```
👤 You: What are the security best practices for CDK Lambda functions?

🤖 CDK Agent: Here are the key security best practices for CDK Lambda functions...

[Agent provides comprehensive security guidance]
```

## Available CDK Operations

The agent has access to comprehensive CDK tools through the AWS CDK MCP server, including:

- **Project Operations**: `cdk init`, `cdk bootstrap`
- **Stack Management**: `cdk deploy`, `cdk destroy`, `cdk diff`
- **Development Tools**: `cdk synth`, `cdk ls`, `cdk doctor`
- **Configuration**: Environment setup, context management
- **Troubleshooting**: Error diagnosis and resolution

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CDK Agent     │◄──►│   Strands SDK    │◄──►│  Bedrock Model  │
│   (cdk_agent.py)│    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌──────────────────┐
│   MCP Client    │◄──►│ AWS CDK MCP      │
│                 │    │ Server           │
└─────────────────┘    └──────────────────┘
```

## Code Structure

### CDKAgent Class
- **`__init__()`**: Initialize model and MCP client
- **`initialize()`**: Connect to CDK MCP server and setup tools
- **`chat()`**: Process user messages and return responses
- **`get_available_tools()`**: List available CDK tools

### Key Components
- **Model Configuration**: Uses Claude 3.5 Haiku for precise CDK guidance
- **MCP Integration**: Connects to `awslabs.cdk-mcp-server@latest`
- **Error Handling**: Comprehensive error handling and user feedback
- **Context Management**: Proper resource management with context managers

## Troubleshooting

### Common Issues

**Error: "uvx command not found"**
```bash
pip install uv
```

**Error: "AWS credentials not found"**
```bash
export AWS_BEDROCK_API_KEY=your_key
# OR
aws configure
```

**Error: "CDK MCP server connection failed"**
- Check internet connection
- Verify uvx is working: `uvx --version`
- Try running the test: `python test_cdk_agent.py`

**Error: "No tools available from CDK MCP server"**
- Ensure the CDK MCP server is accessible
- Check if there are any firewall restrictions
- Verify the MCP server package name is correct

### Debug Mode
For detailed debugging, modify the agent initialization:
```python
cdk_agent = CDKAgent()
# Add debug prints in the initialize() method
```

## Advanced Usage

### Custom Model Configuration
```python
from cdk_agent import CDKAgent

# Use a different model
agent = CDKAgent(model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0")
```

### Programmatic Usage
```python
from cdk_agent import CDKAgent

# Create and initialize agent
cdk_agent = CDKAgent()
if cdk_agent.initialize():
    # Use the agent programmatically
    response = cdk_agent.chat("How do I create an S3 bucket with CDK?")
    print(response)
```

## Contributing

To extend the CDK agent:

1. **Add new capabilities** by modifying the system prompt
2. **Enhance error handling** in the CDKAgent class methods
3. **Add new interaction modes** in the main() function
4. **Improve tool integration** by extending MCP client usage

## Related Files

- `mcp_agent_guide.py` - General MCP agent examples
- `simple_mcp_working_example.py` - Basic MCP integration
- `MCP_GUIDE_RU.md` - Comprehensive MCP guide (Russian)
- `INSTALL_MCP_RU.md` - Installation instructions (Russian)

## Resources

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [AWS CDK MCP Server](https://github.com/awslabs/mcp)
- [Strands Agents Documentation](https://strandsagents.com/latest/)
- [Model Context Protocol](https://modelcontextprotocol.io/)