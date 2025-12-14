# Streamlit Agent Application

A Streamlit web application that provides a user-friendly interface to interact with the AWS Solutions Architect agent.

## Features

- **Interactive Web Interface**: Clean, responsive Streamlit-based UI
- **AWS Architecture Queries**: Submit questions and get expert architectural guidance
- **Visual Diagrams**: Automatically generated AWS architecture diagrams
- **Real-time Processing**: Live status updates during query processing
- **Browser Testing**: Automated end-to-end testing capabilities

## Project Structure

```
streamlit_agent/
├── app.py                 # Main application entry point
├── components/            # Core application components
│   └── __init__.py
├── tests/                 # Test suite
│   └── __init__.py
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r streamlit_agent/requirements.txt
```

2. Ensure the generated-diagrams directory exists (created automatically)

## Usage

Run the Streamlit application:

```bash
streamlit run streamlit_agent/app.py
```

The application will be available at `http://localhost:8501`

## Development

This application is built following the specification in `.kiro/specs/streamlit-agent/`:

- **Requirements**: See `requirements.md` for detailed functional requirements
- **Design**: See `design.md` for architecture and component design
- **Tasks**: See `tasks.md` for implementation plan

## Dependencies

- **Streamlit**: Web application framework
- **Strands Agents**: AI agent framework for AWS architecture guidance
- **MCP**: Model Context Protocol for tool integration
- **Diagrams**: Python library for generating architecture diagrams
- **Pytest/Hypothesis**: Testing frameworks for unit and property-based testing

## Testing

The application includes comprehensive testing:

- **Unit Tests**: Individual component functionality
- **Property-Based Tests**: Universal behavior validation
- **Browser Automation**: End-to-end workflow testing using Chrome DevTools MCP

Run tests with:
```bash
pytest streamlit_agent/tests/
```

## Requirements Validation

This implementation addresses the following requirements:

- **Requirement 4.1**: Application accessible via web browser ✅
- **Requirement 5.1**: Generated-diagrams directory creation ✅

Additional requirements will be implemented in subsequent tasks as per the implementation plan.