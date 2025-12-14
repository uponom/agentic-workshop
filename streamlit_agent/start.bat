@echo off
REM Streamlit Agent Application Startup Script (Windows)

setlocal enabledelayedexpansion

REM Get the directory where this script is located
cd /d "%~dp0"

echo ========================================
echo   Streamlit Agent Application Startup  
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Error: requirements.txt not found
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
python -c "import streamlit, strands" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies are already installed
)

REM Create necessary directories
echo Creating directories...
if not exist "generated-diagrams" mkdir "generated-diagrams"
if not exist "logs" mkdir "logs"
if not exist "test_screenshots" mkdir "test_screenshots"

REM Set environment variables for better Streamlit experience
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

REM Default values
set PORT=8501
set HOST=localhost
set DEBUG_MODE=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto start_app
if "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--host" (
    set HOST=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--debug" (
    set DEBUG_MODE=true
    shift
    goto parse_args
)
if "%~1"=="--help" (
    echo Usage: %0 [OPTIONS]
    echo Options:
    echo   --port PORT     Set the port ^(default: 8501^)
    echo   --host HOST     Set the host ^(default: localhost^)
    echo   --debug         Enable debug mode
    echo   --help          Show this help message
    pause
    exit /b 0
)
echo Unknown option: %~1
pause
exit /b 1

:start_app
REM Launch the application
echo Starting Streamlit Agent Application...
echo Application will be available at: http://%HOST%:%PORT%
echo Press Ctrl+C to stop the application

if "%DEBUG_MODE%"=="true" (
    python start.py --port %PORT% --host %HOST% --debug
) else (
    python start.py --port %PORT% --host %HOST%
)

if errorlevel 1 (
    echo Application failed to start
    pause
    exit /b 1
)

pause