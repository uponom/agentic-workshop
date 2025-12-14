from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
import os

# Создаем папку для диаграмм если её нет
os.makedirs("diagrams", exist_ok=True)

aws_docs_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    )
)

aws_diag_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=[
                "--with",
                "sarif-om,jschema_to_python",
                "awslabs.aws-diagram-mcp-server@latest",
            ],
        )
    )
)

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=0.3,  # Снижаем температуру для более предсказуемого поведения
)

SYSTEM_PROMPT = """
You are an expert AWS Solutions Architect. You help with AWS documentation and create architecture diagrams.

For diagram generation:
- Use simple, valid Python syntax for AWS diagrams
- Don't include any import statements in the diagram code
- Use basic AWS service names
- Keep the architecture simple and clear
- Save files to the current directory with .png extension

Always provide the full file path of generated diagrams.
"""

def main():
    print("Инициализация MCP клиентов...")
    
    with aws_diag_client, aws_docs_client:
        print("Получение списка доступных инструментов...")
        
        # Получаем инструменты отдельно для отладки
        docs_tools = aws_docs_client.list_tools_sync()
        diag_tools = aws_diag_client.list_tools_sync()
        
        print(f"Инструменты документации: {[tool.name for tool in docs_tools]}")
        print(f"Инструменты диаграмм: {[tool.name for tool in diag_tools]}")
        
        all_tools = docs_tools + diag_tools
        
        print("Создание агента...")
        agent = Agent(tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)

        print("Отправка запроса агенту...")
        response = agent(
            "Create a simple AWS architecture diagram with: S3 bucket, CloudFront, and Lambda function. Save as 'simple_architecture.png'"
        )
        
        print("Ответ агента:")
        print(response)

if __name__ == "__main__":
    main()