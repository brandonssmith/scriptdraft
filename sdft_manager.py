"""
SDft Manager Component
Handles saving and loading screenplay documents in custom XML format (.sdft)
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QTextBlockFormat, QFont
from PyQt6.QtCore import Qt

class SDftManager:
    """Manages SDft (ScriptDraft Format) file operations"""
    
    def __init__(self):
        self.namespace = "http://scriptdraft.app/sdft"
        ET.register_namespace('sdft', self.namespace)
        
    def save_document(self, screenplay_editor, title_page_manager=None, file_path=None):
        """Save the screenplay document in SDft format"""
        if not file_path:
            file_path, _ = QFileDialog.getSaveFileName(
                None, "Save Screenplay", "", "ScriptDraft Files (*.sdft)"
            )
            
        if not file_path:
            return False
            
        if not file_path.endswith('.sdft'):
            file_path += '.sdft'
            
        try:
            # Create the root element
            root = ET.Element(f"{{{self.namespace}}}screenplay")
            root.set("version", "1.0")
            root.set("format", "industry-standard")
            
            # Add metadata
            metadata = ET.SubElement(root, f"{{{self.namespace}}}metadata")
            
            # Add title page information if available
            if title_page_manager:
                title_page_info = title_page_manager.get_title_page_info()
                title_elem = ET.SubElement(metadata, f"{{{self.namespace}}}title")
                title_elem.text = title_page_info.get('title', 'Untitled Screenplay')
                
                author_elem = ET.SubElement(metadata, f"{{{self.namespace}}}author")
                author_elem.text = title_page_info.get('author', '')
                
                contact_elem = ET.SubElement(metadata, f"{{{self.namespace}}}contact_info")
                contact_elem.text = title_page_info.get('contact_info', '')
            else:
                title_elem = ET.SubElement(metadata, f"{{{self.namespace}}}title")
                title_elem.text = "Untitled Screenplay"
            
            # Add content
            content = ET.SubElement(root, f"{{{self.namespace}}}content")
            
            # Process each block in the document
            cursor = screenplay_editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            
            while not cursor.atEnd():
                block = cursor.block()
                text = block.text()
                
                if text.strip():  # Only process non-empty blocks
                    element_type = self.detect_element_type(text)
                    element = self.create_element_element(content, element_type, text)
                    
                    # Add formatting information
                    self.add_formatting_info(element, block, screenplay_editor)
                
                cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
            
            # Create pretty XML
            xml_str = self.prettify_xml(root)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)
                
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Could not save SDft file: {str(e)}")
            return False
            
    def load_document(self, screenplay_editor, title_page_manager=None, file_path=None):
        """Load a screenplay document from SDft format"""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(
                None, "Open Screenplay", "", "ScriptDraft Files (*.sdft)"
            )
            
        if not file_path:
            return False
            
        try:
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Load title page information if available
            if title_page_manager:
                metadata = root.find(f"{{{self.namespace}}}metadata")
                if metadata is not None:
                    title_elem = metadata.find(f"{{{self.namespace}}}title")
                    author_elem = metadata.find(f"{{{self.namespace}}}author")
                    contact_elem = metadata.find(f"{{{self.namespace}}}contact_info")
                    
                    title = title_elem.text if title_elem is not None else ""
                    author = author_elem.text if author_elem is not None else ""
                    contact_info = contact_elem.text if contact_elem is not None else ""
                    
                    title_page_manager.set_title_page_info(title, author, contact_info)
            
            # Clear current content
            screenplay_editor.clear()
            
            # Process content
            content = root.find(f"{{{self.namespace}}}content")
            if content is not None:
                for element in content.findall(f"{{{self.namespace}}}element"):
                    element_type = element.get("type", "Action")
                    text = element.text or ""
                    
                    # Insert text with proper formatting
                    self.insert_formatted_element(screenplay_editor, element_type, text, element)
                    
            return True
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Could not load SDft file: {str(e)}")
            return False
            
    def detect_element_type(self, text):
        """Detect element type from text content"""
        # Scene heading patterns
        if re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)', text, re.IGNORECASE):
            return "Scene Heading"
            
        # Transition patterns
        if re.match(r'^(FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP)', text, re.IGNORECASE):
            return "Transition"
            
        # Character name patterns
        if (text.isupper() and 
            not re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.|FADE|CUT|DISSOLVE)', text, re.IGNORECASE) and
            not text.endswith('.') and
            len(text.split()) <= 3):
            return "Character"
            
        # Parenthetical patterns
        if text.startswith('(') and text.endswith(')'):
            return "Parenthetical"
            
        # Shot patterns
        if re.match(r'^(CLOSE|WIDE|MEDIUM|EXTREME|POV|ANGLE)', text, re.IGNORECASE):
            return "Shot"
            
        # Default to Action
        return "Action"
        
    def create_element_element(self, parent, element_type, text):
        """Create an element XML element"""
        element = ET.SubElement(parent, f"{{{self.namespace}}}element")
        element.set("type", element_type)
        element.text = text
        return element
        
    def add_formatting_info(self, element, block, screenplay_editor):
        """Add formatting information to the element"""
        # Get block format
        block_format = block.blockFormat()
        
        # Add indentation information
        formatting = ET.SubElement(element, f"{{{self.namespace}}}formatting")
        
        # Left margin (indentation)
        left_margin = block_format.leftMargin()
        if left_margin > 0:
            left_margin_elem = ET.SubElement(formatting, f"{{{self.namespace}}}left_margin")
            left_margin_elem.text = str(left_margin)
            
        # Right margin
        right_margin = block_format.rightMargin()
        if right_margin > 0:
            right_margin_elem = ET.SubElement(formatting, f"{{{self.namespace}}}right_margin")
            right_margin_elem.text = str(right_margin)
            
        # Alignment
        alignment = block_format.alignment()
        alignment_elem = ET.SubElement(formatting, f"{{{self.namespace}}}alignment")
        if alignment == Qt.AlignmentFlag.AlignLeft:
            alignment_elem.text = "left"
        elif alignment == Qt.AlignmentFlag.AlignRight:
            alignment_elem.text = "right"
        elif alignment == Qt.AlignmentFlag.AlignCenter:
            alignment_elem.text = "center"
        else:
            alignment_elem.text = "left"
            
        # Top and bottom margins
        top_margin = block_format.topMargin()
        if top_margin > 0:
            top_margin_elem = ET.SubElement(formatting, f"{{{self.namespace}}}top_margin")
            top_margin_elem.text = str(top_margin)
            
        bottom_margin = block_format.bottomMargin()
        if bottom_margin > 0:
            bottom_margin_elem = ET.SubElement(formatting, f"{{{self.namespace}}}bottom_margin")
            bottom_margin_elem.text = str(bottom_margin)
            
        # Character formatting
        char_format = block.charFormat()
        char_formatting = ET.SubElement(formatting, f"{{{self.namespace}}}character_format")
        
        # Font weight
        font_weight = char_format.fontWeight()
        weight_elem = ET.SubElement(char_formatting, f"{{{self.namespace}}}font_weight")
        weight_elem.text = str(font_weight)
        
        # Font capitalization
        font_cap = char_format.fontCapitalization()
        cap_elem = ET.SubElement(char_formatting, f"{{{self.namespace}}}font_capitalization")
        cap_elem.text = str(font_cap)
        
        # Font italic
        font_italic = char_format.fontItalic()
        italic_elem = ET.SubElement(char_formatting, f"{{{self.namespace}}}font_italic")
        italic_elem.text = str(font_italic)
        
    def insert_formatted_element(self, screenplay_editor, element_type, text, element_xml):
        """Insert a formatted element into the screenplay editor"""
        cursor = screenplay_editor.textCursor()
        
        # Move to end of document
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Insert text
        cursor.insertText(text)
        
        # Apply formatting
        self.apply_formatting_from_xml(cursor, element_type, element_xml)
        
        # Insert newline
        cursor.insertText("\n")
        
    def apply_formatting_from_xml(self, cursor, element_type, element_xml):
        """Apply formatting from XML element"""
        # Select the inserted text
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        
        # Apply character formatting
        char_format = QTextCharFormat()
        
        # Set font weight based on element type
        if element_type in ["Scene Heading", "Character", "Transition", "Shot"]:
            char_format.setFontWeight(700)  # Bold
        else:
            char_format.setFontWeight(400)  # Normal
            
        # Set font capitalization
        if element_type in ["Scene Heading", "Character", "Transition", "Shot"]:
            char_format.setFontCapitalization(QFont.Capitalization.AllUppercase)
        else:
            char_format.setFontCapitalization(QFont.Capitalization.MixedCase)
            
        # Set font italic
        if element_type == "Parenthetical":
            char_format.setFontItalic(True)
            
        cursor.setCharFormat(char_format)
        
        # Apply block formatting
        block_format = QTextBlockFormat()
        
        # Get formatting from XML if available
        formatting_xml = element_xml.find(f"{{{self.namespace}}}formatting")
        if formatting_xml is not None:
            # Left margin
            left_margin_elem = formatting_xml.find(f"{{{self.namespace}}}left_margin")
            if left_margin_elem is not None:
                block_format.setLeftMargin(float(left_margin_elem.text))
                
            # Right margin
            right_margin_elem = formatting_xml.find(f"{{{self.namespace}}}right_margin")
            if right_margin_elem is not None:
                block_format.setRightMargin(float(right_margin_elem.text))
                
            # Alignment
            alignment_elem = formatting_xml.find(f"{{{self.namespace}}}alignment")
            if alignment_elem is not None:
                alignment_text = alignment_elem.text
                if alignment_text == "right":
                    block_format.setAlignment(Qt.AlignmentFlag.AlignRight)
                elif alignment_text == "center":
                    block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    
            # Top margin
            top_margin_elem = formatting_xml.find(f"{{{self.namespace}}}top_margin")
            if top_margin_elem is not None:
                block_format.setTopMargin(float(top_margin_elem.text))
                
            # Bottom margin
            bottom_margin_elem = formatting_xml.find(f"{{{self.namespace}}}bottom_margin")
            if bottom_margin_elem is not None:
                block_format.setBottomMargin(float(bottom_margin_elem.text))
        else:
            # Apply default formatting based on element type
            self.apply_default_block_format(block_format, element_type)
            
        cursor.setBlockFormat(block_format)
        
    def apply_default_block_format(self, block_format, element_type):
        """Apply default block formatting based on element type"""
        # Convert inches to pixels (assuming 96 DPI)
        inch_to_pixels = 96
        
        if element_type == "Scene Heading":
            block_format.setIndent(0)
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(12)
            block_format.setBottomMargin(12)
            
        elif element_type == "Action":
            block_format.setIndent(0)
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(6)
            block_format.setBottomMargin(6)
            
        elif element_type == "Character":
            block_format.setIndent(0)
            block_format.setLeftMargin(4 * inch_to_pixels)  # 4 inches from left
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(12)
            block_format.setBottomMargin(6)
            
        elif element_type == "Dialogue":
            block_format.setIndent(0)
            block_format.setLeftMargin(2.5 * inch_to_pixels)  # 2.5 inches from left
            block_format.setRightMargin(2 * inch_to_pixels)   # 2 inches from right
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(6)
            block_format.setBottomMargin(6)
            
        elif element_type == "Parenthetical":
            block_format.setIndent(0)
            block_format.setLeftMargin(3.5 * inch_to_pixels)  # 3.5 inches from left
            block_format.setRightMargin(2.5 * inch_to_pixels) # 2.5 inches from right
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(6)
            block_format.setBottomMargin(6)
            
        elif element_type == "Transition":
            block_format.setIndent(0)
            block_format.setAlignment(Qt.AlignmentFlag.AlignRight)
            block_format.setTopMargin(12)
            block_format.setBottomMargin(12)
            
        else:
            block_format.setIndent(0)
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(6)
            block_format.setBottomMargin(6)
            
    def prettify_xml(self, element):
        """Create pretty XML string"""
        rough_string = ET.tostring(element, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ") 