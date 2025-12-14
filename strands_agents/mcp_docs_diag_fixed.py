from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
import os

# Создаем папку для диаграмм
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
    temperature=0.3,
)

SYSTEM_PROMPT = """
Вы эксперт AWS Solutions Architect. Вы помогаете с документацией AWS и создаете архитектурные диаграммы.

Доступные инструменты:
- read_documentation: читает документацию AWS
- search_documentation: ищет в документации AWS  
- recommend: дает рекомендации по AWS
- generate_diagram: создает диаграммы архитектуры AWS
- get_diagram_examples: показывает примеры диаграмм
- list_icons: показывает доступные иконки

Для создания диаграмм:
1. Сначала получите примеры с помощью get_diagram_examples
2. Используйте generate_diagram с простым кодом Python
3. Не включайте import statements в код диаграммы
4. Используйте базовые имена AWS сервисов
5. Сохраняйте файлы в папку diagrams/

Всегда указывайте полный путь к созданным диаграммам.
"""

def main():
    print("Запуск AWS Solutions Architect агента...")
    
    with aws_diag_client, aws_docs_client:
        all_tools = aws_diag_client.list_tools_sync() + aws_docs_client.list_tools_sync()
        
        print(f"Доступные инструменты: {[tool.tool_name for tool in all_tools]}")
        
        agent = Agent(tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)

        # Сначала получаем примеры диаграмм
        print("\n=== Получение примеров диаграмм ===")
        examples_response = agent("Покажи мне примеры диаграмм с помощью get_diagram_examples")
        print("Примеры:", examples_response)
        
        # Теперь создаем диаграмму
        print("\n=== Создание диаграммы ===")
        diagram_response = agent(
            "Создай простую диаграмму AWS архитектуры: S3 bucket для статического сайта, CloudFront distribution и Lambda function. Сохрани как 'static_website_architecture.png' в папку diagrams/"
        )
        print("Результат:", diagram_response)

if __name__ == "__main__":
    main()