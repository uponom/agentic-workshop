from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from strands.tools import tool
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.network import CloudFront, APIGateway
from diagrams.aws.database import RDS, Dynamodb
from diagrams.onprem.client import Users
import os

# Создаем папку для диаграмм
os.makedirs("generated-diagrams", exist_ok=True)

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

# Создаем локальный инструмент для генерации диаграмм
@tool
def create_local_diagram(
    diagram_type: str,
    filename: str, 
    title: str
) -> str:
    """
    Creates AWS architecture diagrams locally using Python diagrams library
    
    Args:
        diagram_type: Type of diagram - "static_website", "serverless_api", "web_app", or "custom"
        filename: Name for the diagram file (without extension)
        title: Title for the diagram
    
    Returns:
        Success message with file path
    """
    
    try:
        filepath = f"generated-diagrams/{filename}"
        
        if diagram_type == "static_website":
            with Diagram(title, show=False, filename=filepath, direction="TB"):
                users = Users("Website Visitors")
                cloudfront = CloudFront("CloudFront CDN")
                s3 = S3("S3 Static Website")
                lambda_api = Lambda("Lambda API")
                
                users >> cloudfront >> s3
                users >> cloudfront >> lambda_api
                
        elif diagram_type == "serverless_api":
            with Diagram(title, show=False, filename=filepath, direction="LR"):
                users = Users("API Clients")
                api_gateway = APIGateway("API Gateway")
                lambda_func = Lambda("Lambda Function")
                dynamodb = Dynamodb("DynamoDB")
                
                users >> api_gateway >> lambda_func >> dynamodb
                
        elif diagram_type == "web_app":
            with Diagram(title, show=False, filename=filepath, direction="TB"):
                users = Users("Users")
                cloudfront = CloudFront("CloudFront")
                s3_frontend = S3("S3 Frontend")
                lambda_api = Lambda("Lambda API")
                database = RDS("RDS Database")
                
                users >> cloudfront >> s3_frontend
                users >> cloudfront >> lambda_api >> database
                
        elif diagram_type == "custom":
            with Diagram(title, show=False, filename=filepath):
                s3 = S3("S3 Bucket")
                lambda_func = Lambda("Lambda Function")
                s3 >> lambda_func
        
        full_path = f"{filepath}.png"
        return f"✅ Диаграмма создана: {full_path}\n📁 Полный путь: {os.path.abspath(full_path)}"
        
    except Exception as e:
        return f"❌ Ошибка создания диаграммы: {str(e)}"

# Функция для сохранения ответа агента
def save_agent_response(filename: str, response: str, title: str = "AWS Architecture Analysis"):
    """
    Сохраняет ответ агента в markdown файл
    
    Args:
        filename: Имя файла (без расширения)
        response: Ответ агента для сохранения
        title: Заголовок документа
    """
    try:
        md_filepath = f"generated-diagrams/{filename}.md"
        
        # Создаем содержимое markdown файла
        markdown_content = f"""# {title}

*Сгенерировано AWS Solutions Architect агентом*

---

{response}

---

**Файлы:**
- 📊 Диаграмма: `{filename}.png`
- 📝 Документация: `{filename}.md`

*Создано: {os.path.basename(__file__)} в {os.getcwd()}*
"""
        
        # Сохраняем файл
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"📝 Документация сохранена: {md_filepath}")
        return md_filepath
        
    except Exception as e:
        print(f"⚠️ Ошибка сохранения документации: {e}")
        return None

SYSTEM_PROMPT = """
You are an expert AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. You can query AWS Documentation and create architecture diagrams.

Available tools:
📚 Documentation tools:
- read_documentation: Get specific AWS service information
- search_documentation: Find relevant topics in AWS docs
- recommend: Get architectural recommendations

🎨 Diagram tools:
- get_diagram_examples: Show diagram examples from AWS
- list_icons: Show available AWS service icons  
- create_local_diagram: Create diagrams locally (RECOMMENDED for Windows)

When creating diagrams, prefer create_local_diagram with these types:
- "static_website": S3 + CloudFront + Lambda
- "serverless_api": API Gateway + Lambda + DynamoDB  
- "web_app": Full web application architecture
- "custom": Simple custom architecture

Always provide comprehensive architectural guidance with best practices and working diagram files.
"""

def main():
    print("🚀 AWS Solutions Architect агент с локальными диаграммами")
    
    # Локальный инструмент уже создан через декоратор @tool
    
    with aws_diag_client, aws_docs_client:
        # Получаем MCP инструменты
        mcp_tools = aws_diag_client.list_tools_sync() + aws_docs_client.list_tools_sync()
        
        # Добавляем локальный инструмент
        all_tools = mcp_tools + [create_local_diagram]
        
        print(f"🛠️ Доступно инструментов: {len(all_tools)}")
        for tool in all_tools:
            tool_name = getattr(tool, 'tool_name', getattr(tool, 'name', 'unknown'))
            print(f"   - {tool_name}")
        
        agent = Agent(tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)

        print("\n🎯 Тестирование создания диаграммы...")
        response = agent(
            "Создай диаграмму статического веб-сайта с S3, CloudFront и Lambda. Сохрани как 'static_website_architecture' с заголовком 'Static Website Architecture'"
        )
        
        print("📄 Ответ агента:")
        print(response)
        
        # Сохраняем ответ агента в markdown файл
        print("\n💾 Сохранение документации...")
        save_agent_response(
            filename="static_website_architecture",
            response=response,
            title="Static Website Architecture - AWS Solutions"
        )
        
        print("\n✨ Готово! Проверьте папку generated-diagrams/")

if __name__ == "__main__":
    main()