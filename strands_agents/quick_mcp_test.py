#!/usr/bin/env python3
"""
Быстрый тест агента Strands с MCP сервером
Этот файл можно запустить сразу для проверки работоспособности
"""

import os
import sys
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

def check_prerequisites():
    """Проверка необходимых условий"""
    print("🔍 Проверка предварительных условий...")
    
    # Проверяем AWS credentials
    has_bedrock_key = bool(os.getenv("AWS_BEDROCK_API_KEY"))
    has_aws_creds = bool(os.getenv("AWS_ACCESS_KEY_ID"))
    
    if not (has_bedrock_key or has_aws_creds):
        print("⚠️  Предупреждение: Не найдены AWS credentials")
        print("   Установите одну из переменных:")
        print("   export AWS_BEDROCK_API_KEY=your_key")
        print("   или настройте AWS credentials: aws configure")
        print()
    else:
        print("✅ AWS credentials найдены")
    
    # Проверяем доступность uvx
    try:
        import subprocess
        result = subprocess.run(["uvx", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ uvx доступен")
        else:
            print("❌ uvx не работает корректно")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ uvx не найден. Установите: pip install uv")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке uvx: {e}")
        return False
    
    return True

def create_simple_mcp_agent():
    """Создание простого MCP агента для тестирования"""
    
    print("🤖 Создание MCP агента...")
    
    try:
        # Создаем MCP клиент с AWS Documentation сервером
        mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.aws-documentation-mcp-server@latest"]
            )
        ))
        
        print("🔗 Подключение к MCP серверу...")
        
        # Используем контекстный менеджер
        with mcp_client:
            # Получаем список инструментов
            print("📋 Получение списка инструментов...")
            tools = mcp_client.list_tools_sync()
            
            if not tools:
                print("❌ MCP сервер не предоставил инструментов")
                return None
            
            print(f"✅ Найдено {len(tools)} инструментов:")
            for i, tool in enumerate(tools[:3], 1):  # Показываем первые 3
                print(f"   {i}. {tool.name}: {tool.description[:60]}...")
            
            if len(tools) > 3:
                print(f"   ... и еще {len(tools) - 3} инструментов")
            
            # Создаем агента
            print("🧠 Создание агента...")
            agent = Agent(
                tools=tools,
                system_prompt="""Вы эксперт по AWS с доступом к официальной документации.
                
                Используйте доступные инструменты для поиска актуальной информации 
                в документации AWS. Предоставляйте точные и подробные ответы.
                """
            )
            
            print("✅ Агент успешно создан!")
            return agent
            
    except Exception as e:
        print(f"❌ Ошибка при создании агента: {e}")
        print("\nВозможные причины:")
        print("1. Нет интернет-соединения для загрузки MCP сервера")
        print("2. Проблемы с AWS credentials")
        print("3. uvx не установлен или работает некорректно")
        return None

def test_agent(agent):
    """Тестирование агента с различными запросами"""
    
    print("\n🧪 Тестирование агента...")
    
    test_queries = [
        "Что такое AWS Lambda?",
        "Как создать S3 bucket?",
        "Расскажи про Amazon EC2"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Тест {i}: {query}")
        print("🤔 Агент думает...")
        
        try:
            response = agent(query)
            
            # Обрезаем длинный ответ для читаемости
            if len(response) > 300:
                display_response = response[:300] + "..."
            else:
                display_response = response
            
            print(f"💬 Ответ: {display_response}")
            
        except Exception as e:
            print(f"❌ Ошибка при выполнении запроса: {e}")
    
    print("\n✅ Тестирование завершено!")

def interactive_mode(agent):
    """Интерактивный режим для общения с агентом"""
    
    print("\n🎯 Интерактивный режим")
    print("Введите ваши вопросы об AWS (или 'quit' для выхода):")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n👤 Вы: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'выход']:
                print("👋 До свидания!")
                break
            
            if not user_input:
                continue
            
            print("🤔 Агент думает...")
            response = agent(user_input)
            print(f"🤖 Агент: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def main():
    """Главная функция"""
    
    print("=" * 60)
    print("🚀 Быстрый тест агента Strands с MCP сервером")
    print("=" * 60)
    
    # Проверяем предварительные условия
    if not check_prerequisites():
        print("\n❌ Не выполнены предварительные условия")
        print("Установите необходимые зависимости и повторите попытку")
        sys.exit(1)
    
    # Создаем агента
    agent = create_simple_mcp_agent()
    
    if not agent:
        print("\n❌ Не удалось создать агента")
        sys.exit(1)
    
    # Выбираем режим работы
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Интерактивный режим
        interactive_mode(agent)
    else:
        # Автоматическое тестирование
        test_agent(agent)
        
        print("\n" + "=" * 60)
        print("🎉 Тест завершен успешно!")
        print("Для интерактивного режима запустите:")
        print("python quick_mcp_test.py --interactive")
        print("=" * 60)

if __name__ == "__main__":
    main()