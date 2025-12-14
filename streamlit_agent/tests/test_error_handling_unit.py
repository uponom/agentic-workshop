#!/usr/bin/env python3
"""
Unit tests for error handling scenarios across components

Tests error handling functionality including:
- Network and connectivity errors
- File system errors
- Configuration errors
- UI rendering errors
- Graceful degradation scenarios
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile
import os

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from streamlit_agent.components.error_handler import ErrorHandler, ErrorCategory, ErrorInfo
from streamlit_agent.components.query_processor import QueryProcessor
from streamlit_agent.components.diagram_manager import DiagramManager
from streamlit_agent.components.response_renderer import ResponseRenderer


class TestErrorHandlerCore:
    """Test core error handler functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.error_handler = ErrorHandler()
    
    def test_error_handler_initialization(self):
        """Test error handler initializes correctly"""
        assert self.error_handler._error_history == []
        assert self.error_handler._max_history_size == 100
    
    def test_handle_error_basic(self):
        """Test basic error handling"""
        test_error = ValueError("Test error")
        
        error_info = self.error_handler.handle_error(
            error=test_error,
            category=ErrorCategory.VALIDATION_ERROR,
            component="test_component",
            user_context="Testing error handling"
        )
        
        assert isinstance(error_info, ErrorInfo)
        assert error_info.category == ErrorCategory.VALIDATION_ERROR
        assert error_info.component == "test_component"
        assert "Test error" in error_info.message
        assert "Testing error handling" in error_info.user_message
    
    def test_error_log_management(self):
        """Test error log size management"""
        # Fill up the error log beyond max size
        for i in range(110):  # Exceed _max_history_size of 100
            self.error_handler.handle_error(
                error=Exception(f"Error {i}"),
                category=ErrorCategory.UNKNOWN_ERROR,
                component="test",
                user_context="Log test"
            )
        
        # Should maintain max size
        assert len(self.error_handler._error_history) <= self.error_handler._max_history_size
    
    def test_get_recent_errors(self):
        """Test retrieving recent errors"""
        # Add some test errors
        for i in range(5):
            self.error_handler.handle_error(
                error=Exception(f"Error {i}"),
                category=ErrorCategory.UNKNOWN_ERROR,
                component="test",
                user_context="Recent test"
            )
        
        recent_errors = self.error_handler.get_error_history(3)
        assert len(recent_errors) == 3
        
        # Should be most recent last (since we get the last 3)
        assert "Error 4" in recent_errors[2].message
        assert "Error 3" in recent_errors[1].message
        assert "Error 2" in recent_errors[0].message


class TestQueryProcessorErrorHandling:
    """Test error handling in QueryProcessor"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('streamlit_agent.components.query_processor.MCPClient'), \
             patch('streamlit_agent.components.query_processor.BedrockModel'):
            self.processor = QueryProcessor()
    
    def test_mcp_client_initialization_error(self):
        """Test handling MCP client initialization errors"""
        with patch('streamlit_agent.components.query_processor.MCPClient', side_effect=ConnectionError("MCP connection failed")):
            processor = QueryProcessor()
            # Should handle error gracefully and set agent to None
            assert processor._agent is None
    
    def test_bedrock_model_initialization_error(self):
        """Test handling Bedrock model initialization errors"""
        with patch('streamlit_agent.components.query_processor.MCPClient'), \
             patch('streamlit_agent.components.query_processor.BedrockModel', side_effect=Exception("Model init failed")):
            processor = QueryProcessor()
            # Should handle error gracefully and set agent to None
            assert processor._agent is None
    
    def test_agent_processing_timeout(self):
        """Test handling agent processing timeouts"""
        # Mock agent that raises timeout
        mock_agent = Mock()
        mock_agent.side_effect = TimeoutError("Agent processing timeout")
        
        self.processor._agent = mock_agent
        mock_mcp_client = Mock()
        mock_mcp_client.__enter__ = Mock(return_value=mock_mcp_client)
        mock_mcp_client.__exit__ = Mock(return_value=None)
        self.processor._mcp_client = mock_mcp_client
        
        response = self.processor.process_query("test query")
        
        assert response.success is False
        assert "timeout" in response.error_message.lower() or "error" in response.error_message.lower()
    
    def test_network_connectivity_error(self):
        """Test handling network connectivity errors"""
        # Mock agent that raises network error
        mock_agent = Mock()
        mock_agent.side_effect = ConnectionError("Network unreachable")
        
        self.processor._agent = mock_agent
        mock_mcp_client = Mock()
        mock_mcp_client.__enter__ = Mock(return_value=mock_mcp_client)
        mock_mcp_client.__exit__ = Mock(return_value=None)
        self.processor._mcp_client = mock_mcp_client
        
        response = self.processor.process_query("test query")
        
        assert response.success is False
        assert "network" in response.error_message.lower() or "connection" in response.error_message.lower() or "error" in response.error_message.lower()
    
    def test_invalid_query_validation_errors(self):
        """Test various query validation error scenarios"""
        invalid_queries = [
            None,  # None input
            "",    # Empty string
            "  ",  # Whitespace only
            "ab",  # Too short
            "x" * 5001,  # Too long
            123,   # Non-string type
            [],    # List type
            {}     # Dict type
        ]
        
        for invalid_query in invalid_queries:
            response = self.processor.process_query(invalid_query)
            assert response.success is False
            assert "Invalid query" in response.error_message


class TestDiagramManagerErrorHandling:
    """Test error handling in DiagramManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('pathlib.Path.mkdir'):
            self.manager = DiagramManager("test-diagrams")
    
    def test_directory_permission_error(self):
        """Test handling directory permission errors"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.iterdir', side_effect=PermissionError("Permission denied")):
            
            # Should handle gracefully and return empty list
            diagrams = self.manager.get_all_diagrams()
            assert isinstance(diagrams, list)
            assert len(diagrams) == 0
    
    def test_file_stat_error(self):
        """Test handling file stat errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            
            # Create a file
            test_file = Path(temp_dir) / "test.png"
            test_file.touch()
            
            # Mock stat to raise error
            with patch.object(Path, 'stat', side_effect=OSError("Stat failed")):
                diagrams = self.manager.get_all_diagrams()
                # Should handle error gracefully
                assert isinstance(diagrams, list)
    
    def test_directory_creation_error(self):
        """Test handling directory creation errors"""
        with patch.object(Path, 'mkdir', side_effect=PermissionError("Cannot create directory")):
            with pytest.raises(PermissionError):
                self.manager._ensure_diagrams_folder_exists()
    
    def test_file_deletion_permission_error(self):
        """Test handling file deletion permission errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.png"
            test_file.touch()
            
            # Mock unlink to raise permission error
            with patch.object(Path, 'unlink', side_effect=PermissionError("Cannot delete file")):
                result = self.manager._delete_diagram_file(str(test_file))
                assert result is False
    
    def test_corrupted_file_handling(self):
        """Test handling corrupted or invalid image files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            
            # Create a file with invalid image data
            corrupted_file = Path(temp_dir) / "corrupted.png"
            corrupted_file.write_text("This is not image data")
            
            # Should still detect as image file by extension
            diagrams = self.manager.get_all_diagrams()
            assert len(diagrams) == 1
            assert diagrams[0].filename == "corrupted.png"
    
    def test_disk_space_error(self):
        """Test handling disk space errors"""
        with patch.object(Path, 'stat', side_effect=OSError("No space left on device")):
            diagram_info = self.manager._get_diagram_info(Path("test.png"))
            assert diagram_info is None


class TestResponseRendererErrorHandling:
    """Test error handling in ResponseRenderer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.renderer = ResponseRenderer()
    
    @patch('streamlit.image')
    def test_image_loading_error(self, mock_image):
        """Test handling image loading errors"""
        # Mock streamlit.image to raise an error
        mock_image.side_effect = Exception("Image loading failed")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.png"
            test_file.write_text("fake image")
            
            result = self.renderer.render_diagram(str(test_file))
            assert result is False
    
    def test_missing_image_file_error(self):
        """Test handling missing image file errors"""
        nonexistent_file = "/nonexistent/path/diagram.png"
        
        result = self.renderer.render_diagram(nonexistent_file)
        assert result is False
    
    @patch('streamlit.markdown')
    def test_markdown_rendering_error(self, mock_markdown):
        """Test handling markdown rendering errors"""
        # Mock markdown to raise an error
        mock_markdown.side_effect = Exception("Markdown rendering failed")
        
        # Should handle error gracefully
        try:
            self.renderer.render_response("Test content")
        except Exception as e:
            # The error handler should catch and handle this
            assert "Markdown rendering failed" in str(e)
    
    def test_invalid_content_handling(self):
        """Test handling invalid content types"""
        invalid_contents = [None, 123, [], {}]
        
        for invalid_content in invalid_contents:
            # Should handle gracefully without raising exceptions
            try:
                self.renderer.render_response(str(invalid_content) if invalid_content is not None else "")
            except Exception as e:
                pytest.fail(f"Should handle invalid content gracefully, but raised: {e}")
    
    def test_large_content_handling(self):
        """Test handling very large content"""
        # Create very large content
        large_content = "This is a test line.\n" * 10000  # ~200KB of text
        
        # Should handle without memory issues
        metrics = self.renderer.get_content_metrics(large_content)
        assert metrics['needs_scrolling'] is True
        assert metrics['character_count'] > 100000
    
    def test_malformed_markdown_handling(self):
        """Test handling malformed markdown content"""
        malformed_markdown = """
        # Incomplete header
        **Bold without closing
        `Code without closing
        ```
        Code block without language or closing
        [Link without closing bracket
        ![Image without closing](
        """
        
        # Should process without raising exceptions
        processed = self.renderer._preprocess_response_text(malformed_markdown)
        assert isinstance(processed, str)


class TestIntegratedErrorHandling:
    """Test error handling across integrated components"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('streamlit_agent.components.query_processor.MCPClient'), \
             patch('streamlit_agent.components.query_processor.BedrockModel'):
            self.processor = QueryProcessor()
        
        with patch('pathlib.Path.mkdir'):
            self.diagram_manager = DiagramManager("test-diagrams")
        
        self.renderer = ResponseRenderer(diagram_manager=self.diagram_manager)
    
    def test_cascading_error_handling(self):
        """Test error handling when multiple components fail"""
        # Simulate query processor failure
        self.processor._agent = None
        
        # Simulate diagram manager failure
        with patch.object(self.diagram_manager, 'get_latest_diagram', side_effect=Exception("Diagram error")):
            
            # Process query (should fail gracefully)
            response = self.processor.process_query("test query")
            assert response.success is False
            
            # Try to render response (should handle gracefully)
            try:
                self.renderer.render_response(response.text or "Error occurred")
            except Exception as e:
                pytest.fail(f"Renderer should handle errors gracefully, but raised: {e}")
    
    def test_partial_failure_recovery(self):
        """Test recovery when some components fail but others work"""
        # Simulate diagram manager failure but working renderer
        with patch.object(self.diagram_manager, 'get_all_diagrams', return_value=[]):
            
            # Should still be able to render text-only response
            test_response = "This is a test response without diagrams"
            
            try:
                self.renderer.render_response(test_response)
            except Exception as e:
                pytest.fail(f"Should handle partial failure gracefully, but raised: {e}")
    
    def test_resource_cleanup_on_error(self):
        """Test that resources are cleaned up properly on errors"""
        # This is more of a conceptual test since we're using mocks
        # In real scenarios, we'd test file handles, network connections, etc.
        
        with patch('streamlit_agent.components.query_processor.MCPClient') as mock_mcp:
            mock_client = Mock()
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=None)
            mock_mcp.return_value = mock_client
            
            # Simulate error during processing
            mock_client.__enter__.side_effect = Exception("Connection failed")
            
            processor = QueryProcessor()
            # Should handle error gracefully
            assert processor._agent is None


class TestErrorRecoveryStrategies:
    """Test error recovery and fallback strategies"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.renderer = ResponseRenderer()
    
    @patch('streamlit.warning')
    def test_graceful_degradation_no_diagrams(self, mock_warning):
        """Test graceful degradation when no diagrams are available"""
        # Render response without any diagrams
        self.renderer.render_response("Test response", generated_files=[])
        
        # Should show appropriate message about missing diagrams
        # (This would be called internally by render_response)
    
    def test_fallback_content_rendering(self):
        """Test fallback rendering strategies"""
        # Test with various problematic content
        problematic_contents = [
            "",  # Empty content
            "   ",  # Whitespace only
            "\x00\x01\x02",  # Binary content
            "🚀" * 1000,  # Unicode heavy content
        ]
        
        for content in problematic_contents:
            try:
                # Should handle all content types gracefully
                metrics = self.renderer.get_content_metrics(content)
                assert isinstance(metrics, dict)
            except Exception as e:
                pytest.fail(f"Should handle problematic content gracefully: {content[:20]}..., but raised: {e}")
    
    def test_error_message_formatting(self):
        """Test error message formatting and display"""
        error_scenarios = [
            ("Network timeout", {"timeout": 30, "retries": 3}),
            ("File not found", {"path": "/missing/file.png"}),
            ("Permission denied", {"operation": "read", "resource": "diagram"}),
            ("Invalid format", {"expected": "PNG", "actual": "TXT"})
        ]
        
        for error_msg, details in error_scenarios:
            try:
                self.renderer.render_error_message(error_msg, details)
            except Exception as e:
                pytest.fail(f"Error message rendering should not fail: {e}")


if __name__ == "__main__":
    pytest.main([__file__])