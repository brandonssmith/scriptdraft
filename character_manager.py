"""
Character Manager Component
Manages character names and provides SmartType functionality
"""

import re
from PyQt6.QtWidgets import QListWidget, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

class CharacterManager(QWidget):
    """Manages character names and provides SmartType functionality"""
    
    character_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.characters = set()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Characters")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Add character section
        add_layout = QHBoxLayout()
        self.character_input = QLineEdit()
        self.character_input.setPlaceholderText("Enter character name")
        self.character_input.returnPressed.connect(self.add_character)
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_character)
        
        add_layout.addWidget(self.character_input)
        add_layout.addWidget(add_button)
        layout.addLayout(add_layout)
        
        # Character list
        self.character_list = QListWidget()
        self.character_list.itemDoubleClicked.connect(self.on_character_selected)
        layout.addWidget(self.character_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_character)
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_characters)
        
        cleanup_button = QPushButton("Clean Up")
        cleanup_button.clicked.connect(self.cleanup_characters)
        
        button_layout.addWidget(remove_button)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(cleanup_button)
        layout.addLayout(button_layout)
        
    def add_character(self):
        """Add a character to the list"""
        name = self.character_input.text().strip()
        if name:
            # Convert to uppercase for consistency
            name = name.upper()
            self.characters.add(name)
            self.update_character_list()
            self.character_input.clear()
            
    def remove_character(self):
        """Remove selected character"""
        current_item = self.character_list.currentItem()
        if current_item:
            character_name = current_item.text()
            self.characters.discard(character_name)
            self.update_character_list()
            
    def clear_characters(self):
        """Clear all characters"""
        self.characters.clear()
        self.update_character_list()
        
    def cleanup_characters(self):
        """Clean up character list by removing invalid names and fragments"""
        cleaned_characters = set()
        
        for character in self.characters:
            if self.is_valid_character_name(character):
                cleaned_characters.add(character)
                
        self.characters = cleaned_characters
        self.update_character_list()
        
    def update_character_list(self):
        """Update the character list display"""
        self.character_list.clear()
        for character in sorted(self.characters):
            self.character_list.addItem(character)
            
    def on_character_selected(self, item):
        """Handle character selection"""
        character_name = item.text()
        self.character_selected.emit(character_name)
        
    def update_from_text(self, text):
        """Update character list from screenplay text"""
        # Only add names from lines that are formatted as Character (i.e., after Enter or line break)
        lines = text.split('\n')
        found_characters = set()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Only consider lines that are likely formatted as Character
            if self.is_character_line(line):
                character_name = self.extract_character_name(line)
                if character_name and self.is_valid_character_name(character_name):
                    found_characters.add(character_name)
        # Replace the character set (not update) to avoid keeping partials
        self.characters = found_characters
        self.update_character_list()
        
    def is_valid_character_name(self, name):
        """Check if a character name is valid (complete, not a fragment)"""
        # Must be at least 2 characters long
        if len(name) < 2:
            return False
            
        # Must not be a scene heading fragment
        scene_fragments = ['I', 'IN', 'INT', 'E', 'EX', 'EXT']
        if name in scene_fragments:
            return False
            
        # Must not be a transition fragment
        transition_fragments = ['F', 'FA', 'FAD', 'FADE', 'C', 'CU', 'CUT', 'D', 'DI', 'DIS', 'DISS', 'DISSOLVE']
        if name in transition_fragments:
            return False
            
        # Must not be a shot fragment
        shot_fragments = ['C', 'CL', 'CLO', 'CLOSE', 'W', 'WI', 'WID', 'WIDE', 'M', 'ME', 'MED', 'MEDIUM']
        if name in shot_fragments:
            return False
            
        # Must not be a single letter (except for very specific cases)
        if len(name) == 1 and name not in ['A', 'I']:  # Allow 'A' and 'I' as valid single-letter names
            return False
            
        # Must not be a common word fragment
        common_fragments = ['A', 'AN', 'THE', 'AND', 'OR', 'BUT', 'IF', 'OF', 'TO', 'IN', 'ON', 'AT', 'BY', 'FOR', 'WITH']
        if name in common_fragments:
            return False
            
        return True
        
    def is_character_line(self, line):
        """Check if a line looks like a character name"""
        # Character names are typically:
        # - All uppercase
        # - No periods (except for abbreviations)
        # - Short (1-4 words)
        # - Not scene headings or transitions
        
        if not line.isupper():
            return False
            
        # Exclude scene headings
        if re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)', line, re.IGNORECASE):
            return False
            
        # Exclude transitions
        if re.match(r'^(FADE|CUT|DISSOLVE|SMASH|MATCH|JUMP)', line, re.IGNORECASE):
            return False
            
        # Exclude shot descriptions
        if re.match(r'^(CLOSE|WIDE|MEDIUM|EXTREME|POV|ANGLE)', line, re.IGNORECASE):
            return False
            
        # Exclude lines that end with periods (likely dialogue)
        if line.endswith('.'):
            return False
            
        # Check word count (allow up to 4 words for character names)
        words = line.split()
        if len(words) > 4:
            return False
            
        # Must have at least one word
        if len(words) == 0:
            return False
            
        return True
        
    def extract_character_name(self, line):
        """Extract character name from a line"""
        # Remove common prefixes/suffixes
        name = line.strip()
        
        # Remove parentheticals
        name = re.sub(r'\s*\([^)]*\)\s*', '', name)
        
        # Remove common character modifiers
        modifiers = [
            r'\s*\(CONT\'D\)\s*',
            r'\s*\(CONTINUED\)\s*',
            r'\s*\(V\.O\.\)\s*',
            r'\s*\(O\.S\.\)\s*',
            r'\s*\(O\.C\.\)\s*',
            r'\s*\(O\.F\.F\.\)\s*'
        ]
        
        for modifier in modifiers:
            name = re.sub(modifier, '', name, flags=re.IGNORECASE)
            
        # Clean up extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove any remaining punctuation at the end
        name = re.sub(r'[.!?]+$', '', name)
        
        return name
        
    def get_characters(self):
        """Get list of all characters"""
        return sorted(self.characters)
        
    def has_character(self, name):
        """Check if character exists"""
        return name.upper() in self.characters 