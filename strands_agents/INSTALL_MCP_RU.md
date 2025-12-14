# Инструкция по установке и настройке MCP с агентами Strands

## Шаг 1: Установка зависимостей

### Основные пакеты

```bash
# Установка Strands Agents SDK
pip install strands-agents strands-agents-tools

# Установка MCP
pip install mcp

# Установка uv/uvx для запуска MCP серверов
pip install uv
```

### Провайдеры моделей (выберите нужный)

```bash
# Для Amazon Bedrock (по умолчанию, уже включен)
# Дополнительная установка не требуется

# Для Anthropic Claude
pip install 'strands-agents[anthropic]'

# Для OpenAI GPT
pip install 'strands-agents[openai]'

# Для Google Gemini
pip install 'strands-agents[gemini]'

# Для Meta Llama
pip install 'strands-agents[llamaapi]'
```

## Шаг 2: Настройка credentials

### Вариант A: Amazon Bedrock (рекомендуется для начала)

#### Способ 1: API ключ Bedrock (для разработки)
```bash
# 1. Откройте Bedrock Console: https://console.aws.amazon.com/bedrock
# 2. Перейдите в раздел "API keys"
# 3. Создайте новый API ключ (срок действия 30 дней)
# 4. Скопируйте ключ и установите переменную окружения:

export AWS_BEDROCK_API_KEY=your_bedrock_api_key_here
```

#### Способ 2: AWS credentials (для продакшена)
```bash
# Установите AWS CLI
pip install awscli

# Настройте credentials
aws configure

# Или установите переменные окружения
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2
```

#### Включение доступа к моделям в Bedrock
1. Откройте [Bedrock Console](https://console.aws.amazon.com/bedrock)
2. В левом меню выберите "Model access"
3. Нажмите "Manage model access"
4. Включите нужные модели (например, Claude 3.5 Sonnet)
5. Подождите несколько минут для активации

### Вариант B: Другие провайдеры

#### Anthropic Claude
```bash
# 1. Получите API ключ: https://console.anthropic.com/
# 2. Установите переменную окружения:
export ANTHROPIC_API_KEY=your_anthropic_key_here
```

#### OpenAI GPT
```bash
# 1. Получите API ключ: https://platform.openai.com/api-keys
# 2. Установите переменную окружения:
export OPENAI_API_KEY=your_openai_key_here
```

#### Google Gemini
```bash
# 1. Получите API ключ: https://aistudio.google.com/apikey
# 2. Установите переменную окружения:
export GOOGLE_API_KEY=your_google_key_here
```

## Шаг 3: Проверка установки

### Быстрая проверка
```bash
# Проверьте установку Strands
python -c "import strands; print('Strands OK')"

# Проверьте установку MCP
python -c "import mcp; print('MCP OK')"

# Проверьте uvx
uvx --version
```

### Тест с простым агентом
```python
# Создайте файл test_installation.py
from strands import Agent

# Простой агент без MCP (для проверки базовой функциональности)
agent = Agent(system_prompt="Вы полезный ассистент.")
response = agent("Привет! Как дела?")
print(response)
```

## Шаг 4: Первый MCP агент

### Создайте файл first_mcp_agent.py:

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

# Используем агента с MCP инструментами
with mcp_client:
    tools = mcp_client.list_tools_sync()
    print(f"Найдено {len(tools)} MCP инструментов")
    
    agent = Agent(
        tools=tools,
        system_prompt="Вы эксперт по AWS. Используйте доступные инструменты."
    )
    
    response = agent("Что такое AWS Lambda?")
    print(response)
```

### Запустите тест:
```bash
python first_mcp_agent.py
```

## Шаг 5: Использование готовых примеров

В этой папке есть готовые примеры:

```bash
# Быстрый тест (автоматический)
python quick_mcp_test.py

# Интерактивный режим
python quick_mcp_test.py --interactive

# Полное руководство с примерами
python mcp_agent_guide.py

# Создание собственного MCP сервера
python custom_mcp_server_example.py calculator
```

## Популярные MCP серверы

### AWS Documentation
```bash
uvx awslabs.aws-documentation-mcp-server@latest
```

### File System Operations
```bash
uvx file-system-mcp-server@latest
```

### SQLite Database
```bash
uvx sqlite-mcp-server@latest /path/to/database.db
```

### GitHub Integration
```bash
# Требует GITHUB_TOKEN
export GITHUB_TOKEN=your_github_token
uvx github-mcp-server@latest
```

### Web Search
```bash
uvx web-search-mcp-server@latest
```

## Устранение проблем

### Проблема: "uvx command not found"
```bash
# Решение: установите uv
pip install uv

# Или через curl (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Или через PowerShell (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Проблема: "AWS credentials not found"
```bash
# Проверьте переменные окружения
echo $AWS_BEDROCK_API_KEY
echo $AWS_ACCESS_KEY_ID

# Или установите их
export AWS_BEDROCK_API_KEY=your_key
```

### Проблема: "Access denied to model"
1. Откройте Bedrock Console
2. Включите доступ к нужной модели в разделе "Model access"
3. Подождите несколько минут

### Проблема: "Connection timeout"
- Проверьте интернет-соединение
- Убедитесь, что firewall не блокирует соединения
- Попробуйте другой MCP сервер

### Проблема: "Module not found"
```bash
# Переустановите пакеты
pip uninstall strands-agents mcp
pip install strands-agents strands-agents-tools mcp
```

## Следующие шаги

1. **Изучите примеры** в файлах этой папки
2. **Попробуйте разные MCP серверы** из списка выше
3. **Создайте собственный MCP сервер** используя `custom_mcp_server_example.py`
4. **Интегрируйте с вашим приложением** используя полученные знания

## Полезные ссылки

- [Документация Strands Agents](https://strandsagents.com)
- [Официальный сайт MCP](https://modelcontextprotocol.io)
- [Список MCP серверов](https://github.com/punkpeye/awesome-mcp-servers)
- [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
- [Anthropic Console](https://console.anthropic.com/)
- [OpenAI Platform](https://platform.openai.com/)

## Поддержка

Если у вас возникли проблемы:

1. Проверьте этот файл с инструкциями
2. Запустите `quick_mcp_test.py` для диагностики
3. Изучите примеры в `mcp_agent_guide.py`
4. Обратитесь к официальной документации