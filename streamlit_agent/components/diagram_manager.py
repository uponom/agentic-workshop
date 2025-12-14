#!/usr/bin/env python3
"""
DiagramManager Component

Handles diagram file detection, monitoring, and management for the Streamlit Agent application.
This component is responsible for monitoring the generated-diagrams folder, detecting new files,
implementing latest diagram detection logic, and providing cross-platform file path handling.

Key responsibilities:
- Monitor generated-diagrams folder for new files
- Detect and return the most recently generated diagram
- Handle file path operations across different operating systems
- Provide file system monitoring capabilities
- Manage diagram metadata and information
"""

import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import platform
from .error_handler import error_handler, ErrorCategory, with_error_boundary, handle_graceful_degradation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DiagramInfo:
    """Information about a diagram file"""
    filepath: str
    filename: str
    title: str
    created_at: datetime
    file_size: int
    exists: bool


class DiagramManager:
    """
    Manages diagram file detection and display with cross-platform file path handling
    and automatic monitoring of the generated-diagrams folder.
    """
    
    def __init__(self, diagrams_folder: str = "generated-diagrams"):
        """
        Initialize the DiagramManager
        
        Args:
            diagrams_folder: Path to the diagrams folder (default: "generated-diagrams")
        """
        self.diagrams_folder = Path(diagrams_folder)
        self.supported_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}
        self._last_scan_time = 0
        self._cached_diagrams: List[DiagramInfo] = []
        self._cache_duration = 5  # Cache for 5 seconds to avoid excessive file system calls
        
        # Ensure diagrams folder exists
        self._ensure_diagrams_folder_exists()
        
        logger.info(f"DiagramManager initialized with folder: {self.diagrams_folder}")
    
    @with_error_boundary("diagram_manager", handle_graceful_degradation, ErrorCategory.DIAGRAM_ERROR)
    def get_latest_diagram(self) -> Optional[DiagramInfo]:
        """
        Get the most recently generated diagram file
        
        Returns:
            Optional[DiagramInfo]: Information about the latest diagram, or None if no diagrams exist
        """
        try:
            diagrams = self.get_all_diagrams()
            
            if not diagrams:
                logger.debug("No diagrams found in folder")
                return None
            
            # Sort by creation time (most recent first)
            latest = max(diagrams, key=lambda d: d.created_at)
            logger.debug(f"Latest diagram: {latest.filename} created at {latest.created_at}")
            
            return latest
        except Exception as e:
            error_handler.handle_diagram_error(
                error=e,
                diagram_name="latest diagram",
                show_in_ui=False  # Let the error boundary handle UI display
            )
            raise
    
    @with_error_boundary("diagram_manager", handle_graceful_degradation, ErrorCategory.FILE_SYSTEM_ERROR)
    def get_all_diagrams(self, force_refresh: bool = False) -> List[DiagramInfo]:
        """
        Get all diagram files in the monitored folder
        
        Args:
            force_refresh: Force refresh of the cache
            
        Returns:
            List[DiagramInfo]: List of all diagram files with metadata
        """
        current_time = time.time()
        
        # Use cache if it's still valid and not forcing refresh
        if not force_refresh and (current_time - self._last_scan_time) < self._cache_duration:
            return self._cached_diagrams.copy()
        
        diagrams = []
        
        try:
            if not self.diagrams_folder.exists():
                logger.warning(f"Diagrams folder does not exist: {self.diagrams_folder}")
                # Try to create the folder
                try:
                    self._ensure_diagrams_folder_exists()
                except Exception as create_error:
                    error_handler.handle_file_system_error(
                        error=create_error,
                        operation="create_directory",
                        file_path=str(self.diagrams_folder),
                        show_in_ui=False
                    )
                return diagrams
            
            # Scan for image files
            for file_path in self.diagrams_folder.iterdir():
                if file_path.is_file() and self._is_supported_image(file_path):
                    try:
                        diagram_info = self._get_diagram_info(file_path)
                        if diagram_info and diagram_info.exists:
                            diagrams.append(diagram_info)
                    except Exception as file_error:
                        # Log individual file errors but continue processing
                        error_handler.handle_file_system_error(
                            error=file_error,
                            operation="read_file_info",
                            file_path=str(file_path),
                            show_in_ui=False
                        )
                        continue
            
            # Update cache
            self._cached_diagrams = diagrams
            self._last_scan_time = current_time
            
            logger.debug(f"Found {len(diagrams)} diagrams in folder")
            
        except Exception as e:
            error_handler.handle_file_system_error(
                error=e,
                operation="scan_directory",
                file_path=str(self.diagrams_folder),
                show_in_ui=False
            )
            # Return cached diagrams if available, empty list otherwise
            return self._cached_diagrams.copy() if self._cached_diagrams else []
        
        # Final validation: filter out any diagrams whose files no longer exist
        valid_diagrams = []
        for diagram in diagrams:
            try:
                if os.path.exists(diagram.filepath):
                    valid_diagrams.append(diagram)
                else:
                    logger.warning(f"Diagram file no longer exists: {diagram.filepath}")
            except Exception as check_error:
                logger.warning(f"Error checking diagram file {diagram.filepath}: {check_error}")
                continue
        
        return valid_diagrams
    
    def monitor_for_new_diagrams(self, last_check_time: Optional[datetime] = None) -> List[DiagramInfo]:
        """
        Monitor for new diagrams created since the last check
        
        Args:
            last_check_time: Time of last check (optional)
            
        Returns:
            List[DiagramInfo]: List of new diagrams created since last check
        """
        all_diagrams = self.get_all_diagrams(force_refresh=True)
        
        if last_check_time is None:
            return all_diagrams
        
        # Filter for diagrams created after the last check
        new_diagrams = [
            diagram for diagram in all_diagrams
            if diagram.created_at > last_check_time
        ]
        
        if new_diagrams:
            logger.info(f"Found {len(new_diagrams)} new diagrams since {last_check_time}")
        
        return new_diagrams
    
    def get_diagram_by_filename(self, filename: str) -> Optional[DiagramInfo]:
        """
        Get diagram information by filename
        
        Args:
            filename: Name of the diagram file
            
        Returns:
            Optional[DiagramInfo]: Diagram information if found, None otherwise
        """
        diagrams = self.get_all_diagrams()
        
        for diagram in diagrams:
            if diagram.filename == filename:
                return diagram
        
        return None
    
    def cleanup_old_diagrams(self, max_age_hours: int = 24, max_count: int = 50) -> int:
        """
        Clean up old diagram files to manage disk space
        
        Args:
            max_age_hours: Maximum age in hours before deletion
            max_count: Maximum number of diagrams to keep
            
        Returns:
            int: Number of files deleted
        """
        diagrams = self.get_all_diagrams(force_refresh=True)
        
        if not diagrams:
            return 0
        
        deleted_count = 0
        current_time = datetime.now()
        
        # Sort by creation time (oldest first)
        diagrams.sort(key=lambda d: d.created_at)
        
        try:
            # Delete files older than max_age_hours
            for diagram in diagrams:
                age_hours = (current_time - diagram.created_at).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    self._delete_diagram_file(diagram.filepath)
                    deleted_count += 1
                    logger.info(f"Deleted old diagram: {diagram.filename} (age: {age_hours:.1f}h)")
            
            # If still too many files, delete oldest ones
            remaining_diagrams = self.get_all_diagrams(force_refresh=True)
            if len(remaining_diagrams) > max_count:
                # Sort again and delete excess
                remaining_diagrams.sort(key=lambda d: d.created_at)
                excess_count = len(remaining_diagrams) - max_count
                
                for i in range(excess_count):
                    diagram = remaining_diagrams[i]
                    self._delete_diagram_file(diagram.filepath)
                    deleted_count += 1
                    logger.info(f"Deleted excess diagram: {diagram.filename}")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        if deleted_count > 0:
            # Clear cache after cleanup
            self._cached_diagrams = []
            self._last_scan_time = 0
        
        return deleted_count
    
    def get_folder_info(self) -> Dict[str, Any]:
        """
        Get information about the diagrams folder
        
        Returns:
            Dict[str, Any]: Folder information including path, existence, permissions, etc.
        """
        info = {
            'folder_path': str(self.diagrams_folder.resolve()),
            'folder_exists': self.diagrams_folder.exists(),
            'is_directory': self.diagrams_folder.is_dir() if self.diagrams_folder.exists() else False,
            'platform': platform.system(),
            'total_diagrams': 0,
            'total_size_bytes': 0,
            'readable': False,
            'writable': False
        }
        
        try:
            if self.diagrams_folder.exists():
                # Check permissions
                info['readable'] = os.access(self.diagrams_folder, os.R_OK)
                info['writable'] = os.access(self.diagrams_folder, os.W_OK)
                
                # Get diagram count and total size
                diagrams = self.get_all_diagrams()
                info['total_diagrams'] = len(diagrams)
                info['total_size_bytes'] = sum(d.file_size for d in diagrams)
                
                # Get folder stats
                folder_stat = self.diagrams_folder.stat()
                info['created_at'] = datetime.fromtimestamp(folder_stat.st_ctime)
                info['modified_at'] = datetime.fromtimestamp(folder_stat.st_mtime)
        
        except Exception as e:
            logger.error(f"Error getting folder info: {e}")
            info['error'] = str(e)
        
        return info
    
    def _ensure_diagrams_folder_exists(self) -> None:
        """Ensure the diagrams folder exists, create if necessary"""
        try:
            self.diagrams_folder.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured diagrams folder exists: {self.diagrams_folder}")
        except Exception as e:
            logger.error(f"Failed to create diagrams folder: {e}")
            raise
    
    def _is_supported_image(self, file_path: Path) -> bool:
        """
        Check if file is a supported image format
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool: True if supported image format, False otherwise
        """
        return file_path.suffix.lower() in self.supported_extensions
    
    def _get_diagram_info(self, file_path: Path) -> Optional[DiagramInfo]:
        """
        Get detailed information about a diagram file
        
        Args:
            file_path: Path to the diagram file
            
        Returns:
            Optional[DiagramInfo]: Diagram metadata or None if error
        """
        try:
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            # Use cross-platform file path handling
            normalized_path = self._normalize_file_path(str(file_path))
            
            return DiagramInfo(
                filepath=normalized_path,
                filename=file_path.name,
                title=self._generate_diagram_title(file_path.name),
                created_at=datetime.fromtimestamp(stat.st_ctime),
                file_size=stat.st_size,
                exists=True
            )
            
        except Exception as e:
            logger.warning(f"Error getting diagram info for {file_path}: {e}")
            return None
    
    def _normalize_file_path(self, file_path: str) -> str:
        """
        Normalize file path for cross-platform compatibility
        
        Args:
            file_path: Original file path
            
        Returns:
            str: Normalized file path
        """
        # Convert to Path object and back to string for normalization
        normalized = Path(file_path).resolve()
        
        # Use forward slashes for consistency (works on all platforms)
        return str(normalized).replace('\\', '/')
    
    def _generate_diagram_title(self, filename: str) -> str:
        """
        Generate a human-readable title from filename
        
        Args:
            filename: Original filename
            
        Returns:
            str: Human-readable title
        """
        # Remove extension
        name = Path(filename).stem
        
        # Replace underscores and hyphens with spaces
        title = name.replace('_', ' ').replace('-', ' ')
        
        # Capitalize words
        title = ' '.join(word.capitalize() for word in title.split())
        
        # Add "Diagram" if not present and doesn't already have architecture/diagram
        lower_title = title.lower()
        if 'diagram' not in lower_title and 'architecture' not in lower_title:
            title += ' Diagram'
        
        return title
    
    def _delete_diagram_file(self, file_path: str) -> bool:
        """
        Safely delete a diagram file with comprehensive error handling
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                logger.debug(f"Deleted diagram file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except PermissionError as e:
            error_handler.handle_file_system_error(
                error=e,
                operation="delete",
                file_path=file_path,
                show_in_ui=False
            )
            return False
        except Exception as e:
            error_handler.handle_file_system_error(
                error=e,
                operation="delete",
                file_path=file_path,
                show_in_ui=False
            )
            return False
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def get_status_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the DiagramManager status
        
        Returns:
            Dict[str, Any]: Status summary
        """
        folder_info = self.get_folder_info()
        diagrams = self.get_all_diagrams()
        latest = self.get_latest_diagram()
        
        return {
            'folder_path': folder_info['folder_path'],
            'folder_exists': folder_info['folder_exists'],
            'total_diagrams': len(diagrams),
            'latest_diagram': latest.filename if latest else None,
            'latest_created_at': latest.created_at if latest else None,
            'total_size': self._format_file_size(folder_info.get('total_size_bytes', 0)),
            'cache_valid': (time.time() - self._last_scan_time) < self._cache_duration,
            'supported_formats': list(self.supported_extensions)
        }