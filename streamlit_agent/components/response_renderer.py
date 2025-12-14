#!/usr/bin/env python3
"""
ResponseRenderer Component

Handles formatting and display of agent responses in the Streamlit interface.
This component is responsible for rendering markdown content, handling code blocks,
managing technical formatting, and providing scrollable content areas for long responses.

Key responsibilities:
- Render markdown content appropriately
- Handle long responses with proper formatting
- Display text and images in coordinated layout
- Preserve technical formatting and code blocks
- Provide scrollable content areas for better UX
"""

import streamlit as st
import re
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import logging
from datetime import datetime
from .diagram_manager import DiagramInfo
from .error_handler import error_handler, ErrorCategory, with_error_boundary, handle_graceful_degradation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseRenderer:
    """
    Handles formatting and display of agent responses with markdown support,
    code block preservation, and coordinated layout for text and diagrams.
    """
    
    def __init__(self, diagram_manager=None):
        """
        Initialize the ResponseRenderer
        
        Args:
            diagram_manager: Optional DiagramManager instance for diagram handling
        """
        self.max_content_height = 600  # Maximum height for scrollable content
        self.code_block_theme = "dark"  # Theme for code blocks
        self.diagram_manager = diagram_manager
        
    @with_error_boundary("response_renderer", handle_graceful_degradation, ErrorCategory.UI_ERROR)
    def render_response(self, response_text: str, generated_files: Optional[List[str]] = None) -> None:
        """
        Render agent response with simple, reliable formatting
        
        Args:
            response_text: The agent's text response
            generated_files: List of generated file paths (optional)
        """
        # Ultra-simple rendering to avoid any complex errors
        if not response_text:
            st.warning("⚠️ No response content to display")
            return
        
        # Display the response text directly
        st.markdown("### 📝 AWS Architecture Guidance")
        st.markdown(response_text)
        
        # Display only diagrams generated for this specific request
        if generated_files:
            st.markdown("### 🏗️ Generated Diagrams")
            for file_path in generated_files:
                if file_path and os.path.exists(file_path):
                    # Extract filename for caption
                    filename = os.path.basename(file_path)
                    # Create a nice title from filename
                    title = filename.replace('_', ' ').replace('.png', '').title()
                    st.image(file_path, caption=title)
    
    @with_error_boundary("response_renderer", handle_graceful_degradation, ErrorCategory.DIAGRAM_ERROR)
    def render_diagram(self, image_path: str, caption: Optional[str] = None) -> bool:
        """
        Render a single diagram image with comprehensive error handling
        
        Args:
            image_path: Path to the image file
            caption: Optional caption for the image
            
        Returns:
            bool: True if successfully rendered, False otherwise
        """
        try:
            if not os.path.exists(image_path):
                error_info = error_handler.handle_diagram_error(
                    error=FileNotFoundError(f"Diagram file not found: {image_path}"),
                    diagram_name=Path(image_path).name,
                    show_in_ui=True
                )
                return False
            
            # Get diagram info
            diagram_info = self._get_diagram_info(image_path)
            
            if not diagram_info.exists:
                error_info = error_handler.handle_diagram_error(
                    error=FileNotFoundError(f"Cannot access diagram file: {image_path}"),
                    diagram_name=diagram_info.filename,
                    show_in_ui=True
                )
                return False
            
            # Display the image with error handling
            try:
                st.image(
                    image_path,
                    caption=caption or diagram_info.title
                    # Use default width (auto-fit to container)
                )
                
                # Show file information
                st.caption(f"📁 {diagram_info.filename} • 📏 {self._format_file_size(diagram_info.file_size)}")
                
                return True
                
            except Exception as display_error:
                error_handler.handle_diagram_error(
                    error=display_error,
                    diagram_name=diagram_info.filename,
                    show_in_ui=True
                )
                return False
            
        except Exception as e:
            error_handler.handle_diagram_error(
                error=e,
                diagram_name=Path(image_path).name if image_path else "unknown",
                show_in_ui=True
            )
            return False
    
    def render_scrollable_content(self, content: str, max_height: Optional[int] = None) -> None:
        """
        Render content in a scrollable container for long responses
        
        Args:
            content: Content to render
            max_height: Maximum height in pixels (optional)
        """
        # Simplified rendering without custom HTML to avoid issues
        with st.container():
            # Use Streamlit's built-in text area for long content
            st.text_area(
                "Response Content",
                value=content,
                height=min(max_height or self.max_content_height, 400),
                disabled=True,
                label_visibility="collapsed"
            )
    
    def _preprocess_response_text(self, text: str) -> str:
        """
        Preprocess response text to handle formatting and clean up content
        
        Args:
            text: Raw response text
            
        Returns:
            str: Processed text ready for rendering
        """
        # Remove excessive whitespace while preserving code blocks
        lines = text.split('\n')
        processed_lines = []
        in_code_block = False
        
        for line in lines:
            # Check for code block markers
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                processed_lines.append(line)
            elif in_code_block:
                # Preserve all whitespace in code blocks
                processed_lines.append(line)
            else:
                # Clean up regular text lines
                stripped = line.strip()
                if stripped or (processed_lines and processed_lines[-1].strip()):
                    processed_lines.append(line)
        
        # Join lines and handle multiple consecutive empty lines
        result = '\n'.join(processed_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
    def _extract_diagram_files(self, generated_files: List[str]) -> List[DiagramInfo]:
        """
        Extract and validate diagram files from generated files list
        
        Args:
            generated_files: List of generated file paths
            
        Returns:
            List[DiagramInfo]: List of valid diagram files with metadata
        """
        diagram_files = []
        
        for file_path in generated_files:
            if self._is_image_file(file_path):
                diagram_info = self._get_diagram_info(file_path)
                if diagram_info.exists:
                    diagram_files.append(diagram_info)
        
        # Sort by filename for consistent ordering
        diagram_files.sort(key=lambda x: x.filename)
        
        return diagram_files
    
    def _is_image_file(self, file_path: str) -> bool:
        """Check if file is a supported image format"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}
        return Path(file_path).suffix.lower() in image_extensions
    
    def _get_diagram_info(self, file_path: str) -> DiagramInfo:
        """
        Get detailed information about a diagram file
        
        Args:
            file_path: Path to the diagram file
            
        Returns:
            DiagramInfo: Metadata about the diagram
        """
        path = Path(file_path)
        
        try:
            if path.exists():
                stat = path.stat()
                title = self._generate_diagram_title(path.name)
                
                return DiagramInfo(
                    filepath=str(path),
                    filename=path.name,
                    title=title,
                    created_at=datetime.fromtimestamp(stat.st_mtime),
                    file_size=stat.st_size,
                    exists=True
                )
            else:
                return DiagramInfo(
                    filepath=str(path),
                    filename=path.name,
                    title=path.name,
                    created_at=datetime.now(),
                    file_size=0,
                    exists=False
                )
        except Exception as e:
            logger.warning(f"Error getting diagram info for {file_path}: {e}")
            return DiagramInfo(
                filepath=str(path),
                filename=path.name,
                title=path.name,
                created_at=datetime.now(),
                file_size=0,
                exists=False
            )
    
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
        
        # Add "Architecture" if not present
        if 'architecture' not in title.lower():
            title += ' Architecture'
        
        return title
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _render_coordinated_layout(self, text: str, diagram_files: List[DiagramInfo]) -> None:
        """
        Render text and diagrams in a coordinated layout with responsive design
        
        Args:
            text: Processed response text
            diagram_files: List of diagram files to display
        """
        # Simplified layout to avoid complex rendering issues
        st.markdown("### 📝 AWS Architecture Guidance")
        
        # Render text first
        try:
            st.markdown(text)
        except Exception:
            # Fallback to plain text if markdown fails
            st.text(text)
        
        # Render diagrams
        if diagram_files:
            st.markdown("### 🏗️ Generated Diagrams")
            
            for i, diagram in enumerate(diagram_files):
                try:
                    if os.path.exists(diagram.filepath):
                        st.image(diagram.filepath, caption=diagram.title)
                    else:
                        st.warning(f"📁 Diagram file not found: {diagram.filename}")
                except Exception as e:
                    st.error(f"❌ Error displaying diagram: {diagram.filename}")
        
        # Add simple summary for multiple diagrams
        if len(diagram_files) > 1:
            st.info(f"📊 Generated {len(diagram_files)} architecture diagrams")

    def _render_compact_layout(self, text: str, diagram: DiagramInfo) -> None:
        """Render compact layout for short content with single diagram"""
        # Single row with diagram on right
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("### 📝 Architecture Guidance")
            st.markdown(text)
        
        with col2:
            st.markdown("### 🏗️ Generated Diagram")
            self.render_diagram(diagram.filepath, caption=diagram.title)

    def _render_standard_two_column_layout(self, text: str, diagram_files: List[DiagramInfo]) -> None:
        """Render standard two-column layout"""
        # Responsive column sizing based on content
        content_metrics = self.get_content_metrics(text)
        
        if content_metrics['needs_scrolling']:
            # More space for text when scrolling is needed
            col_ratio = [3, 2]
        else:
            # Balanced layout for shorter content
            col_ratio = [2, 1]
        
        col1, col2 = st.columns(col_ratio)
        
        with col1:
            st.markdown("### 📝 Architecture Guidance")
            
            # Show content metrics for long content
            if content_metrics['needs_scrolling']:
                st.caption(f"📊 {content_metrics['word_count']} words • ~{content_metrics['estimated_reading_time']:.1f} min read")
            
            # Render content with appropriate scrolling
            if content_metrics['needs_scrolling']:
                self.render_scrollable_content(text)
            else:
                st.markdown(text)
        
        with col2:
            st.markdown("### 🏗️ Architecture Diagrams")
            
            # Render diagrams with proper spacing
            for i, diagram_info in enumerate(diagram_files):
                if i > 0:
                    st.markdown("---")
                
                success = self.render_diagram(
                    diagram_info.filepath,
                    caption=diagram_info.title
                )
                
                if not success:
                    st.error(f"Failed to load: {diagram_info.filename}")

    def _render_stacked_layout(self, text: str, diagram_files: List[DiagramInfo]) -> None:
        """Render stacked layout for multiple diagrams"""
        # Text section first
        st.markdown("### 📝 Architecture Guidance")
        
        content_metrics = self.get_content_metrics(text)
        if content_metrics['needs_scrolling']:
            st.caption(f"📊 {content_metrics['word_count']} words • ~{content_metrics['estimated_reading_time']:.1f} min read")
            self.render_scrollable_content(text, max_height=400)  # Shorter for stacked layout
        else:
            st.markdown(text)
        
        # Diagrams section with grid layout
        st.markdown("---")
        st.markdown("### 🏗️ Architecture Diagrams")
        
        # Create grid layout for multiple diagrams
        if len(diagram_files) <= 3:
            # Single row for up to 3 diagrams
            cols = st.columns(len(diagram_files))
            for i, diagram_info in enumerate(diagram_files):
                with cols[i]:
                    self.render_diagram(diagram_info.filepath, caption=diagram_info.title)
        else:
            # Multiple rows for more diagrams
            diagrams_per_row = 2
            for i in range(0, len(diagram_files), diagrams_per_row):
                row_diagrams = diagram_files[i:i + diagrams_per_row]
                # Ensure we create the right number of columns for the row
                num_cols = len(row_diagrams)
                cols = st.columns(num_cols)
                
                for j, diagram_info in enumerate(row_diagrams):
                    with cols[j]:
                        self.render_diagram(diagram_info.filepath, caption=diagram_info.title)

    def _render_diagram_summary(self, diagram_files: List[DiagramInfo]) -> None:
        """Render summary information for multiple diagrams"""
        st.markdown("---")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Diagrams", len(diagram_files))
        
        with col2:
            total_size = sum(d.file_size for d in diagram_files)
            st.metric("Total Size", self._format_file_size(total_size))
        
        with col3:
            latest = max(diagram_files, key=lambda d: d.created_at)
            st.metric("Latest", latest.created_at.strftime('%H:%M:%S'))
        
        # Expandable details
        with st.expander("📋 Diagram Details"):
            for diagram in diagram_files:
                st.text(f"• {diagram.title} ({self._format_file_size(diagram.file_size)})")
                st.caption(f"  📁 {diagram.filename} • 📅 {diagram.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _render_text_only_response(self, text: str) -> None:
        """
        Render text-only response without diagrams
        
        Args:
            text: Processed response text
        """
        st.markdown("### 📝 AWS Architecture Guidance")
        
        # Always use simple markdown rendering to avoid issues
        try:
            st.markdown(text)
        except Exception as e:
            # Fallback to plain text if markdown fails
            st.text(text)
        
        # Show message about missing diagrams
        try:
            self.render_no_diagrams_message()
        except Exception:
            # If this fails, just show a simple message
            st.info("💡 No diagrams were generated for this response.")
    
    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """
        Convert markdown to HTML for custom rendering
        
        Args:
            markdown_text: Markdown formatted text
            
        Returns:
            str: HTML formatted text
        """
        # Simple markdown to HTML conversion for basic formatting
        html = markdown_text
        
        # Handle code blocks
        html = re.sub(
            r'```(\w+)?\n(.*?)\n```',
            r'<pre><code class="language-\1">\2</code></pre>',
            html,
            flags=re.DOTALL
        )
        
        # Handle inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Handle bold text
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        
        # Handle italic text
        html = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', html)
        
        # Handle headers (before line break replacement)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Handle line breaks (after header processing)
        html = html.replace('\n', '<br>')
        
        return html
    
    def render_error_message(self, error_message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Render error messages with proper formatting
        
        Args:
            error_message: Main error message
            details: Optional additional error details
        """
        st.error(f"❌ {error_message}")
        
        if details:
            with st.expander("🔍 Error Details"):
                for key, value in details.items():
                    st.text(f"{key}: {value}")
    
    def render_loading_placeholder(self, message: str = "Processing...") -> None:
        """
        Render a loading placeholder while content is being processed
        
        Args:
            message: Loading message to display
        """
        with st.container():
            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    padding: 2rem;
                    color: #666;
                    font-style: italic;
                ">
                    🔄 {message}
                </div>
                """,
                unsafe_allow_html=True
            )
    
    def render_no_diagrams_message(self) -> None:
        """
        Render a fallback message when no diagrams are available
        """
        st.info("💡 No diagrams were generated for this response. Consider asking for specific architectural recommendations to get visual diagrams.")
    
    def render_diagram_error(self, error_message: str, diagram_name: str = "diagram") -> None:
        """
        Render an error message for corrupted or missing diagram files
        
        Args:
            error_message: The error message to display
            diagram_name: Name of the diagram that failed to load
        """
        st.error(f"❌ Failed to load {diagram_name}: {error_message}")
        
        # Provide helpful suggestions
        with st.expander("🔧 Troubleshooting"):
            st.markdown("""
            **Possible causes:**
            - The diagram file may be corrupted
            - The file may have been moved or deleted
            - There may be insufficient permissions to access the file
            - The file format may not be supported
            
            **Supported formats:** PNG, JPG, JPEG, GIF, BMP, SVG, WEBP
            """)
    
    def render_diagram_gallery(self, diagrams: List[DiagramInfo], max_display: int = 3) -> None:
        """
        Render multiple diagrams in a gallery layout
        
        Args:
            diagrams: List of diagram information objects
            max_display: Maximum number of diagrams to display at once
        """
        if not diagrams:
            self.render_no_diagrams_message()
            return
        
        # Sort diagrams by creation time (most recent first)
        sorted_diagrams = sorted(diagrams, key=lambda d: d.created_at, reverse=True)
        
        # Display up to max_display diagrams
        display_diagrams = sorted_diagrams[:max_display]
        
        st.markdown("### 🏗️ Architecture Diagrams")
        
        for i, diagram_info in enumerate(display_diagrams):
            if i > 0:
                st.markdown("---")  # Separator between diagrams
            
            # Show diagram metadata
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{diagram_info.title}**")
            with col2:
                st.caption(f"📅 {diagram_info.created_at.strftime('%H:%M:%S')}")
            
            # Try to render the diagram
            success = self.render_diagram(
                diagram_info.filepath,
                caption=f"{diagram_info.title} • {self._format_file_size(diagram_info.file_size)}"
            )
            
            if not success:
                self.render_diagram_error(
                    f"Could not load image file: {diagram_info.filename}",
                    diagram_info.title
                )
        
        # Show information about additional diagrams if any
        if len(sorted_diagrams) > max_display:
            remaining = len(sorted_diagrams) - max_display
            st.info(f"📊 {remaining} additional diagram(s) available. Use the diagram manager to view all diagrams.")
    
    def set_diagram_manager(self, diagram_manager) -> None:
        """
        Set the DiagramManager instance for this renderer
        
        Args:
            diagram_manager: DiagramManager instance
        """
        self.diagram_manager = diagram_manager
    
    def get_content_metrics(self, text: str) -> Dict[str, Any]:
        """
        Get metrics about the content for rendering decisions
        
        Args:
            text: Content to analyze
            
        Returns:
            Dict[str, Any]: Content metrics
        """
        lines = text.split('\n')
        words = text.split()
        
        # Count code blocks
        code_blocks = len(re.findall(r'```.*?```', text, re.DOTALL))
        
        # Estimate reading time (average 200 words per minute)
        reading_time_minutes = len(words) / 200
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'line_count': len(lines),
            'code_blocks': code_blocks,
            'estimated_reading_time': reading_time_minutes,
            'needs_scrolling': len(text) > 2000
        }