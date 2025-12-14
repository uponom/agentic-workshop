from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import AnthropicModel
from strands.tools.mcp import MCPClient
import os

# Создаем папку для диаграмм
os.makedirs("diagrams", exist_ok=True)

# Проверяем наличие API ключа Anthropic
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_key:
    print("ОШИБКА: Не найден ANTHROPIC_API_KEY")
    print("Установите переменную окружения:")
    print('$env:ANTHROPIC_API_KEY="your_anthropic_api_key"')
    exit(1)

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

# Используем Anthropic модель вместо Bedrock
anthropic_model = AnthropicModel(
    model="claude-3-5-sonnet-20241022",
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
1. Используйте generate_diagram с простым кодом Python
2. НЕ включайте import statements в код диаграммы
3. Используйте базовые имена AWS сервисов
4. Код должен быть простым и понятным
5. Сохраняйте файлы с расширением .png

Пример правильного кода для диаграммы:
```
# Создание простой архитектуры
with Diagram("Static Website", show=False, filename="static_website"):
    user = Users("Users")
    
    with Cluster("AWS Cloud"):
        cf = Cloudfront("CloudFront")
        s3 = S3("S3 Bucket")
        lambda_func = Lambda("Lambda Function")
    
    user >> cf >> s3
    cf >> lambda_func
```

Всегда указывайте полный путь к созданным диаграммам.
"""

def main():
    print("Запуск AWS Solutions Architect агента с Anthropic...")
    
    try:
        with aws_diag_client, aws_docs_client:
            all_tools = aws_diag_client.list_tools_sync() + aws_docs_client.list_tools_sync()
            
            print(f"Доступные инструменты: {[tool.tool_name for tool in all_tools]}")
            
            agent = Agent(tools=all_tools, model=anthropic_model, system_prompt=SYSTEM_PROMPT)

            # Сначала получаем примеры диаграмм
            print("\n=== Получение примеров диаграмм ===")
            examples_response = agent("Покажи мне примеры диаграмм с помощью get_diagram_examples")
            print("Примеры:", examples_response)
            
            # Теперь создаем диаграмму
            print("\n=== Создание диаграммы ===")
            diagram_response = agent(
                "Создай простую диаграмму AWS архитектуры для статического веб-сайта: S3 bucket, CloudFront distribution и Lambda function. Сохрани как 'static_website_architecture.png'"
            )
            print("Результат:", diagram_response)
            
    except Exception as e:
        print(f"Ошибка: {e}")
        print("\nВозможные причины:")
        print("1. Не установлен uvx (нужен для MCP серверов)")
        print("2. Проблемы с сетевым подключением")
        print("3. Неправильный API ключ Anthropic")

if __name__ == "__main__":
    main()