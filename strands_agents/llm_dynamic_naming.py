"""
AWS Solutions Architect агент с LLM-генерацией имен файлов и заголовков
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
import json

# Создаем папку для диаграмм
os.makedirs("generated-diagrams", exist_ok=True)

# Глобальные переменные для хранения последних сгенерированных значений
last_generated_filename = ""
last_generated_title = ""
current_user_query = ""

@tool
def generate_filename_and_title(user_query: str) -> str:
    """
    Генерирует имя файла и заголовок на основе запроса пользователя с помощью LLM
    
    Args:
        user_query: Запрос пользователя
        
    Returns:
        JSON строка с filename и title
    """
    
    try:
        # Создаем отдельную LLM для генерации имен
        naming_model = BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            temperature=0.1,
        )
        
        naming_prompt = f"""
Проанализируй следующий запрос пользователя и создай:
1. Имя файла (filename) - короткое, описательное, на английском, используя только буквы, цифры и подчеркивания
2. Заголовок (title) - красивый заголовок для документа на русском языке

Запрос пользователя: "{user_query}"

Правила для имени файла:
- Только английские буквы, цифры и подчеркивания
- Максимум 40 символов
- Отражает суть запроса
- Без пробелов и специальных символов

Правила для заголовка:
- На русском языке
- Красивый и понятный
- Отражает содержание архитектуры
- Может содержать технические термины

Верни результат ТОЛЬКО в формате JSON:
{{"filename": "имя_файла", "title": "Заголовок документа"}}
"""
        
        response = naming_model(naming_prompt)
        
        # Извлекаем JSON из ответа
        try:
            # Ищем JSON в ответе
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                filename = result.get('filename', 'aws_architecture')
                title = result.get('title', 'AWS Architecture')
                
                # Очищаем имя файла от недопустимых символов
                filename = re.sub(r'[^\w\-_]', '', filename)
                filename = re.sub(r'_+', '_', filename).strip('_')
                
                if not filename:
                    filename = f"aws_architecture_{datetime.datetime.now().strftime('%H%M')}"
                
                global last_generated_filename, last_generated_title
                last_generated_filename = filename
                last_generated_title = title
                
                return json.dumps({"filename": filename, "title": title}, ensure_ascii=False)
            
        except json.JSONDecodeError:
            pass
        
        # Fallback если не удалось распарсить JSON
        timestamp = datetime.datetime.now().strftime("%H%M")
        fallback_filename = f"aws_architecture_{timestamp}"
        fallback_title = "AWS Cloud Architecture"
        
        global last_generated_filename, last_generated_title
        last_generated_filename = fallback_filename
        last_generated_title = fallback_title
        
        return json.dumps({"filename": fallback_filename, "title": fallback_title}, ensure_ascii=False)
        
    except Exception as e:
        # Fallback в случае ошибки
        timestamp = datetime.datetime.now().strftime("%H%M")
        error_filename = f"aws_architecture_{timestamp}"
        error_title = "AWS Architecture"
        
        global last_generated_filename, last_generated_title
        last_generated_filename = error_filename
        last_generated_title = error_title
        
        return json.dumps({"filename": error_filename, "title": error_title}, ensure_ascii=False)

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
        
        # Генерируем имя файла и заголовок с помощью LLM
        naming_result = generate_filename_and_title(context)
        naming_data = json.loads(naming_result)
        
        filename = naming_data['filename']
        title = naming_data['title']
        
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
        
        return f"✅ Диаграмма создана: {full_path}\n📁 Файл: {filename}\n📋 Заголовок: {title}"
        
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
- **Инструменты**: MCP серверы + локальная генерация диаграмм + LLM именование
- **Создано в**: `{os.getcwd()}`

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
- generate_filename_and_title: Generate smart filenames and titles using LLM

🔧 Naming tools:
- generate_filename_and_title: Creates intelligent filenames and titles based on user query

When creating diagrams, use create_aws_diagram with these types:
- "static_website": S3 + CloudFront + Lambda architecture
- "serverless_api": API Gateway + Lambda + DynamoDB  
- "web_app": Full web application architecture
- "custom": Simple custom architecture

IMPORTANT WORKFLOW:
1. First call generate_filename_and_title(user_query) to create smart naming
2. Then call create_aws_diagram with the query_context parameter
3. The system will automatically save both diagram and documentation with matching names

The LLM will generate appropriate filenames and titles for ANY topic, not just predefined AWS services.

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
            all_tools = mcp_tools + [create_aws_diagram, generate_filename_and_title]
            
            return Agent(tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)
            
    except Exception as e:
        print(f"⚠️ Ошибка подключения MCP серверов: {e}")
        print("🔄 Создание агента только с локальными инструментами...")
        
        return Agent(tools=[create_aws_diagram, generate_filename_and_title], model=bedrock_model, system_prompt=SYSTEM_PROMPT)

def process_user_query(agent, user_query):
    """Обрабатывает запрос пользователя"""
    
    global current_user_query
    current_user_query = user_query
    
    print(f"\n🔄 Обработка запроса: {user_query}")
    print("-" * 60)
    
    try:
        # Отправляем запрос агенту
        response = agent(user_query)
        
        print("\n📄 Ответ агента:")
        print(response)
        
        # Сохраняем ответ в markdown файл
        print("\n💾 Сохранение документации...")
        save_agent_response(response)
        
        print(f"\n✅ Запрос обработан успешно!")
        print(f"📁 Файлы сохранены как: {last_generated_filename}.png и {last_generated_filename}.md")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка обработки запроса: {e}")
        return False

def main():
    """Главная функция"""
    
    print("🚀 AWS Solutions Architect с LLM-генерацией имен файлов")
    print("=" * 60)
    print("Агент использует LLM для создания умных имен файлов и заголовков")
    print("на основе ЛЮБОЙ темы запроса пользователя.\n")
    
    # Настраиваем агента
    print("🔧 Настройка агента...")
    agent = setup_agent()
    
    # Примеры запросов для демонстрации разнообразных тем
    demo_queries = [
        "Создай архитектуру для системы мониторинга IoT устройств в умном городе",
        "Спроектируй платформу для онлайн обучения с видеостримингом и тестированием",
        "Разработай архитектуру для системы анализа финансовых рисков в реальном времени",
        "Создай решение для обработки медицинских изображений с использованием машинного обучения",
        "Спроектируй платформу для многопользовательской онлайн игры с глобальным охватом"
    ]
    
    print(f"\n📋 Демонстрация с {len(demo_queries)} разнообразными примерами:")
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*60}")
        print(f"🎯 Пример {i} из {len(demo_queries)}")
        
        success = process_user_query(agent, query)
        
        if success:
            print("✨ Пример завершен успешно!")
        else:
            print("⚠️ Пример завершен с ошибками")
    
    print(f"\n{'='*60}")
    print("🎉 Демонстрация завершена!")
    
    # Показываем созданные файлы
    print("\n📁 Созданные файлы:")
    if os.path.exists("generated-diagrams"):
        files = [f for f in os.listdir("generated-diagrams") if f.endswith(('.png', '.md'))]
        files.sort()
        
        for file in files[-10:]:  # Показываем последние 10 файлов
            print(f"   - {file}")
        
        print(f"\n💡 Всего создано файлов: {len(files)}")
    
    print("📂 Все файлы находятся в папке: generated-diagrams/")

if __name__ == "__main__":
    main()