# Объяснение файла mcp_docs_diag.py

## Обзор
Файл `mcp_docs_diag.py` демонстрирует создание AWS Solutions Architect агента с использованием:
- **Strands Agent SDK** - для создания AI агентов
- **MCP (Model Context Protocol)** - для подключения внешних инструментов
- **AWS Bedrock** - для работы с Claude модель

## Компоненты файла

### 1. Импорты
```python
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
```

- `mcp` - библиотека для работы с Model Context Protocol
- `strands` - SDK для создания AI агентов
- `BedrockModel` - модель для работы с AWS Bedrock
- `MCPClient` - клиент для подключения к MCP серверам

### 2. MCP клиенты

#### AWS Documentation клиент
```python
aws_docs_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    )
)
```

**Что делает:**
- Создает клиент для доступа к документации AWS
- Использует `uvx` (Python package runner) для запуска MCP сервера
- Подключается к официальному серверу документации AWS от awslabs
- Предоставляет инструменты: `read_documentation`, `search_documentation`, `recommend`

#### AWS Diagram клиент
```python
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
```

**Что делает:**
- Создает клиент для генерации диаграмм AWS архитектуры
- Включает дополнительные зависимости `sarif-om` и `jschema_to_python`
- Предоставляет инструменты: `generate_diagram`, `get_diagram_examples`, `list_icons`

### 3. Модель Bedrock
```python
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    temperature=0.7,
)
```

**Параметры:**
- `model_id` - конкретная версия Claude Sonnet через AWS Bedrock
- `temperature=0.7` - баланс между креативностью и точностью

### 4. Системный промпт
```python
SYSTEM_PROMPT = """
You are an expert AWS Certified Solutions Architect...
"""
```

**Определяет роль агента:**
- Эксперт AWS Solutions Architect
- Может консультировать по best practices AWS
- Умеет искать в документации AWS
- Создает диаграммы архитектуры
- Сохраняет результаты в папку `generated-diagrams`

### 5. Создание и запуск агента
```python
with aws_diag_client, aws_docs_client:
    all_tools = aws_diag_client.list_tools_sync() + aws_docs_client.list_tools_sync()
    agent = Agent(tools=all_tools, model=bedrock_model, system_prompt=SYSTEM_PROMPT)
    
    response = agent(
        "Get the documentation for AWS Lambda then create a diagram of a website that uses AWS Lambda for a static website hosted on S3"
    )
```

**Процесс:**
1. **Context manager** - управляет соединениями с MCP серверами
2. **Объединение инструментов** - собирает все доступные инструменты из обоих клиентов
3. **Создание агента** - инициализирует агента с инструментами, моделью и системным промптом
4. **Выполнение задачи** - отправляет запрос агенту

## Доступные инструменты

### Документация AWS (3 инструмента):
- `read_documentation` - читает конкретные разделы документации
- `search_documentation` - ищет информацию в документации
- `recommend` - дает рекомендации по AWS сервисам

### Диаграммы AWS (3 инструмента):
- `generate_diagram` - создает диаграммы архитектуры
- `get_diagram_examples` - показывает примеры диаграмм
- `list_icons` - показывает доступные иконки AWS сервисов

## Проблемы и решения

### 1. Проблема с генерацией диаграмм
**Причины:**
- Неправильные параметры для `generate_diagram`
- Включение import statements в код диаграммы
- Проблемы с путями к файлам
- Системные зависимости (Graphviz)

**Решения:**
- Использовать простой код без imports
- Указывать правильные пути для сохранения
- Установить Graphviz системно

### 2. Проблема с AWS credentials
**Причина:** Отсутствуют AWS credentials для Bedrock

**Решения:**
- Настроить AWS CLI: `aws configure`
- Использовать Bedrock API key: `$env:AWS_BEDROCK_API_KEY="key"`
- Переключиться на Anthropic API: `$env:ANTHROPIC_API_KEY="key"`

### 3. Проблема с MCP серверами
**Причины:**
- Не установлен `uvx`
- Проблемы с сетевым подключением
- Неправильные версии зависимостей

**Решения:**
- Установить uv/uvx: `pip install uv`
- Проверить интернет соединение
- Обновить зависимости

## Альтернативные подходы

### 1. Использование Anthropic вместо Bedrock
```python
from strands.models import AnthropicModel

anthropic_model = AnthropicModel(
    model="claude-3-5-sonnet-20241022",
    temperature=0.3,
)
```

### 2. Создание диаграмм без MCP
```python
from diagrams import Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3

with Diagram("Architecture", show=False):
    s3 = S3("S3 Bucket")
    lambda_func = Lambda("Lambda")
    s3 >> lambda_func
```

## Заключение

Файл `mcp_docs_diag.py` демонстрирует мощную интеграцию между:
- AI агентами (Strands)
- Внешними инструментами (MCP)
- AWS сервисами (Bedrock, документация)
- Генерацией диаграмм

Это позволяет создать агента, который может одновременно:
- Искать информацию в документации AWS
- Генерировать архитектурные диаграммы
- Давать экспертные рекомендации по AWS
- Автоматизировать процесс проектирования решений