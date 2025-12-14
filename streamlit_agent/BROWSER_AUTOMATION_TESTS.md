# Browser Automation Tests for Streamlit Agent

This document describes the comprehensive browser automation test suite for the Streamlit Agent application. The tests validate application startup, accessibility, complete query-to-results workflow, diagram generation and display, and UI element functionality.

## Overview

The browser automation tests are designed to validate all requirements specified in the design document:

- **Requirement 4.1**: Application startup and accessibility
- **Requirement 4.2**: Complete query-to-results workflow validation  
- **Requirement 4.3**: Diagram generation and display testing
- **Requirement 4.4**: UI elements presence and functionality verification
- **Requirement 4.5**: End-to-end workflow confirmation

## Test Components

### 1. Test Files

- **`tests/test_comprehensive_browser_automation.py`**: Main pytest test suite with both real and mocked tests
- **`run_browser_automation_tests.py`**: Standalone test runner for when MCP server is available
- **`components/test_automation.py`**: Core TestAutomation component with browser automation logic

### 2. Test Categories

#### Framework Tests (Always Available)
These tests validate the test framework itself and can run without the MCP server:

- `test_application_startup_and_accessibility_mock`: Mocked version of startup test
- `test_test_automation_framework_functionality`: Framework component validation
- `test_data_structures_and_types`: Data structure validation
- `test_factory_functions_and_utilities`: Utility function validation

#### Browser Automation Tests (Require MCP Server)
These tests require the Chrome DevTools MCP server to be available:

- `test_application_startup_and_accessibility`: Real browser startup validation
- `test_complete_query_to_results_workflow`: End-to-end query processing
- `test_diagram_generation_and_display`: Diagram display validation
- `test_ui_elements_presence_and_functionality`: UI interaction testing
- `test_end_to_end_workflow_confirmation`: Complete workflow validation
- `test_error_handling_and_recovery`: Error handling validation
- `test_performance_and_responsiveness`: Performance testing

## Prerequisites

### Required for All Tests
- Python 3.11+
- pytest and pytest-asyncio
- Streamlit Agent application components

### Required for Browser Automation Tests
- **Streamlit Application**: Must be running on the target URL (default: http://localhost:8501)
- **Chrome DevTools MCP Server**: Available via `uvx mcp-chrome-devtools@latest`
- **uvx Command**: Must be available in PATH for MCP server execution

### Installation

1. Install required Python packages:
```bash
pip install pytest pytest-asyncio streamlit strands-agents
```

2. Install uvx (if not already available):
```bash
# Using pip
pip install uv

# Or using other package managers as per uv documentation
```

3. Verify MCP server availability:
```bash
uvx mcp-chrome-devtools@latest --help
```

## Running Tests

### Option 1: Using pytest (Recommended for Development)

Run all tests (framework tests will pass, browser tests will be skipped if MCP server unavailable):
```bash
pytest streamlit_agent/tests/test_comprehensive_browser_automation.py -v
```

Run only framework tests (no MCP server required):
```bash
pytest streamlit_agent/tests/test_comprehensive_browser_automation.py -k "mock or framework or data_structures or factory" -v
```

Run with verbose output:
```bash
pytest streamlit_agent/tests/test_comprehensive_browser_automation.py -v -s
```

### Option 2: Using Standalone Test Runner

The standalone test runner provides more control and better reporting for browser automation tests.

Basic usage:
```bash
python streamlit_agent/run_browser_automation_tests.py
```

With options:
```bash
python streamlit_agent/run_browser_automation_tests.py \
    --app-url http://localhost:8501 \
    --timeout 60 \
    --verbose \
    --save-report test_results.json
```

Skip prerequisite checks (useful for testing):
```bash
python streamlit_agent/run_browser_automation_tests.py --skip-mcp-check --individual-tests
```

### Option 3: Using Test Automation Demo

For interactive testing and demonstration:
```bash
python streamlit_agent/test_automation_demo.py
```

## Test Configuration

### Environment Variables
- `SKIP_BROWSER_TESTS`: Set to `True` to skip all browser automation tests
- `MCP_SERVER_TIMEOUT`: Timeout for MCP server operations (default: 30 seconds)

### Test Parameters
- **App URL**: Target Streamlit application URL (default: http://localhost:8501)
- **Timeout**: Default timeout for operations (default: 30 seconds)
- **Test Queries**: Predefined queries for workflow testing

## Test Results and Reporting

### Test Output
Tests provide detailed output including:
- Test execution status (PASS/FAIL)
- Execution duration
- Error messages and details
- Screenshots (when browser automation is available)

### Report Generation
The standalone test runner can generate detailed JSON reports:
```bash
python streamlit_agent/run_browser_automation_tests.py --save-report detailed_report.json
```

Report includes:
- Test summary statistics
- Individual test results with details
- Screenshots and diagnostic information
- Performance metrics

### Screenshots
When browser automation is available, tests automatically capture screenshots:
- Stored in `test_screenshots/` directory
- Named with test name and timestamp
- Included in test results for debugging

## Troubleshooting

### Common Issues

#### 1. MCP Server Not Available
**Error**: `mcp-chrome-devtools was not found in the package registry`

**Solution**:
- Install uvx: `pip install uv`
- Verify uvx works: `uvx --help`
- Test MCP server: `uvx mcp-chrome-devtools@latest --help`

#### 2. Streamlit Application Not Running
**Error**: `Application accessibility check failed`

**Solution**:
- Start Streamlit application: `streamlit run streamlit_agent/app.py`
- Verify application is accessible: Open http://localhost:8501 in browser
- Check firewall and port availability

#### 3. Browser Automation Failures
**Error**: `Failed to setup browser automation environment`

**Solution**:
- Ensure Chrome/Chromium is installed
- Check that MCP server can launch browser
- Verify no other processes are using the browser automation

#### 4. Test Timeouts
**Error**: Tests timeout during execution

**Solution**:
- Increase timeout: `--timeout 60`
- Check system performance
- Verify application responsiveness

### Debug Mode

Enable verbose logging for detailed debugging:
```bash
python streamlit_agent/run_browser_automation_tests.py --verbose
```

Or with pytest:
```bash
pytest streamlit_agent/tests/test_comprehensive_browser_automation.py -v -s --log-cli-level=DEBUG
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Browser Automation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r streamlit_agent/requirements.txt
        pip install uv
    
    - name: Start Streamlit app
      run: |
        streamlit run streamlit_agent/app.py &
        sleep 10  # Wait for app to start
    
    - name: Run framework tests
      run: |
        pytest streamlit_agent/tests/test_comprehensive_browser_automation.py -k "mock or framework" -v
    
    - name: Run browser automation tests
      run: |
        python streamlit_agent/run_browser_automation_tests.py --save-report ci_results.json
    
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: ci_results.json
```

## Development Guidelines

### Adding New Tests

1. **Framework Tests**: Add to the main test class without MCP server dependency
2. **Browser Tests**: Add with `@skip_if_no_mcp_server` decorator
3. **Standalone Tests**: Add to the `BrowserAutomationTestRunner` class

### Test Structure
```python
@pytest.mark.asyncio
@skip_if_no_mcp_server  # For browser tests only
async def test_new_functionality(self, test_automation):
    """Test description and requirements validation"""
    # Setup
    setup_success = await test_automation.setup_browser()
    assert setup_success, "Browser setup failed"
    
    try:
        # Test logic
        result = await test_automation.some_test_method()
        
        # Assertions
        assert result.success, f"Test failed: {result.message}"
        
    finally:
        # Cleanup
        await test_automation.teardown_browser()
```

### Best Practices

1. **Always use try/finally**: Ensure browser cleanup even if tests fail
2. **Meaningful assertions**: Provide clear error messages
3. **Screenshot capture**: Take screenshots for debugging complex failures
4. **Timeout handling**: Set appropriate timeouts for different operations
5. **Error handling**: Handle MCP server unavailability gracefully

## Performance Considerations

### Test Execution Time
- Framework tests: < 5 seconds
- Browser automation tests: 30-120 seconds per test
- Full test suite: 5-10 minutes (depending on application responsiveness)

### Resource Usage
- Memory: ~100-200MB for browser automation
- CPU: Moderate during test execution
- Network: Minimal (local application testing)

### Optimization Tips
- Run framework tests first for quick feedback
- Use `--individual-tests` for faster iteration
- Increase timeouts for slower systems
- Run browser tests in parallel (with proper isolation)

## Conclusion

The browser automation test suite provides comprehensive validation of the Streamlit Agent application. It supports both development workflows (with mocked tests) and production validation (with full browser automation). The flexible architecture allows tests to run in various environments while providing detailed feedback and reporting capabilities.

For questions or issues, refer to the test code documentation or create an issue in the project repository.