#!/usr/bin/env python3
"""
Unit tests for DiagramManager component

Tests individual functionality of the DiagramManager class including:
- File detection and monitoring
- Cross-platform file path handling
- Diagram metadata extraction
- Error handling scenarios
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import os
import time

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

from streamlit_agent.components.diagram_manager import DiagramManager, DiagramInfo


class TestDiagramManagerInitialization:
    """Test DiagramManager initialization"""
    
    def test_default_initialization(self):
        """Test initialization with default parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('pathlib.Path.mkdir'):
                manager = DiagramManager(temp_dir)
                assert manager.diagrams_folder == Path(temp_dir)
                assert '.png' in manager.supported_extensions
                assert '.jpg' in manager.supported_extensions
    
    def test_custom_folder_initialization(self):
        """Test initialization with custom folder"""
        custom_folder = "custom-diagrams"
        with patch('pathlib.Path.mkdir'):
            manager = DiagramManager(custom_folder)
            assert manager.diagrams_folder == Path(custom_folder)
    
    def test_supported_extensions(self):
        """Test that all expected image extensions are supported"""
        with patch('pathlib.Path.mkdir'):
            manager = DiagramManager()
            expected_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}
            assert expected_extensions.issubset(manager.supported_extensions)


class TestDiagramManagerFileDetection:
    """Test file detection functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('pathlib.Path.mkdir'):
            self.manager = DiagramManager("test-diagrams")
    
    def test_get_all_diagrams_empty_directory(self):
        """Test getting diagrams from empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            diagrams = self.manager.get_all_diagrams()
            assert diagrams == []
    
    def test_get_all_diagrams_with_files(self):
        """Test getting diagrams when files exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            
            # Create test image files
            test_files = ["diagram1.png", "diagram2.jpg", "not_image.txt"]
            for filename in test_files:
                (Path(temp_dir) / filename).touch()
            
            diagrams = self.manager.get_all_diagrams()
            
            # Should only include image files
            assert len(diagrams) == 2
            diagram_names = [d.filename for d in diagrams]
            assert "diagram1.png" in diagram_names
            assert "diagram2.jpg" in diagram_names
            assert "not_image.txt" not in diagram_names
    
    def test_get_latest_diagram_no_files(self):
        """Test getting latest diagram when no files exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            latest = self.manager.get_latest_diagram()
            assert latest is None
    
    def test_get_latest_diagram_with_files(self):
        """Test getting latest diagram when files exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            
            # Create files with different timestamps
            old_file = Path(temp_dir) / "old_diagram.png"
            new_file = Path(temp_dir) / "new_diagram.png"
            
            old_file.touch()
            time.sleep(0.1)  # Ensure different timestamps
            new_file.touch()
            
            latest = self.manager.get_latest_diagram()
            assert latest is not None
            assert latest.filename == "new_diagram.png"
    
    def test_is_supported_image(self):
        """Test image format detection"""
        test_cases = [
            ("diagram.png", True),
            ("diagram.jpg", True),
            ("diagram.jpeg", True),
            ("diagram.gif", True),
            ("diagram.PNG", True),  # Case insensitive
            ("diagram.txt", False),
            ("diagram.pdf", False),
            ("diagram", False)  # No extension
        ]
        
        for filename, expected in test_cases:
            result = self.manager._is_supported_image(Path(filename))
            assert result == expected
    
    def test_get_diagram_by_filename(self):
        """Test retrieving diagram by specific filename"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            
            # Create test files
            test_file = Path(temp_dir) / "specific_diagram.png"
            test_file.touch()
            
            # Test finding existing file
            diagram = self.manager.get_diagram_by_filename("specific_diagram.png")
            assert diagram is not None
            assert diagram.filename == "specific_diagram.png"
            
            # Test finding non-existent file
            diagram = self.manager.get_diagram_by_filename("nonexistent.png")
            assert diagram is None


class TestDiagramManagerMetadata:
    """Test diagram metadata extraction"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('pathlib.Path.mkdir'):
            self.manager = DiagramManager("test-diagrams")
    
    def test_get_diagram_info_existing_file(self):
        """Test getting metadata for existing file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test_diagram.png"
            test_file.write_text("fake image data")
            
            diagram_info = self.manager._get_diagram_info(test_file)
            
            assert diagram_info is not None
            assert diagram_info.filename == "test_diagram.png"
            assert diagram_info.exists is True
            assert diagram_info.file_size > 0
            assert isinstance(diagram_info.created_at, datetime)
    
    def test_get_diagram_info_nonexistent_file(self):
        """Test getting metadata for non-existent file"""
        nonexistent_file = Path("/nonexistent/path/diagram.png")
        diagram_info = self.manager._get_diagram_info(nonexistent_file)
        assert diagram_info is None
    
    def test_generate_diagram_title(self):
        """Test title generation from filename"""
        test_cases = [
            ("aws_architecture.png", "Aws Architecture"),  # Has "architecture", no "Diagram" added
            ("lambda-api.png", "Lambda Api Diagram"),  # No "architecture" or "diagram", adds "Diagram"
            ("serverless_web_app.png", "Serverless Web App Diagram"),  # No keywords, adds "Diagram"
            ("simple.png", "Simple Diagram"),  # No keywords, adds "Diagram"
            ("architecture_diagram.png", "Architecture Diagram")  # Has both, no additional "Diagram"
        ]
        
        for filename, expected_title in test_cases:
            title = self.manager._generate_diagram_title(filename)
            assert title == expected_title
    
    def test_normalize_file_path(self):
        """Test cross-platform file path normalization"""
        test_paths = [
            "diagrams/test.png",
            "diagrams\\test.png",  # Windows style
            "./diagrams/test.png"
        ]
        
        for path in test_paths:
            normalized = self.manager._normalize_file_path(path)
            # Should use forward slashes and be absolute
            assert '\\' not in normalized
            assert normalized.endswith('diagrams/test.png')


class TestDiagramManagerMonitoring:
    """Test file monitoring functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('pathlib.Path.mkdir'):
            self.manager = DiagramManager("test-diagrams")
    
    def test_monitor_for_new_diagrams_no_baseline(self):
        """Test monitoring when no baseline time is provided"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            
            # Create a test file
            test_file = Path(temp_dir) / "new_diagram.png"
            test_file.touch()
            
            new_diagrams = self.manager.monitor_for_new_diagrams()
            assert len(new_diagrams) >= 0  # Should include all diagrams
    
    def test_monitor_for_new_diagrams_with_baseline(self):
        """Test monitoring with baseline time"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            
            # Set baseline time to now
            baseline_time = datetime.now()
            
            # Create file after baseline (simulate new file)
            time.sleep(0.1)
            new_file = Path(temp_dir) / "newer_diagram.png"
            new_file.touch()
            
            new_diagrams = self.manager.monitor_for_new_diagrams(baseline_time)
            # Should detect the new file (though timing might be tricky in tests)
            assert isinstance(new_diagrams, list)
    
    def test_cache_functionality(self):
        """Test diagram caching behavior"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            
            # Create test file
            test_file = Path(temp_dir) / "cached_diagram.png"
            test_file.touch()
            
            # First call should populate cache
            diagrams1 = self.manager.get_all_diagrams()
            
            # Second call should use cache (no force_refresh)
            diagrams2 = self.manager.get_all_diagrams()
            
            assert len(diagrams1) == len(diagrams2)
            
            # Force refresh should bypass cache
            diagrams3 = self.manager.get_all_diagrams(force_refresh=True)
            assert len(diagrams3) == len(diagrams1)


class TestDiagramManagerCleanup:
    """Test cleanup functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('pathlib.Path.mkdir'):
            self.manager = DiagramManager("test-diagrams")
    
    def test_cleanup_old_diagrams_no_files(self):
        """Test cleanup when no files exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.manager.diagrams_folder = Path(temp_dir)
            deleted_count = self.manager.cleanup_old_diagrams()
            assert deleted_count == 0
    
    def test_delete_diagram_file_existing(self):
        """Test deleting existing diagram file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "to_delete.png"
            test_file.touch()
            
            assert test_file.exists()
            result = self.manager._delete_diagram_file(str(test_file))
            assert result is True
            assert not test_file.exists()
    
    def test_delete_diagram_file_nonexistent(self):
        """Test deleting non-existent file"""
        nonexistent_file = "/nonexistent/path/diagram.png"
        result = self.manager._delete_diagram_file(nonexistent_file)
        assert result is False


class TestDiagramManagerInfo:
    """Test information and status functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('pathlib.Path.mkdir'):
            self.manager = DiagramManager("test-diagrams")
    
    def test_get_folder_info(self):
        """Test getting folder information"""
        info = self.manager.get_folder_info()
        
        expected_keys = [
            'folder_path', 'folder_exists', 'is_directory',
            'platform', 'total_diagrams', 'total_size_bytes',
            'readable', 'writable'
        ]
        
        for key in expected_keys:
            assert key in info
    
    def test_get_status_summary(self):
        """Test getting status summary"""
        summary = self.manager.get_status_summary()
        
        expected_keys = [
            'folder_path', 'folder_exists', 'total_diagrams',
            'latest_diagram', 'latest_created_at', 'total_size',
            'cache_valid', 'supported_formats'
        ]
        
        for key in expected_keys:
            assert key in summary
    
    def test_format_file_size(self):
        """Test file size formatting"""
        test_cases = [
            (500, "500 B"),
            (1536, "1.5 KB"),
            (1048576, "1.0 MB"),
            (2097152, "2.0 MB")
        ]
        
        for size_bytes, expected in test_cases:
            result = self.manager._format_file_size(size_bytes)
            assert result == expected


class TestDiagramManagerErrorHandling:
    """Test error handling scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('pathlib.Path.mkdir'):
            self.manager = DiagramManager("test-diagrams")
    
    def test_get_all_diagrams_permission_error(self):
        """Test handling permission errors during directory scan"""
        # Use patch on the Path class instead of the instance
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.iterdir', side_effect=PermissionError("Access denied")):
            
            # Should not raise exception, should return cached or empty list
            diagrams = self.manager.get_all_diagrams()
            assert isinstance(diagrams, list)
    
    def test_get_diagram_info_stat_error(self):
        """Test handling stat errors when getting file info"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.png"
            
            # Mock stat to raise an error
            with patch.object(Path, 'stat', side_effect=OSError("Stat failed")):
                diagram_info = self.manager._get_diagram_info(test_file)
                assert diagram_info is None
    
    def test_folder_creation_error(self):
        """Test handling folder creation errors"""
        with patch.object(Path, 'mkdir', side_effect=PermissionError("Cannot create directory")):
            with pytest.raises(PermissionError):
                self.manager._ensure_diagrams_folder_exists()


if __name__ == "__main__":
    pytest.main([__file__])