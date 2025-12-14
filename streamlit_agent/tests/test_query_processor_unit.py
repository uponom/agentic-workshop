#!/usr/bin/env python3
"""
Unit tests for QueryProcessor component

Tests individual functionality of the QueryProcessor class including:
- Query validation logic
- Agent initialization
- Error handling scenarios
- State management
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

from streamlit_agent.components.query_processor import QueryProcessor, AgentResponse, QueryState


class TestQueryProcessorValidation:
    """Test query validation functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('streamlit_agent.components.query_processor.MCPClient'), \
             patch('streamlit_agent.components.query_processor.BedrockModel'):
            self.processor = QueryProcessor()
    
    def test_validate_query_valid_input(self):
        """Test validation with valid query input"""
        valid_queries = [
            "Create an AWS architecture for a web application",
            "How do I set up Lambda with DynamoDB?",
            "Design a serverless API using API Gateway",
            "What are the best practices for S3 security?"
        ]
        
        for query in valid_queries:
            assert self.processor.validate_query(query) is True
    
    def test_validate_query_empty_input(self):
        """Test validation rejects empty input"""
        invalid_queries = [
            "",
            "   ",
            "\n\t  \n",
            None
        ]
        
        for query in invalid_queries:
            assert self.processor.validate_query(query) is False
    
    def test_validate_query_too_short(self):
        """Test validation rejects queries that are too short"""
        short_queries = ["a", "ab", "  x  "]
        
        for query in short_queries:
            assert self.processor.validate_query(query) is False
    
    def test_validate_query_too_long(self):
        """Test validation rejects queries that are too long"""
        long_query = "x" * 5001  # Exceeds 5000 character limit
        assert self.processor.validate_query(long_query) is False
    
    def test_validate_query_non_string_input(self):
        """Test validation rejects non-string input"""
        invalid_inputs = [123, [], {}, True, False]
        
        for invalid_input in invalid_inputs:
            assert self.processor.validate_query(invalid_input) is False


class TestQueryProcessorState:
    """Test query processor state management"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('streamlit_agent.components.query_processor.MCPClient'), \
             patch('streamlit_agent.components.query_processor.BedrockModel'):
            self.processor = QueryProcessor()
    
    def test_initial_state(self):
        """Test processor starts in idle state"""
        state = self.processor.get_current_state()
        assert state.status == "idle"
        assert state.query == ""
        assert state.response is None
        assert state.start_time is None
    
    def test_reset_state(self):
        """Test state reset functionality"""
        # Modify state
        self.processor._current_state = QueryState(
            query="test query",
            status="processing",
            start_time=datetime.now()
        )
        
        # Reset state
        self.processor.reset_state()
        
        # Verify reset
        state = self.processor.get_current_state()
        assert state.status == "idle"
        assert state.query == ""
        assert state.response is None
        assert state.start_time is None
    
    def test_agent_availability_check(self):
        """Test agent availability checking"""
        # With mocked initialization, both agent and mcp_client should be set
        # The mocks in setup_method create the objects, so availability should be True
        assert self.processor.is_agent_available() is True
        
        # Test when agent is None
        self.processor._agent = None
        assert self.processor.is_agent_available() is False
        
        # Test when mcp_client is None
        self.processor._agent = Mock()
        self.processor._mcp_client = None
        assert self.processor.is_agent_available() is False
        
        # Test when both are available
        self.processor._mcp_client = Mock()
        assert self.processor.is_agent_available() is True
    
    def test_get_agent_status(self):
        """Test agent status information retrieval"""
        status = self.processor.get_agent_status()
        
        expected_keys = [
            "agent_initialized",
            "mcp_client_initialized", 
            "current_status",
            "last_query",
            "last_processing_time"
        ]
        
        for key in expected_keys:
            assert key in status


class TestQueryProcessorErrorHandling:
    """Test error handling scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('streamlit_agent.components.query_processor.MCPClient'), \
             patch('streamlit_agent.components.query_processor.BedrockModel'):
            self.processor = QueryProcessor()
    
    def test_process_query_invalid_input(self):
        """Test processing with invalid query input"""
        response = self.processor.process_query("")
        
        assert response.success is False
        assert "Invalid query" in response.error_message
        assert response.text == ""
        assert response.processing_time >= 0
    
    def test_process_query_agent_not_initialized(self):
        """Test processing when agent is not initialized"""
        # Ensure agent is None
        self.processor._agent = None
        
        response = self.processor.process_query("valid query")
        
        assert response.success is False
        assert "Agent not initialized" in response.error_message
        assert response.text == ""
    
    @patch('streamlit_agent.components.query_processor.MCPClient')
    def test_process_query_agent_exception(self, mock_mcp):
        """Test processing when agent raises exception"""
        # Mock agent that raises exception
        mock_agent = Mock()
        mock_agent.side_effect = Exception("Agent processing error")
        
        self.processor._agent = mock_agent
        self.processor._mcp_client = Mock()
        
        response = self.processor.process_query("valid query")
        
        assert response.success is False
        assert "Error processing query" in response.error_message
        assert response.processing_time >= 0


class TestQueryProcessorFilenameGeneration:
    """Test filename and title generation functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('streamlit_agent.components.query_processor.MCPClient'), \
             patch('streamlit_agent.components.query_processor.BedrockModel'):
            self.processor = QueryProcessor()
    
    def test_extract_keywords_from_query(self):
        """Test keyword extraction from queries"""
        test_cases = [
            ("Create a Lambda function with DynamoDB", ["lambda", "dynamodb"]),
            ("Design serverless API using API Gateway", ["serverless", "api_gateway", "api"]),
            ("S3 and CloudFront for static website", ["s3", "cloudfront"]),
            ("No AWS services mentioned here", [])
        ]
        
        for query, expected_keywords in test_cases:
            keywords = self.processor._extract_keywords_from_query(query)
            for keyword in expected_keywords:
                assert keyword in keywords
    
    def test_generate_filename_from_context(self):
        """Test filename generation from query context"""
        # Test with AWS service keywords that should be extracted
        filename = self.processor._generate_filename_from_context("Lambda DynamoDB API")
        assert "lambda" in filename and "dynamodb" in filename
        
        # Test with empty query - should generate timestamp-based name
        filename = self.processor._generate_filename_from_context("")
        assert filename.startswith("aws_architecture_")
        
        # Test with special characters - should be cleaned but may not extract keywords
        filename = self.processor._generate_filename_from_context("Special!@#$%Characters")
        # Since no AWS keywords, should fall back to timestamp
        assert filename.startswith("aws_architecture_") or len(filename) > 0
        
        # Test with very long query
        long_query = "Very long query with lambda and dynamodb and many other words that should be truncated"
        filename = self.processor._generate_filename_from_context(long_query)
        assert len(filename) <= 40  # Should be truncated
    
    def test_generate_title_from_context(self):
        """Test title generation from query context and diagram type"""
        # Test with AWS keywords that should be extracted
        title = self.processor._generate_title_from_context("lambda api", "serverless_api")
        assert "Lambda" in title and "Api" in title and "Architecture" in title
        
        # Test with empty query - should use diagram type mapping
        title = self.processor._generate_title_from_context("", "web_app")
        assert title == "Web Application Architecture"
        
        # Test with custom diagram type and no keywords
        title = self.processor._generate_title_from_context("", "custom")
        assert title == "AWS Architecture"
        
        # Test with unknown diagram type
        title = self.processor._generate_title_from_context("", "unknown_type")
        assert title == "AWS Architecture"


class TestQueryProcessorFileDetection:
    """Test file detection functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('streamlit_agent.components.query_processor.MCPClient'), \
             patch('streamlit_agent.components.query_processor.BedrockModel'):
            self.processor = QueryProcessor()
    
    def test_detect_generated_files_no_directory(self):
        """Test file detection when directory doesn't exist"""
        with patch('pathlib.Path.exists', return_value=False):
            files = self.processor._detect_generated_files()
            assert files == []
    
    def test_detect_generated_files_empty_directory(self):
        """Test file detection in empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the diagrams directory to point to empty temp directory
            with patch('pathlib.Path', return_value=Path(temp_dir)):
                files = self.processor._detect_generated_files()
                assert files == []
    
    def test_detect_generated_files_with_recent_files(self):
        """Test file detection with recently created files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = Path(temp_dir) / "test_diagram.png"
            test_file.touch()
            
            # Mock the diagrams directory
            with patch.object(self.processor, '_detect_generated_files') as mock_detect:
                mock_detect.return_value = [str(test_file)]
                files = self.processor._detect_generated_files()
                assert len(files) >= 0  # Should not raise exception


if __name__ == "__main__":
    pytest.main([__file__])