from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient

def test_mcp_servers():
    """Тестирует доступность и инструменты MCP серверов"""
    
    print("=== Тестирование AWS Documentation MCP Server ===")
    aws_docs_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
            )
        )
    )
    
    print("=== Тестирование AWS Diagram MCP Server ===")
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
        with aws_docs_client:
            print("\n--- AWS Docs Client подключен ---")
            docs_tools = aws_docs_client.list_tools_sync()
            print(f"Количество инструментов: {len(docs_tools)}")
            for i, tool in enumerate(docs_tools):
                print(f"  - Инструмент {i+1}: {tool.tool_name}")
                if hasattr(tool, 'tool_spec'):
                    spec = tool.tool_spec
                    if hasattr(spec, 'description'):
                        print(f"    Описание: {spec.description}")
                    if hasattr(spec, 'inputSchema'):
                        print(f"    Схема: {spec.inputSchema}")
                
    except Exception as e:
        print(f"Ошибка с AWS Docs Client: {e}")
    
    try:
        with aws_diag_client:
            print("\n--- AWS Diagram Client подключен ---")
            diag_tools = aws_diag_client.list_tools_sync()
            print(f"Количество инструментов: {len(diag_tools)}")
            for i, tool in enumerate(diag_tools):
                print(f"  - Инструмент {i+1}: {tool.tool_name}")
                if hasattr(tool, 'tool_spec'):
                    spec = tool.tool_spec
                    if hasattr(spec, 'description'):
                        print(f"    Описание: {spec.description}")
                    if hasattr(spec, 'inputSchema'):
                        print(f"    Схема: {spec.inputSchema}")
                    
    except Exception as e:
        print(f"Ошибка с AWS Diagram Client: {e}")

if __name__ == "__main__":
    test_mcp_servers()