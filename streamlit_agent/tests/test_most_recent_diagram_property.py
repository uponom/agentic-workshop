#!/usr/bin/env python3
"""
Property-based tests for most recent diagram selection

**Feature: streamlit-agent, Property 3: Most recent diagram selection**
**Validates: Requirements 2.3**

This module contains property-based tests that verify the most recent diagram
selection functionality in the Streamlit agent application.
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


class TestMostRecentDiagramProperty:
    """Property-based tests for most recent diagram selection"""

    @given(st.integers(min_value=2, max_value=8))
    @settings(max_examples=15, deadline=None)
    def test_most_recent_diagram_selection_property(self, num_diagrams):
        """
        **Feature: streamlit-agent, Property 3: Most recent diagram selection**
        **Validates: Requirements 2.3**
        
        Property: For any set of multiple diagram files with different creation times, 
        the system should display the most recently created diagram by default.
        
        This test verifies that:
        1. The latest diagram is correctly identified from multiple files
        2. Creation time ordering is properly maintained
        3. The system consistently returns the most recent diagram
        """
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Create multiple diagrams with staggered creation times
            created_diagrams = []
            for i in range(num_diagrams):
                filename = f"architecture_{i:02d}.png"
                file_path = diagrams_folder / filename
                
                # Create test image file
                self._create_test_image_file(file_path)
                created_diagrams.append((filename, datetime.now()))
                
                # Ensure different creation times (important for ordering)
                time.sleep(0.03)
            
            # Test 2: Verify the latest diagram is correctly identified
            diagram_manager.get_all_diagrams(force_refresh=True)
            latest_diagram = diagram_manager.get_latest_diagram()
            
            assert latest_diagram is not None, "Latest diagram should be found"
            
            # The latest should be the last created file
            expected_latest_name = f"architecture_{num_diagrams-1:02d}.png"
            assert latest_diagram.filename == expected_latest_name, \
                f"Latest diagram should be {expected_latest_name}, but got {latest_diagram.filename}"
            
            # Test 3: Verify creation time ordering is correct
            all_diagrams = diagram_manager.get_all_diagrams()
            assert len(all_diagrams) == num_diagrams
            
            # Sort by creation time and verify the latest matches
            sorted_by_time = sorted(all_diagrams, key=lambda d: d.created_at)
            actual_latest = sorted_by_time[-1]
            
            assert actual_latest.filename == latest_diagram.filename, \
                "Latest diagram should match the most recently created file by timestamp"
            
            # Test 4: Verify consistency across multiple calls
            for _ in range(3):
                consistent_latest = diagram_manager.get_latest_diagram()
                assert consistent_latest.filename == latest_diagram.filename, \
                    "Latest diagram should be consistent across multiple calls"
            
            # Test 5: Add a new diagram and verify it becomes the new latest
            new_filename = "newest_architecture.png"
            new_file_path = diagrams_folder / new_filename
            time.sleep(0.03)  # Ensure it's newer
            self._create_test_image_file(new_file_path)
            
            # Force refresh and get new latest
            diagram_manager.get_all_diagrams(force_refresh=True)
            new_latest = diagram_manager.get_latest_diagram()
            
            assert new_latest.filename == new_filename, \
                f"New latest should be {new_filename}, but got {new_latest.filename}"
            
            # Verify the new latest is actually newer than the previous latest
            assert new_latest.created_at > latest_diagram.created_at, \
                "New latest diagram should have a more recent creation time"

    @given(
        st.lists(
            st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
            min_size=2,
            max_size=5
        )
    )
    @settings(max_examples=10, deadline=None)
    def test_latest_diagram_with_various_filenames_property(self, filenames):
        """
        **Feature: streamlit-agent, Property 3: Most recent diagram selection**
        **Validates: Requirements 2.3**
        
        Property: For any set of diagram files with various filenames but different 
        creation times, the system should correctly identify the most recent one 
        regardless of filename alphabetical order.
        
        This test verifies that creation time, not filename, determines the latest diagram.
        """
        # Filter out empty or duplicate filenames
        valid_filenames = list(set(name.strip() for name in filenames if name.strip()))
        assume(len(valid_filenames) >= 2)
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Create diagrams with various filenames in alphabetical order
            # but reverse chronological order (to test that time wins over name)
            created_files = []
            
            # Sort filenames alphabetically
            sorted_filenames = sorted(valid_filenames)
            
            # Create files in alphabetical order but we want the LAST alphabetical
            # name to be created FIRST (so it's older)
            for i, base_filename in enumerate(reversed(sorted_filenames)):
                filename = f"{base_filename}_{i}.png"
                file_path = diagrams_folder / filename
                
                self._create_test_image_file(file_path)
                created_files.append((filename, datetime.now()))
                
                # Ensure different creation times
                time.sleep(0.03)
            
            # Test 2: Verify the latest is the last created, not the last alphabetically
            diagram_manager.get_all_diagrams(force_refresh=True)
            latest_diagram = diagram_manager.get_latest_diagram()
            
            assert latest_diagram is not None, "Latest diagram should be found"
            
            # The latest should be the last created file (first in reversed list)
            expected_latest_base = sorted_filenames[0]  # First alphabetically, but last created
            expected_latest_name = f"{expected_latest_base}_{len(sorted_filenames)-1}.png"
            
            assert latest_diagram.filename == expected_latest_name, \
                f"Latest diagram should be {expected_latest_name} (most recent by time), but got {latest_diagram.filename}"
            
            # Test 3: Verify that alphabetical order doesn't affect selection
            all_diagrams = diagram_manager.get_all_diagrams()
            
            # Get the alphabetically first and last filenames
            alpha_first = min(d.filename for d in all_diagrams)
            alpha_last = max(d.filename for d in all_diagrams)
            
            # The latest by time should not necessarily be the alphabetically last
            if len(all_diagrams) > 1:
                # This test only makes sense if we have different filenames
                time_latest = latest_diagram.filename
                
                # Verify that time-based selection can differ from alphabetical selection
                # (This will be true in our test setup since we created files in reverse alpha order)
                assert time_latest != alpha_last or len(set(d.filename for d in all_diagrams)) == 1, \
                    "Latest by time should be independent of alphabetical order"

    @given(st.integers(min_value=1, max_value=5))
    @settings(max_examples=8, deadline=None)
    def test_latest_diagram_after_file_operations_property(self, initial_count):
        """
        **Feature: streamlit-agent, Property 3: Most recent diagram selection**
        **Validates: Requirements 2.3**
        
        Property: For any sequence of file operations (create, delete), the system 
        should always correctly identify the most recent remaining diagram.
        
        This test verifies that the latest diagram selection remains correct 
        after various file operations.
        """
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            diagrams_folder = Path(temp_dir) / "generated-diagrams"
            
            # Initialize DiagramManager with test folder
            diagram_manager = DiagramManager(str(diagrams_folder))
            
            # Test 1: Create initial set of diagrams
            initial_files = []
            for i in range(initial_count):
                filename = f"initial_{i:02d}.png"
                file_path = diagrams_folder / filename
                
                self._create_test_image_file(file_path)
                initial_files.append(filename)
                time.sleep(0.02)
            
            # Test 2: Verify initial latest
            if initial_count > 0:
                diagram_manager.get_all_diagrams(force_refresh=True)
                initial_latest = diagram_manager.get_latest_diagram()
                
                assert initial_latest is not None
                expected_initial = f"initial_{initial_count-1:02d}.png"
                assert initial_latest.filename == expected_initial
            
            # Test 3: Add more diagrams and verify latest updates
            additional_files = []
            for i in range(2):  # Add 2 more files
                filename = f"additional_{i:02d}.png"
                file_path = diagrams_folder / filename
                
                time.sleep(0.02)  # Ensure newer timestamp
                self._create_test_image_file(file_path)
                additional_files.append(filename)
            
            # Verify latest is now from additional files
            diagram_manager.get_all_diagrams(force_refresh=True)
            after_addition_latest = diagram_manager.get_latest_diagram()
            
            assert after_addition_latest.filename == "additional_01.png", \
                "Latest should be the most recently added file"
            
            # Test 4: Delete the latest file and verify new latest
            latest_file_path = diagrams_folder / "additional_01.png"
            if latest_file_path.exists():
                latest_file_path.unlink()
            
            # Verify latest is now the second most recent
            diagram_manager.get_all_diagrams(force_refresh=True)
            after_deletion_latest = diagram_manager.get_latest_diagram()
            
            if after_deletion_latest:  # Should still have files
                # Should be either additional_00.png or the last initial file
                expected_candidates = ["additional_00.png"]
                if initial_count > 0:
                    expected_candidates.append(f"initial_{initial_count-1:02d}.png")
                
                assert after_deletion_latest.filename in expected_candidates, \
                    f"After deletion, latest should be one of {expected_candidates}, got {after_deletion_latest.filename}"
            
            # Test 5: Add a final diagram and verify it becomes latest
            final_filename = "final_diagram.png"
            final_file_path = diagrams_folder / final_filename
            time.sleep(0.02)
            self._create_test_image_file(final_file_path)
            
            diagram_manager.get_all_diagrams(force_refresh=True)
            final_latest = diagram_manager.get_latest_diagram()
            
            assert final_latest.filename == final_filename, \
                f"Final latest should be {final_filename}, got {final_latest.filename}"

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])