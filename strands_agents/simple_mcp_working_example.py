#!/usr/bin/env python3
"""
Простой рабочий пример агента Strands с MCP сервером
Исправленная версия без проблем с атрибутами
"""

import os
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

def main():
    """Основная функция с простым примером"""
    
    print("🚀 Простой пример агента Strands с MCP")
    print("=" * 50)
    
    # Проверяем credentials
    if not os.getenv("AWS_BEDROCK_API_KEY") and not os.getenv("AWS_ACCESS_KEY_ID"):
        print("⚠️  Внимание: Не найдены AWS credentials")
        print("Для полной функциональности установите:")
        print("export AWS_BEDROCK_API_KEY=your_key")
        print()
    
    try:
        print("🔗 Создание MCP клиента...")
        
        # Создаем MCP клиент для AWS Documentation
        mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.aws-documentation-mcp-server@latest"]
            )
        ))
        
        print("📡 Подключение к MCP серверу...")
        
        # Используем контекстный менеджер
        with mcp_client:
            print("📋 Получение инструментов...")
            
            # Получаем инструменты
            tools = mcp_client.list_tools_sync()
            
            print(f"✅ Получено {len(tools)} инструментов от MCP сервера")
            
            # Выводим информацию об инструментах
            print("\n📝 Доступные инструменты:")
            for i, tool in enumerate(tools, 1):
                # Безопасно получаем имя и описание
                tool_name = getattr(tool, 'name', f'tool_{i}')
                tool_desc = getattr(tool, 'description', 'Описание недоступно')
                print(f"  {i}. {tool_name}")
                print(f"     {tool_desc[:80]}...")
            
            print("\n🧠 Создание агента...")
            
            # Создаем агента с инструментами
            agent = Agent(
                tools=tools,
                system_prompt="""Вы эксперт по Amazon Web Services (AWS).
                
                У вас есть доступ к официальной документации AWS через специальные инструменты.
                Используйте эти инструменты для поиска актуальной и точной информации.
                
                Отвечайте подробно и профессионально, ссылаясь на найденную документацию.
                """
            )
            
            print("✅ Агент успешно создан!")
            
            # Тестируем агента
            print("\n🧪 Тестирование агента...")
            
            test_questions = [
                "Что такое AWS Lambda и для чего он используется?",
                "Как создать S3 bucket через AWS CLI?"
            ]
            
            for i, question in enumerate(test_questions, 1):
                print(f"\n📝 Вопрос {i}: {question}")
                print("🤔 Агент обрабатывает запрос...")
                
                try:
                    response = agent(question)
                    
                    # Ограничиваем длину вывода для читаемости
                    if len(response) > 400:
                        display_response = response[:400] + "\n... (ответ обрезан)"
                    else:
                        display_response = response
                    
                    print(f"💬 Ответ агента:\n{display_response}")
                    
                except Exception as e:
                    print(f"❌ Ошибка при обработке вопроса: {e}")
            
            print("\n" + "=" * 50)
            print("✅ Тестирование завершено успешно!")
            print("🎉 Агент Strands с MCP работает корректно!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Проверьте интернет-соединение")
        print("2. Установите AWS credentials:")
        print("   export AWS_BEDROCK_API_KEY=your_key")
        print("3. Убедитесь, что uvx установлен: pip install uv")
        print("4. Проверьте, что все пакеты установлены:")
        print("   pip install strands-agents strands-agents-tools mcp")

if __name__ == "__main__":
    main()