"""
Style Applier - Apply extracted template styles to new documents
"""

import json
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class StyleApplier:
    """Apply template styles to new documents"""

    def __init__(self, template_stats: Dict[str, Any]):
        self.stats = template_stats
        self.doc = None

    def create_document_from_template(self) -> Document:
        """Create new document with template settings"""
        self.doc = Document()
        self._apply_document_settings()
        return self.doc

    def _apply_document_settings(self):
        """Apply page setup and margins from template"""
        if 'sections' not in self.stats:
            return

        section_info = self.stats['sections']
        section = self.doc.sections[0]

        # Apply margins
        margins = section_info.get('margins', {})
        if margins:
            section.top_margin = Inches(margins.get('top', 0.5))
            section.bottom_margin = Inches(margins.get('bottom', 0.5))
            section.left_margin = Inches(margins.get('left', 0.5))
            section.right_margin = Inches(margins.get('right', 0.5))

    def apply_heading_style(self, paragraph, level: int = 1):
        """Apply heading style based on template patterns"""
        patterns = self.stats.get('formatting_patterns', {})
        heading_styles = patterns.get('heading_styles', [])

        # Use template heading style if available
        target_style = f'Heading {level}'
        if heading_styles and len(heading_styles) >= level:
            target_style = heading_styles[level - 1]

        # Apply style if it exists in document
        try:
            paragraph.style = target_style
        except:
            # Fallback to manual formatting
            self._apply_manual_heading(paragraph, level)

    def _apply_manual_heading(self, paragraph, level: int):
        """Apply manual heading formatting"""
        patterns = self.stats.get('formatting_patterns', {})
        common_fonts = patterns.get('common_fonts', {})

        # Get most common font
        font_name = max(common_fonts.keys()) if common_fonts else 'Calibri'

        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(14 - (level * 2))  # Decreasing size by level
            run.font.bold = True

    def apply_body_style(self, paragraph):
        """Apply body text style from template"""
        patterns = self.stats.get('formatting_patterns', {})
        common_fonts = patterns.get('common_fonts', {})
        common_sizes = patterns.get('common_sizes', {})

        # Get most common font and size
        font_name = max(common_fonts, key=common_fonts.get) if common_fonts else 'Calibri'
        font_size = max(common_sizes, key=common_sizes.get) if common_sizes else 11

        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(font_size)

    def apply_list_style(self, paragraph):
        """Apply list/bullet style from template"""
        patterns = self.stats.get('formatting_patterns', {})
        list_styles = patterns.get('list_styles', [])

        # Use template list style if available
        if list_styles:
            try:
                paragraph.style = list_styles[0]
                return
            except:
                pass

        # Fallback to List Bullet
        try:
            paragraph.style = 'List Bullet'
        except:
            # Manual bullet formatting
            paragraph.paragraph_format.left_indent = Inches(0.25)
            paragraph.paragraph_format.first_line_indent = Inches(-0.25)

    def get_template_font(self) -> str:
        """Get the most common font from template"""
        patterns = self.stats.get('formatting_patterns', {})
        common_fonts = patterns.get('common_fonts', {})
        return max(common_fonts, key=common_fonts.get) if common_fonts else 'Calibri'

    def get_template_size(self, context: str = 'body') -> int:
        """Get appropriate font size based on context"""
        patterns = self.stats.get('formatting_patterns', {})
        common_sizes = patterns.get('common_sizes', {})

        if not common_sizes:
            return 11

        sizes = list(common_sizes.keys())
        sizes.sort()

        if context == 'heading':
            return int(max(sizes)) if sizes else 14
        elif context == 'name':
            return int(max(sizes) + 4) if sizes else 18
        else:
            return int(min(sizes)) if sizes else 11


# Usage helper
def load_template_stats(file_path: str) -> Dict[str, Any]:
    """Load template statistics from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading template stats: {str(e)}")
        raise