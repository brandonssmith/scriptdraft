"""
Title Page Manager Component
Handles title page creation and display with industry-standard formatting
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QLabel, QTextEdit, QPushButton, QGroupBox, QGridLayout)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QTextBlockFormat

class TitlePageManager(QWidget):
    """Manages title page creation and display"""
    
    title_page_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.title = ""
        self.author = ""
        self.contact_info = ""
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the title page interface"""
        layout = QVBoxLayout(self)
        
        # Title page display area
        self.title_display = QTextEdit()
        self.title_display.setReadOnly(True)
        self.title_display.setMaximumHeight(400)
        self.title_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: black;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 20px;
                font-family: 'Courier New';
            }
        """)
        layout.addWidget(self.title_display)
        
        # Title page editor
        editor_group = QGroupBox("Title Page Information")
        editor_layout = QGridLayout(editor_group)
        
        # Title
        title_label = QLabel("Title:")
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter screenplay title")
        self.title_input.textChanged.connect(self.update_title_display)
        editor_layout.addWidget(title_label, 0, 0)
        editor_layout.addWidget(self.title_input, 0, 1)
        
        # Author
        author_label = QLabel("Author:")
        author_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Enter author name")
        self.author_input.textChanged.connect(self.update_title_display)
        editor_layout.addWidget(author_label, 1, 0)
        editor_layout.addWidget(self.author_input, 1, 1)
        
        # Contact Information
        contact_label = QLabel("Contact Info:")
        contact_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.contact_input = QTextEdit()
        self.contact_input.setMaximumHeight(80)
        self.contact_input.setPlaceholderText("Enter contact information (address, phone, email)")
        self.contact_input.textChanged.connect(self.update_title_display)
        editor_layout.addWidget(contact_label, 2, 0)
        editor_layout.addWidget(self.contact_input, 2, 1)
        
        layout.addWidget(editor_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_title_page)
        
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Initialize display
        self.update_title_display()
        
    def update_title_display(self):
        """Update the title page display"""
        self.title = self.title_input.text().strip()
        self.author = self.author_input.text().strip()
        self.contact_info = self.contact_input.toPlainText().strip()
        
        # Create formatted title page
        title_page_text = self.create_formatted_title_page()
        
        # Apply formatting
        self.title_display.clear()
        cursor = self.title_display.textCursor()
        cursor.insertText(title_page_text)
        self.apply_title_page_formatting()
        self.apply_contact_info_bottom_left()
        
        # Emit signal
        self.title_page_updated.emit()
        
    def create_formatted_title_page(self):
        """Create the formatted title page text"""
        lines = []
        
        # Add spacing for centering
        for _ in range(20):
            lines.append("")
            
        # Title (centered, bold, large)
        if self.title:
            lines.append(self.title.upper())
        else:
            lines.append("UNTITLED SCREENPLAY")
            
        # Add spacing
        for _ in range(8):
            lines.append("")
            
        # Author (centered)
        if self.author:
            lines.append(f"by")
            lines.append("")
            lines.append(self.author)
        else:
            lines.append("by")
            lines.append("")
            lines.append("AUTHOR NAME")
            
        # Add spacing
        for _ in range(8):
            lines.append("")
            
        # Contact information (centered, smaller)
        if self.contact_info:
            contact_lines = self.contact_info.split('\n')
            for line in contact_lines:
                if line.strip():
                    lines.append(line.strip())
                    
        return '\n'.join(lines)
        
    def apply_title_page_formatting(self):
        """Apply formatting to the title page display"""
        cursor = self.title_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Set document margins for centering
        doc = self.title_display.document()
        doc.setDocumentMargin(72)  # 1 inch margins
        
        # Apply formatting to title
        lines = self.title_display.toPlainText().split('\n')
        current_line = 0
        
        for i, line in enumerate(lines):
            if line.strip():
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, i)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                
                # Apply formatting based on line content
                if line == self.title.upper() if self.title else line == "UNTITLED SCREENPLAY":
                    # Title formatting
                    char_format = QTextCharFormat()
                    char_format.setFontFamily("Courier New")
                    char_format.setFontPointSize(18)
                    char_format.setFontWeight(QFont.Weight.Bold)
                    cursor.setCharFormat(char_format)
                    
                    # Center the title
                    block_format = QTextBlockFormat()
                    block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cursor.setBlockFormat(block_format)
                    
                elif line == "by":
                    # "by" formatting
                    char_format = QTextCharFormat()
                    char_format.setFontFamily("Courier New")
                    char_format.setFontPointSize(12)
                    char_format.setFontWeight(QFont.Weight.Normal)
                    cursor.setCharFormat(char_format)
                    
                    block_format = QTextBlockFormat()
                    block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cursor.setBlockFormat(block_format)
                    
                elif line == self.author if self.author else line == "AUTHOR NAME":
                    # Author formatting
                    char_format = QTextCharFormat()
                    char_format.setFontFamily("Courier New")
                    char_format.setFontPointSize(14)
                    char_format.setFontWeight(QFont.Weight.Bold)
                    cursor.setCharFormat(char_format)
                    
                    block_format = QTextBlockFormat()
                    block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cursor.setBlockFormat(block_format)
                    
                elif line in self.contact_info.split('\n') if self.contact_info else False:
                    # Contact info formatting
                    char_format = QTextCharFormat()
                    char_format.setFontFamily("Courier New")
                    char_format.setFontPointSize(10)
                    char_format.setFontWeight(QFont.Weight.Normal)
                    cursor.setCharFormat(char_format)
                    
                    block_format = QTextBlockFormat()
                    block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cursor.setBlockFormat(block_format)
                    
    def apply_contact_info_bottom_left(self):
        """Apply formatting to move contact info to the bottom left of the page (up to 4 lines)"""
        doc = self.title_display.document()
        block_count = doc.blockCount()
        contact_lines = self.contact_info.split('\n') if self.contact_info else []
        # Only use up to 4 lines
        contact_lines = contact_lines[:4]
        if not contact_lines:
            return
        # Find the last non-empty block (for contact info)
        block_idx = block_count - len(contact_lines)
        for i, line in enumerate(contact_lines):
            block = doc.findBlockByNumber(block_idx + i)
            cursor = self.title_display.textCursor()
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            # Set left alignment and smaller font
            char_format = QTextCharFormat()
            char_format.setFontFamily("Courier New")
            char_format.setFontPointSize(10)
            char_format.setFontWeight(QFont.Weight.Normal)
            cursor.setCharFormat(char_format)
            block_format = QTextBlockFormat()
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setBottomMargin(0)
            cursor.setBlockFormat(block_format)
        # Add extra newlines to push contact info to the bottom
        extra_lines = max(0, 30 - block_count)
        if extra_lines > 0:
            self.title_display.append("\n" * extra_lines)
        
    def clear_title_page(self):
        """Clear all title page information"""
        self.title_input.clear()
        self.author_input.clear()
        self.contact_input.clear()
        
    def get_title_page_info(self):
        """Get title page information"""
        return {
            'title': self.title,
            'author': self.author,
            'contact_info': self.contact_info
        }
        
    def set_title_page_info(self, title, author, contact_info):
        """Set title page information"""
        self.title_input.setText(title or "")
        self.author_input.setText(author or "")
        self.contact_input.setPlainText(contact_info or "")
        
    def has_content(self):
        """Check if title page has any content"""
        return bool(self.title or self.author or self.contact_info) 