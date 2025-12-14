"""
Простой тест динамического именования файлов
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

# Глобальные переменные
last_generated_filename = ""
last_generated_title = ""

def extract_keywords_from_query(query: str) -> list:
    """Извлекает ключевые слова из запроса пользователя"""
    aws_services = [
        'lambda', 'ec2', 's3', 'rds', 'dynamodb', 'cloudfront', 'api gateway', 'apigateway',
        'ecs', 'eks', 'fargate', 'elasticache', 'aurora', 'kinesis', 'sqs', 'sns'
    ]
    
    architecture_types = [
        'serverless', 'microservices', 'web application', 'web app', 'api', 'rest api',
        'real-time', 'streaming', 'batch processing', 'data pipeline'
    ]
    
    industries = [
        'ecommerce', 'e-commerce', 'fintech', 'healthcare', 'gaming', 'iot', 'retail'
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
        global last_generated_filename, last_generated_title
        
        # Генерируем имя файла и заголовок на основе контекста
        filename = generate_filename_from_context(query_context)
        
        # Генерируем заголовок
        keywords = extract_keywords_from_query(query_context)
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

def test_dynamic_naming():
    """Тестирует динамическое именование без агента"""
    
    print("🧪 Тест динамического именования файлов")
    print("=" * 45)
    
    test_queries = [
        ("Create a serverless e-commerce API with Lambda and DynamoDB", "serverless_api"),
        ("Design a web application for healthcare using EC2 and RDS", "web_app"),
        ("Build an IoT data pipeline with Kinesis and S3", "custom"),
        ("Create a gaming platform with CloudFront", "static_website")
    ]
    
    for i, (query, diagram_type) in enumerate(test_queries, 1):
        print(f"\n🔄 Тест {i}: {query}")
        print("-" * 50)
        
        # Создаем диаграмму
        result = create_aws_diagram(diagram_type, query)
        print(result)
        
        # Создаем mock ответ агента
        mock_response = f"""## Архитектурный анализ

Для запроса: "{query}"

### Рекомендуемая архитектура:
- Тип диаграммы: {diagram_type}
- Ключевые компоненты: {', '.join(extract_keywords_from_query(query))}

### Best Practices:
1. Используйте Multi-AZ развертывание
2. Включите мониторинг CloudWatch
3. Настройте автоматическое масштабирование
4. Обеспечьте безопасность с помощью IAM

Эта архитектура обеспечивает высокую доступность и масштабируемость."""
        
        # Сохраняем ответ
        save_agent_response(mock_response)
        
        print(f"✅ Тест {i} завершен")
    
    print("\n" + "=" * 45)
    print("✨ Все тесты завершены!")

def main():
    test_dynamic_naming()
    
    # Показываем созданные файлы
    print("\n📁 Созданные файлы:")
    for file in os.listdir("generated-diagrams"):
        if file.endswith(('.png', '.md')):
            print(f"   - {file}")

if __name__ == "__main__":
    main()