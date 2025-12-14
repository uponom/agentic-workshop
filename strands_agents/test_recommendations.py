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

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=0.3,
)

SYSTEM_PROMPT = """
Вы эксперт AWS Solutions Architect. Используйте инструмент recommend для предоставления рекомендаций по AWS сервисам.
"""

def main():
    print("💡 Тестирование рекомендаций AWS...")
    
    with aws_docs_client:
        tools = aws_docs_client.list_tools_sync()
        agent = Agent(tools=tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)

        print("\n🏗️ Запрос рекомендаций для веб-приложения...")
        response = agent("Дай рекомендации по AWS сервисам для создания масштабируемого веб-приложения с базой данных")
        print("Рекомендации:", response)

if __name__ == "__main__":
    main()