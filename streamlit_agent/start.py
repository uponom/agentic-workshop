#!/usr/bin/env python3
"""
Streamlit Agent Application Startup Script

This script serves as the main entry point for the Streamlit Agent application.
It handles proper initialization of all components, directory creation, and
application configuration before launching the Streamlit web interface.

Usage:
    python streamlit_agent/start.py
    
    Or with custom configuration:
    python streamlit_agent/start.py --port 8501 --debug
"""

import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Add the parent directory to Python path for imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

class ApplicationConfig:
    """Application configuration management"""
    
    def __init__(self):
        self.config = {
            'port': 8501,
            'host': 'localhost',
            'debug': False,
            'log_level': 'INFO',
            'generated_diagrams_dir': 'generated-diagrams',
            'logs_dir': 'logs',
            'test_screenshots_dir': 'test_screenshots',
            'agent_timeout': 120,
            'max_diagrams': 100,
            'cleanup_old_diagrams': True,
            'max_diagram_age_hours': 24
        }
        self.config_file = Path(__file__).parent / 'config.json'
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file if it exists"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
                    logging.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logging.warning(f"Failed to load config file: {e}")
        return self.config
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
                logging.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logging.warning(f"Failed to save config file: {e}")
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values"""
        self.config.update(kwargs)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

class DirectoryManager:
    """Manages application directory structure"""
    
    def __init__(self, config: ApplicationConfig):
        self.config = config
        self.base_dir = Path(__file__).parent
        self.required_dirs = [
            self.config.get('generated_diagrams_dir'),
            self.config.get('logs_dir'),
            self.config.get('test_screenshots_dir')
        ]
    
    def create_directories(self) -> bool:
        """Create all required directories"""
        success = True
        
        for dir_name in self.required_dirs:
            dir_path = self.base_dir / dir_name
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logging.info(f"[OK] Directory ready: {dir_path}")
            except Exception as e:
                logging.error(f"[ERROR] Failed to create directory {dir_path}: {e}")
                success = False
        
        # Also create the global generated-diagrams directory for compatibility
        try:
            global_diagrams_dir = Path.cwd() / 'generated-diagrams'
            global_diagrams_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"[OK] Global diagrams directory ready: {global_diagrams_dir}")
        except Exception as e:
            logging.warning(f"[WARNING] Could not create global diagrams directory: {e}")
        
        return success
    
    def validate_directories(self) -> Dict[str, bool]:
        """Validate that all required directories exist and are writable"""
        status = {}
        
        for dir_name in self.required_dirs:
            dir_path = self.base_dir / dir_name
            try:
                # Check if directory exists
                exists = dir_path.exists() and dir_path.is_dir()
                
                # Check if directory is writable
                writable = False
                if exists:
                    test_file = dir_path / '.write_test'
                    try:
                        test_file.touch()
                        test_file.unlink()
                        writable = True
                    except Exception:
                        writable = False
                
                status[dir_name] = exists and writable
                
                if status[dir_name]:
                    logging.info(f"[OK] Directory validated: {dir_path}")
                else:
                    logging.error(f"[ERROR] Directory validation failed: {dir_path}")
                    
            except Exception as e:
                logging.error(f"[ERROR] Error validating directory {dir_path}: {e}")
                status[dir_name] = False
        
        return status

class ComponentInitializer:
    """Initializes and validates application components"""
    
    def __init__(self, config: ApplicationConfig):
        self.config = config
    
    def validate_dependencies(self) -> Dict[str, bool]:
        """Validate that all required dependencies are available"""
        dependencies = {
            'streamlit': False,
            'strands': False,
            'boto3': False,
            'pillow': False,
            'pytest': False,
            'hypothesis': False
        }
        
        # Check each dependency
        for dep_name in dependencies.keys():
            try:
                if dep_name == 'strands':
                    import strands
                elif dep_name == 'streamlit':
                    import streamlit
                elif dep_name == 'boto3':
                    import boto3
                elif dep_name == 'pillow':
                    import PIL
                elif dep_name == 'pytest':
                    import pytest
                elif dep_name == 'hypothesis':
                    import hypothesis
                
                dependencies[dep_name] = True
                logging.info(f"[OK] Dependency available: {dep_name}")
                
            except ImportError as e:
                logging.error(f"[ERROR] Missing dependency: {dep_name} - {e}")
                dependencies[dep_name] = False
        
        return dependencies
    
    def validate_components(self) -> Dict[str, bool]:
        """Validate that application components can be imported"""
        components = {
            'query_processor': False,
            'agent_wrapper': False,
            'diagram_manager': False,
            'response_renderer': False,
            'error_handler': False,
            'test_automation': False
        }
        
        try:
            # Import components to validate they're available
            from components import (
                QueryProcessor, AgentResponse, QueryState, StreamlitAgentWrapper,
                AgentResult, ProcessingStatus, ResponseRenderer, DiagramManager,
                DiagramInfo, error_handler, ErrorCategory, with_error_boundary,
                handle_graceful_degradation, TestAutomation
            )
            
            # Test component instantiation
            components['query_processor'] = True
            components['agent_wrapper'] = True
            components['diagram_manager'] = True
            components['response_renderer'] = True
            components['error_handler'] = True
            components['test_automation'] = True
            
            logging.info("[OK] All application components validated successfully")
            
        except Exception as e:
            logging.error(f"[ERROR] Component validation failed: {e}")
            
            # Try to identify which specific component failed
            try:
                from components import QueryProcessor
                components['query_processor'] = True
            except:
                pass
            
            try:
                from components import StreamlitAgentWrapper
                components['agent_wrapper'] = True
            except:
                pass
            
            try:
                from components import DiagramManager
                components['diagram_manager'] = True
            except:
                pass
            
            try:
                from components import ResponseRenderer
                components['response_renderer'] = True
            except:
                pass
            
            try:
                from components import error_handler
                components['error_handler'] = True
            except:
                pass
            
            try:
                from components import TestAutomation
                components['test_automation'] = True
            except:
                pass
        
        return components

class ApplicationStarter:
    """Main application starter that coordinates initialization and launch"""
    
    def __init__(self):
        self.config = ApplicationConfig()
        self.directory_manager = None
        self.component_initializer = None
        self.logger = None
    
    def setup_logging(self) -> None:
        """Setup application logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO').upper())
        
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent / self.config.get('logs_dir', 'logs')
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / 'startup.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Application startup logging initialized")
    
    def parse_arguments(self) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Streamlit Agent Application Startup Script'
        )
        
        parser.add_argument(
            '--port', 
            type=int, 
            default=self.config.get('port'),
            help='Port to run Streamlit on (default: 8501)'
        )
        
        parser.add_argument(
            '--host',
            type=str,
            default=self.config.get('host'),
            help='Host to bind to (default: localhost)'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode'
        )
        
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default=self.config.get('log_level'),
            help='Set logging level'
        )
        
        parser.add_argument(
            '--config-file',
            type=str,
            help='Path to configuration file'
        )
        
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Only validate setup, do not start application'
        )
        
        parser.add_argument(
            '--create-config',
            action='store_true',
            help='Create default configuration file and exit'
        )
        
        return parser.parse_args()
    
    def initialize_application(self, args: argparse.Namespace) -> bool:
        """Initialize all application components"""
        
        # Update configuration with command line arguments
        self.config.update_config(
            port=args.port,
            host=args.host,
            debug=args.debug,
            log_level=args.log_level
        )
        
        # Load configuration file if specified
        if args.config_file:
            self.config.config_file = Path(args.config_file)
        
        self.config.load_config()
        
        # Setup logging with updated configuration
        self.setup_logging()
        
        self.logger.info("=" * 60)
        self.logger.info("STREAMLIT AGENT APPLICATION STARTUP")
        self.logger.info("=" * 60)
        
        # Initialize managers
        self.directory_manager = DirectoryManager(self.config)
        self.component_initializer = ComponentInitializer(self.config)
        
        # Validate and create directories
        self.logger.info("Creating application directories...")
        if not self.directory_manager.create_directories():
            self.logger.error("Failed to create required directories")
            return False
        
        # Validate directory permissions
        self.logger.info("Validating directory permissions...")
        dir_status = self.directory_manager.validate_directories()
        if not all(dir_status.values()):
            self.logger.error("Directory validation failed")
            for dir_name, status in dir_status.items():
                if not status:
                    self.logger.error(f"  [ERROR] {dir_name}: Not accessible")
            return False
        
        # Validate dependencies
        self.logger.info("Validating dependencies...")
        dep_status = self.component_initializer.validate_dependencies()
        missing_deps = [dep for dep, available in dep_status.items() if not available]
        
        if missing_deps:
            self.logger.error(f"Missing dependencies: {', '.join(missing_deps)}")
            self.logger.error("Please install missing dependencies with:")
            self.logger.error("  pip install -r requirements.txt")
            return False
        
        # Validate components
        self.logger.info("Validating application components...")
        comp_status = self.component_initializer.validate_components()
        failed_components = [comp for comp, available in comp_status.items() if not available]
        
        if failed_components:
            self.logger.error(f"Component validation failed: {', '.join(failed_components)}")
            return False
        
        self.logger.info("[OK] Application initialization completed successfully")
        return True
    
    def launch_streamlit(self, args: argparse.Namespace) -> None:
        """Launch the Streamlit application"""
        
        app_path = Path(__file__).parent / 'app.py'
        
        # Build Streamlit command
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            str(app_path),
            '--server.port', str(args.port),
            '--server.address', args.host,
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false'
        ]
        
        if args.debug:
            cmd.extend(['--logger.level', 'debug'])
        
        self.logger.info(f"Launching Streamlit application...")
        self.logger.info(f"Command: {' '.join(cmd)}")
        self.logger.info(f"Application will be available at: http://{args.host}:{args.port}")
        
        try:
            # Launch Streamlit
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            self.logger.info("Application shutdown requested by user")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Streamlit failed to start: {e}")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Unexpected error during startup: {e}")
            sys.exit(1)
    
    def run(self) -> None:
        """Main entry point for application startup"""
        
        try:
            # Parse command line arguments
            args = self.parse_arguments()
            
            # Handle special commands
            if args.create_config:
                self.config.save_config()
                print(f"Configuration file created: {self.config.config_file}")
                return
            
            # Initialize application
            if not self.initialize_application(args):
                self.logger.error("Application initialization failed")
                sys.exit(1)
            
            # Handle validation-only mode
            if args.validate_only:
                self.logger.info("Validation completed successfully")
                return
            
            # Launch Streamlit application
            self.launch_streamlit(args)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Critical startup error: {e}")
            else:
                print(f"Critical startup error: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    starter = ApplicationStarter()
    starter.run()

if __name__ == "__main__":
    main()