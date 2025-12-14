"""
Тест локального создания диаграмм без AWS Bedrock
"""
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.network import CloudFront, APIGateway
from diagrams.aws.database import RDS, Dynamodb
from diagrams.onprem.client import Users
import os
import datetime

# Создаем папку для диаграмм
os.makedirs("../generated-diagrams", exist_ok=True)

def extract_keywords_from_query(query: str) -> list:
    """Извлекает ключевые слова из запроса пользователя"""
    aws_services = [
        'lambda', 'ec2', 's3', 'rds', 'dynamodb', 'cloudfront', 'api gateway', 'apigateway',
        'ecs', 'eks', 'fargate', 'elasticache', 'aurora', 'redshift', 'kinesis',
        'sqs', 'sns', 'step functions', 'stepfunctions', 'cognito', 'iam'
    ]
    
    architecture_types = [
        'serverless', 'microservices', 'web application', 'web app', 'api', 'rest api',
        'real-time', 'streaming', 'batch processing', 'data pipeline', 'etl',
        'музыка', 'стриминг', 'spotify'
    ]
    
    industries = [
        'ecommerce', 'e-commerce', 'fintech', 'healthcare', 'gaming', 'iot', 'music'
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
    import re
    
    keywords = extract_keywords_from_query(query)
    
    if not keywords:
        timestamp = datetime.datetime.now().strftime("%H%M")
        return f"aws_architecture_{timestamp}"
    
    filename = '_'.join(keywords)
    filename = re.sub(r'[^\w\-_]', '', filename)
    filename = re.sub(r'_+', '_', filename).strip('_')
    
    return filename[:40] if len(filename) > 40 else filename

def create_music_streaming_diagram(query_context: str = ""):
    """Создает диаграмму для музыкальной стриминговой платформы"""
    
    filename = generate_filename_from_context(query_context)
    keywords = extract_keywords_from_query(query_context)
    
    if keywords:
        title = ' '.join(word.replace('_', ' ').title() for word in keywords) + ' Architecture'
    else:
        title = "Music Streaming Platform Architecture"
    
    filepath = f"../generated-diagrams/{filename}"
    
    print(f"🎵 Создание диаграммы: {title}")
    print(f"📁 Файл: {filename}")
    
    with Diagram(title, show=False, filename=filepath, direction="TB"):
        # Пользователи
        users = Users("Music Listeners")
        
        # CDN и фронтенд
        cloudfront = CloudFront("CloudFront CDN")
        s3_frontend = S3("S3 Web App")
        
        # API Gateway и микросервисы
        api_gateway = APIGateway("API Gateway")
        
        # Lambda функции для разных сервисов
        auth_lambda = Lambda("Authentication")
        music_lambda = Lambda("Music Catalog")
        streaming_lambda = Lambda("Streaming Service")
        playlist_lambda = Lambda("Playlist Manager")
        
        # Хранилища данных
        user_db = RDS("User Database")
        music_metadata = Dynamodb("Music Metadata")
        s3_music = S3("Music Files Storage")
        
        # Связи
        users >> cloudfront >> s3_frontend
        users >> cloudfront >> api_gateway
        
        api_gateway >> auth_lambda >> user_db
        api_gateway >> music_lambda >> music_metadata
        api_gateway >> streaming_lambda >> s3_music
        api_gateway >> playlist_lambda >> music_metadata
    
    full_path = f"{filepath}.png"
    
    return {
        "success": True,
        "filepath": full_path,
        "filename": filename,
        "title": title,
        "full_path": os.path.abspath(full_path)
    }

def save_architecture_description(result: dict, query: str):
    """Сохраняет описание архитектуры в markdown файл"""
    
    md_filepath = f"../generated-diagrams/{result['filename']}.md"
    
    markdown_content = f"""# {result['title']}

*Архитектура музыкальной стриминговой платформы*

## Описание архитектуры

Эта архитектура представляет собой современную облачную платформу для стриминга музыки, подобную Spotify, построенную на AWS.

### Компоненты:

**Фронтенд и CDN:**
- **CloudFront CDN** - глобальная сеть доставки контента для быстрой загрузки веб-приложения
- **S3 Web App** - статический веб-сайт, размещенный в S3

**API и микросервисы:**
- **API Gateway** - единая точка входа для всех API запросов
- **Authentication Lambda** - сервис аутентификации и авторизации пользователей
- **Music Catalog Lambda** - управление каталогом музыки и метаданными
- **Streaming Service Lambda** - обработка запросов на стриминг музыки
- **Playlist Manager Lambda** - управление плейлистами пользователей

**Хранилища данных:**
- **User Database (RDS)** - реляционная база данных для пользовательских данных
- **Music Metadata (DynamoDB)** - NoSQL база для метаданных треков и плейлистов
- **Music Files Storage (S3)** - хранилище аудиофайлов

### Преимущества архитектуры:

1. **Масштабируемость** - serverless компоненты автоматически масштабируются
2. **Производительность** - CDN обеспечивает быструю доставку контента
3. **Надежность** - распределенная архитектура с высокой доступностью
4. **Экономичность** - оплата только за использованные ресурсы

### Поток данных:

1. Пользователи обращаются к веб-приложению через CloudFront
2. API запросы проходят через API Gateway к соответствующим Lambda функциям
3. Аутентификация проверяется в RDS
4. Метаданные музыки хранятся в DynamoDB для быстрого доступа
5. Аудиофайлы стримятся напрямую из S3

---

**Исходный запрос:** {query}

**Файлы:**
- 📊 Диаграмма: `{result['filename']}.png`
- 📝 Документация: `{result['filename']}.md`

*Создано: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return md_filepath

if __name__ == "__main__":
    # Тестируем создание диаграммы
    user_query = "Спроектируй платформу для стриминга музыки как Spotify"
    
    print("🎵 Создание диаграммы музыкальной стриминговой платформы...")
    
    try:
        result = create_music_streaming_diagram(user_query)
        
        if result["success"]:
            print(f"✅ Диаграмма создана: {result['filepath']}")
            print(f"📁 Файл: {result['filename']}")
            print(f"📋 Заголовок: {result['title']}")
            print(f"🔗 Полный путь: {result['full_path']}")
            
            # Сохраняем описание архитектуры
            md_path = save_architecture_description(result, user_query)
            print(f"📝 Документация сохранена: {md_path}")
            
            print("\n✨ Готово! Проверьте папку generated-diagrams/")
        else:
            print("❌ Ошибка создания диаграммы")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()