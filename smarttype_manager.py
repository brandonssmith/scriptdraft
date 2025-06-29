"""
SmartType Manager Component
Provides auto-complete functionality for character names and locations
"""

import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton,
                             QCompleter, QComboBox, QCheckBox, QGroupBox, QApplication, QTextEdit)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent

class SmartTypeManager(QWidget):
    """Manages SmartType auto-complete functionality"""
    
    suggestion_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.characters = set()
        self.locations = set()
        self.suggestions = []
        self.current_word = ""
        self.cursor_position = 0
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("SmartType Settings")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Location management
        loc_group = QGroupBox("Locations")
        loc_layout = QVBoxLayout(loc_group)
        
        # Location input
        loc_input_layout = QHBoxLayout()
        self.loc_input = QLineEdit()
        self.loc_input.setPlaceholderText("Add location name")
        self.loc_input.returnPressed.connect(self.add_location)
        
        loc_add_btn = QPushButton("Add")
        loc_add_btn.clicked.connect(self.add_location)
        
        loc_input_layout.addWidget(self.loc_input)
        loc_input_layout.addWidget(loc_add_btn)
        loc_layout.addLayout(loc_input_layout)
        
        # Location list
        self.loc_list = QListWidget()
        self.loc_list.itemDoubleClicked.connect(self.on_loc_selected)
        loc_layout.addWidget(self.loc_list)
        
        # Location buttons
        loc_btn_layout = QHBoxLayout()
        loc_remove_btn = QPushButton("Remove")
        loc_remove_btn.clicked.connect(self.remove_location)
        loc_clear_btn = QPushButton("Clear All")
        loc_clear_btn.clicked.connect(self.clear_locations)
        
        loc_btn_layout.addWidget(loc_remove_btn)
        loc_btn_layout.addWidget(loc_clear_btn)
        loc_layout.addLayout(loc_btn_layout)
        
        layout.addWidget(loc_group)
        
        # Settings
        settings_group = QGroupBox("SmartType Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        self.auto_complete_enabled = QCheckBox("Enable auto-complete")
        self.auto_complete_enabled.setChecked(True)
        settings_layout.addWidget(self.auto_complete_enabled)
        
        self.auto_capitalize = QCheckBox("Auto-capitalize suggestions")
        self.auto_capitalize.setChecked(True)
        settings_layout.addWidget(self.auto_capitalize)
        
        self.show_suggestions = QCheckBox("Show suggestion popup")
        self.show_suggestions.setChecked(True)
        settings_layout.addWidget(self.show_suggestions)
        
        layout.addWidget(settings_group)
        
        # Suggestion popup
        self.suggestion_popup = QListWidget()
        self.suggestion_popup.setVisible(False)
        self.suggestion_popup.itemClicked.connect(self.on_suggestion_selected)
        self.suggestion_popup.setMaximumHeight(150)
        self.suggestion_popup.setMaximumWidth(300)
        self.suggestion_popup.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.suggestion_popup.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: 2px solid #4a4a4a;
                border-radius: 6px;
                color: white;
                font-family: 'Courier New';
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #4a4a4a;
                border: 1px solid #6a6a6a;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
        
        # Timer for delayed suggestions
        self.suggestion_timer = QTimer()
        self.suggestion_timer.setSingleShot(True)
        self.suggestion_timer.timeout.connect(self.show_suggestions_popup)
        
    def add_location(self):
        """Add a location to the list"""
        name = self.loc_input.text().strip()
        if name:
            if self.auto_capitalize.isChecked():
                name = name.upper()
            self.locations.add(name)
            self.update_location_list()
            self.loc_input.clear()
            
    def remove_location(self):
        """Remove selected location"""
        current_item = self.loc_list.currentItem()
        if current_item:
            location_name = current_item.text()
            self.locations.discard(location_name)
            self.update_location_list()
            
    def clear_locations(self):
        """Clear all locations"""
        self.locations.clear()
        self.update_location_list()
        
    def update_location_list(self):
        """Update the location list display"""
        self.loc_list.clear()
        for location in sorted(self.locations):
            self.loc_list.addItem(location)
            
    def on_loc_selected(self, item):
        """Handle location selection"""
        location_name = item.text()
        self.suggestion_selected.emit(location_name)
        
    def process_text_input(self, text, cursor_position):
        """Process text input and generate suggestions"""
        if not self.auto_complete_enabled.isChecked():
            return
            
        # Get the current word being typed
        self.current_word = self.get_current_word(text, cursor_position)
        self.cursor_position = cursor_position
        
        if len(self.current_word) >= 2:  # Start suggesting after 2 characters
            self.suggestion_timer.start(300)  # 300ms delay
        else:
            self.hide_suggestions_popup()
            
    def get_current_word(self, text, cursor_position):
        """Extract the current word being typed"""
        if cursor_position > len(text):
            return ""
            
        # Find the start of the current word
        start = cursor_position
        while start > 0 and text[start - 1].isalnum():
            start -= 1
            
        # Find the end of the current word
        end = cursor_position
        while end < len(text) and text[end].isalnum():
            end += 1
            
        return text[start:end]
        
    def generate_suggestions(self, partial_word):
        """Generate suggestions based on partial word"""
        suggestions = []
        partial_upper = partial_word.upper()
        
        # Add character suggestions
        for character in self.characters:
            if character.upper().startswith(partial_upper):
                suggestions.append(character)
                
        # Add location suggestions
        for location in self.locations:
            if location.upper().startswith(partial_upper):
                suggestions.append(location)
                
        # Add common screenplay terms
        common_terms = [
            "INT.", "EXT.", "INT/EXT.", "I/E.",
            "FADE", "CUT", "DISSOLVE", "SMASH", "MATCH", "JUMP",
            "CONT'D", "CONTINUED", "V.O.", "O.S.", "O.C.", "O.F.F."
        ]
        
        for term in common_terms:
            if term.upper().startswith(partial_upper):
                suggestions.append(term)
                
        return suggestions[:10]  # Limit to 10 suggestions
        
    def show_suggestions_popup(self):
        """Show the suggestions popup"""
        if not self.show_suggestions.isChecked():
            return
            
        suggestions = self.generate_suggestions(self.current_word)
        
        if suggestions:
            self.suggestion_popup.clear()
            for suggestion in suggestions:
                self.suggestion_popup.addItem(suggestion)
            
            # Position the popup near the cursor
            self.position_popup_near_cursor()
            
            self.suggestion_popup.setVisible(True)
            self.suggestion_popup.raise_()
            self.suggestions = suggestions
        else:
            self.hide_suggestions_popup()
            
    def position_popup_near_cursor(self):
        """Position the suggestion popup near the cursor"""
        # Get the main application window
        app = QApplication.instance()
        if not app:
            return
            
        # Get the active window (should be the main window)
        main_window = app.activeWindow()
        if not main_window:
            return
            
        # Get the text editor widget
        text_editor = None
        for child in main_window.findChildren(QTextEdit):
            if child.hasFocus():
                text_editor = child
                break
                
        if not text_editor:
            return
            
        # Get cursor position in screen coordinates
        cursor = text_editor.textCursor()
        rect = text_editor.cursorRect(cursor)
        global_pos = text_editor.mapToGlobal(rect.bottomLeft())
        
        # Position popup below the cursor
        popup_x = global_pos.x()
        popup_y = global_pos.y() + 5  # 5 pixels below cursor
        
        # Ensure popup doesn't go off screen
        screen_geometry = app.primaryScreen().geometry()
        popup_width = min(300, self.suggestion_popup.sizeHint().width())
        popup_height = min(150, self.suggestion_popup.sizeHint().height())
        
        if popup_x + popup_width > screen_geometry.right():
            popup_x = screen_geometry.right() - popup_width - 10
            
        if popup_y + popup_height > screen_geometry.bottom():
            popup_y = global_pos.y() - popup_height - 5  # Show above cursor
            
        self.suggestion_popup.move(popup_x, popup_y)
        self.suggestion_popup.resize(popup_width, popup_height)
        
    def hide_suggestions_popup(self):
        """Hide the suggestions popup"""
        self.suggestion_popup.setVisible(False)
        
    def on_suggestion_selected(self, item):
        """Handle suggestion selection"""
        suggestion = item.text()
        self.suggestion_selected.emit(suggestion)
        self.hide_suggestions_popup()
        
    def get_suggestions(self):
        """Get current suggestions"""
        return self.suggestions
        
    def update_from_character_manager(self, characters):
        """Update character list from character manager"""
        # Only use full, valid character names
        self.characters = set([c for c in characters if len(c) > 1])
        # No need to update a character list UI anymore
        
    def update_from_scene_manager(self, scenes):
        """Update location list from scene manager"""
        # Only use full, valid locations
        locations = set()
        for scene in scenes:
            # Extract location from scene heading (after INT./EXT./etc.)
            match = re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)\s*([^\-]+)', scene, re.IGNORECASE)
            if match:
                location = match.group(2).strip()
                if location and len(location) > 1:
                    locations.add(location)
        self.locations = locations
        self.update_location_list()
        
    def get_characters(self):
        """Get list of all characters"""
        return sorted(self.characters)
        
    def get_locations(self):
        """Get list of all locations"""
        return sorted(self.locations) 