# Streamlit Agent Application - Configuration Guide

This guide provides comprehensive information about configuring the Streamlit Agent application for different environments and use cases.

## 📋 Configuration Overview

The Streamlit Agent application uses a JSON-based configuration system that allows you to customize:

- Server settings (host, port, debug mode)
- Directory locations for generated content
- Agent behavior and timeouts
- Logging configuration
- Diagram management settings
- Streamlit-specific options

## 🚀 Quick Configuration Setup

### 1. Create Configuration File

```bash
# Option A: Generate default configuration
python start.py --create-config

# Option B: Copy from template
cp config.template.json config.json

# Option C: Start with minimal configuration
echo '{"port": 8501, "debug": false}' > config.json
```

### 2. Basic Configuration

Edit `config.json` with your preferred settings:

```json
{
  "port": 8501,
  "host": "localhost",
  "debug": false,
  "log_level": "INFO"
}
```

### 3. Use Configuration

```bash
# Use default config.json
python start.py

# Use specific configuration file
python start.py --config-file my-config.json

# Override specific settings
python start.py --port 8080 --debug
```

## ⚙️ Configuration Reference

### Core Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `port` | integer | 8501 | Streamlit server port |
| `host` | string | "localhost" | Streamlit server host |
| `debug` | boolean | false | Enable debug mode |
| `log_level` | string | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR) |

**Example:**
```json
{
  "port": 8501,
  "host": "0.0.0.0",
  "debug": true,
  "log_level": "DEBUG"
}
```

### Directory Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `generated_diagrams_dir` | string | "generated-diagrams" | Directory for generated AWS diagrams |
| `logs_dir` | string | "logs" | Directory for application logs |
| `test_screenshots_dir` | string | "test_screenshots" | Directory for browser test screenshots |

**Example:**
```json
{
  "generated_diagrams_dir": "output/diagrams",
  "logs_dir": "logs/app",
  "test_screenshots_dir": "tests/screenshots"
}
```

### Agent Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `agent_timeout` | integer | 120 | Agent processing timeout (seconds) |
| `max_diagrams` | integer | 100 | Maximum number of diagrams to keep |
| `cleanup_old_diagrams` | boolean | true | Auto-cleanup old diagrams |
| `max_diagram_age_hours` | integer | 24 | Maximum age for diagrams (hours) |

**Example:**
```json
{
  "agent_timeout": 180,
  "max_diagrams": 50,
  "cleanup_old_diagrams": true,
  "max_diagram_age_hours": 12
}
```

### Advanced Configuration Objects

#### Streamlit Configuration

```json
{
  "streamlit_config": {
    "server.headless": true,
    "browser.gatherUsageStats": false,
    "server.enableCORS": false,
    "server.enableXsrfProtection": false,
    "server.maxUploadSize": 200,
    "server.maxMessageSize": 200
  }
}
```

#### Agent Configuration

```json
{
  "agent_config": {
    "model_temperature": 0.7,
    "max_tokens": 4000,
    "timeout_seconds": 120,
    "retry_attempts": 3,
    "retry_delay": 5
  }
}
```

#### Diagram Configuration

```json
{
  "diagram_config": {
    "auto_cleanup": true,
    "max_file_size_mb": 10,
    "supported_formats": ["png", "jpg", "jpeg"],
    "compression_quality": 85,
    "max_width": 2048,
    "max_height": 2048
  }
}
```

#### Logging Configuration

```json
{
  "logging_config": {
    "log_to_file": true,
    "log_to_console": true,
    "max_log_size_mb": 50,
    "backup_count": 5,
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

## 🌍 Environment-Specific Configurations

### Development Configuration

**File: `config.dev.json`**
```json
{
  "port": 8501,
  "host": "localhost",
  "debug": true,
  "log_level": "DEBUG",
  "agent_timeout": 60,
  "cleanup_old_diagrams": false,
  "streamlit_config": {
    "server.headless": false,
    "browser.gatherUsageStats": false,
    "server.runOnSave": true
  },
  "logging_config": {
    "log_to_console": true,
    "log_to_file": true
  }
}
```

**Usage:**
```bash
python start.py --config-file config.dev.json
```

### Production Configuration

**File: `config.prod.json`**
```json
{
  "port": 80,
  "host": "0.0.0.0",
  "debug": false,
  "log_level": "WARNING",
  "agent_timeout": 300,
  "cleanup_old_diagrams": true,
  "max_diagram_age_hours": 6,
  "streamlit_config": {
    "server.headless": true,
    "browser.gatherUsageStats": false,
    "server.enableCORS": true,
    "server.enableXsrfProtection": true
  },
  "logging_config": {
    "log_to_console": false,
    "log_to_file": true,
    "max_log_size_mb": 100,
    "backup_count": 10
  }
}
```

**Usage:**
```bash
python start.py --config-file config.prod.json
```

### Testing Configuration

**File: `config.test.json`**
```json
{
  "port": 8502,
  "host": "localhost",
  "debug": true,
  "log_level": "DEBUG",
  "agent_timeout": 30,
  "generated_diagrams_dir": "test_diagrams",
  "logs_dir": "test_logs",
  "test_screenshots_dir": "test_screenshots",
  "cleanup_old_diagrams": false,
  "streamlit_config": {
    "server.headless": true,
    "browser.gatherUsageStats": false
  }
}
```

**Usage:**
```bash
python start.py --config-file config.test.json
```

## 🔧 Configuration Management

### Configuration Validation

The application automatically validates configuration on startup:

```bash
# Validate configuration without starting
python start.py --validate-only

# Check specific configuration file
python start.py --config-file config.prod.json --validate-only
```

### Configuration Merging

Configuration sources are merged in this order (later sources override earlier ones):

1. **Default values** (hardcoded in application)
2. **Configuration file** (`config.json` or specified file)
3. **Command line arguments** (highest priority)

**Example:**
```bash
# config.json has port: 8501
# This command will use port 8080 (command line overrides file)
python start.py --port 8080
```

### Environment Variables

Some settings can be controlled via environment variables:

```bash
# Set environment variables
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=localhost
export STREAMLIT_LOGGER_LEVEL=DEBUG

# Start application (will use environment variables)
python start.py
```

**Supported Environment Variables:**
- `STREAMLIT_SERVER_PORT`
- `STREAMLIT_SERVER_ADDRESS`
- `STREAMLIT_LOGGER_LEVEL`
- `PYTHONPATH`

### Configuration Templates

#### Minimal Configuration
```json
{
  "port": 8501,
  "debug": false
}
```

#### Basic Configuration
```json
{
  "port": 8501,
  "host": "localhost",
  "debug": false,
  "log_level": "INFO",
  "agent_timeout": 120
}
```

#### Complete Configuration
```json
{
  "port": 8501,
  "host": "localhost",
  "debug": false,
  "log_level": "INFO",
  "generated_diagrams_dir": "generated-diagrams",
  "logs_dir": "logs",
  "test_screenshots_dir": "test_screenshots",
  "agent_timeout": 120,
  "max_diagrams": 100,
  "cleanup_old_diagrams": true,
  "max_diagram_age_hours": 24,
  "streamlit_config": {
    "server.headless": true,
    "browser.gatherUsageStats": false,
    "server.enableCORS": false,
    "server.enableXsrfProtection": false
  },
  "agent_config": {
    "model_temperature": 0.7,
    "max_tokens": 4000,
    "timeout_seconds": 120
  },
  "diagram_config": {
    "auto_cleanup": true,
    "max_file_size_mb": 10,
    "supported_formats": ["png", "jpg", "jpeg"]
  },
  "logging_config": {
    "log_to_file": true,
    "log_to_console": true,
    "max_log_size_mb": 50,
    "backup_count": 5
  }
}
```

## 🔒 Security Configuration

### Production Security Settings

```json
{
  "streamlit_config": {
    "server.enableCORS": true,
    "server.enableXsrfProtection": true,
    "server.maxUploadSize": 50,
    "server.maxMessageSize": 50
  },
  "logging_config": {
    "log_to_console": false,
    "log_to_file": true
  }
}
```

### Network Security

```json
{
  "host": "127.0.0.1",  // Localhost only
  "port": 8501,
  "streamlit_config": {
    "server.enableCORS": false,
    "server.enableXsrfProtection": true
  }
}
```

### File System Security

```json
{
  "generated_diagrams_dir": "/secure/path/diagrams",
  "logs_dir": "/secure/path/logs",
  "diagram_config": {
    "max_file_size_mb": 5,
    "supported_formats": ["png"]
  }
}
```

## 🚀 Performance Configuration

### High Performance Settings

```json
{
  "agent_timeout": 300,
  "max_diagrams": 200,
  "cleanup_old_diagrams": true,
  "max_diagram_age_hours": 2,
  "streamlit_config": {
    "server.maxUploadSize": 200,
    "server.maxMessageSize": 200
  },
  "agent_config": {
    "timeout_seconds": 300,
    "max_tokens": 8000
  }
}
```

### Resource-Constrained Settings

```json
{
  "agent_timeout": 60,
  "max_diagrams": 20,
  "cleanup_old_diagrams": true,
  "max_diagram_age_hours": 1,
  "streamlit_config": {
    "server.maxUploadSize": 50,
    "server.maxMessageSize": 50
  },
  "agent_config": {
    "timeout_seconds": 60,
    "max_tokens": 2000
  },
  "diagram_config": {
    "max_file_size_mb": 2,
    "compression_quality": 70
  }
}
```

## 🐛 Debug Configuration

### Full Debug Mode

```json
{
  "debug": true,
  "log_level": "DEBUG",
  "streamlit_config": {
    "server.headless": false,
    "logger.level": "debug"
  },
  "logging_config": {
    "log_to_console": true,
    "log_to_file": true,
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
  }
}
```

### Performance Debugging

```json
{
  "debug": true,
  "log_level": "DEBUG",
  "agent_config": {
    "timeout_seconds": 600,
    "retry_attempts": 1
  },
  "logging_config": {
    "log_to_console": true,
    "log_format": "%(asctime)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]"
  }
}
```

## 📊 Monitoring Configuration

### Logging for Monitoring

```json
{
  "log_level": "INFO",
  "logging_config": {
    "log_to_file": true,
    "log_to_console": false,
    "max_log_size_mb": 100,
    "backup_count": 30,
    "log_format": "%(asctime)s - %(levelname)s - %(message)s"
  }
}
```

### Health Check Configuration

```json
{
  "streamlit_config": {
    "server.enableCORS": true,
    "server.enableStaticServing": true
  },
  "agent_timeout": 30,
  "cleanup_old_diagrams": true
}
```

## 🔄 Configuration Best Practices

### 1. Version Control

```bash
# Track configuration changes
git add config.json
git commit -m "Update production configuration"

# Use different configs for different environments
git add config.dev.json config.prod.json config.test.json
```

### 2. Configuration Validation

```bash
# Always validate before deployment
python start.py --config-file config.prod.json --validate-only

# Test configuration changes
python start.py --config-file config.new.json --validate-only
```

### 3. Backup Configurations

```bash
# Backup current configuration
cp config.json config.backup.$(date +%Y%m%d_%H%M%S).json

# Keep configuration history
mkdir -p config_history
cp config.json config_history/config.$(date +%Y%m%d_%H%M%S).json
```

### 4. Environment-Specific Files

```bash
# Development
config.dev.json

# Staging
config.staging.json

# Production
config.prod.json

# Testing
config.test.json

# Local development (not in version control)
config.local.json
```

### 5. Sensitive Information

```bash
# Never commit sensitive information
echo "config.local.json" >> .gitignore
echo "config.secret.json" >> .gitignore

# Use environment variables for secrets
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

## 🛠️ Configuration Troubleshooting

### Common Configuration Issues

#### 1. JSON Syntax Errors
```bash
# Validate JSON syntax
python -c "import json; json.load(open('config.json'))"

# Use JSON formatter
cat config.json | python -m json.tool
```

#### 2. Invalid Configuration Values
```bash
# Check configuration validation
python start.py --validate-only

# Review validation errors in logs
tail logs/startup.log
```

#### 3. Permission Issues
```bash
# Check file permissions
ls -la config.json

# Fix permissions if needed
chmod 644 config.json
```

### Configuration Debugging

```bash
# Enable debug mode
python start.py --debug --log-level DEBUG

# Check configuration loading
grep -i "config" logs/startup.log

# Validate specific settings
python -c "
import json
config = json.load(open('config.json'))
print('Port:', config.get('port', 'Not set'))
print('Debug:', config.get('debug', 'Not set'))
"
```

## 📚 Configuration Examples

### Docker Configuration

```json
{
  "host": "0.0.0.0",
  "port": 8501,
  "debug": false,
  "log_level": "INFO",
  "streamlit_config": {
    "server.headless": true,
    "browser.gatherUsageStats": false
  },
  "logging_config": {
    "log_to_console": true,
    "log_to_file": false
  }
}
```

### Load Balancer Configuration

```json
{
  "host": "0.0.0.0",
  "port": 8501,
  "streamlit_config": {
    "server.enableCORS": true,
    "server.enableXsrfProtection": false,
    "server.baseUrlPath": "/streamlit-agent"
  }
}
```

### Multi-Instance Configuration

```json
{
  "port": 8501,
  "generated_diagrams_dir": "/shared/diagrams",
  "logs_dir": "/shared/logs/instance1",
  "cleanup_old_diagrams": false,
  "streamlit_config": {
    "server.enableCORS": true
  }
}
```

---

**Need help with configuration?** Check the troubleshooting section or review the log files for detailed configuration validation messages.