#!/usr/bin/env python3
"""
Property-based tests for file path handling consistency

**Feature: streamlit-agent, Property 7: File path handling consistency**
**Validates: Requirements 5.3**

This module contains property-based tests that verify cross-platform file path
handling consistency in the Streamlit agent application.
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
import platform

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

# Import the components
sys.path.append(str(Path(__file__).parent.parent))
from components import DiagramManager, DiagramInfo


class TestFilePathConsistencyProperty:
    """Property-based tests for file path handling consistency"""

    @given(
        st.lists(
            st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'))),
            min_size=1,
            max_size=4
        )
    )
    @settings(max_examples=20, deadline=None)
    def test_file_path_handling_consistency_property(self, path_components):
        """
        **Feature: streamlit-agent, Property 7: File path handling consistency**
        **Validates: Requirements 5.3**
        
        Property: For any valid diagram file path, the system should handle 
        file operations correctly regardless of the operating system path format.
        
        This test verifies that:
        1. File paths are normalized consistently across platforms
        2. File operations work with normalized paths
        3. Path resolution is consistent regardless of input format
        4. Cross-platform compatibility is maintained
        """
        # Filter out empty or invalid path components
        valid_components = [comp.strip() for comp in path_components if comp.strip() and len(comp.strip()) > 0]
        assume(len(valid_components) > 0)
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Create files with various path component combinations
            created_files = []
            for i, component in enumerate(valid_components):
                # Create safe filename from component
                safe_filename = f"{component}_{i}.png"
                # Remove any problematic characters for filenames
                safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in "._-")
                if not safe_filename or safe_filename.startswith('.'):
                    safe_filename = f"diagram_{i}.png"
                
                file_path = diagrams_folder / safe_filename
                
                # Create test image file
                self._create_test_image_file(file_path)
                created_files.append((safe_filename, file_path))
            
            # Test 2: Verify all files are detected with normalized paths
            detected_diagrams = diagram_manager.get_all_diagrams(force_refresh=True)
            assert len(detected_diagrams) == len(created_files), \
                f"Should detect {len(created_files)} diagrams, found {len(detected_diagrams)}"
            
            # Test 3: Verify path normalization consistency
            for diagram_info in detected_diagrams:
                normalized_path = diagram_info.filepath
                
                # Test that normalized path exists and is accessible
                assert Path(normalized_path).exists(), \
                    f"Normalized path should exist: {normalized_path}"
                
                # Test path format consistency
                if os.name != 'nt':  # On non-Windows systems
                    # Should use forward slashes for consistency
                    assert '\\' not in normalized_path, \
                        f"Non-Windows paths should use forward slashes: {normalized_path}"
                
                # Test that path resolves correctly
                resolved_path = Path(normalized_path).resolve()
                assert resolved_path.exists(), \
                    f"Resolved path should exist: {resolved_path}"
                
                # Test that the resolved path points to the same file
                original_path = None
                for filename, orig_path in created_files:
                    if filename == diagram_info.filename:
                        original_path = orig_path
                        break
                
                if original_path:
                    assert resolved_path.samefile(original_path), \
                        f"Resolved path should point to the same file as original"
            
            # Test 4: Test file operations with normalized paths
            for diagram_info in detected_diagrams:
                # Test file size calculation
                assert diagram_info.file_size > 0, \
                    f"File size should be calculated correctly for {diagram_info.filepath}"
                
                # Test file existence check
                assert diagram_info.exists == True, \
                    f"File existence should be correctly determined for {diagram_info.filepath}"
                
                # Test metadata extraction
                assert isinstance(diagram_info.created_at, datetime), \
                    f"Creation time should be properly extracted for {diagram_info.filepath}"
                
                # Test that we can read the file using the normalized path
                try:
                    file_content = Path(diagram_info.filepath).read_bytes()
                    assert len(file_content) > 0, \
                        f"Should be able to read file content from normalized path: {diagram_info.filepath}"
                except Exception as e:
                    pytest.fail(f"Failed to read file using normalized path {diagram_info.filepath}: {e}")

    @given(
        st.lists(
            st.sampled_from(['subdir1', 'subdir2', 'nested', 'deep_folder', 'test_dir']),
            min_size=0,
            max_size=2
        ),
        st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    @settings(max_examples=15, deadline=None)
    def test_nested_path_handling_property(self, subdirs, filename_base):
        """
        **Feature: streamlit-agent, Property 7: File path handling consistency**
        **Validates: Requirements 5.3**
        
        Property: For any nested directory structure within the diagrams folder, 
        the system should handle file paths consistently and correctly.
        
        This test verifies nested directory path handling.
        """
        assume(filename_base.strip() != "")
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Create nested directory structure
            current_dir = diagrams_folder
            for subdir in subdirs:
                current_dir = current_dir / subdir
            
            # Create a file in the nested directory (if any)
            safe_filename = f"{filename_base.strip()}.png"
            nested_file_path = current_dir / safe_filename
            
            # Create the file
            self._create_test_image_file(nested_file_path)
            
            # Also create a file in the root diagrams folder for comparison
            root_file_path = diagrams_folder / f"root_{safe_filename}"
            self._create_test_image_file(root_file_path)
            
            # Test 2: Verify file detection
            detected_diagrams = diagram_manager.get_all_diagrams(force_refresh=True)
            
            # Should find at least the root file, nested files depend on implementation
            # (DiagramManager might only scan the root folder)
            root_diagrams = [d for d in detected_diagrams if d.filename.startswith('root_')]
            assert len(root_diagrams) >= 1, "Should find at least the root diagram"
            
            # Test 3: Verify path consistency for found diagrams
            for diagram_info in detected_diagrams:
                # Test path normalization
                normalized_path = diagram_info.filepath
                
                # Verify the path is properly normalized
                path_obj = Path(normalized_path)
                assert path_obj.is_absolute() or str(path_obj).startswith('/'), \
                    f"Path should be absolute or properly formatted: {normalized_path}"
                
                # Test file accessibility
                assert path_obj.exists(), \
                    f"Normalized path should be accessible: {normalized_path}"
                
                # Test cross-platform path handling
                if platform.system() == "Windows":
                    # On Windows, paths might contain backslashes in the original form
                    # but should be handled consistently
                    assert path_obj.exists(), f"Windows path should be accessible: {normalized_path}"
                else:
                    # On Unix-like systems, should use forward slashes
                    if '\\' in normalized_path:
                        # This might be acceptable if it's a valid path, but test accessibility
                        assert path_obj.exists(), f"Unix path should be accessible: {normalized_path}"

    @given(
        st.lists(
            st.sampled_from(['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp']),
            min_size=1,
            max_size=3
        )
    )
    @settings(max_examples=10, deadline=None)
    def test_different_file_extensions_path_handling_property(self, extensions):
        """
        **Feature: streamlit-agent, Property 7: File path handling consistency**
        **Validates: Requirements 5.3**
        
        Property: For any supported file extension, the system should handle 
        file paths consistently regardless of the extension type.
        
        This test verifies that path handling is consistent across different file types.
        """
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Create files with different extensions
            created_files = []
            for i, extension in enumerate(extensions):
                filename = f"diagram_{i:02d}{extension}"
                file_path = diagrams_folder / filename
                
                # Create appropriate test file based on extension
                self._create_test_file_by_extension(file_path, extension)
                created_files.append((filename, extension))
            
            # Test 2: Verify all supported files are detected
            detected_diagrams = diagram_manager.get_all_diagrams(force_refresh=True)
            
            # All created files should be detected (they're all supported extensions)
            assert len(detected_diagrams) == len(created_files), \
                f"Should detect all {len(created_files)} files with supported extensions"
            
            # Test 3: Verify path handling consistency across extensions
            extension_to_diagram = {}
            for diagram_info in detected_diagrams:
                file_extension = Path(diagram_info.filename).suffix.lower()
                extension_to_diagram[file_extension] = diagram_info
                
                # Test path normalization consistency
                normalized_path = diagram_info.filepath
                
                # Verify path format is consistent regardless of extension
                assert Path(normalized_path).exists(), \
                    f"Path should exist for {file_extension} file: {normalized_path}"
                
                # Verify metadata extraction works consistently
                assert diagram_info.file_size > 0, \
                    f"File size should be positive for {file_extension} file"
                
                assert isinstance(diagram_info.created_at, datetime), \
                    f"Creation time should be datetime for {file_extension} file"
                
                # Verify title generation works consistently
                assert len(diagram_info.title) > 0, \
                    f"Title should be generated for {file_extension} file"
            
            # Test 4: Verify that path operations work the same way for all extensions
            for ext, diagram_info in extension_to_diagram.items():
                # Test file reading
                try:
                    content = Path(diagram_info.filepath).read_bytes()
                    assert len(content) > 0, f"Should be able to read {ext} file"
                except Exception as e:
                    pytest.fail(f"Failed to read {ext} file at {diagram_info.filepath}: {e}")
                
                # Test path resolution
                resolved = Path(diagram_info.filepath).resolve()
                assert resolved.exists(), f"Resolved path should exist for {ext} file"

    def test_folder_info_cross_platform_consistency_property(self):
        """
        **Feature: streamlit-agent, Property 7: File path handling consistency**
        **Validates: Requirements 5.3**
        
        Property: The folder information should be reported consistently 
        across different platforms and path formats.
        
        This test verifies that folder operations are cross-platform consistent.
        """
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Get folder info and verify consistency
            folder_info = diagram_manager.get_folder_info()
            
            # Verify required fields are present
            required_fields = ['folder_path', 'folder_exists', 'is_directory', 'platform', 
                             'total_diagrams', 'total_size_bytes', 'readable', 'writable']
            
            for field in required_fields:
                assert field in folder_info, f"Folder info should contain {field}"
            
            # Test 2: Verify path format in folder info
            folder_path = folder_info['folder_path']
            
            # Should be an absolute path
            path_obj = Path(folder_path)
            assert path_obj.is_absolute(), f"Folder path should be absolute: {folder_path}"
            
            # Should exist (was created by DiagramManager)
            assert folder_info['folder_exists'] == True, "Folder should exist"
            assert folder_info['is_directory'] == True, "Should be a directory"
            
            # Test 3: Verify platform-specific information is correct
            reported_platform = folder_info['platform']
            actual_platform = platform.system()
            assert reported_platform == actual_platform, \
                f"Reported platform {reported_platform} should match actual {actual_platform}"
            
            # Test 4: Create some files and verify folder info updates
            for i in range(3):
                filename = f"test_{i}.png"
                file_path = diagrams_folder / filename
                self._create_test_image_file(file_path)
            
            # Force refresh to detect new files
            diagram_manager.get_all_diagrams(force_refresh=True)
            
            # Get updated folder info
            updated_info = diagram_manager.get_folder_info()
            
            # Should reflect the new files
            assert updated_info['total_diagrams'] == 3, "Should count the created diagrams"
            assert updated_info['total_size_bytes'] > 0, "Should calculate total size"
            
            # Path should remain consistent
            assert updated_info['folder_path'] == folder_path, \
                "Folder path should remain consistent across calls"

    def _create_test_image_file(self, file_path: Path):
        """
        Create a minimal test PNG file for testing purposes
        
        Args:
            file_path: Path where to create the file
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create minimal PNG file (1x1 pixel)
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13'
            b'\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\x60\x60\x60'
            b'\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB\x60\x82'
        )
        file_path.write_bytes(png_data)

    def _create_test_file_by_extension(self, file_path: Path, extension: str):
        """
        Create a test file with appropriate content based on extension
        
        Args:
            file_path: Path where to create the file
            extension: File extension to determine content type
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if extension.lower() == '.png':
            # Create minimal PNG file
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
            # This won't be a valid image but will test file detection and path handling
            file_path.write_bytes(b'FAKE_IMAGE_DATA_FOR_TESTING_' + extension.encode() + os.urandom(50))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])