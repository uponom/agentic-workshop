from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.network import CloudFront, APIGateway
from diagrams.aws.database import Dynamodb
from diagrams.onprem.client import Users
import os

# Создаем папку для диаграмм
os.makedirs("generated-diagrams", exist_ok=True)

print("Создаем тестовую диаграмму...")

try:
    with Diagram("Test Music Streaming Architecture", show=False, filename="generated-diagrams/test_music_streaming", direction="TB"):
        users = Users("Music Listeners")
        cloudfront = CloudFront("CloudFront CDN")
        s3_music = S3("S3 Music Storage")
        api_gateway = APIGateway("API Gateway")
        lambda_streaming = Lambda("Streaming Service")
        dynamodb = Dynamodb("DynamoDB")
        
        users >> cloudfront >> s3_music
        users >> api_gateway >> lambda_streaming >> dynamodb
    
    print("✅ Диаграмма создана успешно!")
    print(f"📁 Файл: {os.path.abspath('generated-diagrams/test_music_streaming.png')}")
    
except Exception as e:
    print(f"❌ Ошибка создания диаграммы: {e}")
    import traceback
    traceback.print_exc()