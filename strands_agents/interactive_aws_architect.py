"""
Интерактивный AWS Solutions Architect агент с динамическим именованием файлов
"""

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
import datetime
import re

# Создаем папку для диаграмм
os.makedirs("generated-diagrams", exist_ok=True)

# Глобальные переменные для хранения последних сгенерированных значений
last_generated_filename = ""
last_generated_title = ""
current_user_query = ""

def extract_keywords_from_query(query: str) -> list:
    """Извлекает ключевые слова из запроса пользователя"""
    aws_services = [
        'lambda', 'ec2', 's3', 'rds', 'dynamodb', 'cloudfront', 'api gateway', 'apigateway',
        'ecs', 'eks', 'fargate', 'elasticache', 'aurora', 'redshift', 'kinesis',
        'sqs', 'sns', 'step functions', 'stepfunctions', 'cognito', 'iam'
    ]
    
    architecture_types = [
        'serverless', 'microservices', 'web application', 'web app', 'api', 'rest api',
        'real-time', 'streaming', 'batch processing', 'data pipeline', 'etl'
    ]
    
    industries = [
        'ecommerce', 'e-commerce', 'fintech', 'healthcare', 'gaming', 'iot', 'retail',
        'banking', 'media', 'social', 'education'
    ]
    
    query_lower = query.lower()
    keywords = []
    
    for service in aws_services:
        if service in query_lower:
            keywords.append(service.replace(' ', '_'))
    
    for arch_type in architecture_types:
        if arch_type in query_lower:
            keywords.append(arch_type.replace(' ', '_'))
    
    for industry in industries:
        if industry in query_lower:
            keywords.append(industry)
    
    return list(dict.fromkeys(keywords))[:3]

def generate_filename_from_context(query: str = "") -> str:
    """Генерирует имя файла на основе контекста запроса"""
    keywords = extract_keywords_from_query(query)
    
    if not keywords:
        timestamp = datetime.datetime.now().strftime("%H%M")
        return f"aws_architecture_{timestamp}"
    
    filename = '_'.join(keywords)
    filename = re.sub(r'[^\w\-_]', '', filename)
    filename = re.sub(r'_+', '_', filename).strip('_')
    
    return filename[:40] if len(filename) > 40 else filename

@tool
def create_aws_diagram(
    diagram_type: str,
    query_context: str = ""
) -> str:
    """
    Creates AWS architecture diagrams locally using Python diagrams library
    
    Args:
        diagram_type: Type of diagram - "static_website", "serverless_api", "web_app", or "custom"
        query_context: Original user query for generating filename and title
    
    Returns:
        Success message with file path and generated filename
    """
    
    try:
        global last_generated_filename, last_generated_title, current_user_query
        
        # Используем текущий запрос пользователя если query_context пустой
        context = query_context or current_user_query
        
        # Генерируем имя файла и заголовок на основе контекста
        filename = generate_filename_from_context(context)
        
        # Генерируем заголовок
        keywords = extract_keywords_from_query(context)
        if keywords:
            title = ' '.join(word.replace('_', ' ').title() for word in keywords) + ' Architecture'
        else:
            title_map = {
                "static_website": "Static Website Architecture",
                "serverless_api": "Serverless API Architecture", 
                "web_app": "Web Application Architecture",
                "custom": "AWS Architecture"
            }
            title = title_map.get(diagram_type, "AWS Architecture")
        
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
        
        # Сохраняем информацию для последующего использования
        last_generated_filename = filename
        last_generated_title = title
        
        return f"✅ Диаграмма создана: {full_path}\n📁 Файл: {filename}\n📋 Заголовок: {title}\n🔗 Полный путь: {os.path.abspath(full_path)}"
        
    except Exception as e:
        return f"❌ Ошибка создания диаграммы: {str(e)}"

def save_agent_response(response: str, filename: str = None, title: str = None):
    """Сохраняет ответ агента в markdown файл"""
    try:
        global last_generated_filename, last_generated_title
        
        if filename is None:
            filename = last_generated_filename or f"aws_architecture_{datetime.datetime.now().strftime('%H%M')}"
        if title is None:
            title = last_generated_title or "AWS Architecture Analysis"
            
        md_filepath = f"generated-diagrams/{filename}.md"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_content = f"""# {title}

*Сгенерировано AWS Solutions Architect агентом*  
*Дата создания: {timestamp}*

---

{response}

---

## 📁 Связанные файлы

- 📊 **Диаграмма**: `{filename}.png`
- 📝 **Документация**: `{filename}.md`

## 🔧 Техническая информация

- **Агент**: AWS Solutions Architect MCP Agent
- **Инструменты**: MCP серверы + локальная генерация диаграмм
- **Создано в**: `{os.getcwd()}`
- **Файл агента**: `{os.path.basename(__file__)}`

---

*Этот документ создан автоматически и содержит экспертные рекомендации по архитектуре AWS.*
"""
        
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"📝 Документация сохранена: {md_filepath}")
        return md_filepath
        
    except Exception as e:
        print(f"⚠️ Ошибка сохранения документации: {e}")
        return None

def setup_agent():
    """Настраивает агента с MCP инструментами"""
    
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        temperature=0.3,
    )

    SYSTEM_PROMPT = """
You are an expert AWS Certified Solutions Architect. Your role is to help customers understand best practices on building on AWS. You can query AWS Documentation and create architecture diagrams.

Available tools:
📚 Documentation tools:
- read_documentation: Get specific AWS service information
- search_documentation: Find relevant topics in AWS docs
- recommend: Get architectural recommendations

🎨 Diagram tools:
- create_aws_diagram: Create diagrams locally (RECOMMENDED - works reliably)

When creating diagrams, use create_aws_diagram with these types:
- "static_website": S3 + CloudFront + Lambda architecture
- "serverless_api": API Gateway + Lambda + DynamoDB  
- "web_app": Full web application architecture
- "custom": Simple custom architecture

IMPORTANT: Always pass the original user query as query_context parameter to create_aws_diagram. This helps generate appropriate filenames and titles automatically.

Example: create_aws_diagram(diagram_type="serverless_api", query_context="Create a serverless e-commerce API with Lambda and DynamoDB")

Always provide comprehensive architectural guidance with best practices and working diagram files.
"""
    
    try:
        # Пытаемся подключить MCP серверы
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
        
        with aws_diag_client, aws_docs_client:
            print("✅ MCP серверы подключены")
            mcp_tools = aws_diag_client.list_tools_sync() + aws_docs_client.list_tools_sync()
            all_tools = mcp_tools + [create_aws_diagram]
            
            return Agent(tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)
            
    except Exception as e:
        print(f"⚠️ Ошибка подключения MCP серверов: {e}")
        print("🔄 Создание агента только с локальными диаграммами...")
        
        return Agent(tools=[create_aws_diagram], model=bedrock_model, system_prompt=SYSTEM_PROMPT)

def interactive_session():
    """Запускает интерактивную сессию с агентом"""
    
    print("🚀 Интерактивный AWS Solutions Architect")
    print("=" * 50)
    print("Введите ваши запросы по архитектуре AWS.")
    print("Агент автоматически создаст диаграммы и документацию.")
    print("Введите 'exit' для выхода.\n")
    
    agent = setup_agent()
    
    while True:
        try:
            # Получаем запрос от пользователя
            user_input = input("🤖 Ваш запрос: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'выход']:
                print("👋 До свидания!")
                break
            
            if not user_input:
                continue
            
            # Сохраняем текущий запрос для использования в инструментах
            global current_user_query
            current_user_query = user_input
            
            print(f"\n🔄 Обработка запроса: {user_input}")
            print("-" * 50)
            
            # Отправляем запрос агенту
            response = agent(user_input)
            
            print("\n📄 Ответ агента:")
            print(response)
            
            # Сохраняем ответ в markdown файл
            print("\n💾 Сохранение документации...")
            save_agent_response(response)
            
            print("\n✨ Готово! Проверьте папку generated-diagrams/")
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Сессия прервана пользователем")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            print("Попробуйте еще раз или введите 'exit' для выхода")

def demo_session():
    """Демонстрационная сессия с примерами запросов"""
    
    print("🎯 Демонстрационная сессия")
    print("=" * 30)
    
    demo_queries = [
        "Create a serverless e-commerce platform with Lambda, API Gateway, and DynamoDB",
        "Design a scalable web application for a fintech startup using EC2 and RDS",
        "Build a real-time analytics pipeline for IoT data using Kinesis and S3"
    ]
    
    agent = setup_agent()
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔄 Демо запрос {i}: {query}")
        print("-" * 50)
        
        global current_user_query
        current_user_query = query
        
        try:
            response = agent(query)
            print(f"\n📄 Ответ агента:")
            print(response[:500] + "..." if len(response) > 500 else response)
            
            save_agent_response(response)
            print(f"\n✅ Демо {i} завершено")
            
        except Exception as e:
            print(f"❌ Ошибка в демо {i}: {e}")
        
        print("=" * 50)

def main():
    """Главная функция"""
    
    print("Выберите режим:")
    print("1. Интерактивная сессия")
    print("2. Демонстрация")
    
    choice = input("Ваш выбор (1 или 2): ").strip()
    
    if choice == "1":
        interactive_session()
    elif choice == "2":
        demo_session()
    else:
        print("Неверный выбор. Запуск интерактивной сессии...")
        interactive_session()

if __name__ == "__main__":
    main()