#!/usr/bin/env python3
"""
Agent Wrapper for Streamlit Integration

This module provides an async wrapper around the existing AWS Solutions Architect agent
to enable seamless integration with Streamlit's reactive UI framework.

Key features:
- Async processing with status updates
- Proper error handling and timeout management
- Status callback system for real-time UI updates
- Resource management with proper cleanup
- Thread-safe operations for Streamlit compatibility
"""

import os
import sys
import asyncio
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Callable, Dict, Any
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

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
class ProcessingStatus:
    """Status information during agent processing"""
    stage: str  # 'initializing', 'processing', 'generating_diagram', 'completing', 'error'
    message: str
    progress: float  # 0.0 to 1.0
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class AgentResult:
    """Result from agent processing"""
    text: str
    success: bool
    error_message: Optional[str] = None
    generated_files: List[str] = None
    processing_time: float = 0.0
    status_history: List[ProcessingStatus] = None
    
    def __post_init__(self):
        if self.generated_files is None:
            self.generated_files = []
        if self.status_history is None:
            self.status_history = []


class StreamlitAgentWrapper:
    """
    Async wrapper for the AWS Solutions Architect agent optimized for Streamlit integration.
    
    This wrapper provides:
    - Async processing with real-time status updates
    - Timeout management and cancellation support
    - Thread-safe operations for Streamlit compatibility
    - Proper resource cleanup and error handling
    """
    
    def __init__(self, timeout_seconds: int = 120):
        """
        Initialize the agent wrapper
        
        Args:
            timeout_seconds: Maximum time to wait for agent processing
        """
        self.timeout_seconds = timeout_seconds
        self._agent = None
        self._mcp_client = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="agent_worker")
        self._is_initialized = False
        self._initialization_lock = threading.Lock()
        
        # Status callback system
        self._status_callbacks: List[Callable[[ProcessingStatus], None]] = []
        
        # Initialize agent in background
        self._initialize_agent()
    
    def add_status_callback(self, callback: Callable[[ProcessingStatus], None]):
        """Add a callback function to receive status updates"""
        self._status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable[[ProcessingStatus], None]):
        """Remove a status callback"""
        if callback in self._status_callbacks:
            self._status_callbacks.remove(callback)
    
    def _emit_status(self, stage: str, message: str, progress: float, details: Optional[Dict[str, Any]] = None):
        """Emit status update to all registered callbacks"""
        status = ProcessingStatus(
            stage=stage,
            message=message,
            progress=progress,
            timestamp=datetime.now(),
            details=details
        )
        
        for callback in self._status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.warning(f"Status callback error: {e}")
    
    def _initialize_agent(self):
        """Initialize the Strands agent with MCP client and tools"""
        with self._initialization_lock:
            if self._is_initialized:
                return
            
            try:
                self._emit_status("initializing", "Setting up MCP client...", 0.1)
                
                # Create MCP client for AWS documentation
                self._mcp_client = MCPClient(
                    lambda: stdio_client(
                        StdioServerParameters(
                            command="uvx", 
                            args=["awslabs.aws-documentation-mcp-server@latest"]
                        )
                    )
                )
                
                self._emit_status("initializing", "Configuring Bedrock model...", 0.3)
                
                # Initialize Bedrock model
                bedrock_model = BedrockModel(
                    model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
                    temperature=0.7,
                )
                
                self._emit_status("initializing", "Creating diagram generation tools...", 0.5)
                
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
                - create_aws_diagram: Creates custom diagrams based on AWS services (ONLY tool for diagrams!)

                CRITICAL REQUIREMENTS:
                1. You MUST create a visual diagram for each architectural request using ONLY create_aws_diagram
                2. DO NOT use other tools for creating diagrams
                3. ALWAYS call create_aws_diagram FIRST before detailed explanation

                How to use create_aws_diagram:
                - Analyze the user's requirements and identify relevant AWS services
                - Call: create_aws_diagram(services="service1,service2,service3", query_context="user's original query")
                - The tool will automatically create intelligent connections between services

                Available AWS services for diagrams:
                Compute: lambda, ec2, ecs, fargate
                Storage: s3, ebs, efs
                Database: rds, dynamodb, elasticache, redshift
                Network: cloudfront, apigateway, elb, vpc, route53
                Integration: sqs, sns, stepfunctions
                Security: iam, cognito
                Analytics: kinesis, athena

                Examples:
                - Web application: "cloudfront,s3,apigateway,lambda,rds"
                - Serverless API: "apigateway,lambda,dynamodb"
                - Microservices: "elb,ecs,rds,elasticache,sqs"
                - Data pipeline: "kinesis,lambda,s3,athena"

                Mandatory workflow:
                1. Analyze user requirements and select appropriate AWS services
                2. Call: create_aws_diagram(services="comma-separated-services", query_context="user's original query")
                3. Then provide detailed architectural explanation matching the diagram

                Always pass the original user query as query_context for automatic file naming.
                Always provide comprehensive architectural guidance with best practices and working diagram files.
                The diagram will automatically show intelligent connections between the services you specify.
                """
                
                self._emit_status("initializing", "Initializing agent with tools...", 0.7)
                
                # Initialize agent with MCP client context
                with self._mcp_client:
                    mcp_tools = self._mcp_client.list_tools_sync()
                    all_tools = mcp_tools + [diagram_tool]
                    
                    self._agent = Agent(
                        tools=all_tools, 
                        model=bedrock_model, 
                        system_prompt=system_prompt
                    )
                
                self._emit_status("initializing", "Agent initialization complete", 1.0)
                self._is_initialized = True
                logger.info("StreamlitAgentWrapper initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize StreamlitAgentWrapper: {e}")
                self._emit_status("error", f"Initialization failed: {str(e)}", 0.0)
                self._agent = None
                self._is_initialized = False
                raise
    
    def _create_diagram_tool(self):
        """Create the local diagram generation tool with status updates"""
        
        @tool
        def create_aws_diagram(services: str, query_context: str = "") -> str:
            """
            Creates AWS architecture diagrams locally using Python diagrams library based on specified services
            
            Args:
                services: Comma-separated list of AWS services to include (e.g., "s3,lambda,dynamodb,apigateway,cloudfront,rds,ec2,ecs,sns,sqs")
                query_context: Original user query for generating filename and title
            
            Returns:
                Success message with file path and generated filename
            """
            try:
                self._emit_status("generating_diagram", f"Creating diagram with services: {services}...", 0.8)
                
                from diagrams import Diagram
                from diagrams.aws.compute import Lambda, EC2, ECS, Fargate
                from diagrams.aws.storage import S3, EBS, EFS
                from diagrams.aws.network import CloudFront, APIGateway, ELB, VPC, Route53
                from diagrams.aws.database import RDS, Dynamodb, ElastiCache, Redshift
                from diagrams.aws.integration import SQS, SNS, StepFunctions
                from diagrams.aws.security import IAM, Cognito
                from diagrams.aws.analytics import Kinesis, Athena
                from diagrams.onprem.client import Users
                
                # Parse services list
                service_list = [s.strip().lower() for s in services.split(',')]
                
                # Generate filename and title based on context
                filename = self._generate_filename_from_context(query_context)
                title = self._generate_title_from_context(query_context, "custom")
                
                # Ensure generated-diagrams directory exists
                os.makedirs("generated-diagrams", exist_ok=True)
                filepath = f"generated-diagrams/{filename}"
                
                # Add Graphviz to PATH if on Windows
                if os.name == 'nt':
                    os.environ['PATH'] += ";C:\\Program Files\\Graphviz\\bin"
                
                # Create dynamic diagram based on services
                with Diagram(title, show=False, filename=filepath, direction="TB"):
                    # Always start with users
                    users = Users("Users")
                    
                    # Create service instances based on the list
                    aws_services = {}
                    
                    # Map service names to diagram components
                    service_mapping = {
                        's3': lambda: S3("S3 Storage"),
                        'lambda': lambda: Lambda("Lambda Function"),
                        'ec2': lambda: EC2("EC2 Instance"),
                        'ecs': lambda: ECS("ECS Container"),
                        'fargate': lambda: Fargate("Fargate"),
                        'rds': lambda: RDS("RDS Database"),
                        'dynamodb': lambda: Dynamodb("DynamoDB"),
                        'elasticache': lambda: ElastiCache("ElastiCache"),
                        'redshift': lambda: Redshift("Redshift"),
                        'apigateway': lambda: APIGateway("API Gateway"),
                        'cloudfront': lambda: CloudFront("CloudFront CDN"),
                        'elb': lambda: ELB("Load Balancer"),
                        'vpc': lambda: VPC("VPC"),
                        'route53': lambda: Route53("Route 53"),
                        'sqs': lambda: SQS("SQS Queue"),
                        'sns': lambda: SNS("SNS Topic"),
                        'stepfunctions': lambda: StepFunctions("Step Functions"),
                        'iam': lambda: IAM("IAM"),
                        'cognito': lambda: Cognito("Cognito"),
                        'kinesis': lambda: Kinesis("Kinesis"),
                        'athena': lambda: Athena("Athena"),
                        'ebs': lambda: EBS("EBS Volume"),
                        'efs': lambda: EFS("EFS")
                    }
                    
                    # Create instances for requested services
                    for service in service_list:
                        if service in service_mapping:
                            aws_services[service] = service_mapping[service]()
                    
                    # Create intelligent connections based on common patterns
                    self._create_intelligent_connections(users, aws_services, service_list)
                
                full_path = f"{filepath}.png"
                
                self._emit_status("generating_diagram", "Diagram generation complete", 0.9)
                
                return f"✅ Diagram created: {full_path}\n📁 File: {filename}\n📋 Title: {title}\n🔗 Full path: {os.path.abspath(full_path)}"
                
            except Exception as e:
                self._emit_status("error", f"Diagram generation failed: {str(e)}", 0.0)
                return f"❌ Error creating diagram: {str(e)}"
        
        return create_aws_diagram
    
    def _create_intelligent_connections(self, users, aws_services, service_list):
        """Create intelligent connections between AWS services based on common patterns"""
        
        # Common connection patterns
        web_entry_points = ['cloudfront', 'elb', 'apigateway']
        compute_services = ['lambda', 'ec2', 'ecs', 'fargate']
        databases = ['rds', 'dynamodb', 'elasticache', 'redshift']
        storage = ['s3', 'ebs', 'efs']
        messaging = ['sqs', 'sns']
        
        # Find entry point (what users connect to first)
        entry_point = None
        for service in web_entry_points:
            if service in aws_services:
                entry_point = aws_services[service]
                break
        
        # If no web entry point, connect to first compute service
        if not entry_point:
            for service in compute_services:
                if service in aws_services:
                    entry_point = aws_services[service]
                    break
        
        # Connect users to entry point
        if entry_point:
            users >> entry_point
        
        # Create logical flow connections
        current_service = entry_point
        
        # Connect web services to compute services
        if 'cloudfront' in aws_services and 's3' in aws_services:
            aws_services['cloudfront'] >> aws_services['s3']
        
        if 'apigateway' in aws_services:
            # API Gateway typically connects to Lambda
            for compute in ['lambda', 'ecs', 'fargate']:
                if compute in aws_services:
                    aws_services['apigateway'] >> aws_services[compute]
                    current_service = aws_services[compute]
                    break
        
        if 'elb' in aws_services:
            # Load balancer connects to compute services
            for compute in ['ec2', 'ecs', 'fargate']:
                if compute in aws_services:
                    aws_services['elb'] >> aws_services[compute]
                    current_service = aws_services[compute]
                    break
        
        # Connect compute services to databases
        if current_service:
            for db in databases:
                if db in aws_services:
                    current_service >> aws_services[db]
                    break
        
        # Connect compute services to storage
        for compute in compute_services:
            if compute in aws_services:
                for storage_service in storage:
                    if storage_service in aws_services and storage_service != 's3':  # S3 already handled above
                        aws_services[compute] >> aws_services[storage_service]
                        break
        
        # Connect messaging services
        for compute in compute_services:
            if compute in aws_services:
                for msg in messaging:
                    if msg in aws_services:
                        aws_services[compute] >> aws_services[msg]
                        break
        
        # Connect Step Functions if present
        if 'stepfunctions' in aws_services:
            for compute in compute_services:
                if compute in aws_services:
                    aws_services['stepfunctions'] >> aws_services[compute]
                    break
        
        # If no connections were made, create a simple chain
        if len(aws_services) > 1 and not any('>>' in str(service) for service in aws_services.values()):
            services_list = list(aws_services.values())
            for i in range(len(services_list) - 1):
                services_list[i] >> services_list[i + 1]
    
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
        """Generate title based on query context"""
        keywords = self._extract_keywords_from_query(query)
        
        if keywords:
            return ' '.join(word.replace('_', ' ').title() for word in keywords) + ' Architecture'
        
        # Fallback to generic title
        return "AWS Architecture Solution"
    
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
    
    def _process_query_sync(self, query: str) -> AgentResult:
        """Synchronous query processing (runs in thread pool) with comprehensive error handling"""
        start_time = datetime.now()
        status_history = []
        
        try:
            # Validate query
            if not self._validate_query(query):
                validation_error = ValueError("Invalid query: Query must be between 3 and 5000 characters and contain meaningful content.")
                error_handler.handle_error(
                    error=validation_error,
                    category=ErrorCategory.VALIDATION_ERROR,
                    component="agent_wrapper",
                    user_context="Query validation failed",
                    show_in_ui=False
                )
                raise validation_error
            
            # Check if agent is initialized
            if not self._is_initialized or not self._agent:
                init_error = RuntimeError("Agent not initialized. Please check your configuration and try again.")
                error_handler.handle_error(
                    error=init_error,
                    category=ErrorCategory.CONFIGURATION_ERROR,
                    component="agent_wrapper",
                    user_context="Agent initialization failed",
                    show_in_ui=False
                )
                raise init_error
            
            self._emit_status("processing", "Starting query processing...", 0.2)
            logger.info(f"Processing query: {query[:100]}...")
            
            # Track existing files before processing
            existing_files = self._get_existing_diagram_files()
            
            # Process query with agent using MCP client context
            try:
                with self._mcp_client:
                    self._emit_status("processing", "Executing agent query...", 0.4)
                    agent_response_text = self._agent(query)
            except Exception as agent_error:
                error_handler.handle_agent_error(
                    error=agent_error,
                    query=query,
                    show_in_ui=False
                )
                raise
            
            self._emit_status("completing", "Finalizing response...", 0.95)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Check for generated files by comparing before and after
            try:
                generated_files = self._detect_new_files(existing_files)
            except Exception as file_error:
                error_handler.handle_file_system_error(
                    error=file_error,
                    operation="detect_generated_files",
                    show_in_ui=False
                )
                generated_files = []  # Continue without generated files
            
            self._emit_status("completing", "Query processing complete", 1.0)
            
            # Create successful response
            result = AgentResult(
                text=agent_response_text,
                success=True,
                generated_files=generated_files,
                processing_time=processing_time,
                status_history=status_history
            )
            
            logger.info(f"Query processed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            # Calculate processing time even for errors
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Handle the error appropriately based on type
            if isinstance(e, (ValueError, TypeError)):
                category = ErrorCategory.VALIDATION_ERROR
            elif isinstance(e, (ConnectionError, TimeoutError)):
                category = ErrorCategory.NETWORK_ERROR
            elif isinstance(e, (FileNotFoundError, PermissionError, OSError)):
                category = ErrorCategory.FILE_SYSTEM_ERROR
            else:
                category = ErrorCategory.AGENT_ERROR
            
            error_handler.handle_error(
                error=e,
                category=category,
                component="agent_wrapper",
                user_context=f"Query processing failed: {query[:50]}...",
                show_in_ui=False
            )
            
            self._emit_status("error", f"Processing failed: {str(e)}", 0.0)
            
            # Create error response
            return AgentResult(
                text="",
                success=False,
                error_message=str(e),
                processing_time=processing_time,
                status_history=status_history
            )
    
    async def process_query_async(self, query: str) -> AgentResult:
        """
        Process query asynchronously with timeout and status updates
        
        Args:
            query: User query string
            
        Returns:
            AgentResult: Processing result with status information
        """
        try:
            # Submit to thread pool for async execution
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(self._executor, self._process_query_sync, query)
            
            # Wait for completion with timeout
            result = await asyncio.wait_for(future, timeout=self.timeout_seconds)
            return result
            
        except asyncio.TimeoutError:
            self._emit_status("error", f"Query processing timed out after {self.timeout_seconds} seconds", 0.0)
            return AgentResult(
                text="",
                success=False,
                error_message=f"Query processing timed out after {self.timeout_seconds} seconds. Please try a simpler query or check your connection.",
                processing_time=self.timeout_seconds
            )
        except Exception as e:
            self._emit_status("error", f"Async processing error: {str(e)}", 0.0)
            return AgentResult(
                text="",
                success=False,
                error_message=f"Async processing error: {str(e)}",
                processing_time=0.0
            )
    
    def _validate_query(self, query: str) -> bool:
        """Validate user query input"""
        if not query or not isinstance(query, str):
            return False
        
        stripped_query = query.strip()
        if not stripped_query:
            return False
        
        if len(stripped_query) < 3 or len(stripped_query) > 5000:
            return False
        
        return True
    
    def _get_existing_diagram_files(self) -> set:
        """Get set of existing diagram files before processing"""
        existing_files = set()
        
        try:
            diagrams_dir = Path("generated-diagrams")
            if diagrams_dir.exists():
                for file_path in diagrams_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg'}:
                        existing_files.add(str(file_path))
        except Exception as e:
            logger.warning(f"Error getting existing files: {e}")
        
        return existing_files
    
    def _detect_new_files(self, existing_files: set) -> List[str]:
        """Detect new files by comparing current files with existing files"""
        new_files = []
        
        try:
            diagrams_dir = Path("generated-diagrams")
            if diagrams_dir.exists():
                current_files = set()
                for file_path in diagrams_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg'}:
                        current_files.add(str(file_path))
                
                # Find files that are in current_files but not in existing_files
                new_files = list(current_files - existing_files)
                
                # Sort by modification time (newest first) for consistent ordering
                if new_files:
                    new_files.sort(key=lambda f: Path(f).stat().st_mtime, reverse=True)
            
        except Exception as e:
            logger.warning(f"Error detecting new files: {e}")
        
        return new_files
    
    def _detect_generated_files(self) -> List[str]:
        """Detect files generated during agent processing (legacy method for compatibility)"""
        generated_files = []
        
        try:
            diagrams_dir = Path("generated-diagrams")
            if diagrams_dir.exists():
                # Look for very recently created files (within last 30 seconds)
                # This is more precise for detecting files from current request
                current_time = datetime.now()
                for file_path in diagrams_dir.iterdir():
                    if file_path.is_file():
                        # Check file modification time
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        time_diff = (current_time - file_mtime).total_seconds()
                        
                        # If file was modified within last 30 seconds, consider it generated
                        # This is much more precise for current request detection
                        if time_diff <= 30:
                            generated_files.append(str(file_path))
            
        except Exception as e:
            logger.warning(f"Error detecting generated files: {e}")
        
        return generated_files
    
    def is_available(self) -> bool:
        """Check if the agent wrapper is ready for processing"""
        return self._is_initialized and self._agent is not None and self._mcp_client is not None
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get detailed status information"""
        return {
            "initialized": self._is_initialized,
            "agent_available": self._agent is not None,
            "mcp_client_available": self._mcp_client is not None,
            "timeout_seconds": self.timeout_seconds,
            "executor_active": not self._executor._shutdown
        }
    
    def shutdown(self):
        """Shutdown the agent wrapper and cleanup resources"""
        try:
            self._executor.shutdown(wait=True, cancel_futures=True)
            logger.info("StreamlitAgentWrapper shutdown complete")
        except Exception as e:
            logger.warning(f"Error during shutdown: {e}")
    
    def __del__(self):
        """Cleanup on object destruction"""
        try:
            self.shutdown()
        except:
            pass