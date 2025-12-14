from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

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
    temperature=0.3,
)

SYSTEM_PROMPT = """
Вы эксперт AWS Solutions Architect. Используйте доступные инструменты для поиска информации в документации AWS и предоставления точных ответов.
"""

def main():
    print("🔍 Тестирование поиска в документации AWS...")
    
    with aws_diag_client, aws_docs_client:
        all_tools = aws_diag_client.list_tools_sync() + aws_docs_client.list_tools_sync()
        agent = Agent(tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)

        # Тест поиска в документации
        print("\n📚 Поиск информации о AWS Lambda...")
        response = agent("Найди основную информацию о AWS Lambda - что это такое и как работает")
        print("Ответ:", response)

if __name__ == "__main__":
    main()