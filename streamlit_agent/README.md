# Streamlit Agent Application

A Streamlit web application that provides a user-friendly interface to interact with the AWS Solutions Architect agent. This application allows users to submit AWS architecture queries and receive expert guidance along with automatically generated architecture diagrams.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection (for MCP server dependencies)

### Installation & Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd streamlit_agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application:**
   
   **Option A: Using the startup script (Recommended)**
   ```bash
   # Windows
   start.bat
   
   # Unix/Linux/macOS
   ./start.sh
   
   # Cross-platform Python
   python start.py
   ```
   
   **Option B: Direct Streamlit launch**
   ```bash
   streamlit run app.py
   ```

4. **Access the application:**
   Open your web browser and navigate to `http://localhost:8501`

## 📋 Features

- **🌐 Interactive Web Interface**: Clean, responsive Streamlit-based UI
- **🏗️ AWS Architecture Queries**: Submit questions and get expert architectural guidance
- **📊 Visual Diagrams**: Automatically generated AWS architecture diagrams
- **⏱️ Real-time Processing**: Live status updates during query processing
- **🧪 Browser Testing**: Automated end-to-end testing capabilities
- **🔧 Configurable**: Extensive configuration options for customization
- **📝 Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📁 Project Structure

```
streamlit_agent/
├── app.py                      # Main Streamlit application
├── start.py                    # Application startup script
├── start.sh                    # Unix startup script
├── start.bat                   # Windows startup script
├── config.json                 # Application configuration
├── config.template.json        # Configuration template
├── requirements.txt            # Python dependencies
├── components/                 # Core application components
│   ├── __init__.py
│   ├── agent_wrapper.py        # Agent integration wrapper
│   ├── query_processor.py      # Query processing logic
│   ├── diagram_manager.py      # Diagram file management
│   ├── response_renderer.py    # Response formatting and display
│   ├── error_handler.py        # Error handling utilities
│   └── test_automation.py      # Browser automation testing
├── tests/                      # Comprehensive test suite
│   ├── test_*_unit.py         # Unit tests
│   ├── test_*_property.py     # Property-based tests
│   └── test_*_integration.py  # Integration tests
├── generated-diagrams/         # Generated AWS architecture diagrams
├── logs/                       # Application logs
├── test_screenshots/           # Browser automation screenshots
└── docs/                       # Additional documentation
    ├── STARTUP_GUIDE.md        # Detailed startup guide
    ├── BROWSER_AUTOMATION_TESTS.md
    └── *.md                    # Other documentation files
```

## ⚙️ Configuration

### Configuration File

The application uses a JSON configuration file for customization. Create one using:

```bash
python start.py --create-config
```

Or copy the template:
```bash
cp config.template.json config.json
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `port` | 8501 | Streamlit server port |
| `host` | localhost | Streamlit server host |
| `debug` | false | Enable debug mode |
| `log_level` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `generated_diagrams_dir` | generated-diagrams | Directory for generated diagrams |
| `logs_dir` | logs | Directory for log files |
| `test_screenshots_dir` | test_screenshots | Directory for test screenshots |
| `agent_timeout` | 120 | Agent processing timeout (seconds) |
| `max_diagrams` | 100 | Maximum number of diagrams to keep |
| `cleanup_old_diagrams` | true | Auto-cleanup old diagrams |
| `max_diagram_age_hours` | 24 | Maximum age for diagrams (hours) |

### Advanced Configuration

The configuration file supports nested objects for detailed customization:

```json
{
  "streamlit_config": {
    "server.headless": true,
    "browser.gatherUsageStats": false,
    "server.enableCORS": false
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
  }
}
```

## 🎯 Usage

### Basic Usage

1. **Start the application** using one of the startup methods above
2. **Enter your AWS architecture query** in the text input field
3. **Click "Submit Query"** or press Enter
4. **View the results** including:
   - Expert architectural guidance and recommendations
   - Automatically generated AWS architecture diagrams
   - Technical details and best practices

### Example Queries

- "Design a serverless web application architecture"
- "How to build a scalable e-commerce platform on AWS?"
- "Create a data pipeline for real-time analytics"
- "Design a microservices architecture with containers"
- "Build a secure multi-tier web application"

### Advanced Features

- **Real-time Status Updates**: Monitor query processing progress
- **Diagram Management**: Automatically displays the most recent diagram
- **Error Handling**: Graceful error recovery and user feedback
- **Browser Testing**: Automated end-to-end testing capabilities

## 🧪 Testing

The application includes comprehensive testing at multiple levels:

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_*_unit.py          # Unit tests
pytest tests/test_*_property.py     # Property-based tests
pytest tests/test_*_integration.py  # Integration tests

# Run with coverage
pytest --cov=components tests/

# Run browser automation tests
python run_browser_automation_tests.py
```

### Test Categories

1. **Unit Tests**: Test individual component functionality
   - Query processing validation
   - Diagram file operations
   - Response rendering
   - Error handling scenarios

2. **Property-Based Tests**: Validate universal behaviors
   - Query processing consistency
   - File detection reliability
   - Response rendering preservation
   - Status feedback management

3. **Browser Automation Tests**: End-to-end workflow validation
   - Application startup and accessibility
   - Complete query-to-results workflow
   - UI element presence and functionality
   - Cross-browser compatibility

## 🔧 Development

### Development Setup

1. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov hypothesis
   ```

2. **Enable debug mode:**
   ```bash
   python start.py --debug --log-level DEBUG
   ```

3. **Run in development mode with auto-reload:**
   ```bash
   streamlit run app.py --server.runOnSave true
   ```

### Architecture Overview

The application follows a layered architecture:

- **Presentation Layer**: Streamlit UI components
- **Business Logic Layer**: Query processing, agent interaction, file management
- **Integration Layer**: Strands agent integration, MCP client connections
- **Data Layer**: Generated diagrams, documentation files, application state

### Key Components

- **QueryProcessor**: Handles user input validation and agent communication
- **AgentWrapper**: Manages integration with the Strands AWS Solutions Architect agent
- **DiagramManager**: Monitors and manages generated diagram files
- **ResponseRenderer**: Formats and displays agent responses with proper markdown rendering
- **ErrorHandler**: Provides comprehensive error handling and user feedback

## 🛠️ Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Symptoms:**
- Import errors
- Missing dependencies
- Port binding failures

**Solutions:**
```bash
# Check dependencies
python start.py --validate-only

# Install missing dependencies
pip install -r requirements.txt

# Use different port
python start.py --port 8502

# Check logs
cat logs/startup.log
```

#### 2. Agent Connection Issues

**Symptoms:**
- Timeout errors
- MCP server connection failures
- No response from agent

**Solutions:**
```bash
# Check internet connection
# Verify MCP server availability
# Check agent timeout settings in config.json

# Enable debug mode for detailed logs
python start.py --debug
```

#### 3. Diagram Generation Problems

**Symptoms:**
- No diagrams displayed
- Diagram loading errors
- File permission issues

**Solutions:**
```bash
# Check directory permissions
ls -la generated-diagrams/

# Verify diagram generation
# Check logs for diagram-related errors
tail -f logs/streamlit_agent_errors.log

# Clear old diagrams
rm -rf generated-diagrams/*
```

#### 4. Browser Automation Test Failures

**Symptoms:**
- Chrome DevTools connection errors
- UI element not found
- Screenshot capture failures

**Solutions:**
```bash
# Ensure Chrome is installed and accessible
# Check Chrome DevTools MCP server availability
# Verify application is running before tests

# Run tests with debug output
python run_browser_automation_tests.py --debug
```

### Debug Mode

Enable comprehensive debugging:

```bash
python start.py --debug --log-level DEBUG
```

This provides:
- Detailed startup logs
- Component initialization details
- Enhanced error messages
- Streamlit debug output
- MCP client communication logs

### Log Files

Check these log files for troubleshooting:

- `logs/startup.log` - Application startup process
- `logs/streamlit_agent_errors.log` - Runtime errors and issues
- Browser console logs (F12 in browser) - Frontend issues

### Environment Validation

Validate your environment setup:

```bash
# Check Python version
python --version

# Validate application setup
python start.py --validate-only

# Check component imports
python -c "from components import *; print('All components imported successfully')"

# Test MCP server connectivity
# (This is done automatically during startup validation)
```

### Performance Issues

If the application is slow:

1. **Check system resources** (CPU, memory usage)
2. **Increase agent timeout** in configuration
3. **Enable cleanup of old diagrams**
4. **Check network connectivity** for MCP servers
5. **Review log files** for performance bottlenecks

### Getting Help

1. **Check the logs** in `logs/` directory
2. **Run validation** with `python start.py --validate-only`
3. **Enable debug mode** for detailed output
4. **Review configuration** settings
5. **Check system requirements** and dependencies

## 📚 Dependencies

### Core Dependencies

- **Streamlit** (≥1.28.0): Web application framework
- **Strands Agents** (≥0.1.0): AI agent framework for AWS architecture guidance
- **MCP** (≥1.0.0): Model Context Protocol for tool integration
- **Boto3** (≥1.34.0): AWS SDK for Python
- **Pillow** (≥10.0.0): Image processing library
- **Diagrams** (≥0.23.0): Python library for generating architecture diagrams

### Testing Dependencies

- **Pytest** (≥7.4.0): Testing framework
- **Hypothesis** (≥6.82.0): Property-based testing
- **Pytest-asyncio** (≥0.21.0): Async testing support

### Optional Dependencies

- **Chrome DevTools MCP Server**: For browser automation testing
- **AWS CLI**: For enhanced AWS integration (optional)

## 📖 Additional Documentation

- **[Startup Guide](STARTUP_GUIDE.md)**: Detailed startup and configuration guide
- **[Browser Automation Tests](BROWSER_AUTOMATION_TESTS.md)**: Browser testing documentation
- **[Requirements](../.kiro/specs/streamlit-agent/requirements.md)**: Detailed functional requirements
- **[Design](../.kiro/specs/streamlit-agent/design.md)**: Architecture and component design
- **[Tasks](../.kiro/specs/streamlit-agent/tasks.md)**: Implementation plan and progress

## 🤝 Contributing

This application is built following the specification-driven development methodology:

1. **Requirements**: Defined in `requirements.md` using EARS patterns
2. **Design**: Comprehensive design document with correctness properties
3. **Implementation**: Task-driven development with property-based testing
4. **Testing**: Multi-level testing strategy (unit, property-based, integration)

## 📄 License

This project is part of the AWS Solutions Architect agent ecosystem and follows the same licensing terms.

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added browser automation testing
- **v1.2.0**: Enhanced error handling and configuration options
- **v1.3.0**: Comprehensive documentation and troubleshooting guide

---

**Need help?** Check the troubleshooting section above or review the log files in the `logs/` directory for detailed error information.