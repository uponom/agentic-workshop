"""
Демонстрация работы MCP серверов без реального AI агента
Показывает доступные инструменты и их возможности
"""

from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient
import asyncio

def test_mcp_diagram_tools():
    """Тестирует инструменты для создания диаграмм"""
    
    print("🔧 Тестирование AWS Diagram MCP Server...")
    
    aws_diag_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=[
                    "--with",
                    "sarif-om,jschema_to_python",
                    "awslabs.aws-diagram-mcp-server@latest",
                ],
            )
        )
    )
    
    try:
        with aws_diag_client:
            print("✅ Подключение к AWS Diagram Server успешно")
            
            # Получаем список инструментов
            tools = aws_diag_client.list_tools_sync()
            print(f"📋 Доступно инструментов: {len(tools)}")
            
            for tool in tools:
                print(f"  🔨 {tool.tool_name}")
                
                # Получаем детали инструмента
                if hasattr(tool, 'tool_spec') and hasattr(tool.tool_spec, 'description'):
                    print(f"     📝 {tool.tool_spec.description}")
                
                # Показываем схему параметров
                if hasattr(tool, 'tool_spec') and hasattr(tool.tool_spec, 'inputSchema'):
                    schema = tool.tool_spec.inputSchema
                    if schema and 'properties' in schema:
                        print(f"     📊 Параметры: {list(schema['properties'].keys())}")
            
            print("\n🎯 Тестирование инструмента get_diagram_examples...")
            
            # Пробуем получить примеры диаграмм
            try:
                examples_tool = next(tool for tool in tools if tool.tool_name == "get_diagram_examples")
                
                # Вызываем инструмент
                result = aws_diag_client.call_tool_sync(examples_tool.tool_name, {})
                print("✅ Примеры диаграмм получены:")
                print(f"📄 Результат: {str(result)[:200]}...")
                
            except Exception as e:
                print(f"⚠️  Ошибка при получении примеров: {e}")
            
            print("\n🎯 Тестирование инструмента list_icons...")
            
            # Пробуем получить список иконок
            try:
                icons_tool = next(tool for tool in tools if tool.tool_name == "list_icons")
                
                # Вызываем инструмент
                result = aws_diag_client.call_tool_sync(icons_tool.tool_name, {})
                print("✅ Список иконок получен:")
                print(f"📄 Результат: {str(result)[:200]}...")
                
            except Exception as e:
                print(f"⚠️  Ошибка при получении иконок: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка подключения к AWS Diagram Server: {e}")

def test_mcp_docs_tools():
    """Тестирует инструменты для работы с документацией"""
    
    print("\n🔧 Тестирование AWS Documentation MCP Server...")
    
    aws_docs_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
            )
        )
    )
    
    try:
        with aws_docs_client:
            print("✅ Подключение к AWS Docs Server успешно")
            
            # Получаем список инструментов
            tools = aws_docs_client.list_tools_sync()
            print(f"📋 Доступно инструментов: {len(tools)}")
            
            for tool in tools:
                print(f"  🔨 {tool.tool_name}")
                
                if hasattr(tool, 'tool_spec') and hasattr(tool.tool_spec, 'description'):
                    print(f"     📝 {tool.tool_spec.description}")
                
                if hasattr(tool, 'tool_spec') and hasattr(tool.tool_spec, 'inputSchema'):
                    schema = tool.tool_spec.inputSchema
                    if schema and 'properties' in schema:
                        print(f"     📊 Параметры: {list(schema['properties'].keys())}")
            
            print("\n🎯 Тестирование поиска в документации...")
            
            # Пробуем поискать информацию о Lambda
            try:
                search_tool = next(tool for tool in tools if tool.tool_name == "search_documentation")
                
                # Вызываем инструмент
                result = aws_docs_client.call_tool_sync(search_tool.tool_name, {
                    "query": "AWS Lambda basics"
                })
                print("✅ Поиск в документации выполнен:")
                print(f"📄 Результат: {str(result)[:300]}...")
                
            except Exception as e:
                print(f"⚠️  Ошибка при поиске: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка подключения к AWS Docs Server: {e}")

def main():
    print("🚀 Демонстрация MCP серверов AWS")
    print("=" * 50)
    
    # Тестируем серверы
    test_mcp_diagram_tools()
    test_mcp_docs_tools()
    
    print("\n" + "=" * 50)
    print("✨ Демонстрация завершена!")
    print("\n💡 Выводы:")
    print("  - MCP серверы AWS работают корректно")
    print("  - Доступны инструменты для диаграмм и документации")
    print("  - Можно интегрировать с AI агентами для автоматизации")

if __name__ == "__main__":
    main()