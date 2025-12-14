from strands import Agent
from strands.models import BedrockModel
from strands.tools import tool
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.network import CloudFront, APIGateway
from diagrams.aws.database import RDS, Dynamodb
from diagrams.onprem.client import Users
import os
import datetime

# Создаем папку для диаграмм
os.makedirs("generated-diagrams", exist_ok=True)

bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=0.7,
)

def extract_keywords_from_query(query: str) -> list:
    """Извлекает ключевые слова из запроса пользователя"""
    aws_services = [
        'lambda', 'ec2', 's3', 'rds', 'dynamodb', 'cloudfront', 'api gateway', 'apigateway',
        'ecs', 'eks', 'fargate', 'elasticache', 'aurora', 'redshift', 'kinesis',
        'sqs', 'sns', 'step functions', 'stepfunctions', 'cognito', 'iam'
    ]
    
    architecture_types = [
        'serverless', 'microservices', 'web application', 'web app', 'api', 'rest api',
        'real-time', 'streaming', 'batch processing', 'data pipeline', 'etl', 'music', 'spotify'
    ]
    
    query_lower = query.lower()
    keywords = []
    
    for service in aws_services:
        if service in query_lower:
            keywords.append(service.replace(' ', '_'))
    
    for arch_type in architecture_types:
        if arch_type in query_lower:
            keywords.append(arch_type.replace(' ', '_'))
    
    return list(dict.fromkeys(keywords))[:3]

def generate_filename_from_context(query: str = "") -> str:
    """Генерирует имя файла на основе контекста запроса"""
    import re
    
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
        diagram_type: Type of diagram - "static_website", "serverless_api", "web_app", "music_streaming", or "custom"
        query_context: Original user query for generating filename and title
    
    Returns:
        Success message with file path and generated filename
    """
    
    try:
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
                "music_streaming": "Music Streaming Platform Architecture",
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
                
        elif diagram_type == "music_streaming":
            with Diagram(title, show=False, filename=filepath, direction="TB"):
                users = Users("Music Listeners")
                cloudfront = CloudFront("CloudFront CDN")
                s3_music = S3("S3 Music Storage")
                api_gateway = APIGateway("API Gateway")
                lambda_streaming = Lambda("Streaming Service")
                lambda_playlist = Lambda("Playlist Service")
                dynamodb = Dynamodb("DynamoDB")
                rds = RDS("Music Catalog")
                
                users >> cloudfront >> s3_music
                users >> api_gateway >> lambda_streaming >> dynamodb
                users >> api_gateway >> lambda_playlist >> rds
                
        elif diagram_type == "custom":
            with Diagram(title, show=False, filename=filepath):
                s3 = S3("S3 Bucket")
                lambda_func = Lambda("Lambda Function")
                s3 >> lambda_func
        
        full_path = f"{filepath}.png"
        
        return f"✅ Диаграмма создана: {full_path}\n📁 Файл: {filename}\n📋 Заголовок: {title}\n🔗 Полный путь: {os.path.abspath(full_path)}"
        
    except Exception as e:
        return f"❌ Ошибка создания диаграммы: {str(e)}"

SYSTEM_PROMPT = """
Вы - эксперт AWS Solutions Architect. Ваша задача - помочь клиентам понять лучшие практики построения на AWS и создать архитектурные диаграммы.

У вас есть только один инструмент для создания диаграмм:
🎨 create_aws_diagram - создает диаграммы локально (ОБЯЗАТЕЛЬНО используйте этот инструмент!)

Типы диаграмм:
- "static_website": S3 + CloudFront + Lambda
- "serverless_api": API Gateway + Lambda + DynamoDB  
- "web_app": Полная веб-архитектура
- "music_streaming": Архитектура музыкального стриминга
- "custom": Простая кастомная архитектура

КРИТИЧЕСКИ ВАЖНО: 
1. ВСЕГДА вызывайте create_aws_diagram ПЕРВЫМ делом для любого архитектурного запроса
2. Передавайте оригинальный запрос пользователя как query_context
3. Только после создания диаграммы предоставляйте детальное объяснение

Пример:
1. Вызов: create_aws_diagram(diagram_type="music_streaming", query_context="Спроектируй платформу для стриминга музыки как Spotify")
2. Затем детальное архитектурное объяснение

Всегда предоставляйте комплексное архитектурное руководство с лучшими практиками и рабочими файлами диаграмм.
"""

# Создаем агента только с локальным инструментом
agent = Agent(tools=[create_aws_diagram], model=bedrock_model, system_prompt=SYSTEM_PROMPT)

# Тестируем создание диаграммы
print("🤖 Отправка запроса агенту...")

user_query = "Спроектируй платформу для стриминга музыки как Spotify"

response = agent(user_query)

print("\n📄 Ответ агента:")
print(response)

print("\n✨ Готово! Проверьте папку generated-diagrams/")