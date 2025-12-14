# Руководство по созданию агентов Strands с MCP серверами

## Что такое MCP?

Model Context Protocol (MCP) - это открытый протокол, который стандартизирует способ предоставления контекста и инструментов для больших языковых моделей. Strands Agents SDK имеет встроенную поддержку MCP, что позволяет легко расширять возможности агентов через внешние сервисы.

## Быстрый старт

### 1. Установка зависимостей

```bash
# Основные пакеты
pip install strands-agents strands-agents-tools

# Для работы с MCP
pip install mcp

# Для конкретных провайдеров (опционально)
pip install 'strands-agents[anthropic]'  # Anthropic Claude
pip install 'strands-agents[openai]'     # OpenAI GPT
```

### 2. Настройка credentials

```bash
# Для Bedrock (по умолчанию)
export AWS_BEDROCK_API_KEY=your_bedrock_api_key

# Или для других провайдеров
export ANTHROPIC_API_KEY=your_anthropic_key
export OPENAI_API_KEY=your_openai_key
```

### 3. Создание простого агента с MCP

```python
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

# Создаем MCP клиент
mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",
        args=["awslabs.aws-documentation-mcp-server@latest"]
    )
))

# Используем контекстный менеджер
with mcp_client:
    # Получаем инструменты от MCP сервера
    tools = mcp_client.list_tools_sync()
    
    # Создаем агента
    agent = Agent(
        tools=tools,
        system_prompt="Вы эксперт по AWS. Используйте доступные инструменты для поиска информации."
    )
    
    # Тестируем
    response = agent("Что такое AWS Lambda?")
    print(response)
```

## Основные способы подключения к MCP

### 1. Stdio транспорт (для локальных серверов)

```python
# Подключение к MCP серверу через командную строку
mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",
        args=["package-name@latest"]
    )
))
```

### 2. HTTP транспорт (для удаленных серверов)

```python
from mcp.client.streamable_http import streamablehttp_client

# Подключение к HTTP MCP серверу
mcp_client = MCPClient(
    lambda: streamablehttp_client("http://localhost:8000/mcp")
)
```

### 3. Множественные MCP серверы

```python
# Несколько MCP серверов с префиксами
aws_client = MCPClient(
    lambda: stdio_client(StdioServerParameters(
        command="uvx", 
        args=["awslabs.aws-documentation-mcp-server@latest"]
    )),
    prefix="aws"
)

calc_client = MCPClient(
    lambda: streamablehttp_client("http://localhost:8001/mcp"),
    prefix="calc"
)

# Объединяем инструменты
with aws_client, calc_client:
    all_tools = aws_client.list_tools_sync() + calc_client.list_tools_sync()
    agent = Agent(tools=all_tools)
```

## Создание собственного MCP сервера

### Простой калькулятор

```python
from mcp.server import FastMCP

# Создаем MCP сервер
mcp = FastMCP("Calculator Server")

@mcp.tool(description="Сложить два числа")
def add(x: int, y: int) -> int:
    """Сложить два числа и вернуть результат."""
    return x + y

@mcp.tool(description="Умножить два числа")
def multiply(x: int, y: int) -> int:
    """Умножить два числа и вернуть результат."""
    return x * y

# Запускаем сервер
mcp.run(transport="streamable-http", port=8000)
```

### Использование с агентом

```python
# Подключаемся к нашему серверу
calc_client = MCPClient(
    lambda: streamablehttp_client("http://localhost:8000/mcp")
)

with calc_client:
    tools = calc_client.list_tools_sync()
    agent = Agent(
        tools=tools,
        system_prompt="Вы калькулятор. Используйте математические инструменты."
    )
    
    response = agent("Сколько будет 15 умножить на 23?")
    print(response)
```

## Продвинутые возможности

### 1. Фильтрация инструментов

```python
import re

# Загружаем только инструменты поиска
filtered_client = MCPClient(
    lambda: stdio_client(StdioServerParameters(...)),
    tool_filters={
        "allowed": [re.compile(r"^search.*")],  # Только search_*
        "rejected": ["deprecated_tool"]         # Исключаем устаревшие
    }
)
```

### 2. Элицитация (запрос подтверждения)

```python
from pydantic import BaseModel, Field

class ApprovalSchema(BaseModel):
    username: str = Field(description="Кто одобряет?")
    confirmed: bool = Field(description="Подтверждено?")

@mcp.tool()
async def delete_files(paths: list[str]) -> str:
    # Запрашиваем подтверждение
    result = await mcp.get_context().elicit(
        message=f"Удалить файлы: {paths}?",
        schema=ApprovalSchema
    )
    
    if result.action != "accept":
        return "Действие отклонено"
    
    # Выполняем удаление...
    return f"Файлы удалены пользователем {result.data.username}"
```

### 3. Прямой вызов инструментов

```python
# Вызов инструмента без агента
with mcp_client:
    result = mcp_client.call_tool_sync(
        tool_use_id="tool-123",
        name="search_documentation",
        arguments={"query": "Lambda", "max_results": 5}
    )
    print(result)
```

## Популярные MCP серверы

### AWS Documentation
```bash
uvx awslabs.aws-documentation-mcp-server@latest
```

### GitHub
```bash
uvx github-mcp-server@latest
```

### File System
```bash
uvx file-system-mcp-server@latest
```

### SQLite
```bash
uvx sqlite-mcp-server@latest
```

## Лучшие практики

### ✅ Рекомендуется:

1. **Всегда используйте контекстные менеджеры** (`with` statement) для управления соединениями
2. **Добавляйте префиксы** при использовании множественных серверов
3. **Фильтруйте инструменты** для избежания перегрузки агента
4. **Обрабатывайте ошибки** соединения и выполнения инструментов
5. **Используйте четкие описания** для инструментов - модели их читают
6. **Тестируйте инструменты** независимо перед добавлением к агенту

### ❌ Избегайте:

1. Использования MCP клиентов без контекстных менеджеров
2. Слишком большого количества инструментов в одном агенте
3. Неинформативных описаний инструментов
4. Игнорирования ошибок соединения
5. Жестко закодированных URL и параметров

## Устранение проблем

### Ошибка: "MCPClientInitializationError"
**Причина:** Использование MCP клиента вне контекстного менеджера
**Решение:** Всегда используйте `with mcp_client:`

### Ошибка: "Connection failed"
**Причина:** MCP сервер недоступен
**Решение:** 
- Проверьте, что сервер запущен
- Убедитесь в правильности URL/команды
- Проверьте сетевое соединение

### Ошибка: "Tool not found"
**Причина:** Инструмент не зарегистрирован на сервере
**Решение:**
- Проверьте список доступных инструментов: `mcp_client.list_tools_sync()`
- Убедитесь в правильности имени инструмента

### Ошибка: "uvx command not found"
**Причина:** Не установлен uv/uvx
**Решение:** `pip install uv`

## Примеры использования

Смотрите файлы в этой папке:
- `mcp_agent_guide.py` - Полное руководство с примерами
- `custom_mcp_server_example.py` - Создание собственных MCP серверов
- `mcp_working_example.py` - Рабочий пример

## Полезные ссылки

- [Официальная документация MCP](https://modelcontextprotocol.io)
- [Документация Strands Agents](https://strandsagents.com)
- [Репозиторий MCP серверов](https://github.com/modelcontextprotocol/servers)
- [Примеры MCP серверов](https://github.com/punkpeye/awesome-mcp-servers)