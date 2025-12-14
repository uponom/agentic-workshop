from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

# Create MCP client for AWS CDK
cdk_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.cdk-mcp-server@latest"]
        )
    )
)

# Initialize Bedrock model
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    temperature=0.7,
)

# Define system prompt for CDK agent
SYSTEM_PROMPT = """
You are an AWS CDK expert. Your role is to help customers build and understand AWS infrastructure using CDK.
You can assist with CDK code, explain CDK concepts, and provide guidance on best practices for infrastructure as code.
"""

# Create and run the agent
with cdk_client:
    tools = cdk_client.list_tools_sync()
    agent = Agent(tools=tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)
    
    response = agent(
        "How can I create an S3 bucket with python CDK? Show me a simple example."
    )
    print(response)