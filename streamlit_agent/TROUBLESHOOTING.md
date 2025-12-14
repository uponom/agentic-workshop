# Streamlit Agent Application - Troubleshooting Guide

This comprehensive troubleshooting guide helps you diagnose and resolve common issues with the Streamlit Agent application.

## 🔍 Quick Diagnosis

### Health Check Commands

Run these commands to quickly assess the application health:

```bash
# Validate complete setup
python start.py --validate-only

# Check dependencies
pip list | grep -E "(streamlit|strands|boto3|pillow|pytest|hypothesis)"

# Test component imports
python -c "from components import *; print('✅ All components imported successfully')"

# Check directory permissions
ls -la generated-diagrams/ logs/ test_screenshots/

# View recent logs
tail -20 logs/startup.log
tail -20 logs/streamlit_agent_errors.log
```

### Quick Fixes

Before diving into detailed troubleshooting, try these quick fixes:

1. **Restart the application** completely
2. **Clear browser cache** and refresh
3. **Check internet connection** (required for MCP servers)
4. **Verify port availability** (default: 8501)
5. **Update dependencies**: `pip install -r requirements.txt --upgrade`

## 🚨 Common Issues & Solutions

### 1. Application Startup Issues

#### Issue: Import Errors
```
ModuleNotFoundError: No module named 'streamlit'
ModuleNotFoundError: No module named 'strands'
```

**Diagnosis:**
```bash
python -c "import streamlit; print('Streamlit OK')"
python -c "import strands; print('Strands OK')"
```

**Solutions:**
```bash
# Install missing dependencies
pip install -r requirements.txt

# If using virtual environment, ensure it's activated
source venv/bin/activate  # Unix
# or
venv\Scripts\activate     # Windows

# Upgrade pip if needed
pip install --upgrade pip

# Force reinstall if corrupted
pip install --force-reinstall streamlit strands-agents
```

#### Issue: Port Already in Use
```
OSError: [Errno 48] Address already in use
```

**Diagnosis:**
```bash
# Check what's using the port
netstat -an | grep 8501
lsof -i :8501  # Unix only
```

**Solutions:**
```bash
# Use different port
python start.py --port 8502

# Kill process using the port (Unix)
kill -9 $(lsof -t -i:8501)

# Kill process using the port (Windows)
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### Issue: Permission Denied
```
PermissionError: [Errno 13] Permission denied: 'generated-diagrams'
```

**Diagnosis:**
```bash
# Check directory permissions
ls -la generated-diagrams/ logs/
whoami
pwd
```

**Solutions:**
```bash
# Fix directory permissions (Unix)
chmod 755 generated-diagrams/ logs/ test_screenshots/
chmod 644 generated-diagrams/* logs/* test_screenshots/*

# Run with appropriate permissions
sudo python start.py  # Not recommended for production

# Change ownership if needed (Unix)
chown -R $USER:$USER generated-diagrams/ logs/ test_screenshots/
```

### 2. Agent Connection Issues

#### Issue: MCP Server Connection Failures
```
Error: Failed to connect to MCP server
ConnectionError: Unable to establish MCP client connection
```

**Diagnosis:**
```bash
# Test internet connectivity
ping google.com

# Check if uvx is available
uvx --version

# Test MCP server manually
uvx awslabs.aws-documentation-mcp-server@latest --help
```

**Solutions:**
```bash
# Install uvx if missing
pip install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh

# Update MCP server
uvx --force awslabs.aws-documentation-mcp-server@latest

# Check firewall/proxy settings
# Ensure outbound connections are allowed

# Increase timeout in config.json
{
  "agent_timeout": 180,
  "agent_config": {
    "timeout_seconds": 180
  }
}
```

#### Issue: Agent Processing Timeouts
```
TimeoutError: Agent processing timed out after 120 seconds
```

**Diagnosis:**
```bash
# Check system resources
top
htop
ps aux | grep python

# Monitor network activity
netstat -an | grep ESTABLISHED
```

**Solutions:**
```bash
# Increase timeout in configuration
# Edit config.json:
{
  "agent_timeout": 300,
  "agent_config": {
    "timeout_seconds": 300
  }
}

# Restart application with new config
python start.py --config-file config.json

# Check for system resource constraints
# Close unnecessary applications
# Ensure sufficient RAM and CPU available
```

### 3. Diagram Generation Issues

#### Issue: No Diagrams Generated
```
No diagram available for display
Diagram generation failed
```

**Diagnosis:**
```bash
# Check diagram directory
ls -la generated-diagrams/
find . -name "*.png" -mtime -1

# Check diagram generation logs
grep -i "diagram" logs/streamlit_agent_errors.log

# Test diagram library
python -c "from diagrams import Diagram; print('Diagrams library OK')"
```

**Solutions:**
```bash
# Ensure diagrams library is installed
pip install diagrams

# Check system dependencies for diagram generation
# On Ubuntu/Debian:
sudo apt-get install graphviz

# On macOS:
brew install graphviz

# On Windows:
# Download and install Graphviz from official website

# Clear old diagrams and retry
rm -rf generated-diagrams/*
mkdir -p generated-diagrams

# Test diagram generation manually
python -c "
from diagrams import Diagram
from diagrams.aws.compute import Lambda
with Diagram('Test', show=False, filename='generated-diagrams/test'):
    Lambda('Test Lambda')
print('✅ Diagram generation test successful')
"
```

#### Issue: Diagram Display Problems
```
Image failed to load
Corrupted diagram file
```

**Diagnosis:**
```bash
# Check file integrity
file generated-diagrams/*.png
ls -la generated-diagrams/

# Check file permissions
stat generated-diagrams/*.png

# Verify image format
python -c "
from PIL import Image
import os
for f in os.listdir('generated-diagrams'):
    if f.endswith('.png'):
        try:
            img = Image.open(f'generated-diagrams/{f}')
            print(f'✅ {f}: {img.size} {img.mode}')
        except Exception as e:
            print(f'❌ {f}: {e}')
"
```

**Solutions:**
```bash
# Clear corrupted files
find generated-diagrams/ -name "*.png" -size 0 -delete

# Regenerate diagrams
rm -rf generated-diagrams/*.png

# Check disk space
df -h

# Ensure proper file permissions
chmod 644 generated-diagrams/*.png

# Test with simple diagram
python -c "
from diagrams import Diagram
from diagrams.aws.storage import S3
with Diagram('Simple Test', show=False, filename='generated-diagrams/simple_test'):
    S3('Test S3')
"
```

### 4. Browser and UI Issues

#### Issue: Streamlit UI Not Loading
```
This site can't be reached
Connection refused
```

**Diagnosis:**
```bash
# Check if Streamlit is running
ps aux | grep streamlit
netstat -an | grep 8501

# Test direct access
curl http://localhost:8501

# Check browser console (F12)
# Look for JavaScript errors
```

**Solutions:**
```bash
# Restart Streamlit
pkill -f streamlit
python start.py

# Try different browser
# Clear browser cache and cookies

# Check firewall settings
# Ensure localhost access is allowed

# Try different host/port
python start.py --host 0.0.0.0 --port 8502

# Disable browser extensions temporarily
```

#### Issue: Browser Automation Test Failures
```
Chrome DevTools connection failed
Element not found during automation
```

**Diagnosis:**
```bash
# Check Chrome installation
google-chrome --version
chromium --version

# Test Chrome DevTools MCP
# (This requires the MCP server to be properly configured)

# Check test screenshots
ls -la test_screenshots/
```

**Solutions:**
```bash
# Install/update Chrome
# Ubuntu/Debian:
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo apt-get update
sudo apt-get install google-chrome-stable

# macOS:
brew install --cask google-chrome

# Windows:
# Download from https://www.google.com/chrome/

# Run tests with debug output
python run_browser_automation_tests.py --debug

# Check Chrome DevTools MCP server availability
# Ensure proper MCP configuration
```

### 5. Configuration Issues

#### Issue: Configuration File Problems
```
JSON decode error in config.json
Invalid configuration format
```

**Diagnosis:**
```bash
# Validate JSON syntax
python -c "import json; json.load(open('config.json'))"

# Check file permissions
ls -la config.json

# Compare with template
diff config.json config.template.json
```

**Solutions:**
```bash
# Recreate configuration file
cp config.template.json config.json

# Or generate new one
python start.py --create-config

# Validate JSON online or with tool
cat config.json | python -m json.tool

# Fix common JSON issues:
# - Remove trailing commas
# - Ensure proper quotes
# - Check bracket matching
```

#### Issue: Environment Variable Conflicts
```
Unexpected behavior due to environment variables
```

**Diagnosis:**
```bash
# Check relevant environment variables
env | grep -E "(STREAMLIT|PYTHON|PATH)"

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

**Solutions:**
```bash
# Clear conflicting environment variables
unset STREAMLIT_SERVER_PORT
unset STREAMLIT_SERVER_ADDRESS

# Use clean environment
env -i python start.py

# Set required environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 🔧 Advanced Troubleshooting

### Debug Mode Analysis

Enable comprehensive debugging:

```bash
python start.py --debug --log-level DEBUG
```

This provides detailed information about:
- Component initialization
- MCP client connections
- File system operations
- Agent communication
- Error stack traces

### Log Analysis

#### Startup Logs (`logs/startup.log`)
```bash
# Check initialization sequence
grep -E "(OK|ERROR|WARNING)" logs/startup.log

# Look for component failures
grep -A 5 -B 5 "Component validation failed" logs/startup.log

# Check directory creation
grep "Directory" logs/startup.log
```

#### Runtime Logs (`logs/streamlit_agent_errors.log`)
```bash
# Check recent errors
tail -50 logs/streamlit_agent_errors.log

# Look for specific error patterns
grep -E "(Exception|Error|Failed)" logs/streamlit_agent_errors.log

# Check agent communication
grep -i "agent" logs/streamlit_agent_errors.log
```

### Performance Troubleshooting

#### Memory Issues
```bash
# Monitor memory usage
ps aux | grep python
top -p $(pgrep -f streamlit)

# Check for memory leaks
# Run application and monitor memory over time
```

#### CPU Issues
```bash
# Monitor CPU usage
htop
iostat 1

# Profile Python application
python -m cProfile start.py
```

#### Network Issues
```bash
# Monitor network connections
netstat -an | grep python
ss -tulpn | grep python

# Check DNS resolution
nslookup github.com
dig github.com
```

### System-Specific Issues

#### Windows-Specific
```cmd
# Check Windows Defender/Antivirus
# Ensure Python and application are whitelisted

# Check Windows Firewall
netsh advfirewall show allprofiles

# Use Windows-specific commands
dir generated-diagrams
type logs\startup.log
```

#### macOS-Specific
```bash
# Check macOS security settings
# System Preferences > Security & Privacy

# Check Gatekeeper
spctl --status

# Use macOS-specific tools
lsof -i :8501
dtruss -p $(pgrep python)
```

#### Linux-Specific
```bash
# Check SELinux (if enabled)
sestatus
getenforce

# Check systemd logs
journalctl -u streamlit-agent

# Check file system
df -i
mount | grep $(pwd)
```

## 🛡️ Prevention & Best Practices

### Regular Maintenance

1. **Update dependencies regularly:**
   ```bash
   pip list --outdated
   pip install -r requirements.txt --upgrade
   ```

2. **Clean up old files:**
   ```bash
   # Remove old diagrams (older than 24 hours)
   find generated-diagrams/ -name "*.png" -mtime +1 -delete
   
   # Rotate log files
   logrotate -f /path/to/logrotate.conf
   ```

3. **Monitor disk space:**
   ```bash
   df -h
   du -sh generated-diagrams/ logs/ test_screenshots/
   ```

### Configuration Best Practices

1. **Use version control for configuration:**
   ```bash
   git add config.json
   git commit -m "Update application configuration"
   ```

2. **Environment-specific configurations:**
   ```bash
   # Development
   cp config.template.json config.dev.json
   
   # Production
   cp config.template.json config.prod.json
   
   # Use specific config
   python start.py --config-file config.prod.json
   ```

3. **Secure sensitive information:**
   ```bash
   # Don't commit sensitive data
   echo "config.local.json" >> .gitignore
   
   # Use environment variables for secrets
   export AWS_ACCESS_KEY_ID="your-key"
   export AWS_SECRET_ACCESS_KEY="your-secret"
   ```

### Monitoring & Alerting

1. **Set up log monitoring:**
   ```bash
   # Monitor for errors
   tail -f logs/streamlit_agent_errors.log | grep -i error
   
   # Set up log rotation
   # Add to /etc/logrotate.d/streamlit-agent
   ```

2. **Health check endpoints:**
   ```bash
   # Create simple health check
   curl http://localhost:8501/_stcore/health
   ```

3. **Automated testing:**
   ```bash
   # Run tests regularly
   crontab -e
   # Add: 0 */6 * * * cd /path/to/streamlit_agent && python -m pytest tests/
   ```

## 📞 Getting Additional Help

### Information to Collect

When seeking help, collect this information:

1. **System Information:**
   ```bash
   python --version
   pip --version
   uname -a  # Unix
   systeminfo  # Windows
   ```

2. **Application Information:**
   ```bash
   pip list | grep -E "(streamlit|strands|boto3)"
   python start.py --validate-only
   ```

3. **Error Information:**
   ```bash
   tail -50 logs/startup.log
   tail -50 logs/streamlit_agent_errors.log
   ```

4. **Configuration:**
   ```bash
   cat config.json  # Remove sensitive information
   ```

### Support Channels

1. **Check documentation** in the project repository
2. **Review log files** for detailed error information
3. **Search existing issues** in the project issue tracker
4. **Create detailed bug reports** with system information and logs

### Self-Help Resources

1. **Official Documentation:**
   - Streamlit: https://docs.streamlit.io/
   - Strands Agents: https://strandsagents.com/
   - MCP: https://github.com/modelcontextprotocol/specification

2. **Community Resources:**
   - Stack Overflow (tag: streamlit, strands-agents)
   - GitHub Issues and Discussions
   - AWS Documentation

3. **Debugging Tools:**
   - Python debugger: `python -m pdb start.py`
   - Streamlit debug mode: `streamlit run app.py --logger.level debug`
   - Browser developer tools (F12)

---

**Remember:** Most issues can be resolved by carefully reading error messages, checking log files, and following the systematic troubleshooting steps outlined above.