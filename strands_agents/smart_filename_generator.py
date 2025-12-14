"""
Интеллектуальный генератор имен файлов и заголовков на основе запросов пользователя
"""

import re
import datetime
from typing import Tuple

def extract_keywords_from_query(query: str) -> list:
    """
    Извлекает ключевые слова из запроса пользователя
    
    Args:
        query: Запрос пользователя
        
    Returns:
        Список ключевых слов
    """
    
    # AWS сервисы и технологии
    aws_services = [
        'lambda', 'ec2', 's3', 'rds', 'dynamodb', 'cloudfront', 'api gateway', 'apigateway',
        'ecs', 'eks', 'fargate', 'elasticache', 'aurora', 'redshift', 'kinesis',
        'sqs', 'sns', 'step functions', 'stepfunctions', 'cognito', 'iam',
        'vpc', 'cloudwatch', 'cloudformation', 'codepipeline', 'codebuild',
        'elastic beanstalk', 'elasticbeanstalk', 'route53', 'cloudtrail',
        'config', 'secrets manager', 'parameter store', 'systems manager'
    ]
    
    # Типы архитектур и паттернов
    architecture_types = [
        'serverless', 'microservices', 'monolith', 'multi-tier', 'multi tier',
        'web application', 'web app', 'mobile app', 'api', 'rest api',
        'graphql', 'websocket', 'real-time', 'realtime', 'streaming',
        'batch processing', 'data pipeline', 'etl', 'machine learning', 'ml',
        'ai', 'analytics', 'big data', 'data lake', 'data warehouse'
    ]
    
    # Отрасли и типы приложений
    industries = [
        'ecommerce', 'e-commerce', 'fintech', 'healthcare', 'education',
        'gaming', 'media', 'social', 'iot', 'automotive', 'retail',
        'banking', 'insurance', 'logistics', 'manufacturing', 'startup'
    ]
    
    # Характеристики
    characteristics = [
        'scalable', 'high availability', 'fault tolerant', 'secure',
        'cost effective', 'performance', 'multi-region', 'global',
        'enterprise', 'production', 'development', 'staging'
    ]
    
    query_lower = query.lower()
    keywords = []
    
    # Ищем AWS сервисы
    for service in aws_services:
        if service in query_lower:
            keywords.append(service.replace(' ', '_'))
    
    # Ищем типы архитектур
    for arch_type in architecture_types:
        if arch_type in query_lower:
            keywords.append(arch_type.replace(' ', '_'))
    
    # Ищем отрасли
    for industry in industries:
        if industry in query_lower:
            keywords.append(industry)
    
    # Ищем характеристики
    for char in characteristics:
        if char in query_lower:
            keywords.append(char.replace(' ', '_'))
    
    # Удаляем дубликаты и возвращаем первые 4 ключевых слова
    return list(dict.fromkeys(keywords))[:4]

def generate_filename_from_query(query: str) -> str:
    """
    Генерирует имя файла на основе запроса пользователя
    
    Args:
        query: Запрос пользователя
        
    Returns:
        Имя файла (без расширения)
    """
    
    keywords = extract_keywords_from_query(query)
    
    if not keywords:
        # Если ключевые слова не найдены, используем общие термины
        if 'diagram' in query.lower():
            keywords.append('architecture')
        if 'website' in query.lower() or 'web' in query.lower():
            keywords.append('web_app')
        if 'api' in query.lower():
            keywords.append('api')
        if 'database' in query.lower() or 'db' in query.lower():
            keywords.append('database')
    
    # Если все еще нет ключевых слов, используем timestamp
    if not keywords:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        return f"aws_architecture_{timestamp}"
    
    # Объединяем ключевые слова
    filename = '_'.join(keywords)
    
    # Очищаем имя файла от недопустимых символов
    filename = re.sub(r'[^\w\-_]', '', filename)
    filename = re.sub(r'_+', '_', filename)  # Убираем множественные подчеркивания
    filename = filename.strip('_')  # Убираем подчеркивания в начале и конце
    
    # Ограничиваем длину
    if len(filename) > 50:
        filename = filename[:50].rstrip('_')
    
    return filename or f"aws_architecture_{datetime.datetime.now().strftime('%H%M')}"

def generate_title_from_query(query: str) -> str:
    """
    Генерирует заголовок документа на основе запроса пользователя
    
    Args:
        query: Запрос пользователя
        
    Returns:
        Заголовок документа
    """
    
    keywords = extract_keywords_from_query(query)
    
    # Словарь для красивых названий
    service_names = {
        'lambda': 'AWS Lambda',
        'ec2': 'Amazon EC2',
        's3': 'Amazon S3',
        'rds': 'Amazon RDS',
        'dynamodb': 'Amazon DynamoDB',
        'cloudfront': 'Amazon CloudFront',
        'api_gateway': 'Amazon API Gateway',
        'apigateway': 'Amazon API Gateway',
        'ecs': 'Amazon ECS',
        'eks': 'Amazon EKS',
        'fargate': 'AWS Fargate',
        'elasticache': 'Amazon ElastiCache',
        'aurora': 'Amazon Aurora',
        'vpc': 'Amazon VPC',
        'route53': 'Amazon Route 53'
    }
    
    architecture_names = {
        'serverless': 'Serverless',
        'microservices': 'Microservices',
        'web_app': 'Web Application',
        'web_application': 'Web Application',
        'api': 'API',
        'rest_api': 'REST API',
        'ecommerce': 'E-commerce',
        'e-commerce': 'E-commerce',
        'multi_tier': 'Multi-Tier',
        'high_availability': 'High Availability',
        'scalable': 'Scalable'
    }
    
    # Создаем красивые названия из ключевых слов
    title_parts = []
    
    for keyword in keywords:
        if keyword in service_names:
            title_parts.append(service_names[keyword])
        elif keyword in architecture_names:
            title_parts.append(architecture_names[keyword])
        else:
            # Преобразуем подчеркивания в пробелы и делаем заглавными
            pretty_name = keyword.replace('_', ' ').title()
            title_parts.append(pretty_name)
    
    if title_parts:
        title = ' '.join(title_parts) + ' Architecture'
    else:
        # Fallback заголовок
        if 'serverless' in query.lower():
            title = 'Serverless Architecture'
        elif 'web' in query.lower():
            title = 'Web Application Architecture'
        elif 'api' in query.lower():
            title = 'API Architecture'
        elif 'database' in query.lower():
            title = 'Database Architecture'
        else:
            title = 'AWS Cloud Architecture'
    
    return title

def generate_filename_and_title(query: str) -> Tuple[str, str]:
    """
    Генерирует имя файла и заголовок на основе запроса
    
    Args:
        query: Запрос пользователя
        
    Returns:
        Кортеж (filename, title)
    """
    
    filename = generate_filename_from_query(query)
    title = generate_title_from_query(query)
    
    return filename, title

# Тестовые примеры
def test_generator():
    """Тестирует генератор имен файлов и заголовков"""
    
    test_queries = [
        "Create a serverless e-commerce architecture with Lambda and DynamoDB",
        "Design a scalable web application using EC2 and RDS",
        "Build a real-time analytics pipeline with Kinesis and S3",
        "Create a microservices architecture for a fintech application",
        "Design a high availability multi-tier web application",
        "Build an API Gateway with Lambda backend",
        "Create a data lake architecture for big data analytics",
        "Design a secure healthcare application on AWS",
        "Build a gaming platform with global distribution",
        "Create a simple website architecture"
    ]
    
    print("🧪 Тестирование генератора имен файлов и заголовков")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        filename, title = generate_filename_and_title(query)
        print(f"\n{i}. Запрос: {query}")
        print(f"   📁 Файл: {filename}")
        print(f"   📋 Заголовок: {title}")

if __name__ == "__main__":
    test_generator()