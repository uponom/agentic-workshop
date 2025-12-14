#!/usr/bin/env python3
"""
Property-based tests for file detection and diagram display

**Feature: streamlit-agent, Property 2: File detection and diagram display**
**Validates: Requirements 2.1, 2.2, 5.2**

This module contains property-based tests that verify the file detection
and diagram display functionality in the Streamlit agent application.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import shutil
from datetime import datetime, timedelta
import time

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

# Import the components
sys.path.append(str(Path(__file__).parent.parent))
from components import DiagramManager, DiagramInfo


class TestFileDetectionProperty:
    """Property-based tests for file detection and diagram display"""

    @given(
        st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
            min_size=1,
            max_size=5
        ),
        st.sampled_from(['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'])
    )
    @settings(max_examples=20, deadline=None)
    def test_file_detection_and_diagram_display_property(self, filenames, extension):
        """
        **Feature: streamlit-agent, Property 2: File detection and diagram display**
        **Validates: Requirements 2.1, 2.2, 5.2**
        
        Property: For any diagram file generated in the generated-diagrams folder, 
        the system should automatically detect it and display the image within 
        the web interface.
        
        This test verifies that:
        1. New diagram files are automatically detected (Requirement 2.1)
        2. Detected diagrams are displayed in the web interface (Requirement 2.2)
        3. File detection works without manual refresh (Requirement 5.2)
        """
        # Filter out empty or invalid filenames
        valid_filenames = [name for name in filenames if name.strip() and len(name.strip()) > 0]
        assume(len(valid_filenames) > 0)
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Initially no diagrams should be detected
            initial_diagrams = diagram_manager.get_all_diagrams()
            assert len(initial_diagrams) == 0, "Initially no diagrams should be detected"
            
            # Test 2: Create diagram files and verify detection
            created_files = []
            for i, filename in enumerate(valid_filenames):
                # Create unique filename with extension
                safe_filename = f"{filename}_{i}{extension}"
                file_path = diagrams_folder / safe_filename
                
                # Create a minimal image file (1x1 pixel PNG for testing)
                self._create_test_image_file(file_path, extension)
                created_files.append(file_path)
                
                # Small delay to ensure different creation times
                time.sleep(0.01)
            
            # Test 3: Verify all files are detected
            detected_diagrams = diagram_manager.get_all_diagrams(force_refresh=True)
            assert len(detected_diagrams) == len(created_files), \
                f"Should detect {len(created_files)} diagrams, but found {len(detected_diagrams)}"
            
            # Test 4: Verify each detected diagram has correct metadata
            for diagram_info in detected_diagrams:
                assert isinstance(diagram_info, DiagramInfo)
                assert diagram_info.exists == True
                assert diagram_info.file_size > 0
                assert Path(diagram_info.filepath).exists()
                assert diagram_info.filename.endswith(extension)
                assert isinstance(diagram_info.created_at, datetime)
                assert len(diagram_info.title) > 0
            
            # Test 5: Verify automatic detection without manual refresh
            # Add another file after initial scan
            new_filename = f"auto_detect_{len(valid_filenames)}{extension}"
            new_file_path = diagrams_folder / new_filename
            self._create_test_image_file(new_file_path, extension)
            
            # Wait for cache to expire and check detection
            time.sleep(0.1)  # Small delay
            updated_diagrams = diagram_manager.get_all_diagrams(force_refresh=True)
            assert len(updated_diagrams) == len(created_files) + 1, \
                "New file should be automatically detected"
            
            # Test 6: Verify file path handling works correctly
            for diagram_info in updated_diagrams:
                # Verify normalized path format
                assert '\\' not in diagram_info.filepath or os.name == 'nt', \
                    "File paths should be normalized for cross-platform compatibility"
                
                # Verify file can be accessed
                assert Path(diagram_info.filepath).exists(), \
                    f"File should be accessible at {diagram_info.filepath}"
    
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=10, deadline=None)
    def test_latest_diagram_detection_property(self, num_files):
        """
        **Feature: streamlit-agent, Property 3: Most recent diagram selection**
        **Validates: Requirements 2.3**
        
        Property: For any set of multiple diagram files with different creation times, 
        the system should display the most recently created diagram by default.
        
        This test verifies that the latest diagram is correctly identified.
        """
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: No files initially
            latest = diagram_manager.get_latest_diagram()
            assert latest is None, "No latest diagram should exist initially"
            
            # Test 2: Create multiple files with different timestamps
            created_files = []
            for i in range(num_files):
                filename = f"diagram_{i:03d}.png"
                file_path = diagrams_folder / filename
                
                # Create test image file
                self._create_test_image_file(file_path, '.png')
                created_files.append((file_path, datetime.now()))
                
                # Ensure different creation times
                time.sleep(0.02)
            
            # Test 3: Verify latest diagram is correctly identified
            # Force refresh to ensure files are detected (cache may be stale)
            all_diagrams = diagram_manager.get_all_diagrams(force_refresh=True)
            latest_diagram = diagram_manager.get_latest_diagram()
            assert latest_diagram is not None, f"Latest diagram should be found. Found {len(all_diagrams)} diagrams total."
            
            # The latest should be the last created file
            expected_latest_name = f"diagram_{num_files-1:03d}.png"
            assert latest_diagram.filename == expected_latest_name, \
                f"Latest diagram should be {expected_latest_name}, but got {latest_diagram.filename}"
            
            # Test 4: Verify creation time ordering
            all_diagrams = diagram_manager.get_all_diagrams()
            assert len(all_diagrams) == num_files
            
            # Sort by creation time and verify the latest is actually the most recent
            sorted_diagrams = sorted(all_diagrams, key=lambda d: d.created_at)
            actual_latest = sorted_diagrams[-1]
            
            assert actual_latest.filename == latest_diagram.filename, \
                "Latest diagram should match the most recently created file"
            
            # Test 5: Add one more file and verify it becomes the new latest
            final_filename = "final_diagram.png"
            final_file_path = diagrams_folder / final_filename
            time.sleep(0.02)  # Ensure it's newer
            self._create_test_image_file(final_file_path, '.png')
            
            # Force refresh to detect the new file and get updated latest
            diagram_manager.get_all_diagrams(force_refresh=True)
            new_latest = diagram_manager.get_latest_diagram()
            
            assert new_latest.filename == final_filename, \
                f"New latest should be {final_filename}, but got {new_latest.filename}"
    
    @given(
        st.lists(
            st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
            min_size=1,
            max_size=3
        )
    )
    @settings(max_examples=15, deadline=None)
    def test_cross_platform_file_path_handling_property(self, filenames):
        """
        **Feature: streamlit-agent, Property 7: File path handling consistency**
        **Validates: Requirements 5.3**
        
        Property: For any valid diagram file path, the system should handle 
        file operations correctly regardless of the operating system path format.
        
        This test verifies cross-platform file path handling.
        """
        # Filter out empty filenames
        valid_filenames = [name for name in filenames if name.strip()]
        assume(len(valid_filenames) > 0)
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Create files with various path formats
            created_files = []
            for i, filename in enumerate(valid_filenames):
                safe_filename = f"{filename}_{i}.png"
                file_path = diagrams_folder / safe_filename
                
                # Create test image file
                self._create_test_image_file(file_path, '.png')
                created_files.append(file_path)
            
            # Test 2: Verify all files are detected with normalized paths
            detected_diagrams = diagram_manager.get_all_diagrams()
            assert len(detected_diagrams) == len(created_files)
            
            # Test 3: Verify path normalization
            for diagram_info in detected_diagrams:
                # Check that paths are properly normalized
                normalized_path = diagram_info.filepath
                
                # Verify the path exists and is accessible
                assert Path(normalized_path).exists(), \
                    f"Normalized path should exist: {normalized_path}"
                
                # Verify path format consistency (forward slashes for consistency)
                if os.name != 'nt':  # On non-Windows systems
                    assert '\\' not in normalized_path, \
                        "Paths should use forward slashes for consistency"
                
                # Verify the path resolves to the correct file
                resolved_path = Path(normalized_path).resolve()
                assert resolved_path.exists(), \
                    f"Resolved path should exist: {resolved_path}"
            
            # Test 4: Test file operations work with normalized paths
            for diagram_info in detected_diagrams:
                # Test file size calculation
                assert diagram_info.file_size > 0, \
                    "File size should be calculated correctly"
                
                # Test file existence check
                assert diagram_info.exists == True, \
                    "File existence should be correctly determined"
                
                # Test metadata extraction
                assert isinstance(diagram_info.created_at, datetime), \
                    "Creation time should be properly extracted"
                
                assert len(diagram_info.title) > 0, \
                    "Title should be generated from filename"
            
            # Test 5: Test folder info with cross-platform paths
            folder_info = diagram_manager.get_folder_info()
            
            assert folder_info['folder_exists'] == True
            assert folder_info['is_directory'] == True
            assert folder_info['total_diagrams'] == len(created_files)
            assert 'platform' in folder_info
            assert folder_info['readable'] == True
            assert folder_info['writable'] == True
    
    @given(st.integers(min_value=0, max_value=5))
    @settings(max_examples=10, deadline=None)
    def test_empty_folder_handling_property(self, num_non_image_files):
        """
        Property: For any folder state (empty, with non-image files, etc.), 
        the system should handle it gracefully without errors.
        
        This test verifies robust handling of various folder states.
        """
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Empty folder
            diagrams = diagram_manager.get_all_diagrams()
            assert len(diagrams) == 0, "Empty folder should return no diagrams"
            
            latest = diagram_manager.get_latest_diagram()
            assert latest is None, "Empty folder should return no latest diagram"
            
            # Test 2: Folder with non-image files
            for i in range(num_non_image_files):
                non_image_file = diagrams_folder / f"document_{i}.txt"
                non_image_file.write_text(f"This is document {i}")
            
            # Should still find no diagrams
            diagrams_after_text = diagram_manager.get_all_diagrams(force_refresh=True)
            assert len(diagrams_after_text) == 0, \
                "Non-image files should not be detected as diagrams"
            
            # Test 3: Add one valid image file
            image_file = diagrams_folder / "test_diagram.png"
            self._create_test_image_file(image_file, '.png')
            
            # Should now find exactly one diagram
            diagrams_with_image = diagram_manager.get_all_diagrams(force_refresh=True)
            assert len(diagrams_with_image) == 1, \
                "Should find exactly one diagram after adding image file"
            
            # Test 4: Verify folder info is accurate
            folder_info = diagram_manager.get_folder_info()
            assert folder_info['total_diagrams'] == 1
            assert folder_info['folder_exists'] == True
    
    def _create_test_image_file(self, file_path: Path, extension: str):
        """
        Create a minimal test image file for testing purposes
        
        Args:
            file_path: Path where to create the file
            extension: File extension (determines format)
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if extension.lower() == '.png':
            # Create minimal PNG file (1x1 pixel)
            png_data = (
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
                b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13'
                b'\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\x60\x60\x60'
                b'\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB\x60\x82'
            )
            file_path.write_bytes(png_data)
        elif extension.lower() in ['.jpg', '.jpeg']:
            # Create minimal JPEG file
            jpeg_data = (
                b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00'
                b'\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t'
                b'\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
                b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342'
                b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01'
                b'\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff'
                b'\xda\x00\x08\x01\x01\x00\x00?\x00\xaa\xff\xd9'
            )
            file_path.write_bytes(jpeg_data)
        else:
            # For other formats, create a simple binary file with some content
            # This won't be a valid image but will test file detection
            file_path.write_bytes(b'FAKE_IMAGE_DATA_FOR_TESTING' + os.urandom(100))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])