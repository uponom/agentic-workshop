"""
Components module for Streamlit Agent application.

This module contains all the core components used by the Streamlit application
to provide a clean separation of concerns and maintainable code structure.

Available components:
- QueryProcessor: Handles user input validation and agent communication
- StreamlitAgentWrapper: Async wrapper for agent integration with status updates
- ResponseRenderer: Formats and displays agent responses with markdown support
- DiagramManager: Manages diagram file detection and display (to be implemented)
- TestAutomation: Provides browser automation testing capabilities (to be implemented)
"""

from .query_processor import QueryProcessor, AgentResponse, QueryState
from .agent_wrapper import StreamlitAgentWrapper, AgentResult, ProcessingStatus
from .response_renderer import ResponseRenderer
from .diagram_manager import DiagramManager, DiagramInfo
from .error_handler import ErrorHandler, ErrorInfo, ErrorCategory, ErrorSeverity, error_handler, with_error_boundary, handle_graceful_degradation

__all__ = [
    'QueryProcessor', 'AgentResponse', 'QueryState',
    'StreamlitAgentWrapper', 'AgentResult', 'ProcessingStatus',
    'ResponseRenderer', 'DiagramManager', 'DiagramInfo',
    'ErrorHandler', 'ErrorInfo', 'ErrorCategory', 'ErrorSeverity', 
    'error_handler', 'with_error_boundary', 'handle_graceful_degradation'
]