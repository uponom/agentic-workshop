"""
Тест сохранения ответа агента в markdown файл
"""

from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.network import CloudFront
from diagrams.onprem.client import Users
import os

# Создаем папку для диаграмм
os.makedirs("generated-diagrams", exist_ok=True)

def create_test_diagram():
    """Создает тестовую диаграмму"""
    
    filename = "test_architecture"
    filepath = f"generated-diagrams/{filename}"
    
    with Diagram("Test Architecture", show=False, filename=filepath, direction="TB"):
        users = Users("Website Visitors")
        cloudfront = CloudFront("CloudFront CDN")
        s3 = S3("S3 Static Website")
        lambda_api = Lambda("Lambda API")
        
        users >> cloudfront >> s3
        users >> cloudfront >> lambda_api
    
    return filename

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

def main():
    print("🧪 Тест сохранения ответа агента")
    print("=" * 40)
    
    # Создаем диаграмму
    print("🎨 Создание тестовой диаграммы...")
    filename = create_test_diagram()
    print(f"✅ Диаграмма создана: {filename}.png")
    
    # Симулируем ответ агента
    mock_response = """## 🏗️ Test Architecture Analysis

### **Архитектурные компоненты:**

1. **Amazon S3** - Хранилище статических файлов веб-сайта
   - HTML, CSS, JavaScript файлы
   - Изображения и медиа контент
   - Настроен для статического веб-хостинга

2. **Amazon CloudFront** - Content Delivery Network (CDN)
   - Глобальное распространение контента
   - Кэширование на edge-локациях
   - Снижение задержки для пользователей

3. **AWS Lambda** - Serverless вычисления
   - Обработка API запросов
   - Динамическая генерация контента
   - Интеграция с другими AWS сервисами

### **🔄 Поток данных:**

```
Пользователи → CloudFront → S3 (статический контент)
                    ↓
                Lambda (API запросы)
```

### **✅ Преимущества архитектуры:**

- **Масштабируемость**: Автоматическое масштабирование всех компонентов
- **Производительность**: Низкая задержка благодаря CloudFront
- **Надежность**: Высокая доступность AWS сервисов
- **Экономичность**: Оплата только за использование

### **🛡️ Безопасность:**

- HTTPS по умолчанию через CloudFront
- IAM роли для Lambda функций
- S3 bucket policies для контроля доступа

### **📊 Best Practices:**

1. Включите версионирование S3 для резервного копирования
2. Настройте CloudWatch мониторинг для Lambda
3. Используйте CloudFront для кэширования API ответов
4. Реализуйте proper error handling в Lambda функциях

Эта архитектура обеспечивает современное, масштабируемое и экономичное решение для веб-приложений."""

    # Сохраняем ответ
    print("\n💾 Сохранение документации...")
    save_agent_response(
        filename=filename,
        response=mock_response,
        title="Test Architecture - AWS Solutions Analysis"
    )
    
    # Проверяем результат
    print("\n📋 Проверка результатов:")
    diagram_path = f"generated-diagrams/{filename}.png"
    doc_path = f"generated-diagrams/{filename}.md"
    
    if os.path.exists(diagram_path):
        print(f"✅ Диаграмма: {diagram_path}")
    else:
        print(f"❌ Диаграмма не найдена: {diagram_path}")
    
    if os.path.exists(doc_path):
        print(f"✅ Документация: {doc_path}")
        
        # Показываем размер файла
        size = os.path.getsize(doc_path)
        print(f"   Размер: {size} байт")
        
        # Показываем первые строки
        with open(doc_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:5]
            print(f"   Первые строки:")
            for line in lines:
                print(f"     {line.strip()}")
    else:
        print(f"❌ Документация не найдена: {doc_path}")
    
    print("\n✨ Тест завершен!")

if __name__ == "__main__":
    main()