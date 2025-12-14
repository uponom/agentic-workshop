#!/usr/bin/env python3
"""
Пример создания собственного MCP сервера для использования с агентами Strands
"""

# Установите зависимости:
# pip install mcp fastmcp

from mcp.server import FastMCP
from pydantic import BaseModel, Field
import asyncio
import json
import os
from datetime import datetime
import requests

# ===== СОЗДАНИЕ ПРОСТОГО MCP СЕРВЕРА =====

def create_simple_calculator_server():
    """
    Создание простого MCP сервера с калькулятором
    """
    
    # Создаем MCP сервер
    mcp = FastMCP("Calculator Server")
    
    @mcp.tool(description="Сложить два числа")
    def add(x: int, y: int) -> int:
        """Сложить два числа и вернуть результат."""
        return x + y
    
    @mcp.tool(description="Вычесть второе число из первого")
    def subtract(x: int, y: int) -> int:
        """Вычесть y из x и вернуть результат."""
        return x - y
    
    @mcp.tool(description="Умножить два числа")
    def multiply(x: int, y: int) -> int:
        """Умножить два числа и вернуть результат."""
        return x * y
    
    @mcp.tool(description="Разделить первое число на второе")
    def divide(x: float, y: float) -> float:
        """Разделить x на y и вернуть результат."""
        if y == 0:
            raise ValueError("Деление на ноль невозможно")
        return x / y
    
    return mcp

# ===== СОЗДАНИЕ ПРОДВИНУТОГО MCP СЕРВЕРА =====

def create_advanced_tools_server():
    """
    Создание MCP сервера с продвинутыми инструментами
    """
    
    mcp = FastMCP("Advanced Tools Server")
    
    @mcp.tool(description="Получить текущую погоду для города")
    def get_weather(city: str, api_key: str = None) -> str:
        """
        Получить информацию о погоде для указанного города.
        
        Args:
            city: Название города
            api_key: API ключ для сервиса погоды (опционально)
        """
        # Это пример - в реальности используйте настоящий API погоды
        return f"Погода в {city}: Солнечно, 22°C, влажность 65%"
    
    @mcp.tool(description="Сохранить текст в файл")
    def save_to_file(filename: str, content: str) -> str:
        """
        Сохранить текстовый контент в файл.
        
        Args:
            filename: Имя файла для сохранения
            content: Текстовый контент для сохранения
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Файл {filename} успешно сохранен"
        except Exception as e:
            return f"Ошибка при сохранении файла: {e}"
    
    @mcp.tool(description="Прочитать содержимое файла")
    def read_file(filename: str) -> str:
        """
        Прочитать содержимое текстового файла.
        
        Args:
            filename: Имя файла для чтения
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except FileNotFoundError:
            return f"Файл {filename} не найден"
        except Exception as e:
            return f"Ошибка при чтении файла: {e}"
    
    @mcp.tool(description="Получить список файлов в директории")
    def list_files(directory: str = ".") -> str:
        """
        Получить список файлов в указанной директории.
        
        Args:
            directory: Путь к директории (по умолчанию текущая)
        """
        try:
            files = os.listdir(directory)
            return f"Файлы в {directory}:\n" + "\n".join(files)
        except Exception as e:
            return f"Ошибка при получении списка файлов: {e}"
    
    @mcp.tool(description="Получить текущую дату и время")
    def get_current_time() -> str:
        """Получить текущую дату и время."""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    
    return mcp

# ===== MCP СЕРВЕР С ЭЛИЦИТАЦИЕЙ (ЗАПРОС ПОДТВЕРЖДЕНИЯ) =====

def create_server_with_elicitation():
    """
    Создание MCP сервера с функцией элицитации (запрос подтверждения у пользователя)
    """
    
    class ApprovalSchema(BaseModel):
        username: str = Field(description="Кто одобряет действие?")
        confirmed: bool = Field(description="Подтверждено ли действие?")
    
    mcp = FastMCP("Secure Operations Server")
    
    @mcp.tool(description="Удалить файлы (требует подтверждения)")
    async def delete_files(paths: list[str]) -> str:
        """
        Удалить указанные файлы после получения подтверждения пользователя.
        
        Args:
            paths: Список путей к файлам для удаления
        """
        # Запрашиваем подтверждение у пользователя
        result = await mcp.get_context().elicit(
            message=f"Вы действительно хотите удалить файлы: {', '.join(paths)}?",
            schema=ApprovalSchema
        )
        
        if result.action != "accept" or not result.data.confirmed:
            return f"Пользователь {result.data.username} отклонил удаление файлов"
        
        # Выполняем удаление (в реальности здесь был бы код удаления)
        deleted_files = []
        for path in paths:
            try:
                # os.remove(path)  # Раскомментируйте для реального удаления
                deleted_files.append(path)
            except Exception as e:
                return f"Ошибка при удалении {path}: {e}"
        
        return f"Пользователь {result.data.username} подтвердил удаление файлов: {', '.join(deleted_files)}"
    
    return mcp

# ===== ЗАПУСК MCP СЕРВЕРОВ =====

def run_calculator_server():
    """Запустить калькулятор MCP сервер"""
    server = create_simple_calculator_server()
    print("Запуск Calculator MCP Server на порту 8000...")
    server.run(transport="streamable-http", port=8000)

def run_advanced_server():
    """Запустить продвинутый MCP сервер"""
    server = create_advanced_tools_server()
    print("Запуск Advanced Tools MCP Server на порту 8001...")
    server.run(transport="streamable-http", port=8001)

def run_secure_server():
    """Запустить безопасный MCP сервер с элицитацией"""
    server = create_server_with_elicitation()
    print("Запуск Secure Operations MCP Server на порту 8002...")
    server.run(transport="streamable-http", port=8002)

# ===== КЛИЕНТ ДЛЯ ТЕСТИРОВАНИЯ MCP СЕРВЕРОВ =====

def test_mcp_servers():
    """
    Тестирование созданных MCP серверов с агентом Strands
    """
    from mcp.client.streamable_http import streamablehttp_client
    from strands import Agent
    from strands.tools.mcp import MCPClient
    
    print("=== Тестирование MCP серверов ===\n")
    
    # Тестируем калькулятор сервер
    print("1. Тестирование Calculator Server...")
    try:
        calc_client = MCPClient(
            lambda: streamablehttp_client("http://localhost:8000/mcp")
        )
        
        with calc_client:
            tools = calc_client.list_tools_sync()
            print(f"Найдено инструментов: {len(tools)}")
            
            agent = Agent(
                tools=tools,
                system_prompt="Вы калькулятор. Используйте доступные математические инструменты."
            )
            
            # Тестируем вычисления
            response = agent("Сколько будет 125 плюс 375?")
            print(f"Ответ: {response}\n")
            
    except Exception as e:
        print(f"Ошибка при тестировании Calculator Server: {e}\n")
    
    # Тестируем продвинутый сервер
    print("2. Тестирование Advanced Tools Server...")
    try:
        advanced_client = MCPClient(
            lambda: streamablehttp_client("http://localhost:8001/mcp")
        )
        
        with advanced_client:
            tools = advanced_client.list_tools_sync()
            print(f"Найдено инструментов: {len(tools)}")
            
            agent = Agent(
                tools=tools,
                system_prompt="Вы помощник с доступом к файловой системе и другим утилитам."
            )
            
            # Тестируем получение времени
            response = agent("Какое сейчас время?")
            print(f"Ответ: {response}\n")
            
    except Exception as e:
        print(f"Ошибка при тестировании Advanced Tools Server: {e}\n")

# ===== ГЛАВНАЯ ФУНКЦИЯ =====

def main():
    """
    Главная функция для демонстрации создания и использования MCP серверов
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("python custom_mcp_server_example.py [calculator|advanced|secure|test]")
        print()
        print("Команды:")
        print("  calculator - Запустить простой калькулятор MCP сервер")
        print("  advanced   - Запустить продвинутый MCP сервер")
        print("  secure     - Запустить безопасный MCP сервер с элицитацией")
        print("  test       - Протестировать MCP серверы с агентом Strands")
        return
    
    command = sys.argv[1].lower()
    
    if command == "calculator":
        run_calculator_server()
    elif command == "advanced":
        run_advanced_server()
    elif command == "secure":
        run_secure_server()
    elif command == "test":
        test_mcp_servers()
    else:
        print(f"Неизвестная команда: {command}")

if __name__ == "__main__":
    main()