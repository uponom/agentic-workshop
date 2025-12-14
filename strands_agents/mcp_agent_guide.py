#!/usr/bin/env python3
"""
Полное руководство по созданию агента Strands с подключением к MCP серверу
"""

# Сначала установите необходимые пакеты:
# pip install strands-agents strands-agents-tools
# pip install 'strands-agents[anthropic]'  # если используете Anthropic
# pip install mcp

import os
from mcp import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models import BedrockModel

# ===== СПОСОБ 1: Подключение к существующему MCP серверу через stdio =====

def create_mcp_agent_with_stdio():
    """
    Создание агента с подключением к MCP серверу через stdio транспорт
    Подходит для локальных MCP серверов и утилит командной строки
    """
    
    # Создаем MCP клиент с stdio транспортом
    # Пример с AWS Documentation MCP Server
    mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx",  # Используем uvx для запуска MCP сервера
            args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    ))
    
    # Используем контекстный менеджер для управления жизненным циклом соединения
    with mcp_client:
        # Получаем список доступных инструментов от MCP сервера
        tools = mcp_client.list_tools_sync()
        print(f"Найдено {len(tools)} инструментов от MCP сервера")
        
        # Создаем агента с инструментами от MCP сервера
        agent = Agent(
            tools=tools,
            system_prompt="Вы эксперт по AWS. Используйте доступные инструменты для поиска информации в документации AWS."
        )
        
        # Тестируем агента
        response = agent("Что такое AWS Lambda и как его использовать?")
        print("Ответ агента:", response)
        
        return agent

# ===== СПОСОБ 2: Подключение через HTTP транспорт =====

def create_mcp_agent_with_http():
    """
    Создание агента с подключением к MCP серверу через HTTP
    Подходит для удаленных MCP серверов
    """
    
    # Создаем MCP клиент с HTTP транспортом
    mcp_client = MCPClient(
        lambda: streamablehttp_client("http://localhost:8000/mcp")
    )
    
    with mcp_client:
        tools = mcp_client.list_tools_sync()
        
        # Создаем агента с кастомной моделью
        model = BedrockModel(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            temperature=0.7,
            max_tokens=2048
        )
        
        agent = Agent(
            model=model,
            tools=tools,
            system_prompt="Вы полезный ассистент с доступом к внешним инструментам."
        )
        
        return agent

# ===== СПОСОБ 3: Множественные MCP серверы =====

def create_multi_mcp_agent():
    """
    Создание агента с подключением к нескольким MCP серверам
    """
    
    # Первый MCP сервер - AWS документация
    aws_client = MCPClient(
        lambda: stdio_client(StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"]
        )),
        prefix="aws"  # Префикс для избежания конфликтов имен
    )
    
    # Второй MCP сервер - калькулятор (пример)
    calc_client = MCPClient(
        lambda: streamablehttp_client("http://localhost:8001/mcp"),
        prefix="calc"
    )
    
    # Используем оба клиента
    with aws_client, calc_client:
        # Объединяем инструменты от обоих серверов
        aws_tools = aws_client.list_tools_sync()
        calc_tools = calc_client.list_tools_sync()
        all_tools = aws_tools + calc_tools
        
        print(f"Всего инструментов: {len(all_tools)}")
        
        agent = Agent(
            tools=all_tools,
            system_prompt="""Вы универсальный ассистент с доступом к:
            1. Документации AWS (инструменты с префиксом aws_)
            2. Калькулятору (инструменты с префиксом calc_)
            
            Используйте подходящие инструменты для ответа на вопросы пользователя."""
        )
        
        return agent

# ===== СПОСОБ 4: Фильтрация инструментов =====

def create_filtered_mcp_agent():
    """
    Создание агента с фильтрацией инструментов MCP сервера
    """
    import re
    
    # Создаем клиент с фильтрацией инструментов
    mcp_client = MCPClient(
        lambda: stdio_client(StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"]
        )),
        tool_filters={
            "allowed": [re.compile(r"^search.*")],  # Только инструменты поиска
            "rejected": ["deprecated_tool"]  # Исключаем устаревшие инструменты
        }
    )
    
    with mcp_client:
        tools = mcp_client.list_tools_sync()
        
        agent = Agent(
            tools=tools,
            system_prompt="Вы специализируетесь на поиске информации в документации."
        )
        
        return agent

# ===== СПОСОБ 5: Экспериментальный управляемый режим =====

def create_managed_mcp_agent():
    """
    Экспериментальный способ с автоматическим управлением жизненным циклом
    ВНИМАНИЕ: Это экспериментальная функция!
    """
    
    mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    ))
    
    # Прямое использование без контекстного менеджера
    # Соединение управляется автоматически
    agent = Agent(
        tools=[mcp_client],  # Передаем клиент напрямую
        system_prompt="Вы эксперт по AWS документации."
    )
    
    return agent

# ===== ПРЯМОЙ ВЫЗОВ ИНСТРУМЕНТОВ =====

def direct_tool_invocation_example():
    """
    Пример прямого вызова инструментов MCP без агента
    """
    
    mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    ))
    
    with mcp_client:
        # Прямой вызов инструмента
        result = mcp_client.call_tool_sync(
            tool_use_id="tool-123",
            name="search_documentation",
            arguments={"query": "Lambda functions", "max_results": 5}
        )
        
        print("Результат прямого вызова:", result)
        return result

# ===== ОБРАБОТКА ОШИБОК И ЛУЧШИЕ ПРАКТИКИ =====

def robust_mcp_agent():
    """
    Создание надежного агента с обработкой ошибок
    """
    
    try:
        mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.aws-documentation-mcp-server@latest"]
            )
        ))
        
        with mcp_client:
            # Проверяем доступность инструментов
            tools = mcp_client.list_tools_sync()
            
            if not tools:
                print("Предупреждение: MCP сервер не предоставил инструментов")
                return None
            
            print(f"Успешно подключились к MCP серверу. Доступно инструментов: {len(tools)}")
            
            # Выводим информацию о доступных инструментах
            for tool in tools:
                print(f"- {tool.name}: {tool.description}")
            
            agent = Agent(
                tools=tools,
                system_prompt="""Вы профессиональный ассистент с доступом к внешним инструментам.
                
                Правила работы:
                1. Всегда используйте доступные инструменты для получения актуальной информации
                2. Если инструмент возвращает ошибку, объясните это пользователю
                3. Предоставляйте подробные и точные ответы
                4. Ссылайтесь на источники информации когда это возможно
                """
            )
            
            return agent
            
    except Exception as e:
        print(f"Ошибка при создании MCP агента: {e}")
        print("Проверьте:")
        print("1. Установлен ли uvx: pip install uv")
        print("2. Доступен ли интернет для загрузки MCP сервера")
        print("3. Правильно ли указана команда и аргументы")
        return None

# ===== ОСНОВНАЯ ФУНКЦИЯ ДЛЯ ТЕСТИРОВАНИЯ =====

def main():
    """
    Основная функция для демонстрации различных способов создания MCP агентов
    """
    
    print("=== Создание агента Strands с MCP сервером ===\n")
    
    # Проверяем переменные окружения
    if not os.getenv("AWS_BEDROCK_API_KEY") and not os.getenv("AWS_ACCESS_KEY_ID"):
        print("⚠️  Предупреждение: Не найдены AWS credentials")
        print("Установите AWS_BEDROCK_API_KEY или настройте AWS credentials")
        print("export AWS_BEDROCK_API_KEY=your_key")
        print()
    
    # Тестируем надежный способ создания агента
    print("1. Создание надежного MCP агента...")
    agent = robust_mcp_agent()
    
    if agent:
        print("✅ Агент успешно создан!")
        
        # Тестируем агента
        test_queries = [
            "Что такое AWS Lambda?",
            "Как создать EC2 инстанс?",
            "Расскажи о AWS S3"
        ]
        
        for query in test_queries:
            print(f"\n🤖 Вопрос: {query}")
            try:
                response = agent(query)
                print(f"📝 Ответ: {response[:200]}...")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    else:
        print("❌ Не удалось создать агента")

if __name__ == "__main__":
    main()