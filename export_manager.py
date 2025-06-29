"""
Export Manager
Handles export to PDF and FDX (Final Draft XML) formats with industry-standard formatting
"""

import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from lxml import etree
from datetime import datetime

class ExportManager:
    """Manages export functionality for different formats with industry-standard formatting"""
    
    def __init__(self):
        self.setup_pdf_styles()
        
    def setup_pdf_styles(self):
        """Setup PDF styles for industry-standard screenplay formatting"""
        self.styles = getSampleStyleSheet()
        
        # Page setup: 8.5" x 11" with 1" margins on all sides
        # Left margin: 1.5", Right margin: 1", Top/Bottom: 1"
        
        # Scene Heading style (Sluglines)
        self.scene_style = ParagraphStyle(
            'SceneHeading',
            parent=self.styles['Normal'],
            fontName='Courier-Bold',
            fontSize=12,
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=0,  # 1.5" from left edge (handled by page margins)
            rightIndent=0,
            alignment=TA_LEFT
        )
        
        # Action style
        self.action_style = ParagraphStyle(
            'Action',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=12,
            spaceAfter=6,
            spaceBefore=6,
            leftIndent=0,  # No indentation
            rightIndent=0,
            alignment=TA_LEFT
        )
        
        # Character style (4" from left margin)
        self.character_style = ParagraphStyle(
            'Character',
            parent=self.styles['Normal'],
            fontName='Courier-Bold',
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            leftIndent=2.5*inch,  # 4" from left margin (1.5" + 2.5" = 4")
            rightIndent=0,
            alignment=TA_LEFT
        )
        
        # Dialogue style (2.5" from left margin, 2" from right)
        self.dialogue_style = ParagraphStyle(
            'Dialogue',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=12,
            spaceAfter=6,
            spaceBefore=6,
            leftIndent=1*inch,  # 2.5" from left margin (1.5" + 1" = 2.5")
            rightIndent=1*inch,  # 2" from right margin
            alignment=TA_LEFT
        )
        
        # Parenthetical style (3.5" from left margin)
        self.parenthetical_style = ParagraphStyle(
            'Parenthetical',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=12,
            spaceAfter=6,
            spaceBefore=6,
            leftIndent=2*inch,  # 3.5" from left margin (1.5" + 2" = 3.5")
            rightIndent=0.5*inch,  # 2.5" from right margin (1" + 0.5" = 1.5")
            alignment=TA_LEFT
        )
        
        # Transition style (right-aligned)
        self.transition_style = ParagraphStyle(
            'Transition',
            parent=self.styles['Normal'],
            fontName='Courier-Bold',
            fontSize=12,
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=0,
            rightIndent=0,
            alignment=TA_RIGHT
        )
        
        # Title page style
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Normal'],
            fontName='Courier-Bold',
            fontSize=18,
            spaceAfter=24,
            spaceBefore=0,
            leftIndent=0,
            rightIndent=0,
            alignment=TA_CENTER
        )
        
        # Author style
        self.author_style = ParagraphStyle(
            'Author',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=12,
            spaceAfter=48,
            spaceBefore=0,
            leftIndent=0,
            rightIndent=0,
            alignment=TA_CENTER
        )
        
        # Contact info style
        self.contact_style = ParagraphStyle(
            'Contact',
            parent=self.styles['Normal'],
            fontName='Courier',
            fontSize=10,
            spaceAfter=6,
            spaceBefore=0,
            leftIndent=0,
            rightIndent=0,
            alignment=TA_LEFT
        )
        
    def export_to_pdf(self, content, file_path, title="", author="", contact_info=""):
        """Export screenplay content to PDF with industry-standard formatting"""
        # Create document with proper margins
        doc = SimpleDocTemplate(
            file_path, 
            pagesize=letter,
            leftMargin=1.5*inch,  # 1.5" left margin
            rightMargin=1*inch,   # 1" right margin
            topMargin=1*inch,     # 1" top margin
            bottomMargin=1*inch   # 1" bottom margin
        )
        story = []
        
        # Add title page if title is provided
        if title:
            story.extend(self.create_title_page(title, author, contact_info))
            story.append(PageBreak())
        
        # Parse content and create PDF elements
        lines = content.split('\n')
        page_number = 2 if title else 1  # Start page numbering on second page if title page exists
        
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
                
            element_type = self.detect_element_type(line)
            style = self.get_pdf_style(element_type)
            
            # Clean up the text for PDF
            clean_text = self.clean_text_for_pdf(line, element_type)
            story.append(Paragraph(clean_text, style))
            
        doc.build(story)
        
    def create_title_page(self, title, author, contact_info):
        """Create title page elements"""
        elements = []
        
        # Add spacing to position title about one-third down the page
        elements.append(Spacer(1, 3*inch))
        
        # Title
        if title:
            elements.append(Paragraph(title.upper(), self.title_style))
        
        # Author
        if author:
            elements.append(Paragraph(f"Written by<br/>{author}", self.author_style))
        
        # Contact info (bottom left)
        if contact_info:
            # Add spacing to push contact info to bottom
            elements.append(Spacer(1, 4*inch))
            elements.append(Paragraph(contact_info, self.contact_style))
            
        return elements
        
    def export_to_fdx(self, content, file_path, title="", author="", contact_info=""):
        """Export screenplay content to FDX (Final Draft XML) with proper structure"""
        # Create the root element
        root = etree.Element("FinalDraft", DocumentType="Script", Template="No", Version="5")
        
        # Add document properties
        content_elem = etree.SubElement(root, "Content")
        
        # Add title page if title is provided
        if title:
            self.add_fdx_title_page(content_elem, title, author, contact_info)
        
        # Parse content and create FDX elements
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            element_type = self.detect_element_type(line)
            self.create_fdx_element(content_elem, element_type, line)
            
        # Write to file
        tree = etree.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
        
    def add_fdx_title_page(self, parent, title, author, contact_info):
        """Add title page to FDX"""
        # Title
        if title:
            title_para = etree.SubElement(parent, "Paragraph", Type="Title Page")
            title_text = etree.SubElement(title_para, "Text")
            title_text.text = title.upper()
            
        # Author
        if author:
            author_para = etree.SubElement(parent, "Paragraph", Type="Title Page")
            author_text = etree.SubElement(author_para, "Text")
            author_text.text = f"Written by {author}"
            
        # Contact info
        if contact_info:
            contact_para = etree.SubElement(parent, "Paragraph", Type="Title Page")
            contact_text = etree.SubElement(contact_para, "Text")
            contact_text.text = contact_info
        
    def detect_element_type(self, text):
        """Detect element type from text content"""
        # Scene heading patterns (INT./EXT./INT\/EXT./I\/E.)
        if re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)', text, re.IGNORECASE):
            return "Scene Heading"
            
        # Transition patterns
        if re.match(r'^(FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP|BLACK|WHITE)', text, re.IGNORECASE):
            return "Transition"
            
        # Character name patterns (all caps, no periods, not scene headings or transitions)
        if (text.isupper() and 
            not re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.|FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP|BLACK|WHITE)', text, re.IGNORECASE) and
            not text.endswith('.') and
            len(text.split()) <= 3):
            return "Character"
            
        # Parenthetical patterns
        if text.startswith('(') and text.endswith(')'):
            return "Parenthetical"
            
        # Shot patterns
        if re.match(r'^(CLOSE|WIDE|MEDIUM|EXTREME|POV|ANGLE|INSERT|TITLE)', text, re.IGNORECASE):
            return "Shot"
            
        # Default to Action
        return "Action"
        
    def get_pdf_style(self, element_type):
        """Get PDF style for element type"""
        styles = {
            "Scene Heading": self.scene_style,
            "Action": self.action_style,
            "Character": self.character_style,
            "Dialogue": self.dialogue_style,
            "Parenthetical": self.parenthetical_style,
            "Transition": self.transition_style,
            "Shot": self.scene_style
        }
        return styles.get(element_type, self.action_style)
        
    def clean_text_for_pdf(self, text, element_type):
        """Clean text for PDF export"""
        # Convert special characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # Ensure proper formatting
        if element_type == "Scene Heading":
            text = text.upper()
        elif element_type == "Character":
            text = text.upper()
        elif element_type == "Transition":
            text = text.upper()
            
        return text
        
    def create_fdx_element(self, parent, element_type, text):
        """Create FDX element with proper structure"""
        # Map element types to FDX types
        fdx_type_map = {
            "Scene Heading": "Scene Heading",
            "Action": "Action",
            "Character": "Character",
            "Dialogue": "Dialogue",
            "Parenthetical": "Parenthetical",
            "Transition": "Transition",
            "Shot": "Shot"
        }
        
        fdx_type = fdx_type_map.get(element_type, "Action")
        
        # Create the paragraph element
        paragraph = etree.SubElement(parent, "Paragraph", Type=fdx_type)
        
        # Add the text
        text_elem = etree.SubElement(paragraph, "Text")
        text_elem.text = text
        
        return paragraph 