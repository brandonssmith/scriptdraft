#!/usr/bin/env python3
"""
ScriptDraft - Desktop Screenplay Editor
A professional screenplay writing application built with PyQt6
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, QToolBar, QFileDialog, QMessageBox, QLabel, QComboBox, QSplitter, QListWidget, QTabWidget, QStackedWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QKeySequence, QTextCharFormat, QColor, QPalette, QAction
from screenplay_editor import ScreenplayEditor
from export_manager import ExportManager
from import_manager import ImportManager
from character_manager import CharacterManager
from scene_manager import SceneManager
from smarttype_manager import SmartTypeManager
from sdft_manager import SDftManager
from title_page_manager import TitlePageManager

class ScriptDraftApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScriptDraft - Professional Screenplay Editor")
        self.setGeometry(100, 100, 1600, 900)
        
        # Initialize components
        self.smarttype_manager = SmartTypeManager()
        self.screenplay_editor = ScreenplayEditor(self.smarttype_manager)
        self.export_manager = ExportManager()
        self.import_manager = ImportManager()
        self.character_manager = CharacterManager()
        self.scene_manager = SceneManager()
        self.sdft_manager = SDftManager()
        self.title_page_manager = TitlePageManager()
        
        # Current file path
        self.current_file_path = None
        
        # View state
        self.showing_title_page = False
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_connections()
        
        # Set dark theme
        self.set_dark_theme()
        
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Scene and Character management
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Scene manager
        scene_label = QLabel("Scenes")
        scene_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        left_layout.addWidget(scene_label)
        left_layout.addWidget(self.scene_manager)
        
        # Character manager
        character_label = QLabel("Characters")
        character_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        left_layout.addWidget(character_label)
        left_layout.addWidget(self.character_manager)
        
        splitter.addWidget(left_panel)
        
        # Center panel - Main editor or title page
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        # Element type selector (only visible for screenplay editor)
        self.element_layout = QHBoxLayout()
        element_label = QLabel("Element Type:")
        self.element_combo = QComboBox()
        self.element_combo.addItems([
            "Scene Heading", "Action", "Character", "Dialogue", 
            "Parenthetical", "Transition", "Shot"
        ])
        self.element_combo.currentTextChanged.connect(self.on_element_type_changed)
        self.element_layout.addWidget(element_label)
        self.element_layout.addWidget(self.element_combo)
        self.element_layout.addStretch()
        
        # Store references to widgets for visibility control
        self.element_label = element_label
        self.element_combo = self.element_combo
        
        center_layout.addLayout(self.element_layout)
        
        # Stacked widget for title page and screenplay editor
        self.stacked_widget = QStackedWidget()
        
        # Title page view
        self.stacked_widget.addWidget(self.title_page_manager)
        
        # Screenplay editor view
        self.stacked_widget.addWidget(self.screenplay_editor)
        
        center_layout.addWidget(self.stacked_widget)
        
        splitter.addWidget(center_panel)
        
        # Right panel - SmartType manager
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(self.smarttype_manager)
        right_layout.addStretch()
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 1000, 300])
        
        # Start with screenplay editor view
        self.show_screenplay_editor()
        
    def setup_menu(self):
        """Setup the application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_document)
        file_menu.addAction(open_action)
        
        import_fdx_action = QAction("Import &FDX...", self)
        import_fdx_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        import_fdx_action.triggered.connect(self.import_fdx)
        file_menu.addAction(import_fdx_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_document)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_document_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_pdf_action = QAction("Export to &PDF...", self)
        export_pdf_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_pdf_action)
        
        export_fdx_action = QAction("Export to &FDX...", self)
        export_fdx_action.triggered.connect(self.export_fdx)
        file_menu.addAction(export_fdx_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.screenplay_editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.screenplay_editor.redo)
        edit_menu.addAction(redo_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        format_action = QAction("&Auto-Format", self)
        format_action.setShortcut(QKeySequence("Ctrl+Shift+F"))
        format_action.triggered.connect(self.auto_format)
        tools_menu.addAction(format_action)
        
        tools_menu.addSeparator()
        
        smarttype_action = QAction("&SmartType Suggestions", self)
        smarttype_action.setShortcut(QKeySequence("Ctrl+Space"))
        smarttype_action.triggered.connect(self.trigger_smarttype)
        tools_menu.addAction(smarttype_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add toolbar actions
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_document)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_document)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_document)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.screenplay_editor.undo)
        toolbar.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.screenplay_editor.redo)
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
        # Title page toggle button
        self.title_page_action = QAction("Title Page", self)
        self.title_page_action.setCheckable(True)
        self.title_page_action.triggered.connect(self.toggle_title_page)
        toolbar.addAction(self.title_page_action)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.screenplay_editor.textChanged.connect(self.on_text_changed)
        self.screenplay_editor.element_type_changed.connect(self.on_editor_element_type_changed)
        self.character_manager.character_selected.connect(self.insert_character)
        self.scene_manager.scene_selected.connect(self.insert_scene)
        
        # SmartType connections
        self.smarttype_manager.suggestion_selected.connect(self.insert_suggestion)
        
        # Update SmartType manager when character/scene lists change
        self.character_manager.character_selected.connect(self.update_smarttype_characters)
        self.scene_manager.scene_selected.connect(self.update_smarttype_scenes)
        
    def set_dark_theme(self):
        """Apply dark theme to the application"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(70, 70, 70))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Additional colors for better contrast
        palette.setColor(QPalette.ColorRole.Light, QColor(100, 100, 100))
        palette.setColor(QPalette.ColorRole.Midlight, QColor(80, 80, 80))
        palette.setColor(QPalette.ColorRole.Dark, QColor(40, 40, 40))
        palette.setColor(QPalette.ColorRole.Mid, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.Shadow, QColor(20, 20, 20))
        
        self.setPalette(palette)
        
        # Apply stylesheet for better button styling
        self.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #6a6a6a;
                border-radius: 4px;
                padding: 6px 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border: 1px solid #7a7a7a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
                border: 1px solid #5a5a5a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                border: 1px solid #4a4a4a;
                color: #6a6a6a;
            }
            QComboBox {
                background-color: #4a4a4a;
                border: 1px solid #6a6a6a;
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
                min-width: 6em;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #4a4a4a;
                border: 1px solid #6a6a6a;
                color: white;
                selection-background-color: #5a5a5a;
            }
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #6a6a6a;
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #7a7a7a;
            }
            QListWidget {
                background-color: #3a3a3a;
                border: 1px solid #6a6a6a;
                border-radius: 4px;
                color: white;
                alternate-background-color: #4a4a4a;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #5a5a5a;
            }
            QListWidget::item:selected {
                background-color: #5a5a5a;
            }
            QListWidget::item:hover {
                background-color: #4a4a4a;
            }
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #6a6a6a;
                border-radius: 4px;
                color: white;
                selection-background-color: #5a5a5a;
            }
            QLabel {
                color: white;
            }
            QToolBar {
                background-color: #4a4a4a;
                border: none;
                spacing: 3px;
                padding: 3px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
                color: white;
            }
            QToolBar QToolButton:hover {
                background-color: #5a5a5a;
                border: 1px solid #7a7a7a;
            }
            QToolBar QToolButton:pressed {
                background-color: #3a3a3a;
                border: 1px solid #5a5a5a;
            }
            QMenuBar {
                background-color: #4a4a4a;
                color: white;
                border-bottom: 1px solid #6a6a6a;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 10px;
            }
            QMenuBar::item:selected {
                background-color: #5a5a5a;
            }
            QMenu {
                background-color: #4a4a4a;
                border: 1px solid #6a6a6a;
                color: white;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #5a5a5a;
            }
        """)
        
    def on_element_type_changed(self, element_type):
        """Handle element type selection change"""
        self.screenplay_editor.set_current_element_type(element_type)
        
    def on_text_changed(self):
        """Handle text changes in the editor"""
        # Update character and scene lists based on content
        text = self.screenplay_editor.toPlainText()
        self.character_manager.update_from_text(text)
        
        # Clean up any invalid character names that might have been added
        self.character_manager.cleanup_characters()
        
        self.scene_manager.update_from_text(text)
        
        # Update SmartType manager with new characters and locations
        characters = self.character_manager.get_characters()
        scenes = self.scene_manager.get_scenes()
        self.smarttype_manager.update_from_character_manager(characters)
        self.smarttype_manager.update_from_scene_manager(scenes)
        
    def insert_character(self, character_name):
        """Insert a character name at cursor position"""
        self.screenplay_editor.insert_character(character_name)
        
    def insert_scene(self, scene_name):
        """Insert a scene heading at cursor position"""
        self.screenplay_editor.insert_scene(scene_name)
        
    def new_document(self):
        """Create a new document"""
        if self.screenplay_editor.document().isModified():
            reply = QMessageBox.question(
                self, "Save Changes", 
                "Do you want to save your changes?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_document()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
                
        self.screenplay_editor.clear()
        
        # Set initial element type to Scene Heading for new documents
        self.screenplay_editor.set_current_element_type("Scene Heading")
        self.element_combo.setCurrentText("Scene Heading")
        
        self.setWindowTitle("ScriptDraft - Professional Screenplay Editor")
        
    def open_document(self):
        """Open a document"""
        file_path, file_type = QFileDialog.getOpenFileName(
            self, "Open Screenplay", "", 
            "ScriptDraft Files (*.sdft);;Text Files (*.txt);;Final Draft Files (*.fdx);;All Files (*)"
        )
        
        if file_path:
            try:
                if file_path.lower().endswith('.fdx'):
                    # Import FDX file
                    content = self.import_manager.import_from_fdx(file_path)
                    self.screenplay_editor.set_formatted_text(content)
                    self.setWindowTitle(f"ScriptDraft - {os.path.basename(file_path)} (FDX Import)")
                elif file_path.lower().endswith('.sdft'):
                    # Load SDft file
                    if self.sdft_manager.load_document(self.screenplay_editor, self.title_page_manager, file_path):
                        self.current_file_path = file_path
                        self.setWindowTitle(f"ScriptDraft - {os.path.basename(file_path)}")
                        self.screenplay_editor.document().setModified(False)
                else:
                    # Open text file
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.screenplay_editor.set_formatted_text(content)
                        self.setWindowTitle(f"ScriptDraft - {os.path.basename(file_path)}")
                        
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
                
    def save_document(self):
        """Save the current document"""
        if not self.current_file_path:
            self.save_document_as()
        else:
            try:
                if self.current_file_path.lower().endswith('.sdft'):
                    # Save as SDft format
                    if self.sdft_manager.save_document(self.screenplay_editor, self.title_page_manager, self.current_file_path):
                        self.screenplay_editor.document().setModified(False)
                else:
                    # Save as text file
                    content = self.screenplay_editor.toPlainText()
                    with open(self.current_file_path, 'w', encoding='utf-8') as file:
                        file.write(content)
                    self.screenplay_editor.document().setModified(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
                
    def save_document_as(self):
        """Save the document with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Screenplay", "", 
            "ScriptDraft Files (*.sdft);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                if file_path.lower().endswith('.sdft'):
                    # Save as SDft format
                    if self.sdft_manager.save_document(self.screenplay_editor, self.title_page_manager, file_path):
                        self.current_file_path = file_path
                        self.setWindowTitle(f"ScriptDraft - {os.path.basename(file_path)}")
                        self.screenplay_editor.document().setModified(False)
                else:
                    # Save as text file
                    content = self.screenplay_editor.toPlainText()
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(content)
                    self.current_file_path = file_path
                    self.setWindowTitle(f"ScriptDraft - {os.path.basename(file_path)}")
                    self.screenplay_editor.document().setModified(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
                
    def export_pdf(self):
        """Export to PDF"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to PDF", "", 
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                # Get title page information
                title, author, contact_info = self.get_title_page_info()
                
                content = self.screenplay_editor.toPlainText()
                self.export_manager.export_to_pdf(content, file_path, title, author, contact_info)
                QMessageBox.information(self, "Success", "PDF exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export PDF: {str(e)}")
                
    def export_fdx(self):
        """Export to FDX (Final Draft XML)"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to FDX", "", 
            "Final Draft Files (*.fdx)"
        )
        
        if file_path:
            try:
                # Get title page information
                title, author, contact_info = self.get_title_page_info()
                
                content = self.screenplay_editor.toPlainText()
                self.export_manager.export_to_fdx(content, file_path, title, author, contact_info)
                QMessageBox.information(self, "Success", "FDX exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export FDX: {str(e)}")
                
    def get_title_page_info(self):
        """Get title page information from title page manager"""
        title_page_info = self.title_page_manager.get_title_page_info()
        return (
            title_page_info.get('title', ''),
            title_page_info.get('author', ''),
            title_page_info.get('contact_info', '')
        )
        
    def auto_format(self):
        """Auto-format the entire document"""
        self.screenplay_editor.auto_format()
        
    def trigger_smarttype(self):
        """Trigger SmartType suggestions"""
        self.screenplay_editor.handle_smarttype_trigger()
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About ScriptDraft",
            "ScriptDraft - Professional Screenplay Editor\n\n"
            "A cross-platform desktop application for writing screenplays\n"
            "with industry-standard formatting and export capabilities.\n\n"
            "Built with Python and PyQt6"
        )
        
    def closeEvent(self, event):
        """Handle application close event"""
        if self.screenplay_editor.document().isModified():
            reply = QMessageBox.question(
                self, "Save Changes", 
                "Do you want to save your changes?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_document()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def import_fdx(self):
        """Import FDX file specifically"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import FDX File", "", 
            "Final Draft Files (*.fdx)"
        )
        
        if file_path:
            try:
                content = self.import_manager.import_from_fdx(file_path)
                self.screenplay_editor.set_formatted_text(content)
                self.setWindowTitle(f"ScriptDraft - {os.path.basename(file_path)} (FDX Import)")
                QMessageBox.information(self, "Success", "FDX file imported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not import FDX file: {str(e)}")

    def insert_suggestion(self, suggestion):
        """Insert a SmartType suggestion at cursor position"""
        self.screenplay_editor.insert_suggestion(suggestion)
        
    def update_smarttype_characters(self, character_name):
        """Update SmartType manager with new character"""
        characters = self.character_manager.get_characters()
        self.smarttype_manager.update_from_character_manager(characters)
        
    def update_smarttype_scenes(self, scene_name):
        """Update SmartType manager with new scene"""
        scenes = self.scene_manager.get_scenes()
        self.smarttype_manager.update_from_scene_manager(scenes)

    def toggle_title_page(self):
        """Toggle between screenplay editor and title page"""
        if self.title_page_action.isChecked():
            self.show_title_page()
        else:
            self.show_screenplay_editor()
            
    def show_title_page(self):
        """Show the title page"""
        self.stacked_widget.setCurrentIndex(0)
        self.element_label.setVisible(False)
        self.element_combo.setVisible(False)
        self.showing_title_page = True
        
    def show_screenplay_editor(self):
        """Show the screenplay editor"""
        self.stacked_widget.setCurrentIndex(1)
        self.element_label.setVisible(True)
        self.element_combo.setVisible(True)
        self.showing_title_page = False

    def on_editor_element_type_changed(self, element_type):
        """Handle element type change from the editor"""
        # Update the combo box to reflect the new element type
        index = self.element_combo.findText(element_type)
        if index >= 0:
            self.element_combo.setCurrentIndex(index)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ScriptDraft")
    app.setApplicationVersion("1.0.0")
    
    window = ScriptDraftApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 