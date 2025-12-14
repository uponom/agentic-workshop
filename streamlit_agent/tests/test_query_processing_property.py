#!/usr/bin/env python3
"""
Property-based tests for query processing and response display

**Feature: streamlit-agent, Property 1: Query processing and response display**
**Validates: Requirements 1.2, 1.3, 3.1**

This module contains property-based tests that verify the core functionality
of query processing and response display in the Streamlit agent application.
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis import assume
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import streamlit as st_app
from streamlit.testing.v1 import AppTest

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

# Import the app module and components
sys.path.append(str(Path(__file__).parent.parent))
import app
from components import QueryProcessor, AgentResponse


class TestQueryProcessingProperty:
    """Property-based tests for query processing and response display"""

    @given(st.text(min_size=3, max_size=1000))
    @settings(max_examples=10, deadline=None)
    def test_query_processing_and_response_display_property(self, query_text):
        """
        **Feature: streamlit-agent, Property 1: Query processing and response display**
        **Validates: Requirements 1.2, 1.3, 3.1**
        
        Property: For any valid user query, submitting it through the interface 
        should result in the agent processing the query and the complete response 
        being displayed in the web interface.
        
        This test verifies that:
        1. Valid queries are accepted and processed (Requirement 1.2)
        2. Agent responses are displayed in the web interface (Requirement 1.3)
        3. Text responses are displayed in readable format (Requirement 3.1)
        """
        # Filter out queries that are only whitespace or too short (invalid queries)
        assume(query_text.strip() != "")
        assume(len(query_text.strip()) >= 3)
        
        # Create a QueryProcessor instance for testing
        with patch('components.query_processor.MCPClient'), \
             patch('components.query_processor.Agent') as mock_agent_class:
            
            # Mock the agent to return a predictable response
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            mock_agent.return_value = f"Mock AWS architecture response for: {query_text[:50]}..."
            
            query_processor = QueryProcessor()
            
            # Test 1: Query validation accepts valid strings
            is_valid = query_processor.validate_query(query_text)
            assert is_valid == True, f"Valid query '{query_text[:50]}...' should pass validation"
            
            # Test 2: Query processing returns structured response
            with patch.object(query_processor, '_mcp_client'):
                response = query_processor.process_query(query_text.strip())
                
                # Verify response structure
                assert isinstance(response, AgentResponse)
                assert response.success == True
                assert isinstance(response.text, str)
                assert len(response.text) > 0
                assert response.error_message is None
                assert isinstance(response.generated_files, list)
                assert response.processing_time >= 0
                
                # Verify the response contains meaningful content
                assert len(response.text.strip()) > 0
                
            # Test 3: App validation function works with QueryProcessor
            with patch('app.st.session_state') as mock_session:
                mock_session.query_processor = query_processor
                is_app_valid = app.validate_query(query_text)
                assert is_app_valid == True

    @given(st.text(max_size=2))
    @settings(max_examples=5, deadline=None)
    def test_empty_query_rejection_property(self, short_query):
        """
        Property: For any empty, whitespace-only, or too short query, the system should 
        reject it and not process it through the agent.
        
        This validates the input validation requirements.
        """
        # Create QueryProcessor for testing
        with patch('components.query_processor.MCPClient'), \
             patch('components.query_processor.Agent'):
            
            query_processor = QueryProcessor()
            
            # Test various invalid queries
            test_queries = [short_query, "   ", "\t", "\n", "", "a", "ab"]
            
            for query in test_queries:
                is_valid = query_processor.validate_query(query)
                assert is_valid == False, f"Invalid query '{repr(query)}' should be rejected"
                
                # Test app validation function as well
                with patch('app.st.session_state') as mock_session:
                    mock_session.query_processor = query_processor
                    is_app_valid = app.validate_query(query)
                    assert is_app_valid == False, f"App should reject invalid query '{repr(query)}'"

    @given(st.text(min_size=3, max_size=500))
    @settings(max_examples=10, deadline=None)
    def test_session_state_management_property(self, query_text):
        """
        Property: For any valid query, the session state should properly 
        manage the query processing lifecycle.
        
        This validates that the application state is correctly maintained
        throughout the query processing workflow.
        """
        assume(query_text.strip() != "")
        assume(len(query_text.strip()) >= 3)
        
        # Create a mock session state object that behaves like Streamlit's session_state
        class MockSessionState(dict):
            def __getattr__(self, key):
                return self.get(key)
            
            def __setattr__(self, key, value):
                self[key] = value
        
        mock_session = MockSessionState()
        
        with patch('app.st.session_state', mock_session), \
             patch('components.query_processor.MCPClient'), \
             patch('components.query_processor.Agent'):
            
            # Initialize session state
            app.initialize_session_state()
            
            # Verify initial state
            assert mock_session.get('query_submitted', False) == False
            assert mock_session.get('current_query', "") == ""
            assert mock_session.get('processing', False) == False
            assert 'query_processor' in mock_session
            assert 'agent_response' in mock_session
            
            # Simulate query submission
            mock_session['current_query'] = query_text.strip()
            mock_session['processing'] = True
            mock_session['query_submitted'] = True
            
            # Verify state after submission
            assert mock_session['current_query'] == query_text.strip()
            assert mock_session['processing'] == True
            assert mock_session['query_submitted'] == True
            
            # Verify the stored query maintains its content
            stored_query = mock_session['current_query']
            assert len(stored_query) > 0
            assert stored_query == query_text.strip()
            
            # Verify QueryProcessor is available in session state
            assert mock_session['query_processor'] is not None

    def test_application_initialization_property(self):
        """
        Property: The application should initialize correctly and be ready 
        to process queries.
        
        This validates that all necessary components are properly set up.
        """
        # Create a mock session state object that behaves like Streamlit's session_state
        class MockSessionState(dict):
            def __getattr__(self, key):
                return self.get(key)
            
            def __setattr__(self, key, value):
                self[key] = value
        
        mock_session = MockSessionState()
        
        with patch('app.st.session_state', mock_session), \
             patch('os.makedirs') as mock_makedirs, \
             patch('components.query_processor.MCPClient'), \
             patch('components.query_processor.Agent'):
            
            # Test initialization
            app.initialize_session_state()
            
            # Verify session state is properly initialized
            expected_keys = ['query_submitted', 'current_query', 'processing', 'query_processor', 'agent_response']
            for key in expected_keys:
                assert key in mock_session
            
            # Verify initial values
            assert mock_session['query_submitted'] == False
            assert mock_session['current_query'] == ""
            assert mock_session['processing'] == False
            assert mock_session['query_processor'] is not None
            assert mock_session['agent_response'] is None
            
            # Verify QueryProcessor is properly initialized
            query_processor = mock_session['query_processor']
            assert hasattr(query_processor, 'validate_query')
            assert hasattr(query_processor, 'process_query')
            assert hasattr(query_processor, 'is_agent_available')


    @given(st.text(min_size=3, max_size=500))
    @settings(max_examples=10, deadline=None)
    def test_loading_indicator_display_property(self, query_text):
        """
        **Feature: streamlit-agent, Property 8: Loading indicator display**
        **Validates: Requirements 1.5**
        
        Property: For any query being processed, the system should display a loading 
        indicator during the processing period.
        
        This test verifies that:
        1. When processing starts, a loading indicator is shown (Requirement 1.5)
        2. The loading state is properly managed during query processing
        3. Processing status is correctly reflected in session state
        """
        # Filter out invalid queries
        assume(query_text.strip() != "")
        assume(len(query_text.strip()) >= 3)
        
        # Create a mock session state object that behaves like Streamlit's session_state
        class MockSessionState(dict):
            def __getattr__(self, key):
                return self.get(key)
            
            def __setattr__(self, key, value):
                self[key] = value
        
        mock_session = MockSessionState()
        
        with patch('app.st.session_state', mock_session), \
             patch('components.query_processor.MCPClient'), \
             patch('components.query_processor.Agent') as mock_agent_class, \
             patch('app.st.spinner') as mock_spinner, \
             patch('app.st.info') as mock_info, \
             patch('app.st.markdown') as mock_markdown:
            
            # Mock the agent to simulate processing time
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            mock_agent.return_value = f"Mock response for: {query_text[:50]}..."
            
            # Initialize session state
            app.initialize_session_state()
            
            # Verify initial state (not processing)
            assert mock_session.get('processing', False) == False
            
            # Simulate query submission and processing
            mock_session['current_query'] = query_text.strip()
            mock_session['processing'] = True
            mock_session['query_submitted'] = True
            
            # Test 1: Verify processing state is set to True during processing
            assert mock_session['processing'] == True
            assert mock_session['current_query'] == query_text.strip()
            assert mock_session['query_submitted'] == True
            
            # Test 2: Verify loading indicator is displayed when processing
            # Call the render_processing_status function which should show loading indicator
            app.render_processing_status()
            
            # Verify that loading-related UI elements were called
            # The function should call st.info with loading message when processing=True
            mock_info.assert_called()
            
            # Check that the info call contains loading-related text
            info_calls = [call for call in mock_info.call_args_list]
            loading_indicator_shown = any(
                "Processing" in str(call) or "🔄" in str(call) or "processing" in str(call).lower()
                for call in info_calls
            )
            assert loading_indicator_shown, "Loading indicator should be displayed during processing"
            
            # Test 3: Verify query content is displayed during processing
            markdown_calls = [call for call in mock_markdown.call_args_list]
            query_displayed = any(
                query_text.strip() in str(call) or "Your Query" in str(call)
                for call in markdown_calls
            )
            assert query_displayed, "Current query should be displayed during processing"
            
            # Test 4: Simulate processing completion
            mock_session['processing'] = False
            mock_response = AgentResponse(
                text=f"Completed response for: {query_text}",
                success=True,
                processing_time=1.5
            )
            mock_session['agent_response'] = mock_response
            
            # Clear previous mock calls
            mock_info.reset_mock()
            mock_markdown.reset_mock()
            
            # Call render_processing_status again (now with completed processing)
            app.render_processing_status()
            
            # Verify that loading indicator is no longer shown
            info_calls_after = [call for call in mock_info.call_args_list]
            loading_still_shown = any(
                "Processing" in str(call) and "🔄" in str(call)
                for call in info_calls_after
            )
            assert not loading_still_shown, "Loading indicator should not be shown after processing completes"
            
            # Test 5: Verify QueryProcessor processing state management
            query_processor = mock_session['query_processor']
            
            # Simulate processing state in QueryProcessor
            with patch.object(query_processor, '_current_state') as mock_state:
                mock_state.status = "processing"
                mock_state.query = query_text.strip()
                
                # Verify the processor reports processing status
                current_state = query_processor.get_current_state()
                assert current_state.status == "processing"
                assert current_state.query == query_text.strip()
                
                # Simulate completion
                mock_state.status = "completed"
                current_state = query_processor.get_current_state()
                assert current_state.status == "completed"

    @given(st.text(min_size=3, max_size=200))
    @settings(max_examples=5, deadline=None)
    def test_loading_indicator_spinner_integration_property(self, query_text):
        """
        **Feature: streamlit-agent, Property 8: Loading indicator display**
        **Validates: Requirements 1.5**
        
        Property: For any valid query, the Streamlit spinner loading indicator 
        should be properly activated during query processing.
        
        This test specifically verifies the st.spinner integration.
        """
        # Filter out invalid queries
        assume(query_text.strip() != "")
        assume(len(query_text.strip()) >= 3)
        
        with patch('components.query_processor.MCPClient'), \
             patch('components.query_processor.Agent') as mock_agent_class, \
             patch('app.st.spinner') as mock_spinner:
            
            # Mock the agent
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            mock_agent.return_value = f"Response for: {query_text}"
            
            # Create QueryProcessor
            query_processor = QueryProcessor()
            
            # Create a mock context manager for the spinner
            mock_spinner_context = Mock()
            mock_spinner_context.__enter__ = Mock(return_value=mock_spinner_context)
            mock_spinner_context.__exit__ = Mock(return_value=None)
            mock_spinner.return_value = mock_spinner_context
            
            # Mock session state
            class MockSessionState(dict):
                def __getattr__(self, key):
                    return self.get(key)
                
                def __setattr__(self, key, value):
                    self[key] = value
            
            mock_session = MockSessionState()
            mock_session['query_processor'] = query_processor
            mock_session['processing'] = False
            
            # Mock agent wrapper
            mock_agent_wrapper = Mock()
            mock_agent_wrapper.is_available.return_value = True
            mock_session['agent_wrapper'] = mock_agent_wrapper
            
            with patch('app.st.session_state', mock_session), \
                 patch('app.st.form_submit_button', return_value=True), \
                 patch('app.st.text_area', return_value=query_text), \
                 patch('app.st.form'), \
                 patch('app.validate_query', return_value=True):
                
                # Mock the synchronous processing method
                from components.agent_wrapper import AgentResult
                mock_result = AgentResult(
                    text=f"Response for: {query_text}",
                    success=True,
                    error_message=None,
                    generated_files=[],
                    processing_time=1.0
                )
                mock_agent_wrapper._process_query_sync.return_value = mock_result
                
                # Call render_query_form which should trigger spinner during processing
                result = app.render_query_form()
                
                # Verify spinner was called with appropriate loading message
                mock_spinner.assert_called()
                
                # Check that spinner was called with loading-related text
                spinner_calls = mock_spinner.call_args_list
                loading_message_used = any(
                    "Processing" in str(call) or "🔄" in str(call)
                    for call in spinner_calls
                )
                assert loading_message_used, "Spinner should be called with loading message"
                
                # Verify the spinner context manager was properly used
                mock_spinner_context.__enter__.assert_called()
                mock_spinner_context.__exit__.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])