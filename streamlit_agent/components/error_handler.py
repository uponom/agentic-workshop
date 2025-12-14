#!/usr/bin/env python3
"""
Error Handler Component

Provides centralized error handling, logging, and user-friendly error messages
for the Streamlit Agent application. This component implements error boundaries
for all major components and ensures graceful degradation when failures occur.

Key responsibilities:
- Centralized error logging and reporting
- User-friendly error message generation
- Error boundary implementation for components
- Graceful degradation strategies
- Error recovery mechanisms
"""

import logging
import traceback
import streamlit as st
from typing import Optional, Dict, Any, Callable, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    AGENT_ERROR = "agent_error"
    FILE_SYSTEM_ERROR = "file_system_error"
    DIAGRAM_ERROR = "diagram_error"
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    UI_ERROR = "ui_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorInfo:
    """Structured error information"""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    user_message: str
    technical_details: Optional[str] = None
    timestamp: datetime = None
    component: Optional[str] = None
    recovery_suggestions: Optional[list] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.recovery_suggestions is None:
            self.recovery_suggestions = []


class ErrorHandler:
    """
    Centralized error handling system for the Streamlit Agent application.
    
    Provides error boundaries, logging, user-friendly messages, and graceful
    degradation strategies for all application components.
    """
    
    def __init__(self):
        """Initialize the error handler with logging configuration"""
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self._error_history = []
        self._max_history_size = 100
    
    def _setup_logging(self):
        """Configure logging for error handling"""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure file handler for error logs
        error_log_file = logs_dir / "streamlit_agent_errors.log"
        file_handler = logging.FileHandler(error_log_file)
        file_handler.setLevel(logging.ERROR)
        
        # Configure formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
    
    def handle_error(self, 
                    error: Exception, 
                    category: ErrorCategory,
                    component: str,
                    user_context: str = "",
                    show_in_ui: bool = True,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM) -> ErrorInfo:
        """
        Handle an error with comprehensive logging and user feedback
        
        Args:
            error: The exception that occurred
            category: Category of the error
            component: Component where the error occurred
            user_context: Additional context for the user
            show_in_ui: Whether to display error in Streamlit UI
            severity: Severity level of the error
            
        Returns:
            ErrorInfo: Structured error information
        """
        # Create error info
        error_info = self._create_error_info(error, category, component, user_context, severity)
        
        # Log the error
        self._log_error(error_info, error)
        
        # Add to history
        self._add_to_history(error_info)
        
        # Display in UI if requested
        if show_in_ui:
            self._display_error_in_ui(error_info)
        
        return error_info
    
    def handle_file_system_error(self, 
                                error: Exception, 
                                operation: str, 
                                file_path: str = "",
                                show_in_ui: bool = True) -> ErrorInfo:
        """
        Handle file system related errors with specific messaging
        
        Args:
            error: The file system exception
            operation: The operation that failed (e.g., "read", "write", "delete")
            file_path: Path to the file that caused the error
            show_in_ui: Whether to display in UI
            
        Returns:
            ErrorInfo: Structured error information
        """
        user_context = f"File operation '{operation}' failed"
        if file_path:
            user_context += f" for file: {Path(file_path).name}"
        
        error_info = self.handle_error(
            error=error,
            category=ErrorCategory.FILE_SYSTEM_ERROR,
            component="file_system",
            user_context=user_context,
            show_in_ui=show_in_ui,
            severity=ErrorSeverity.MEDIUM
        )
        
        # Add specific recovery suggestions for file system errors
        error_info.recovery_suggestions.extend([
            "Check file permissions",
            "Verify the file path exists",
            "Ensure sufficient disk space",
            "Try refreshing the application"
        ])
        
        return error_info
    
    def handle_diagram_error(self, 
                           error: Exception, 
                           diagram_name: str = "",
                           show_in_ui: bool = True) -> ErrorInfo:
        """
        Handle diagram-related errors with specific messaging
        
        Args:
            error: The diagram-related exception
            diagram_name: Name of the diagram that failed
            show_in_ui: Whether to display in UI
            
        Returns:
            ErrorInfo: Structured error information
        """
        user_context = "Diagram processing failed"
        if diagram_name:
            user_context += f" for: {diagram_name}"
        
        error_info = self.handle_error(
            error=error,
            category=ErrorCategory.DIAGRAM_ERROR,
            component="diagram_manager",
            user_context=user_context,
            show_in_ui=show_in_ui,
            severity=ErrorSeverity.LOW
        )
        
        # Add specific recovery suggestions for diagram errors
        error_info.recovery_suggestions.extend([
            "Check if the diagram file exists",
            "Verify the file format is supported (PNG, JPG, etc.)",
            "Try regenerating the diagram",
            "Check available disk space"
        ])
        
        return error_info
    
    def handle_agent_error(self, 
                          error: Exception, 
                          query: str = "",
                          show_in_ui: bool = True) -> ErrorInfo:
        """
        Handle agent processing errors with specific messaging
        
        Args:
            error: The agent-related exception
            query: The query that caused the error
            show_in_ui: Whether to display in UI
            
        Returns:
            ErrorInfo: Structured error information
        """
        user_context = "Agent processing failed"
        if query:
            query_preview = query[:50] + "..." if len(query) > 50 else query
            user_context += f" for query: {query_preview}"
        
        error_info = self.handle_error(
            error=error,
            category=ErrorCategory.AGENT_ERROR,
            component="agent_wrapper",
            user_context=user_context,
            show_in_ui=show_in_ui,
            severity=ErrorSeverity.HIGH
        )
        
        # Add specific recovery suggestions for agent errors
        error_info.recovery_suggestions.extend([
            "Check your internet connection",
            "Try a simpler query",
            "Verify agent configuration",
            "Wait a moment and try again"
        ])
        
        return error_info
    
    def create_error_boundary(self, 
                            component_name: str, 
                            fallback_function: Optional[Callable] = None,
                            category: ErrorCategory = ErrorCategory.UI_ERROR):
        """
        Create an error boundary decorator for component functions
        
        Args:
            component_name: Name of the component being protected
            fallback_function: Optional fallback function to call on error
            category: Error category for classification
            
        Returns:
            Decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Handle the error
                    error_info = self.handle_error(
                        error=e,
                        category=category,
                        component=component_name,
                        user_context=f"Error in {component_name}",
                        show_in_ui=True,
                        severity=ErrorSeverity.MEDIUM
                    )
                    
                    # Call fallback function if provided
                    if fallback_function:
                        try:
                            return fallback_function(error_info, *args, **kwargs)
                        except Exception as fallback_error:
                            self.logger.error(f"Fallback function failed: {fallback_error}")
                    
                    # Return None or appropriate default value
                    return None
            
            return wrapper
        return decorator
    
    def _create_error_info(self, 
                          error: Exception, 
                          category: ErrorCategory, 
                          component: str, 
                          user_context: str,
                          severity: ErrorSeverity) -> ErrorInfo:
        """Create structured error information"""
        # Generate user-friendly message based on error type and category
        user_message = self._generate_user_friendly_message(error, category, user_context)
        
        # Get technical details
        technical_details = self._get_technical_details(error)
        
        return ErrorInfo(
            category=category,
            severity=severity,
            message=str(error),
            user_message=user_message,
            technical_details=technical_details,
            component=component,
            recovery_suggestions=self._get_default_recovery_suggestions(category)
        )
    
    def _generate_user_friendly_message(self, 
                                      error: Exception, 
                                      category: ErrorCategory, 
                                      user_context: str) -> str:
        """Generate user-friendly error messages"""
        error_type = type(error).__name__
        
        # Category-specific messages
        if category == ErrorCategory.FILE_SYSTEM_ERROR:
            if "permission" in str(error).lower():
                return f"Unable to access file due to permission restrictions. {user_context}"
            elif "not found" in str(error).lower():
                return f"The requested file could not be found. {user_context}"
            elif "disk" in str(error).lower() or "space" in str(error).lower():
                return f"Insufficient disk space for the operation. {user_context}"
            else:
                return f"A file system error occurred. {user_context}"
        
        elif category == ErrorCategory.DIAGRAM_ERROR:
            if "image" in str(error).lower():
                return f"Unable to load or display the diagram image. {user_context}"
            elif "format" in str(error).lower():
                return f"The diagram file format is not supported. {user_context}"
            else:
                return f"An error occurred while processing the diagram. {user_context}"
        
        elif category == ErrorCategory.AGENT_ERROR:
            if "timeout" in str(error).lower():
                return f"The request took too long to process. {user_context}"
            elif "connection" in str(error).lower() or "network" in str(error).lower():
                return f"Unable to connect to the agent service. {user_context}"
            elif "authentication" in str(error).lower() or "auth" in str(error).lower():
                return f"Authentication failed. Please check your credentials. {user_context}"
            else:
                return f"The agent encountered an error while processing your request. {user_context}"
        
        elif category == ErrorCategory.VALIDATION_ERROR:
            return f"The input provided is not valid. {user_context}"
        
        elif category == ErrorCategory.CONFIGURATION_ERROR:
            return f"There is a configuration issue that needs to be resolved. {user_context}"
        
        else:
            return f"An unexpected error occurred. {user_context}"
    
    def _get_technical_details(self, error: Exception) -> str:
        """Get technical details about the error"""
        return f"{type(error).__name__}: {str(error)}\n\nTraceback:\n{traceback.format_exc()}"
    
    def _get_default_recovery_suggestions(self, category: ErrorCategory) -> list:
        """Get default recovery suggestions based on error category"""
        suggestions = {
            ErrorCategory.FILE_SYSTEM_ERROR: [
                "Check file permissions and access rights",
                "Verify the file path is correct",
                "Ensure sufficient disk space is available"
            ],
            ErrorCategory.DIAGRAM_ERROR: [
                "Try refreshing the page",
                "Check if the diagram file exists",
                "Verify the file format is supported"
            ],
            ErrorCategory.AGENT_ERROR: [
                "Check your internet connection",
                "Try again in a few moments",
                "Verify your configuration settings"
            ],
            ErrorCategory.VALIDATION_ERROR: [
                "Check your input format",
                "Ensure all required fields are filled",
                "Review the input requirements"
            ],
            ErrorCategory.CONFIGURATION_ERROR: [
                "Check your configuration settings",
                "Verify all required dependencies are installed",
                "Restart the application"
            ]
        }
        
        return suggestions.get(category, ["Try refreshing the application", "Contact support if the issue persists"])
    
    def _log_error(self, error_info: ErrorInfo, original_error: Exception):
        """Log error information"""
        log_message = (
            f"[{error_info.category.value.upper()}] "
            f"{error_info.component}: {error_info.message}"
        )
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, exc_info=original_error)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, exc_info=original_error)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def _add_to_history(self, error_info: ErrorInfo):
        """Add error to history with size limit"""
        self._error_history.append(error_info)
        
        # Maintain history size limit
        if len(self._error_history) > self._max_history_size:
            self._error_history = self._error_history[-self._max_history_size:]
    
    def _display_error_in_ui(self, error_info: ErrorInfo):
        """Display error in Streamlit UI with appropriate styling"""
        # Choose appropriate Streamlit function based on severity
        if error_info.severity == ErrorSeverity.CRITICAL:
            st.error(f"🚨 **Critical Error**: {error_info.user_message}")
        elif error_info.severity == ErrorSeverity.HIGH:
            st.error(f"❌ **Error**: {error_info.user_message}")
        elif error_info.severity == ErrorSeverity.MEDIUM:
            st.warning(f"⚠️ **Warning**: {error_info.user_message}")
        else:
            st.info(f"ℹ️ **Notice**: {error_info.user_message}")
        
        # Show recovery suggestions if available
        if error_info.recovery_suggestions:
            with st.expander("🔧 Troubleshooting Suggestions"):
                for suggestion in error_info.recovery_suggestions:
                    st.markdown(f"• {suggestion}")
        
        # Show technical details in expandable section for debugging
        if error_info.technical_details and st.session_state.get('show_technical_details', False):
            with st.expander("🔍 Technical Details"):
                st.code(error_info.technical_details, language="text")
    
    def get_error_history(self, limit: int = 10) -> list:
        """Get recent error history"""
        return self._error_history[-limit:] if self._error_history else []
    
    def clear_error_history(self):
        """Clear error history"""
        self._error_history.clear()
        self.logger.info("Error history cleared")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        if not self._error_history:
            return {"total_errors": 0}
        
        # Count by category
        category_counts = {}
        severity_counts = {}
        component_counts = {}
        
        for error in self._error_history:
            # Count by category
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by severity
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by component
            component = error.component or "unknown"
            component_counts[component] = component_counts.get(component, 0) + 1
        
        return {
            "total_errors": len(self._error_history),
            "by_category": category_counts,
            "by_severity": severity_counts,
            "by_component": component_counts,
            "most_recent": self._error_history[-1].timestamp if self._error_history else None
        }
    
    def enable_debug_mode(self):
        """Enable debug mode to show technical details"""
        st.session_state['show_technical_details'] = True
        self.logger.info("Debug mode enabled - technical details will be shown")
    
    def disable_debug_mode(self):
        """Disable debug mode"""
        st.session_state['show_technical_details'] = False
        self.logger.info("Debug mode disabled")


# Global error handler instance
error_handler = ErrorHandler()


def with_error_boundary(component_name: str, 
                       fallback_function: Optional[Callable] = None,
                       category: ErrorCategory = ErrorCategory.UI_ERROR):
    """
    Convenience decorator for adding error boundaries to functions
    
    Args:
        component_name: Name of the component
        fallback_function: Optional fallback function
        category: Error category
        
    Returns:
        Decorator function
    """
    return error_handler.create_error_boundary(component_name, fallback_function, category)


def handle_graceful_degradation(error_info: ErrorInfo, *args, **kwargs):
    """
    Default graceful degradation handler that provides fallback UI
    
    Args:
        error_info: Error information
        *args, **kwargs: Original function arguments
    """
    st.warning(f"⚠️ Some functionality is temporarily unavailable: {error_info.user_message}")
    
    # Provide basic fallback UI
    if error_info.category == ErrorCategory.DIAGRAM_ERROR:
        st.info("📊 Diagram display is currently unavailable. The text response is still available above.")
    elif error_info.category == ErrorCategory.AGENT_ERROR:
        st.info("🤖 Agent processing is temporarily unavailable. Please try again later.")
    elif error_info.category == ErrorCategory.FILE_SYSTEM_ERROR:
        st.info("📁 File operations are temporarily unavailable. Some features may be limited.")
    
    return None