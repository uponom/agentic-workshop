# Streamlit Agent Application Startup Guide

This guide explains how to start the Streamlit Agent application using the provided startup scripts.

## Quick Start

### Windows
```cmd
cd streamlit_agent
start.bat
```

### Unix/Linux/macOS
```bash
cd streamlit_agent
./start.sh
```

### Python (Cross-platform)
```bash
cd streamlit_agent
python start.py
```

## Startup Scripts

### 1. `start.py` - Main Python Startup Script

The main startup script that handles:
- Application configuration management
- Directory creation and validation
- Component initialization and validation
- Dependency checking
- Streamlit application launch

**Usage:**
```bash
python start.py [OPTIONS]
```

**Options:**
- `--port PORT`: Set the port (default: 8501)
- `--host HOST`: Set the host (default: localhost)
- `--debug`: Enable debug mode
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--config-file PATH`: Path to configuration file
- `--validate-only`: Only validate setup, do not start application
- `--create-config`: Create default configuration file and exit

**Examples:**
```bash
# Start with default settings
python start.py

# Start on custom port with debug mode
python start.py --port 8080 --debug

# Validate setup without starting
python start.py --validate-only

# Create configuration file
python start.py --create-config
```

### 2. `start.sh` - Unix/Linux/macOS Shell Script

Convenient shell script for Unix-based systems that:
- Checks for Python and pip availability
- Installs dependencies if needed
- Creates required directories
- Launches the Python startup script

**Usage:**
```bash
./start.sh [OPTIONS]
```

**Options:**
- `--port PORT`: Set the port (default: 8501)
- `--host HOST`: Set the host (default: localhost)
- `--debug`: Enable debug mode
- `--help`: Show help message

### 3. `start.bat` - Windows Batch Script

Windows batch script that provides the same functionality as the shell script:
- Checks for Python and pip availability
- Installs dependencies if needed
- Creates required directories
- Launches the Python startup script

**Usage:**
```cmd
start.bat [OPTIONS]
```

**Options:**
- `--port PORT`: Set the port (default: 8501)
- `--host HOST`: Set the host (default: localhost)
- `--debug`: Enable debug mode
- `--help`: Show help message

## Configuration

### Configuration File

The application supports configuration through a JSON file. Create a configuration file using:

```bash
python start.py --create-config
```

This creates a `config.json` file with default settings. You can also copy `config.template.json` and modify it.

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `port` | 8501 | Streamlit server port |
| `host` | localhost | Streamlit server host |
| `debug` | false | Enable debug mode |
| `log_level` | INFO | Logging level |
| `generated_diagrams_dir` | generated-diagrams | Directory for generated diagrams |
| `logs_dir` | logs | Directory for log files |
| `test_screenshots_dir` | test_screenshots | Directory for test screenshots |
| `agent_timeout` | 120 | Agent processing timeout (seconds) |
| `max_diagrams` | 100 | Maximum number of diagrams to keep |
| `cleanup_old_diagrams` | true | Auto-cleanup old diagrams |
| `max_diagram_age_hours` | 24 | Maximum age for diagrams (hours) |

## Directory Structure

The startup scripts automatically create the following directories:

```
streamlit_agent/
├── generated-diagrams/    # Generated AWS architecture diagrams
├── logs/                  # Application and startup logs
├── test_screenshots/      # Browser automation test screenshots
├── components/            # Application components
├── tests/                 # Test files
├── start.py              # Main startup script
├── start.sh              # Unix shell script
├── start.bat             # Windows batch script
├── config.json           # Configuration file (created on first run)
├── config.template.json  # Configuration template
└── app.py                # Streamlit application
```

## Validation and Troubleshooting

### Validate Setup

Before starting the application, you can validate the setup:

```bash
python start.py --validate-only
```

This checks:
- Required dependencies are installed
- Application components can be imported
- Directories can be created and are writable
- Configuration is valid

### Common Issues

1. **Missing Dependencies**
   ```
   Error: Missing dependencies: streamlit, strands
   ```
   **Solution:** Install dependencies with `pip install -r requirements.txt`

2. **Permission Errors**
   ```
   Error: Directory validation failed
   ```
   **Solution:** Ensure you have write permissions in the application directory

3. **Port Already in Use**
   ```
   Error: Port 8501 is already in use
   ```
   **Solution:** Use a different port with `--port 8502`

4. **Component Import Errors**
   ```
   Error: Component validation failed
   ```
   **Solution:** Ensure all component files are present and Python path is correct

### Debug Mode

Enable debug mode for detailed logging:

```bash
python start.py --debug
```

This provides:
- Detailed startup logs
- Component initialization details
- Enhanced error messages
- Streamlit debug output

### Log Files

Startup logs are saved to:
- `logs/startup.log` - Startup process logs
- `logs/streamlit_agent_errors.log` - Application error logs

## Environment Variables

The startup scripts set the following environment variables:

- `STREAMLIT_SERVER_HEADLESS=true` - Run Streamlit in headless mode
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false` - Disable usage statistics

## Advanced Usage

### Custom Configuration

Create a custom configuration file and use it:

```bash
# Create custom config
cp config.template.json my_config.json
# Edit my_config.json as needed
python start.py --config-file my_config.json
```

### Development Mode

For development with auto-reload:

```bash
python start.py --debug --log-level DEBUG
```

### Production Deployment

For production deployment:

```bash
python start.py --host 0.0.0.0 --port 80 --log-level WARNING
```

## Integration with Other Tools

### Docker

The startup scripts can be used in Docker containers:

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["python", "start.py", "--host", "0.0.0.0"]
```

### Systemd Service

Create a systemd service for automatic startup:

```ini
[Unit]
Description=Streamlit Agent Application
After=network.target

[Service]
Type=simple
User=streamlit
WorkingDirectory=/path/to/streamlit_agent
ExecStart=/usr/bin/python3 start.py --host 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

## Support

For issues with the startup scripts:

1. Check the logs in `logs/startup.log`
2. Run with `--debug` for detailed output
3. Use `--validate-only` to check setup
4. Ensure all dependencies are installed
5. Verify directory permissions