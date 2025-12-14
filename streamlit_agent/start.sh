#!/bin/bash
# Streamlit Agent Application Startup Script (Unix/Linux/macOS)

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Streamlit Agent Application Startup  ${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: requirements.txt not found${NC}"
    exit 1
fi

# Install dependencies if needed
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! python3 -c "import streamlit, strands" &> /dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip3 install -r requirements.txt
else
    echo -e "${GREEN}Dependencies are already installed${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p generated-diagrams
mkdir -p logs
mkdir -p test_screenshots

# Set environment variables for better Streamlit experience
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Parse command line arguments
PORT=8501
HOST="localhost"
DEBUG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --debug)
            DEBUG=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --port PORT     Set the port (default: 8501)"
            echo "  --host HOST     Set the host (default: localhost)"
            echo "  --debug         Enable debug mode"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Launch the application
echo -e "${GREEN}Starting Streamlit Agent Application...${NC}"
echo -e "${BLUE}Application will be available at: http://${HOST}:${PORT}${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the application${NC}"

if [ "$DEBUG" = true ]; then
    python3 start.py --port "$PORT" --host "$HOST" --debug
else
    python3 start.py --port "$PORT" --host "$HOST"
fi