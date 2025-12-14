"""
Простой пример создания диаграмм AWS без MCP серверов
Демонстрирует основные принципы работы с диаграммами
"""

from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.network import CloudFront
from diagrams.onprem.client import Users
from diagrams.aws.database import RDS
import os

def create_static_website_diagram():
    """Создает диаграмму статического веб-сайта"""
    
    # Создаем папку для диаграмм
    os.makedirs("diagrams", exist_ok=True)
    
    # Создаем диаграмму
    with Diagram("Static Website Architecture", 
                 show=False, 
                 filename="diagrams/static_website_architecture",
                 direction="TB"):
        
        # Пользователи
        users = Users("Website Visitors")
        
        # AWS сервисы
        cloudfront = CloudFront("CloudFront CDN")
        s3_bucket = S3("S3 Static Website")
        lambda_api = Lambda("Lambda API")
        
        # Связи между компонентами
        users >> cloudfront >> s3_bucket
        users >> cloudfront >> lambda_api
    
    print("✅ Диаграмма создана: diagrams/static_website_architecture.png")

def create_full_web_app_diagram():
    """Создает диаграмму полноценного веб-приложения"""
    
    with Diagram("Full Web Application", 
                 show=False, 
                 filename="diagrams/full_web_app",
                 direction="TB"):
        
        users = Users("Users")
        
        # Frontend
        cloudfront = CloudFront("CloudFront")
        s3_frontend = S3("S3 Frontend")
        
        # Backend API
        lambda_api = Lambda("Lambda API")
        
        # Database
        database = RDS("RDS Database")
        
        # Связи
        users >> cloudfront >> s3_frontend
        users >> cloudfront >> lambda_api >> database
    
    print("✅ Диаграмма создана: diagrams/full_web_app.png")

def create_serverless_api_diagram():
    """Создает диаграмму serverless API"""
    
    with Diagram("Serverless API Architecture", 
                 show=False, 
                 filename="diagrams/serverless_api",
                 direction="LR"):
        
        from diagrams.aws.network import APIGateway
        from diagrams.aws.database import Dynamodb
        
        users = Users("API Clients")
        api_gateway = APIGateway("API Gateway")
        lambda_func = Lambda("Lambda Function")
        dynamodb = Dynamodb("DynamoDB")
        
        users >> api_gateway >> lambda_func >> dynamodb
    
    print("✅ Диаграмма создана: diagrams/serverless_api.png")

def main():
    print("🚀 Создание примеров AWS диаграмм...")
    print()
    
    try:
        # Создаем разные типы диаграмм
        create_static_website_diagram()
        create_full_web_app_diagram() 
        create_serverless_api_diagram()
        
        print()
        print("📁 Все диаграммы сохранены в папке 'diagrams/'")
        print("🔍 Откройте .png файлы для просмотра архитектур")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Установите библиотеку diagrams:")
        print("   pip install diagrams")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()