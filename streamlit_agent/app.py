#!/usr/bin/env python3
"""
Streamlit Agent Application

Main entry point for the Streamlit web application that provides
a user-friendly interface to interact with the AWS Solutions Architect agent.

This application allows users to:
- Submit queries about AWS architecture
- View agent responses with proper formatting
- Display generated AWS architecture diagrams
- Monitor processing status in real-time

Usage:
    streamlit run streamlit_agent/app.py
"""

import streamlit as st
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path to import the agent
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import components
from components import (QueryProcessor, AgentResponse, QueryState, StreamlitAgentWrapper, 
                       AgentResult, ProcessingStatus, ResponseRenderer, DiagramManager, DiagramInfo,
                       error_handler, ErrorCategory, with_error_boundary, handle_graceful_degradation)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@with_error_boundary("app_initialization", handle_graceful_degradation, ErrorCategory.CONFIGURATION_ERROR)
def initialize_session_state():
    """Initialize Streamlit session state variables with error handling"""
    try:
        if 'query_submitted' not in st.session_state:
            st.session_state.query_submitted = False
        if 'current_query' not in st.session_state:
            st.session_state.current_query = ""
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'query_processor' not in st.session_state:
            st.session_state.query_processor = QueryProcessor()
        if 'agent_wrapper' not in st.session_state:
            st.session_state.agent_wrapper = StreamlitAgentWrapper(timeout_seconds=120)
        if 'agent_response' not in st.session_state:
            st.session_state.agent_response = None
        if 'current_status' not in st.session_state:
            st.session_state.current_status = None
        if 'diagram_manager' not in st.session_state:
            st.session_state.diagram_manager = DiagramManager()
        if 'response_renderer' not in st.session_state:
            st.session_state.response_renderer = ResponseRenderer(st.session_state.diagram_manager)
    except Exception as e:
        error_handler.handle_error(
            error=e,
            category=ErrorCategory.CONFIGURATION_ERROR,
            component="app_initialization",
            user_context="Failed to initialize application components",
            show_in_ui=True
        )
        raise

def validate_query(query: str) -> bool:
    """
    Validate user query input using QueryProcessor
    
    Args:
        query: User input string
        
    Returns:
        bool: True if query is valid, False otherwise
    """
    return st.session_state.query_processor.validate_query(query)

# Status callback removed - using synchronous processing

# Removed async processing function - now using synchronous processing directly

def render_header():
    """Render the application header with improved styling and visual hierarchy"""
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #ff9a00 0%, #ffad33 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .main-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .content-section {
        margin: 1.5rem 0;
        padding: 1rem;
        border-radius: 8px;
        background-color: #f8f9fa;
    }
    .status-indicator {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-ready {
        background-color: #d4edda;
        color: #155724;
    }
    .status-processing {
        background-color: #fff3cd;
        color: #856404;
    }
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with custom styling
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🏗️ AWS Solutions Architect Agent</div>
        <div class="main-subtitle">Expert AWS architecture guidance with visual diagrams</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        agent_status = "Ready" if st.session_state.agent_wrapper.is_available() else "Unavailable"
        status_class = "status-ready" if agent_status == "Ready" else "status-error"
        st.markdown(f'<span class="status-indicator {status_class}">🤖 Agent: {agent_status}</span>', unsafe_allow_html=True)
    
    with col2:
        diagram_manager = st.session_state.diagram_manager
        folder_info = diagram_manager.get_folder_info()
        diagram_count = folder_info.get('total_diagrams', 0)
        st.markdown(f'<span class="status-indicator status-ready">📊 Diagrams: {diagram_count}</span>', unsafe_allow_html=True)
    
    with col3:
        processing_status = "Processing" if st.session_state.get('processing', False) else "Ready"
        status_class = "status-processing" if processing_status == "Processing" else "status-ready"
        st.markdown(f'<span class="status-indicator {status_class}">⚡ Status: {processing_status}</span>', unsafe_allow_html=True)
    
    with col4:
        # Show current time for reference
        import datetime
        current_time = datetime.datetime.now().strftime('%H:%M')
        st.markdown(f'<span class="status-indicator status-ready">🕒 Time: {current_time}</span>', unsafe_allow_html=True)

def render_query_form():
    """
    Render the main query input form with validation and submission handling
    
    Returns:
        str: The submitted query if valid, None otherwise
    """
    st.markdown("### 💬 Ask Your AWS Architecture Question")
    
    # Create form for better UX and handling
    with st.form(key="query_form", clear_on_submit=False):
        query = st.text_area(
            "Enter your AWS architecture question:",
            placeholder="e.g., Design a serverless web application with user authentication and real-time features...",
            height=120,
            help="Describe your AWS architecture requirements, and the agent will provide recommendations and generate diagrams.",
            key="query_input"
        )
        
        # Form submission button
        submitted = st.form_submit_button(
            "🚀 Submit Query", 
            type="primary",
            use_container_width=True
        )
        
        # Handle form submission
        if submitted:
            if validate_query(query):
                st.session_state.query_submitted = True
                st.session_state.current_query = query.strip()
                st.session_state.processing = True
                st.session_state.current_status = None
                
                # Process query using agent wrapper
                try:
                    # Check if agent wrapper is available
                    if not st.session_state.agent_wrapper.is_available():
                        error_handler.handle_error(
                            error=RuntimeError("Agent is not ready"),
                            category=ErrorCategory.CONFIGURATION_ERROR,
                            component="query_form",
                            user_context="Agent initialization incomplete",
                            show_in_ui=True
                        )
                        st.session_state.processing = False
                        return None
                    
                    # Process query with spinner
                    with st.spinner("🔄 Processing your query..."):
                        # Use synchronous processing instead of async
                        agent_wrapper = st.session_state.agent_wrapper
                        result = agent_wrapper._process_query_sync(query.strip())
                        
                        # Convert AgentResult to AgentResponse for compatibility
                        response = AgentResponse(
                            text=result.text,
                            success=result.success,
                            error_message=result.error_message,
                            generated_files=result.generated_files,
                            processing_time=result.processing_time
                        )
                        
                        st.session_state.agent_response = response
                        st.session_state.processing = False
                        st.session_state.current_status = None
                        
                        # Force UI update to show results
                        st.rerun()
                
                except Exception as e:
                    error_handler.handle_agent_error(
                        error=e,
                        query=query,
                        show_in_ui=True
                    )
                    st.session_state.processing = False
                    st.session_state.current_status = None
                    return None
                
                return query.strip()
            else:
                st.error("⚠️ Please enter a valid query (3-5000 characters with meaningful content).")
                return None
    
    return None

def render_processing_status():
    """Render processing status and feedback with coordinated layout"""
    if st.session_state.get('processing', False):
        # Create coordinated layout for processing status
        render_processing_layout()
    
    # Show agent response if available
    elif st.session_state.get('agent_response'):
        response = st.session_state.agent_response
        
        if response.success:
            # Create coordinated layout for successful response
            render_success_layout(response)
        else:
            # Create coordinated layout for error response
            render_error_layout(response)

def render_processing_layout():
    """Render processing status in coordinated layout"""
    # Create main content area with proper spacing
    st.markdown("### ⏳ Processing Your Query")
    
    # Show query in a highlighted container
    if st.session_state.get('current_query'):
        with st.container():
            st.markdown("**Your Query:**")
            st.info(f"💭 {st.session_state.current_query}")
    
    # Create two-column layout for status and progress
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show current status if available
        current_status = st.session_state.get('current_status')
        if current_status:
            # Display status with progress bar
            progress_bar = st.progress(current_status.progress)
            status_text = f"**{current_status.stage.replace('_', ' ').title()}:** {current_status.message}"
            st.markdown(status_text)
            
            # Show timestamp
            st.caption(f"Last update: {current_status.timestamp.strftime('%H:%M:%S')}")
            
            # Show details if available
            if current_status.details:
                with st.expander("📋 Processing Details"):
                    for key, value in current_status.details.items():
                        st.text(f"{key}: {value}")
        else:
            # Show loading animation and message
            with st.spinner("Processing..."):
                st.info("🔄 Processing your query with the AWS Solutions Architect agent...")
    
    with col2:
        # Show processing indicators and tips
        st.markdown("**💡 Processing Tips**")
        st.markdown("""
        - Complex queries may take longer
        - Diagrams are generated automatically
        - You'll see real-time status updates
        """)
        
        # Show estimated time if available
        if st.session_state.get('current_status'):
            st.metric("Progress", f"{st.session_state.current_status.progress:.0%}")

def render_success_layout(response):
    """Render successful response in coordinated layout"""
    # Header with processing time
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### ✅ AWS Architecture Guidance")
    with col2:
        st.metric("Processing Time", f"{response.processing_time:.2f}s")
    
    # Use ResponseRenderer for coordinated content display
    renderer = st.session_state.response_renderer
    renderer.render_response(response.text, response.generated_files)
    
    # Action buttons in a coordinated layout
    render_action_buttons()

def render_error_layout(response):
    """Render error response in coordinated layout"""
    st.markdown("### ❌ Processing Error")
    
    # Create two-column layout for error details
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Use ResponseRenderer to display error
        renderer = st.session_state.response_renderer
        error_details = {
            "Processing Time": f"{response.processing_time:.2f} seconds" if response.processing_time > 0 else "N/A",
            "Error Type": type(response.error_message).__name__ if response.error_message else "Unknown"
        }
        renderer.render_error_message(response.error_message or "Unknown error occurred", error_details)
    
    with col2:
        # Show troubleshooting tips
        st.markdown("**🔧 Troubleshooting**")
        st.markdown("""
        - Check your query format
        - Ensure agent is available
        - Try a simpler query first
        - Check network connectivity
        """)
    
    # Action buttons
    render_action_buttons()

def render_action_buttons():
    """Render action buttons in coordinated layout"""
    st.markdown("---")
    
    # Create button layout
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("🔄 New Query", type="primary", use_container_width=True):
            reset_application_state()
    
    with col2:
        if st.button("📊 View All Diagrams", use_container_width=True):
            show_diagram_gallery()
    
    with col3:
        # Show quick stats
        diagram_manager = st.session_state.diagram_manager
        folder_info = diagram_manager.get_folder_info()
        st.caption(f"📁 {folder_info.get('total_diagrams', 0)} diagrams available")

def reset_application_state():
    """Reset application state for new query"""
    st.session_state.processing = False
    st.session_state.query_submitted = False
    st.session_state.current_query = ""
    st.session_state.agent_response = None
    st.session_state.current_status = None
    st.session_state.query_processor.reset_state()
    st.rerun()

def show_diagram_gallery():
    """Show diagram gallery in sidebar or modal"""
    diagram_manager = st.session_state.diagram_manager
    diagrams = diagram_manager.get_all_diagrams(force_refresh=True)
    
    if diagrams:
        with st.sidebar:
            st.markdown("### 🖼️ Diagram Gallery")
            renderer = st.session_state.response_renderer
            renderer.render_diagram_gallery(diagrams, max_display=5)
    else:
        st.info("No diagrams available to display")

def render_application_status():
    """Render application status information"""
    st.markdown("---")
    st.markdown("### 📊 Application Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Check diagram manager status
        diagram_manager = st.session_state.diagram_manager
        folder_info = diagram_manager.get_folder_info()
        diagrams_status = "✅ Ready" if folder_info['folder_exists'] else "❌ Missing"
        st.metric("Generated Diagrams Folder", diagrams_status)
    
    with col2:
        # Check agent status using agent wrapper
        agent_available = st.session_state.agent_wrapper.is_available()
        agent_status = "✅ Ready" if agent_available else "❌ Not Available"
        st.metric("Agent Integration", agent_status)
    
    with col3:
        st.metric("Browser Testing", "🚧 Pending")
    
    # Show detailed agent status in expander
    with st.expander("🔍 Detailed Agent Status"):
        # Show agent wrapper status
        wrapper_status = st.session_state.agent_wrapper.get_status_info()
        st.markdown("**Agent Wrapper Status:**")
        for key, value in wrapper_status.items():
            if value is not None:
                st.text(f"{key.replace('_', ' ').title()}: {value}")
        
        # Show diagram manager status
        st.markdown("**Diagram Manager Status:**")
        diagram_status = st.session_state.diagram_manager.get_status_summary()
        for key, value in diagram_status.items():
            if value is not None:
                st.text(f"{key.replace('_', ' ').title()}: {value}")
        
        # Show legacy query processor status for comparison
        st.markdown("**Legacy Query Processor Status:**")
        processor_status = st.session_state.query_processor.get_agent_status()
        for key, value in processor_status.items():
            if value is not None:
                st.text(f"{key.replace('_', ' ').title()}: {value}")

def cleanup_resources():
    """Cleanup resources when the app shuts down with comprehensive error handling"""
    try:
        if 'agent_wrapper' in st.session_state:
            st.session_state.agent_wrapper.shutdown()
    except Exception as e:
        error_handler.handle_error(
            error=e,
            category=ErrorCategory.CONFIGURATION_ERROR,
            component="cleanup",
            user_context="Error during application cleanup",
            show_in_ui=False  # Don't show UI errors during cleanup
        )

@with_error_boundary("main_application", handle_graceful_degradation, ErrorCategory.UI_ERROR)
def main():
    """Main application entry point with coordinated layout and comprehensive error handling"""
    
    try:
        # Configure Streamlit page with responsive layout
        st.set_page_config(
            page_title="AWS Solutions Architect Agent",
            page_icon="🏗️",
            layout="wide",
            initial_sidebar_state="auto"
        )
        
        # Initialize session state
        initialize_session_state()
        
        # Create required directories if they don't exist
        required_dirs = ["generated-diagrams", "logs", "test_screenshots"]
        for dir_name in required_dirs:
            try:
                os.makedirs(dir_name, exist_ok=True)
            except Exception as dir_error:
                error_handler.handle_file_system_error(
                    error=dir_error,
                    operation="create_directory",
                    file_path=dir_name,
                    show_in_ui=True
                )
        
        # Also create global generated-diagrams directory for compatibility
        try:
            global_diagrams_dir = Path.cwd() / "generated-diagrams"
            global_diagrams_dir.mkdir(parents=True, exist_ok=True)
        except Exception as dir_error:
            logger.warning(f"Could not create global diagrams directory: {dir_error}")
        
        # Render application with coordinated layout
        render_coordinated_application()
        
        # Register cleanup function (Streamlit doesn't have a built-in cleanup mechanism,
        # but this helps with proper resource management during development)
        import atexit
        atexit.register(cleanup_resources)
        
    except Exception as e:
        error_handler.handle_error(
            error=e,
            category=ErrorCategory.UI_ERROR,
            component="main_application",
            user_context="Critical application error",
            show_in_ui=True
        )
        # Provide minimal fallback UI
        st.error("🚨 Critical application error occurred. Please refresh the page.")
        st.text_area("Error Details", str(e), height=100)

def render_coordinated_application():
    """Render the complete application with coordinated layout and visual hierarchy"""
    
    # Header section
    render_header()
    
    # Main content area with proper spacing and visual hierarchy
    main_container = st.container()
    
    with main_container:
        # Determine application state and render appropriate layout
        if st.session_state.get('processing', False) or st.session_state.get('agent_response'):
            # Results/Processing layout - full width for better content display
            render_results_layout()
        else:
            # Input layout - centered and focused
            render_input_layout()
    
    # Sidebar for additional information and controls
    render_sidebar()
    
    # Footer with application status (collapsed by default)
    with st.expander("📊 Application Status", expanded=False):
        render_application_status()

def render_input_layout():
    """Render input-focused layout for query submission"""
    # Center the input form with proper spacing
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        render_query_form()
    
    # Show recent diagrams preview if available
    diagram_manager = st.session_state.diagram_manager
    all_diagrams = diagram_manager.get_all_diagrams()
    
    if all_diagrams:
        # Sort diagrams by creation time (most recent first)
        recent_diagrams = sorted(all_diagrams, key=lambda d: d.created_at, reverse=True)
        
        st.markdown("---")
        st.markdown("### 🖼️ Recent Architecture Diagrams")
        
        # Show up to 3 most recent diagrams in a grid
        cols = st.columns(min(3, len(recent_diagrams)))
        for i, diagram in enumerate(recent_diagrams[:3]):
            with cols[i]:
                try:
                    # Check if file exists before trying to display
                    if not os.path.exists(diagram.filepath):
                        st.warning(f"📁 {diagram.title}")
                        st.caption(f"File not found: {diagram.filename}")
                        continue
                    
                    st.image(
                        diagram.filepath,
                        caption=diagram.title
                        # Use default width (auto-fit to container)
                    )
                    st.caption(f"📅 {diagram.created_at.strftime('%H:%M')}")
                except Exception as e:
                    logger.error(f"Error loading diagram {diagram.filename}: {e}")
                    st.warning(f"📁 {diagram.title}")
                    st.caption(f"Unable to load image")

def render_results_layout():
    """Render results-focused layout for displaying responses and diagrams"""
    # Full-width layout for results
    render_processing_status()

def render_sidebar():
    """Render sidebar with additional controls and information"""
    with st.sidebar:
        st.markdown("### 🛠️ Controls")
        
        # Quick actions
        if st.button("🔄 Reset Application", use_container_width=True):
            reset_application_state()
        
        if st.button("🧹 Clear Diagrams", use_container_width=True):
            clear_diagrams_with_confirmation()
        
        # Error handling controls
        st.markdown("---")
        st.markdown("### 🔧 Error Handling")
        
        # Debug mode toggle
        debug_mode = st.session_state.get('show_technical_details', False)
        if st.checkbox("Debug Mode", value=debug_mode):
            error_handler.enable_debug_mode()
        else:
            error_handler.disable_debug_mode()
        
        # Error statistics
        error_stats = error_handler.get_error_statistics()
        if error_stats['total_errors'] > 0:
            st.metric("Total Errors", error_stats['total_errors'])
            
            with st.expander("📊 Error Details"):
                if 'by_severity' in error_stats:
                    st.markdown("**By Severity:**")
                    for severity, count in error_stats['by_severity'].items():
                        st.text(f"• {severity.title()}: {count}")
                
                if 'by_category' in error_stats:
                    st.markdown("**By Category:**")
                    for category, count in error_stats['by_category'].items():
                        st.text(f"• {category.replace('_', ' ').title()}: {count}")
        
        # Clear error history button
        if error_stats['total_errors'] > 0:
            if st.button("🗑️ Clear Error History", use_container_width=True):
                error_handler.clear_error_history()
                st.rerun()
        
        # Application metrics
        st.markdown("---")
        st.markdown("### 📈 Metrics")
        
        # Get current metrics with error handling
        try:
            diagram_manager = st.session_state.diagram_manager
            folder_info = diagram_manager.get_folder_info()
            
            st.metric("Total Diagrams", folder_info.get('total_diagrams', 0))
            
            if folder_info.get('total_size_bytes', 0) > 0:
                size_mb = folder_info['total_size_bytes'] / (1024 * 1024)
                st.metric("Storage Used", f"{size_mb:.1f} MB")
        except Exception as e:
            st.error("Unable to load diagram metrics")
        
        # Agent status with error handling
        try:
            agent_available = st.session_state.agent_wrapper.is_available()
            status_color = "🟢" if agent_available else "🔴"
            st.metric("Agent Status", f"{status_color} {'Ready' if agent_available else 'Unavailable'}")
        except Exception as e:
            st.error("Unable to check agent status")
        
        # Show processing history if available
        if hasattr(st.session_state, 'processing_history'):
            st.markdown("---")
            st.markdown("### 📋 Recent Queries")
            for i, query in enumerate(st.session_state.processing_history[-3:]):
                st.caption(f"{i+1}. {query[:50]}...")

def clear_diagrams_with_confirmation():
    """Clear diagrams with user confirmation"""
    diagram_manager = st.session_state.diagram_manager
    folder_info = diagram_manager.get_folder_info()
    
    if folder_info.get('total_diagrams', 0) > 0:
        if st.button("⚠️ Confirm Clear All Diagrams"):
            deleted_count = diagram_manager.cleanup_old_diagrams(max_age_hours=0, max_count=0)
            st.success(f"Cleared {deleted_count} diagrams")
            st.rerun()
    else:
        st.info("No diagrams to clear")

if __name__ == "__main__":
    main()