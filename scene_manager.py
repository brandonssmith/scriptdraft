"""
Scene Manager Component
Manages scene headings and provides scene navigation
"""

import re
from PyQt6.QtWidgets import QListWidget, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

class SceneManager(QWidget):
    """Manages scene headings and provides scene navigation"""
    
    scene_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.scenes = []
        self.locations = set()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Scenes")
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Add scene section
        add_layout = QHBoxLayout()
        self.scene_input = QLineEdit()
        self.scene_input.setPlaceholderText("Enter scene heading")
        self.scene_input.returnPressed.connect(self.add_scene)
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_scene)
        
        add_layout.addWidget(self.scene_input)
        add_layout.addWidget(add_button)
        layout.addLayout(add_layout)
        
        # Scene list
        self.scene_list = QListWidget()
        self.scene_list.itemDoubleClicked.connect(self.on_scene_selected)
        layout.addWidget(self.scene_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_scene)
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_scenes)
        
        button_layout.addWidget(remove_button)
        button_layout.addWidget(clear_button)
        layout.addLayout(button_layout)
        
    def add_scene(self):
        """Add a scene to the list"""
        scene = self.scene_input.text().strip()
        if scene:
            # Ensure proper scene heading format
            if not scene.upper().startswith(('INT.', 'EXT.', 'INT/EXT.', 'I/E.')):
                scene = f"INT. {scene}"
            
            # Convert to uppercase for consistency
            scene = scene.upper()
            
            if scene not in self.scenes:
                self.scenes.append(scene)
                self.update_scene_list()
            
            self.scene_input.clear()
            
    def remove_scene(self):
        """Remove selected scene"""
        current_item = self.scene_list.currentItem()
        if current_item:
            scene_name = current_item.text()
            if scene_name in self.scenes:
                self.scenes.remove(scene_name)
                self.update_scene_list()
            
    def clear_scenes(self):
        """Clear all scenes"""
        self.scenes.clear()
        self.update_scene_list()
        
    def update_scene_list(self):
        """Update the scene list display"""
        self.scene_list.clear()
        for scene in self.scenes:
            self.scene_list.addItem(scene)
            
    def on_scene_selected(self, item):
        """Handle scene selection"""
        scene_name = item.text()
        self.scene_selected.emit(scene_name)
        
    def update_from_text(self, text):
        """Update scene list from screenplay text"""
        # Only add locations from lines that are valid scene headings (not partials)
        lines = text.split('\n')
        found_scenes = []
        found_locations = set()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Only consider lines that are valid scene headings
            if self.is_scene_heading(line):
                scene_name = self.extract_scene_heading(line)
                if scene_name and scene_name not in found_scenes:
                    found_scenes.append(scene_name)
                # Extract location part (after INT./EXT./etc.)
                match = re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)\s*([^\-]+)', line, re.IGNORECASE)
                if match:
                    location = match.group(2).strip()
                    # Only add if it's a valid location (not partial)
                    if location and len(location) > 1:
                        found_locations.add(location)
        # Update the scene list
        self.scenes = found_scenes
        self.locations = found_locations
        self.update_scene_list()
        # Optionally: update a locations list widget if you have one
        
    def is_scene_heading(self, line):
        """Check if a line looks like a scene heading"""
        # Scene headings typically start with:
        # - INT. (Interior)
        # - EXT. (Exterior)
        # - INT/EXT. or I/E. (Interior/Exterior)
        
        return re.match(r'^(INT\.|EXT\.|INT\/EXT\.|I\/E\.)', line, re.IGNORECASE) is not None
        
    def extract_scene_heading(self, line):
        """Extract scene heading from a line"""
        # Clean up the scene heading
        scene = line.strip()
        
        # Remove any trailing periods or extra spaces
        scene = re.sub(r'\s+', ' ', scene)
        
        return scene.upper()
        
    def get_scenes(self):
        """Get list of all scenes"""
        return self.scenes.copy()
        
    def has_scene(self, scene_name):
        """Check if scene exists"""
        return scene_name.upper() in [s.upper() for s in self.scenes]
        
    def get_scene_count(self):
        """Get the number of scenes"""
        return len(self.scenes)
        
    def get_scene_by_index(self, index):
        """Get scene by index"""
        if 0 <= index < len(self.scenes):
            return self.scenes[index]
        return None 