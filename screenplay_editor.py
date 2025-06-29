"""
Screenplay Editor Component
Handles the main text editing with screenplay-specific formatting
"""

import re
from PyQt6.QtWidgets import QTextEdit, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QKeyEvent, QTextBlockFormat, QTextListFormat

class ScreenplayEditor(QTextEdit):
    """Main screenplay editor with industry-standard formatting"""
    
    element_type_changed = pyqtSignal(str)
    
    def __init__(self, smarttype_manager=None):
        super().__init__()
        self.current_element_type = "Scene Heading"  # Start with Scene Heading
        self.smarttype_manager = smarttype_manager
        self.setup_editor()
        self.setup_formats()
        self.setup_smarttype_connections()
        
    def setup_editor(self):
        """Setup the editor appearance and behavior"""
        # Set font to Courier New (industry standard)
        font = QFont("Courier New", 12)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Set margins for screenplay format
        # Industry standard: Left 1.5", Right 1", Top/Bottom 1"
        # Since we can't set exact margins in QTextEdit, we'll use document margins
        # and handle proper indentation in the export
        self.document().setDocumentMargin(72)  # 1 inch margins
        
        # Set line spacing
        self.document().setDefaultFont(font)
        
        # Enable undo/redo
        self.document().setUndoRedoEnabled(True)
        
        # Set background color for better visibility
        self.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #6a6a6a;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Connect text change signal for SmartType
        self.textChanged.connect(self.on_text_changed)
        
    def setup_smarttype_connections(self):
        """Setup connections to SmartType manager"""
        if self.smarttype_manager:
            self.smarttype_manager.suggestion_selected.connect(self.insert_suggestion)
            
    def on_text_changed(self):
        """Handle text changes for SmartType processing and element type detection"""
        if self.smarttype_manager:
            cursor = self.textCursor()
            text = self.toPlainText()
            cursor_position = cursor.position()
            self.smarttype_manager.process_text_input(text, cursor_position)
            
        # Check if current line should be a different element type
        self.check_current_line_element_type()
        
    def check_current_line_element_type(self):
        """Check if the current line should be formatted as a different element type"""
        cursor = self.textCursor()
        current_line = cursor.block().text().strip()
        
        if current_line:
            detected_type = self.detect_element_type(current_line)
            
            # If the detected type is different from current type, update it
            if detected_type != self.current_element_type:
                self.current_element_type = detected_type
                self.apply_format_to_current_line(detected_type)
                self.element_type_changed.emit(detected_type)
        
    def insert_suggestion(self, suggestion):
        """Insert a SmartType suggestion at the current cursor position, replacing the current word"""
        cursor = self.textCursor()
        text = self.toPlainText()
        position = cursor.position()
        
        # Find the start of the current word
        start = position
        while start > 0 and text[start - 1].isalnum():
            start -= 1
        # Find the end of the current word
        end = position
        while end < len(text) and text[end].isalnum():
            end += 1
        
        # Select the current word
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        
        # Replace with the suggestion
        cursor.insertText(suggestion)
        
        # Update cursor position
        cursor.setPosition(start + len(suggestion))
        self.setTextCursor(cursor)
        
    def get_current_word(self):
        """Get the current word being typed at cursor position"""
        cursor = self.textCursor()
        text = self.toPlainText()
        position = cursor.position()
        
        if position > len(text):
            return ""
            
        # Find the start of the current word
        start = position
        while start > 0 and text[start - 1].isalnum():
            start -= 1
            
        # Find the end of the current word
        end = position
        while end < len(text) and text[end].isalnum():
            end += 1
            
        return text[start:end]
        
    def set_smarttype_manager(self, smarttype_manager):
        """Set the SmartType manager"""
        self.smarttype_manager = smarttype_manager
        self.setup_smarttype_connections()
        
    def setup_formats(self):
        """Setup text formats for different screenplay elements with proper indentation"""
        self.formats = {
            "Scene Heading": self.create_scene_heading_format(),
            "Action": self.create_action_format(),
            "Character": self.create_character_format(),
            "Dialogue": self.create_dialogue_format(),
            "Parenthetical": self.create_parenthetical_format(),
            "Transition": self.create_transition_format(),
            "Shot": self.create_shot_format()
        }
        
    def create_scene_heading_format(self):
        """Create format for scene headings - all caps, bold, no indentation"""
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Bold)
        format.setFontCapitalization(QFont.Capitalization.AllUppercase)
        return format
        
    def create_action_format(self):
        """Create format for action lines - normal case, no indentation"""
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Normal)
        format.setFontCapitalization(QFont.Capitalization.MixedCase)
        return format
        
    def create_character_format(self):
        """Create format for character names - all caps, bold, centered (4" from left)"""
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Bold)
        format.setFontCapitalization(QFont.Capitalization.AllUppercase)
        return format
        
    def create_dialogue_format(self):
        """Create format for dialogue - normal case, indented (2.5" from left)"""
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Normal)
        format.setFontCapitalization(QFont.Capitalization.MixedCase)
        return format
        
    def create_parenthetical_format(self):
        """Create format for parentheticals - normal case, italic, indented (3.5" from left)"""
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Normal)
        format.setFontCapitalization(QFont.Capitalization.MixedCase)
        format.setFontItalic(True)
        return format
        
    def create_transition_format(self):
        """Create format for transitions - all caps, bold, right-aligned"""
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Bold)
        format.setFontCapitalization(QFont.Capitalization.AllUppercase)
        return format
        
    def create_shot_format(self):
        """Create format for shot descriptions - all caps, bold"""
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Bold)
        format.setFontCapitalization(QFont.Capitalization.AllUppercase)
        return format
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events for screenplay formatting"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.handle_enter_key()
        elif event.key() == Qt.Key.Key_Tab:
            self.handle_tab_key()
        elif event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.handle_smarttype_trigger()
        else:
            super().keyPressEvent(event)
            
    def handle_smarttype_trigger(self):
        """Handle Ctrl+Space to trigger SmartType suggestions"""
        if self.smarttype_manager:
            # Get current word and show suggestions
            current_word = self.get_current_word()
            if current_word:
                suggestions = self.smarttype_manager.generate_suggestions(current_word)
                if suggestions:
                    self.smarttype_manager.show_suggestions_popup()
                    
    def handle_enter_key(self):
        """Handle Enter key for automatic element type switching"""
        cursor = self.textCursor()
        current_line = cursor.block().text().strip()
        
        # Determine next element type based on current content
        # This will automatically set Action after Scene Heading, Dialogue after Character, etc.
        next_type = self.determine_next_element_type(current_line)
        
        # Insert new line
        cursor.insertText("\n")
        
        # Apply formatting to the new line
        self.apply_format_to_current_line(next_type)
        
        # Update current element type
        self.current_element_type = next_type
        self.element_type_changed.emit(next_type)
        
    def handle_tab_key(self):
        """Handle Tab key for indentation and element switching"""
        cursor = self.textCursor()
        current_line = cursor.block().text().strip()
        
        # If current line is empty or action, convert to character
        if not current_line or self.current_element_type == "Action":
            self.current_element_type = "Character"
            self.apply_format_to_current_line("Character")
            self.element_type_changed.emit("Character")
        # If current line is character, convert to dialogue
        elif self.current_element_type == "Character":
            self.current_element_type = "Dialogue"
            self.apply_format_to_current_line("Dialogue")
            self.element_type_changed.emit("Dialogue")
        # If current line is dialogue, convert to parenthetical
        elif self.current_element_type == "Dialogue":
            self.current_element_type = "Parenthetical"
            self.apply_format_to_current_line("Parenthetical")
            self.element_type_changed.emit("Parenthetical")
        # If current line is parenthetical, convert back to dialogue
        elif self.current_element_type == "Parenthetical":
            self.current_element_type = "Dialogue"
            self.apply_format_to_current_line("Dialogue")
            self.element_type_changed.emit("Dialogue")
        # Otherwise, insert tab
        else:
            cursor.insertText("\t")
            
    def determine_next_element_type(self, current_line):
        """Determine the next element type based on current line content"""
        # Scene heading patterns - always followed by Action
        if re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)', current_line, re.IGNORECASE):
            return "Action"
            
        # Character name patterns (all caps, no periods, not scene headings or transitions)
        # More reliable detection for character names - check if it looks like a character name
        if (current_line.isupper() and 
            not re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.|FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP)', current_line, re.IGNORECASE) and
            not current_line.endswith('.') and
            len(current_line.split()) <= 4 and  # Allow up to 4 words for character names
            len(current_line) > 0):
            return "Dialogue"
            
        # Also check if current element type is Character (for indented character names)
        if self.current_element_type == "Character":
            return "Dialogue"
            
        # Transition patterns - followed by Scene Heading
        if re.match(r'^(FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP)', current_line, re.IGNORECASE):
            return "Scene Heading"
            
        # Parenthetical patterns - followed by Dialogue
        if current_line.startswith('(') and current_line.endswith(')'):
            return "Dialogue"
            
        # Shot patterns - followed by Action
        if re.match(r'^(CLOSE|WIDE|MEDIUM|EXTREME|POV|ANGLE)', current_line, re.IGNORECASE):
            return "Action"
            
        # Default to Action for most cases
        return "Action"
        
    def apply_format_to_current_line(self, element_type):
        """Apply formatting to the current line with proper indentation and alignment"""
        cursor = self.textCursor()
        block = cursor.block()
        
        # Select the entire line
        cursor.setPosition(block.position())
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        
        # Apply the character format
        if element_type in self.formats:
            cursor.setCharFormat(self.formats[element_type])
            
        # Apply block formatting for indentation and alignment
        block_format = self.get_block_format(element_type)
        cursor.setBlockFormat(block_format)
        
    def get_block_format(self, element_type):
        """Get block format for proper indentation and alignment"""
        from PyQt6.QtGui import QTextBlockFormat
        
        block_format = QTextBlockFormat()
        
        # Convert inches to pixels (assuming 96 DPI)
        # 1 inch = 96 pixels
        inch_to_pixels = 96
        
        if element_type == "Scene Heading":
            # Scene headings: no indentation, left-aligned
            block_format.setIndent(0)
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(12)
            block_format.setBottomMargin(12)
            
        elif element_type == "Action":
            # Action lines: no indentation, left-aligned
            block_format.setIndent(0)
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(6)
            block_format.setBottomMargin(6)
            
        elif element_type == "Character":
            # Character names: indented to 4" from left margin
            block_format.setIndent(0)
            block_format.setLeftMargin(4 * inch_to_pixels)  # 4 inches from left
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(12)
            block_format.setBottomMargin(6)
            
        elif element_type == "Dialogue":
            # Dialogue: indented to 2.5" from left margin, 2" from right margin
            block_format.setIndent(0)
            block_format.setLeftMargin(2.5 * inch_to_pixels)  # 2.5 inches from left
            block_format.setRightMargin(2 * inch_to_pixels)   # 2 inches from right
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(6)
            block_format.setBottomMargin(6)
            
        elif element_type == "Parenthetical":
            # Parentheticals: indented to 3.5" from left margin, 2.5" from right margin
            block_format.setIndent(0)
            block_format.setLeftMargin(3.5 * inch_to_pixels)  # 3.5 inches from left
            block_format.setRightMargin(2.5 * inch_to_pixels) # 2.5 inches from right
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(6)
            block_format.setBottomMargin(6)
            
        elif element_type == "Transition":
            # Transitions: right-aligned
            block_format.setIndent(0)
            block_format.setAlignment(Qt.AlignmentFlag.AlignRight)
            block_format.setTopMargin(12)
            block_format.setBottomMargin(12)
            
        else:
            # Default: no indentation, left-aligned
            block_format.setIndent(0)
            block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            block_format.setTopMargin(6)
            block_format.setBottomMargin(6)
            
        return block_format
        
    def set_current_element_type(self, element_type):
        """Set the current element type and apply formatting"""
        self.current_element_type = element_type
        self.apply_format_to_current_line(element_type)
        
    def insert_character(self, character_name):
        """Insert a character name at cursor position with proper formatting"""
        cursor = self.textCursor()
        cursor.insertText(character_name)
        self.current_element_type = "Character"
        self.apply_format_to_current_line("Character")
        self.element_type_changed.emit("Character")
        
    def insert_scene(self, scene_name):
        """Insert a scene heading at cursor position with proper formatting"""
        cursor = self.textCursor()
        cursor.insertText(scene_name)
        self.current_element_type = "Scene Heading"
        self.apply_format_to_current_line("Scene Heading")
        self.element_type_changed.emit("Scene Heading")
        
    def auto_format(self):
        """Auto-format the entire document with proper indentation and alignment"""
        cursor = self.textCursor()
        original_position = cursor.position()
        
        # Start from the beginning
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Process each block
        while not cursor.atEnd():
            block = cursor.block()
            text = block.text().strip()
            
            if text:
                element_type = self.detect_element_type(text)
                
                # Apply character formatting
                cursor.setPosition(block.position())
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(self.formats[element_type])
                
                # Apply block formatting
                block_format = self.get_block_format(element_type)
                cursor.setBlockFormat(block_format)
            
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
            
        # Restore cursor position
        cursor.setPosition(original_position)
        self.setTextCursor(cursor)
        
    def detect_element_type(self, text):
        """Detect element type from text content"""
        # Scene heading patterns - check first
        if re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)', text, re.IGNORECASE):
            return "Scene Heading"
            
        # Transition patterns
        if re.match(r'^(FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP)', text, re.IGNORECASE):
            return "Transition"
            
        # Character name patterns - more reliable detection
        if (text.isupper() and 
            not re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.|FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP)', text, re.IGNORECASE) and
            not text.endswith('.') and
            len(text.split()) <= 4 and  # Allow up to 4 words for character names
            len(text) > 0):
            return "Character"
            
        # Parenthetical patterns
        if text.startswith('(') and text.endswith(')'):
            return "Parenthetical"
            
        # Shot patterns
        if re.match(r'^(CLOSE|WIDE|MEDIUM|EXTREME|POV|ANGLE)', text, re.IGNORECASE):
            return "Shot"
            
        # Default to Action
        return "Action"
        
    def get_formatted_text(self):
        """Get the text with proper screenplay formatting"""
        # This would return text formatted according to industry standards
        # For now, return plain text
        return self.toPlainText()
        
    def set_formatted_text(self, text):
        """Set text and apply formatting"""
        self.setPlainText(text)
        self.auto_format()
        
    def clear(self):
        """Clear the document and reset to Scene Heading format"""
        super().clear()
        self.current_element_type = "Scene Heading"
        self.element_type_changed.emit("Scene Heading") 