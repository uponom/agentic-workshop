#!/usr/bin/env python3
"""
QueryProcessor Component

Handles query validation, agent integration, and error handling for the Streamlit Agent application.
This component serves as the bridge between the Streamlit UI and the underlying Strands agent.

Key responsibilities:
- Validate user queries before processing
- Execute agent calls with proper error handling
- Manage query state and processing status
- Provide structured responses for UI consumption
"""

import os
import sys
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from contextlib import contextmanager

# Add parent directory to path for agent imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from strands.tools import tool
from .error_handler import error_handler, ErrorCategory, with_error_boundary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Structured response from agent processing"""
    text: str
    success: bool
    error_message: Optional[str] = None
    generated_files: List[str] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.generated_files is None:
            self.generated_files = []


@dataclass
class QueryState:
    """Current state of query processing"""
    query: str
    status: str  # 'idle', 'processing', 'completed', 'error'
    response: Optional[AgentResponse] = None
    start_time: Optional[datetime] = None


class QueryProcessor:
    """
    Handles query processing and agent integration for the Streamlit application.
    
    This component manages the complete lifecycle of user queries from validation
    through agent processing to response formatting.
    """
    
    def __init__(self):
        """Initialize the QueryProcessor with agent configuration"""
        self._agent = None
        self._mcp_client = None
        self._current_state = QueryState(query="", status="idle")
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the Strands agent with MCP client and tools with comprehensive error handling"""
        try:
            # Create MCP client for AWS documentation
            try:
                self._mcp_client = MCPClient(
                    lambda: stdio_client(
                        StdioServerParameters(
                            command="uvx", 
                            args=["awslabs.aws-documentation-mcp-server@latest"]
                        )
                    )
                )
            except Exception as mcp_error:
                error_handler.handle_error(
                    error=mcp_error,
                    category=ErrorCategory.NETWORK_ERROR,
                    component="query_processor",
                    user_context="Failed to initialize MCP client",
                    show_in_ui=False
                )
                raise
            
            # Initialize Bedrock model
            try:
                bedrock_model = BedrockModel(
                    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
                    temperature=0.7,
                )
            except Exception as model_error:
                error_handler.handle_error(
                    error=model_error,
                    category=ErrorCategory.CONFIGURATION_ERROR,
                    component="query_processor",
                    user_context="Failed to initialize Bedrock model",
                    show_in_ui=False
                )
                raise
            
            # Create diagram generation tool
            diagram_tool = self._create_diagram_tool()
            
            # System prompt for the agent
            system_prompt = """
            You are an expert AWS Solutions Architect. Your task is to help clients understand 
            AWS best practices and create architectural diagrams.

            Available tools:
            📚 AWS Documentation:
            - read_documentation: Get information about specific AWS services
            - search_documentation: Find relevant topics in AWS documentation
            - recommend: Get architectural recommendations

            🎨 Diagram Creation:
            - create_aws_diagram: Creates diagrams locally (ONLY tool for diagrams!)

            CRITICAL REQUIREMENTS:
            1. You MUST create a visual diagram for each architectural request using ONLY create_aws_diagram
            2. DO NOT use other tools for creating diagrams
            3. ALWAYS call create_aws_diagram FIRST before detailed explanation

            Available diagram types for create_aws_diagram:
            - "static_website": S3 + CloudFront + Lambda
            - "serverless_api": API Gateway + Lambda + DynamoDB  
            - "web_app": Full web architecture
            - "music_streaming": Music streaming platform architecture (for Spotify-like platforms)
            - "custom": Simple custom architecture

            Mandatory workflow:
            1. Call: create_aws_diagram(diagram_type="appropriate_type", query_context="user's original query")
            2. Then provide detailed architectural explanation

            Always pass the original user query as query_context for automatic file naming.
            Always provide comprehensive architectural guidance with best practices and working diagram files.
            """
            
            # Initialize agent with MCP client context
            try:
                with self._mcp_client:
                    mcp_tools = self._mcp_client.list_tools_sync()
                    all_tools = mcp_tools + [diagram_tool]
                    
                    self._agent = Agent(
                        tools=all_tools, 
                        model=bedrock_model, 
                        system_prompt=system_prompt
                    )
            except Exception as agent_error:
                error_handler.handle_error(
                    error=agent_error,
                    category=ErrorCategory.CONFIGURATION_ERROR,
                    component="query_processor",
                    user_context="Failed to initialize agent with tools",
                    show_in_ui=False
                )
                raise
                
            logger.info("QueryProcessor initialized successfully")
            
        except Exception as e:
            error_handler.handle_error(
                error=e,
                category=ErrorCategory.CONFIGURATION_ERROR,
                component="query_processor",
                user_context="Failed to initialize QueryProcessor",
                show_in_ui=False
            )
            self._agent = None
    
    def _create_diagram_tool(self):
        """Create the local diagram generation tool"""
        
        @tool
        def create_aws_diagram(diagram_type: str, query_context: str = "") -> str:
            """
            Creates AWS architecture diagrams locally using Python diagrams library
            
            Args:
                diagram_type: Type of diagram - "static_website", "serverless_api", "web_app", "music_streaming", or "custom"
                query_context: Original user query for generating filename and title
            
            Returns:
                Success message with file path and generated filename
            """
            try:
                from diagrams import Diagram
                from diagrams.aws.compute import Lambda
                from diagrams.aws.storage import S3
                from diagrams.aws.network import CloudFront, APIGateway
                from diagrams.aws.database import RDS, Dynamodb
                from diagrams.onprem.client import Users
                
                # Generate filename and title based on context
                filename = self._generate_filename_from_context(query_context)
                title = self._generate_title_from_context(query_context, diagram_type)
                
                # Ensure generated-diagrams directory exists
                os.makedirs("generated-diagrams", exist_ok=True)
                filepath = f"generated-diagrams/{filename}"
                
                # Add Graphviz to PATH if on Windows
                if os.name == 'nt':
                    os.environ['PATH'] += ";C:\\Program Files\\Graphviz\\bin"
                
                # Create diagram based on type
                if diagram_type == "static_website":
                    with Diagram(title, show=False, filename=filepath, direction="TB"):
                        users = Users("Website Visitors")
                        cloudfront = CloudFront("CloudFront CDN")
                        s3 = S3("S3 Static Website")
                        lambda_api = Lambda("Lambda API")
                        
                        users >> cloudfront >> s3
                        users >> cloudfront >> lambda_api
                        
                elif diagram_type == "serverless_api":
                    with Diagram(title, show=False, filename=filepath, direction="LR"):
                        users = Users("API Clients")
                        api_gateway = APIGateway("API Gateway")
                        lambda_func = Lambda("Lambda Function")
                        dynamodb = Dynamodb("DynamoDB")
                        
                        users >> api_gateway >> lambda_func >> dynamodb
                        
                elif diagram_type == "web_app":
                    with Diagram(title, show=False, filename=filepath, direction="TB"):
                        users = Users("Users")
                        cloudfront = CloudFront("CloudFront")
                        s3_frontend = S3("S3 Frontend")
                        lambda_api = Lambda("Lambda API")
                        database = RDS("RDS Database")
                        
                        users >> cloudfront >> s3_frontend
                        users >> cloudfront >> lambda_api >> database
                        
                elif diagram_type == "music_streaming":
                    with Diagram(title, show=False, filename=filepath, direction="TB"):
                        users = Users("Music Listeners")
                        cloudfront = CloudFront("CloudFront CDN")
                        s3_music = S3("S3 Music Storage")
                        api_gateway = APIGateway("API Gateway")
                        lambda_streaming = Lambda("Streaming Service")
                        lambda_playlist = Lambda("Playlist Service")
                        dynamodb = Dynamodb("DynamoDB")
                        rds = RDS("Music Catalog")
                        
                        users >> cloudfront >> s3_music
                        users >> api_gateway >> lambda_streaming >> dynamodb
                        users >> api_gateway >> lambda_playlist >> rds
                        
                elif diagram_type == "custom":
                    with Diagram(title, show=False, filename=filepath):
                        s3 = S3("S3 Bucket")
                        lambda_func = Lambda("Lambda Function")
                        s3 >> lambda_func
                
                full_path = f"{filepath}.png"
                return f"✅ Diagram created: {full_path}\n📁 File: {filename}\n📋 Title: {title}\n🔗 Full path: {os.path.abspath(full_path)}"
                
            except Exception as e:
                return f"❌ Error creating diagram: {str(e)}"
        
        return create_aws_diagram
    
    def _generate_filename_from_context(self, query: str) -> str:
        """Generate filename based on query context"""
        import re
        
        keywords = self._extract_keywords_from_query(query)
        
        if not keywords:
            timestamp = datetime.now().strftime("%H%M")
            return f"aws_architecture_{timestamp}"
        
        filename = '_'.join(keywords)
        filename = re.sub(r'[^\w\-_]', '', filename)
        filename = re.sub(r'_+', '_', filename).strip('_')
        
        return filename[:40] if len(filename) > 40 else filename
    
    def _generate_title_from_context(self, query: str, diagram_type: str) -> str:
        """Generate title based on query context and diagram type"""
        keywords = self._extract_keywords_from_query(query)
        
        if keywords:
            return ' '.join(word.replace('_', ' ').title() for word in keywords) + ' Architecture'
        
        title_map = {
            "static_website": "Static Website Architecture",
            "serverless_api": "Serverless API Architecture", 
            "web_app": "Web Application Architecture",
            "music_streaming": "Music Streaming Platform Architecture",
            "custom": "AWS Architecture"
        }
        return title_map.get(diagram_type, "AWS Architecture")
    
    def _extract_keywords_from_query(self, query: str) -> List[str]:
        """Extract relevant keywords from user query"""
        aws_services = [
            'lambda', 'ec2', 's3', 'rds', 'dynamodb', 'cloudfront', 'api gateway', 'apigateway',
            'ecs', 'eks', 'fargate', 'elasticache', 'aurora', 'redshift', 'kinesis',
            'sqs', 'sns', 'step functions', 'stepfunctions', 'cognito', 'iam'
        ]
        
        architecture_types = [
            'serverless', 'microservices', 'web application', 'web app', 'api', 'rest api',
            'real-time', 'streaming', 'batch processing', 'data pipeline', 'etl'
        ]
        
        industries = [
            'ecommerce', 'e-commerce', 'fintech', 'healthcare', 'gaming', 'iot'
        ]
        
        query_lower = query.lower()
        keywords = []
        
        for service in aws_services:
            if service in query_lower:
                keywords.append(service.replace(' ', '_'))
        
        for arch_type in architecture_types:
            if arch_type in query_lower:
                keywords.append(arch_type.replace(' ', '_'))
        
        for industry in industries:
            if industry in query_lower:
                keywords.append(industry)
        
        return list(dict.fromkeys(keywords))[:3]
    
    def validate_query(self, query: str) -> bool:
        """
        Validate user query input
        
        Args:
            query: User input string
            
        Returns:
            bool: True if query is valid, False otherwise
        """
        if not query or not isinstance(query, str):
            return False
        
        # Check if query is not empty after stripping whitespace
        stripped_query = query.strip()
        if not stripped_query:
            return False
        
        # Check minimum length (at least 3 characters)
        if len(stripped_query) < 3:
            return False
        
        # Check maximum length (reasonable limit for processing)
        if len(stripped_query) > 5000:
            return False
        
        return True
    
    def process_query(self, query: str) -> AgentResponse:
        """
        Process user query through the agent
        
        Args:
            query: Validated user query string
            
        Returns:
            AgentResponse: Structured response with results or error information
        """
        start_time = datetime.now()
        
        # Update state to processing
        self._current_state = QueryState(
            query=query,
            status="processing",
            start_time=start_time
        )
        
        try:
            # Validate query first
            if not self.validate_query(query):
                error_response = AgentResponse(
                    text="",
                    success=False,
                    error_message="Invalid query: Query must be between 3 and 5000 characters and contain meaningful content.",
                    processing_time=0.0
                )
                self._current_state.status = "error"
                self._current_state.response = error_response
                return error_response
            
            # Check if agent is initialized
            if not self._agent:
                error_response = AgentResponse(
                    text="",
                    success=False,
                    error_message="Agent not initialized. Please check your configuration and try again.",
                    processing_time=0.0
                )
                self._current_state.status = "error"
                self._current_state.response = error_response
                return error_response
            
            logger.info(f"Processing query: {query[:100]}...")
            
            # Process query with agent using MCP client context
            with self._mcp_client:
                agent_response_text = self._agent(query)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Check for generated files
            generated_files = self._detect_generated_files()
            
            # Create successful response
            response = AgentResponse(
                text=agent_response_text,
                success=True,
                generated_files=generated_files,
                processing_time=processing_time
            )
            
            # Update state
            self._current_state.status = "completed"
            self._current_state.response = response
            
            logger.info(f"Query processed successfully in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            # Calculate processing time even for errors
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(f"Error processing query: {e}")
            
            # Create error response
            error_response = AgentResponse(
                text="",
                success=False,
                error_message=f"Error processing query: {str(e)}",
                processing_time=processing_time
            )
            
            # Update state
            self._current_state.status = "error"
            self._current_state.response = error_response
            
            return error_response
    
    def _detect_generated_files(self) -> List[str]:
        """Detect files generated during agent processing"""
        generated_files = []
        
        try:
            diagrams_dir = Path("generated-diagrams")
            if diagrams_dir.exists():
                # Look for recently created files (within last minute)
                current_time = datetime.now()
                for file_path in diagrams_dir.iterdir():
                    if file_path.is_file():
                        # Check file modification time
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        time_diff = (current_time - file_mtime).total_seconds()
                        
                        # If file was modified within last 60 seconds, consider it generated
                        if time_diff <= 60:
                            generated_files.append(str(file_path))
            
        except Exception as e:
            logger.warning(f"Error detecting generated files: {e}")
        
        return generated_files
    
    def get_current_state(self) -> QueryState:
        """Get current query processing state"""
        return self._current_state
    
    def reset_state(self):
        """Reset query processor to idle state"""
        self._current_state = QueryState(query="", status="idle")
        logger.info("QueryProcessor state reset")
    
    def is_agent_available(self) -> bool:
        """Check if the agent is properly initialized and available"""
        return self._agent is not None and self._mcp_client is not None
    
    def get_agent_status(self) -> dict:
        """Get detailed status information about the agent"""
        return {
            "agent_initialized": self._agent is not None,
            "mcp_client_initialized": self._mcp_client is not None,
            "current_status": self._current_state.status,
            "last_query": self._current_state.query if self._current_state.query else None,
            "last_processing_time": self._current_state.response.processing_time if self._current_state.response else None
        }