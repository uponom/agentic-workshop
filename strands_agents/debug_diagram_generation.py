"""
Отладка генерации диаграмм через MCP сервер
Проверяем параметры и схему инструмента generate_diagram
"""

from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient
import json

def debug_diagram_tools():
    """Детальная отладка инструментов диаграмм"""
    
    print("🔧 Отладка AWS Diagram MCP Server...")
    
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
            tools = aws_diag_client.list_tools_sync()
            
            # Найдем инструмент generate_diagram
            generate_tool = None
            for tool in tools:
                if tool.tool_name == "generate_diagram":
                    generate_tool = tool
                    break
            
            if not generate_tool:
                print("❌ Инструмент generate_diagram не найден!")
                return
            
            print("✅ Инструмент generate_diagram найден")
            print(f"📋 Имя: {generate_tool.tool_name}")
            
            # Проверяем схему параметров
            if hasattr(generate_tool, 'tool_spec'):
                spec = generate_tool.tool_spec
                print(f"📝 Описание: {getattr(spec, 'description', 'Нет описания')}")
                
                if hasattr(spec, 'inputSchema'):
                    schema = spec.inputSchema
                    print("📊 Схема параметров:")
                    print(json.dumps(schema, indent=2, ensure_ascii=False))
                    
                    # Анализируем требуемые параметры
                    if 'properties' in schema:
                        print("\n🔍 Анализ параметров:")
                        for param_name, param_info in schema['properties'].items():
                            required = param_name in schema.get('required', [])
                            param_type = param_info.get('type', 'unknown')
                            description = param_info.get('description', 'Нет описания')
                            
                            print(f"  • {param_name} ({param_type}) {'[ОБЯЗАТЕЛЬНЫЙ]' if required else '[ОПЦИОНАЛЬНЫЙ]'}")
                            print(f"    {description}")
                            
                            # Если есть enum значения
                            if 'enum' in param_info:
                                print(f"    Возможные значения: {param_info['enum']}")
            
            # Попробуем получить примеры
            print("\n🎯 Получение примеров диаграмм...")
            try:
                # Исправляем вызов - сначала параметры, потом имя инструмента
                examples_result = aws_diag_client.call_tool_sync("examples_001", "get_diagram_examples", {})
                print("✅ Примеры получены:")
                
                if hasattr(examples_result, 'content') and examples_result.content:
                    for item in examples_result.content:
                        if hasattr(item, 'text'):
                            # Показываем первые 500 символов примеров
                            example_text = item.text[:500]
                            print(f"📄 Пример: {example_text}...")
                            
                            # Ищем паттерны в примерах
                            if 'filename' in example_text.lower():
                                print("   💡 Найден параметр filename в примере")
                            if 'code' in example_text.lower():
                                print("   💡 Найден параметр code в примере")
                            if 'workspace' in example_text.lower():
                                print("   💡 Найден параметр workspace в примере")
                
            except Exception as e:
                print(f"⚠️ Ошибка при получении примеров: {e}")
            
            # Тестируем простой вызов generate_diagram
            print("\n🧪 Тестирование простого вызова generate_diagram...")
            
            # Попробуем разные варианты параметров
            test_cases = [
                {
                    "name": "Минимальные параметры",
                    "params": {
                        "code": """
with Diagram("Simple Architecture", show=False):
    s3 = S3("S3 Bucket")
    lambda_func = Lambda("Lambda Function")
    s3 >> lambda_func
"""
                    }
                },
                {
                    "name": "С filename",
                    "params": {
                        "code": """
with Diagram("Simple Architecture", show=False, filename="test_diagram"):
    s3 = S3("S3 Bucket")
    lambda_func = Lambda("Lambda Function")
    s3 >> lambda_func
""",
                        "filename": "test_diagram"
                    }
                },
                {
                    "name": "С workspace_dir",
                    "params": {
                        "code": """
with Diagram("Simple Architecture", show=False):
    s3 = S3("S3 Bucket")
    lambda_func = Lambda("Lambda Function")
    s3 >> lambda_func
""",
                        "workspace_dir": "."
                    }
                }
            ]
            
            for test_case in test_cases:
                print(f"\n🔬 Тест: {test_case['name']}")
                try:
                    result = aws_diag_client.call_tool_sync(f"test_{test_case['name']}", "generate_diagram", test_case['params'])
                    print(f"📄 Полный результат:")
                    if hasattr(result, 'content') and result.content:
                        for item in result.content:
                            if hasattr(item, 'text'):
                                print(f"   {item.text}")
                    else:
                        print(f"   {str(result)}")
                    
                    # Проверяем статус
                    if hasattr(result, 'status') and result.status == 'success':
                        print("✅ Инструмент вызван успешно!")
                        break
                    else:
                        print("⚠️ Есть ошибки в выполнении")
                    
                except Exception as e:
                    print(f"❌ Ошибка: {str(e)[:200]}...")
                    continue
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

def main():
    print("🚀 Отладка генерации диаграмм MCP")
    print("=" * 50)
    debug_diagram_tools()
    print("\n" + "=" * 50)
    print("✨ Отладка завершена!")

if __name__ == "__main__":
    main()