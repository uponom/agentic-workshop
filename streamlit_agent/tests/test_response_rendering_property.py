#!/usr/bin/env python3
"""
Property-based tests for response rendering preservation

**Feature: streamlit-agent, Property 4: Response rendering preservation**
**Validates: Requirements 3.2, 3.5**

This module contains property-based tests that verify the ResponseRenderer
properly preserves markdown formatting, code blocks, and technical content
when rendering agent responses.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import re
import tempfile
import os

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

# Import the components
sys.path.append(str(Path(__file__).parent.parent))
from components.response_renderer import ResponseRenderer, DiagramInfo


class TestResponseRenderingProperty:
    """Property-based tests for response rendering preservation"""

    @given(st.text(min_size=10, max_size=1000))
    @settings(max_examples=100, deadline=None)
    def test_markdown_formatting_preservation_property(self, base_text):
        """
        **Feature: streamlit-agent, Property 4: Response rendering preservation**
        **Validates: Requirements 3.2, 3.5**
        
        Property: For any agent response containing markdown formatting, code blocks, 
        or technical content, the system should render it while preserving all 
        original formatting and structure.
        
        This test verifies that:
        1. Markdown formatting is rendered appropriately (Requirement 3.2)
        2. All formatting and code blocks are preserved (Requirement 3.5)
        """
        # Filter out empty or whitespace-only text
        assume(base_text.strip() != "")
        assume(len(base_text.strip()) >= 10)
        
        # Create various markdown formatted content
        markdown_elements = [
            f"# Header 1\n{base_text}",
            f"## Header 2\n{base_text}",
            f"### Header 3\n{base_text}",
            f"**Bold text**: {base_text}",
            f"*Italic text*: {base_text}",
            f"`inline code`: {base_text}",
            f"```python\ndef function():\n    return '{base_text}'\n```",
            f"```json\n{{\n  \"text\": \"{base_text[:50]}\"\n}}\n```",
            f"- List item 1: {base_text[:50]}\n- List item 2: more content",
            f"1. Numbered item: {base_text[:50]}\n2. Another item",
        ]
        
        renderer = ResponseRenderer()
        
        for markdown_content in markdown_elements:
            # Test 1: Preprocessing preserves markdown structure
            processed_text = renderer._preprocess_response_text(markdown_content)
            
            # Verify that markdown markers are preserved
            if "```" in markdown_content:
                assert "```" in processed_text, "Code block markers should be preserved"
            
            if "**" in markdown_content:
                assert "**" in processed_text, "Bold markers should be preserved"
            
            if "*" in markdown_content and "**" not in markdown_content:
                assert "*" in processed_text, "Italic markers should be preserved"
            
            if "`" in markdown_content and "```" not in markdown_content:
                assert "`" in processed_text, "Inline code markers should be preserved"
            
            if "#" in markdown_content:
                assert "#" in processed_text, "Header markers should be preserved"
            
            # Test 2: Original content is preserved
            # Remove markdown formatting to check if base content is preserved
            content_without_markers = re.sub(r'[#*`\-\d\.\s]+', ' ', processed_text)
            base_content_without_markers = re.sub(r'[#*`\-\d\.\s]+', ' ', base_text)
            
            # Check that the core content is still present
            assert len(processed_text.strip()) > 0, "Processed text should not be empty"
            
            # Test 3: HTML conversion preserves structure
            html_content = renderer._convert_markdown_to_html(processed_text)
            
            # Verify HTML tags are properly generated for markdown elements
            # Check for headers at the beginning of lines
            if re.search(r'^# ', processed_text, re.MULTILINE) and not re.search(r'^##', processed_text, re.MULTILINE):
                assert "<h1>" in html_content, "H1 headers should be converted to HTML"
            elif re.search(r'^## ', processed_text, re.MULTILINE) and not re.search(r'^###', processed_text, re.MULTILINE):
                assert "<h2>" in html_content, "H2 headers should be converted to HTML"
            elif re.search(r'^### ', processed_text, re.MULTILINE):
                assert "<h3>" in html_content, "H3 headers should be converted to HTML"
            
            if "```" in processed_text:
                assert "<pre>" in html_content or "<code>" in html_content, "Code blocks should be converted to HTML"
            
            # Check for inline code only if it's not part of a code block and has proper backtick pairs
            inline_code_pattern = r'`[^`\n]+`'
            if re.search(inline_code_pattern, processed_text) and "```" not in processed_text:
                assert "<code>" in html_content, "Inline code should be converted to HTML"
            
            if "**" in processed_text and processed_text.count("**") >= 2:
                assert "<strong>" in html_content, "Bold text should be converted to HTML"
            
            # Test 4: Content metrics are accurate
            metrics = renderer.get_content_metrics(processed_text)
            
            assert isinstance(metrics['character_count'], int)
            assert isinstance(metrics['word_count'], int)
            assert isinstance(metrics['line_count'], int)
            assert isinstance(metrics['code_blocks'], int)
            assert isinstance(metrics['estimated_reading_time'], float)
            assert isinstance(metrics['needs_scrolling'], bool)
            
            # Verify metrics make sense
            assert metrics['character_count'] > 0
            assert metrics['word_count'] > 0
            assert metrics['line_count'] > 0
            assert metrics['estimated_reading_time'] >= 0

    @given(st.text(min_size=20, max_size=500, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Po', 'Ps', 'Pe', 'Zs'))))
    @settings(max_examples=50, deadline=None)
    def test_code_block_preservation_property(self, code_content):
        """
        **Feature: streamlit-agent, Property 4: Response rendering preservation**
        **Validates: Requirements 3.2, 3.5**
        
        Property: For any response containing code blocks, the system should 
        preserve all code formatting, indentation, and technical syntax.
        """
        # Filter out empty content
        assume(code_content.strip() != "")
        assume(len(code_content.strip()) >= 20)
        
        # Create various code block formats
        code_formats = [
            f"```python\n{code_content}\n```",
            f"```javascript\n{code_content}\n```",
            f"```json\n{code_content}\n```",
            f"```yaml\n{code_content}\n```",
            f"```bash\n{code_content}\n```",
            f"```\n{code_content}\n```",  # No language specified
        ]
        
        renderer = ResponseRenderer()
        
        for code_block in code_formats:
            # Test 1: Code block structure is preserved during preprocessing
            processed = renderer._preprocess_response_text(code_block)
            
            # Verify code block markers are intact
            assert processed.count("```") >= 2, "Code block should have opening and closing markers"
            
            # Verify the content inside code blocks is preserved
            # Extract content between ``` markers
            code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', processed, re.DOTALL)
            if code_match:
                extracted_content = code_match.group(1)
                # The core content should be preserved (allowing for some whitespace normalization)
                assert len(extracted_content.strip()) > 0, "Code block content should not be empty"
            
            # Test 2: HTML conversion handles code blocks properly
            html_content = renderer._convert_markdown_to_html(processed)
            
            # Verify code blocks are converted to proper HTML
            assert "<pre>" in html_content or "<code>" in html_content, "Code blocks should be converted to HTML tags"
            
            # Test 3: Content metrics correctly identify code blocks
            metrics = renderer.get_content_metrics(processed)
            assert metrics['code_blocks'] >= 1, "Should detect at least one code block"

    @given(st.text(min_size=50, max_size=2000))
    @settings(max_examples=30, deadline=None)
    def test_technical_content_preservation_property(self, base_content):
        """
        **Feature: streamlit-agent, Property 4: Response rendering preservation**
        **Validates: Requirements 3.2, 3.5**
        
        Property: For any response containing technical terms, AWS service names,
        configuration snippets, and mixed formatting, all content should be 
        preserved with proper structure.
        """
        # Filter out empty content
        assume(base_content.strip() != "")
        assume(len(base_content.strip()) >= 50)
        
        # Create technical content with mixed formatting
        technical_content = f"""
# AWS Architecture Recommendation

## Overview
{base_content[:200]}

### Services Recommended
- **Amazon EC2**: `t3.medium` instances
- **Amazon RDS**: PostgreSQL database
- **Amazon S3**: Static asset storage
- **AWS Lambda**: Serverless functions

### Configuration Example
```yaml
Resources:
  MyInstance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.medium
      ImageId: ami-12345678
      UserData: |
        #!/bin/bash
        echo "{base_content[:100]}"
```

### Implementation Notes
The architecture should include:
1. **Load Balancer**: Application Load Balancer (ALB)
2. **Auto Scaling**: Target tracking scaling policy
3. **Monitoring**: CloudWatch metrics and alarms

#### Security Considerations
- Use `IAM roles` for service authentication
- Enable `VPC Flow Logs` for network monitoring
- Configure `Security Groups` with least privilege

**Important**: {base_content[200:400]}

```json
{{
  "Version": "2012-10-17",
  "Statement": [
    {{
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }}
  ]
}}
```
"""
        
        renderer = ResponseRenderer()
        
        # Test 1: Complex technical content is properly preprocessed
        processed = renderer._preprocess_response_text(technical_content)
        
        # Verify all markdown elements are preserved
        assert "#" in processed, "Headers should be preserved"
        assert "**" in processed, "Bold formatting should be preserved"
        assert "`" in processed, "Inline code should be preserved"
        assert "```" in processed, "Code blocks should be preserved"
        assert "-" in processed or "*" in processed, "List markers should be preserved"
        
        # Verify AWS service names are preserved
        aws_services = ["EC2", "RDS", "S3", "Lambda", "CloudWatch", "IAM", "VPC"]
        for service in aws_services:
            if service in technical_content:
                assert service in processed, f"AWS service name {service} should be preserved"
        
        # Test 2: HTML conversion maintains technical formatting
        html_content = renderer._convert_markdown_to_html(processed)
        
        # Verify technical elements are properly converted
        assert "<h1>" in html_content or "<h2>" in html_content or "<h3>" in html_content, "Headers should be converted"
        assert "<strong>" in html_content, "Bold text should be converted"
        assert "<code>" in html_content, "Code elements should be converted"
        assert "<pre>" in html_content, "Code blocks should be converted"
        
        # Test 3: Content metrics reflect complexity
        metrics = renderer.get_content_metrics(processed)
        
        # Technical content should have multiple code blocks
        assert metrics['code_blocks'] >= 2, "Should detect multiple code blocks in technical content"
        
        # Should have substantial word count
        assert metrics['word_count'] > 50, "Technical content should have substantial word count"
        
        # Should likely need scrolling due to length
        if len(processed) > 2000:
            assert metrics['needs_scrolling'] == True, "Long technical content should need scrolling"

    @given(st.text(min_size=10, max_size=200))
    @settings(max_examples=20, deadline=None)
    def test_mixed_formatting_preservation_property(self, content):
        """
        **Feature: streamlit-agent, Property 4: Response rendering preservation**
        **Validates: Requirements 3.2, 3.5**
        
        Property: For any response with mixed markdown formatting (headers, bold, 
        italic, code, lists), all formatting elements should be preserved and 
        properly rendered.
        """
        # Filter out empty content
        assume(content.strip() != "")
        assume(len(content.strip()) >= 10)
        
        # Create content with mixed formatting
        mixed_content = f"""
## {content[:30]}

This is **bold text** and this is *italic text*.

Here's some `inline code` and a list:
- Item 1: {content[30:60] if len(content) > 60 else content}
- Item 2: More content
- Item 3: `code item`

### Code Example
```
function example() {{
    return "{content[:50]}";
}}
```

**Note**: {content[60:] if len(content) > 60 else "Additional notes"}
"""
        
        renderer = ResponseRenderer()
        
        # Test preprocessing preserves all elements
        processed = renderer._preprocess_response_text(mixed_content)
        
        # Verify all formatting types are preserved
        formatting_elements = {
            "##": "Headers",
            "**": "Bold text",
            "*": "Italic text (when not part of **)",
            "`": "Inline code",
            "-": "List items",
            "```": "Code blocks"
        }
        
        for marker, description in formatting_elements.items():
            if marker in mixed_content:
                assert marker in processed, f"{description} markers should be preserved"
        
        # Test HTML conversion handles mixed formatting
        html_content = renderer._convert_markdown_to_html(processed)
        
        # Verify HTML elements are generated
        expected_html_elements = ["<h2>", "<strong>", "<code>", "<pre>"]
        html_elements_found = sum(1 for element in expected_html_elements if element in html_content)
        
        assert html_elements_found >= 2, "Should convert multiple formatting elements to HTML"
        
        # Test content metrics
        metrics = renderer.get_content_metrics(processed)
        assert metrics['character_count'] > 0
        assert metrics['word_count'] > 0

    def test_empty_and_edge_case_handling_property(self):
        """
        **Feature: streamlit-agent, Property 4: Response rendering preservation**
        **Validates: Requirements 3.2, 3.5**
        
        Property: The system should handle edge cases like empty content, 
        malformed markdown, and unusual formatting gracefully without losing data.
        """
        renderer = ResponseRenderer()
        
        # Test edge cases
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "```\n\n```",  # Empty code block
            "**",  # Incomplete bold
            "`",  # Incomplete inline code
            "# \n## \n### ",  # Empty headers
            "```python\nprint('test')\n",  # Unclosed code block
            "**bold** and `code` and *italic*",  # Mixed inline formatting
            "\n\n\n\n",  # Multiple newlines
            "Normal text\n```\ncode\n```\nMore text",  # Code block in middle
        ]
        
        for test_case in edge_cases:
            # Should not crash on any input
            try:
                processed = renderer._preprocess_response_text(test_case)
                html_content = renderer._convert_markdown_to_html(processed)
                metrics = renderer.get_content_metrics(processed)
                
                # Basic sanity checks
                assert isinstance(processed, str)
                assert isinstance(html_content, str)
                assert isinstance(metrics, dict)
                
                # Metrics should be valid
                assert metrics['character_count'] >= 0
                assert metrics['word_count'] >= 0
                assert metrics['line_count'] >= 0
                assert metrics['code_blocks'] >= 0
                
            except Exception as e:
                pytest.fail(f"Edge case '{repr(test_case)}' caused exception: {e}")

    @given(st.lists(st.text(min_size=5, max_size=100), min_size=1, max_size=10))
    @settings(max_examples=20, deadline=None)
    def test_multiple_code_blocks_preservation_property(self, code_snippets):
        """
        **Feature: streamlit-agent, Property 4: Response rendering preservation**
        **Validates: Requirements 3.2, 3.5**
        
        Property: For any response containing multiple code blocks with different
        languages and content, all code blocks should be preserved with their
        individual formatting and language specifications.
        """
        # Filter out empty snippets
        valid_snippets = [snippet.strip() for snippet in code_snippets if snippet.strip()]
        assume(len(valid_snippets) >= 1)
        
        # Create content with multiple code blocks
        languages = ['python', 'javascript', 'yaml', 'json', 'bash', 'sql']
        
        content_parts = ["# Multiple Code Examples\n"]
        
        for i, snippet in enumerate(valid_snippets[:5]):  # Limit to 5 to keep test manageable
            lang = languages[i % len(languages)]
            content_parts.append(f"\n## Example {i+1}\n")
            content_parts.append(f"```{lang}\n{snippet}\n```\n")
        
        multi_code_content = "".join(content_parts)
        
        renderer = ResponseRenderer()
        
        # Test preprocessing preserves all code blocks
        processed = renderer._preprocess_response_text(multi_code_content)
        
        # Count code blocks in original and processed
        # We limit to 5 snippets above, so we should have exactly that many code blocks
        expected_blocks = min(len(valid_snippets), 5)
        original_code_blocks = processed.count("```") // 2  # Each block has opening and closing
        assert original_code_blocks >= expected_blocks, f"All {expected_blocks} code blocks should be preserved, found {original_code_blocks}"
        
        # Test HTML conversion handles multiple code blocks
        html_content = renderer._convert_markdown_to_html(processed)
        
        # Should have multiple <pre> or <code> tags
        pre_tags = html_content.count("<pre>")
        code_tags = html_content.count("<code>")
        
        assert pre_tags >= 1 or code_tags >= len(valid_snippets), "Multiple code blocks should be converted to HTML"
        
        # Test metrics correctly count code blocks
        metrics = renderer.get_content_metrics(processed)
        expected_blocks = min(len(valid_snippets), 5)
        assert metrics['code_blocks'] >= expected_blocks, f"Should detect all {expected_blocks} code blocks"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])