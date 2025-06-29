# ScriptDraft - Professional Screenplay Editor

A cross-platform desktop application for writing screenplays with industry-standard formatting, built with Python and PyQt6.

## Features

### Core Writing Features
- **Industry-Standard Formatting**: Automatic formatting for all screenplay elements
- **SmartType**: Auto-complete for character names, locations, and screenplay terms
- **Element Type Detection**: Automatic detection and formatting of screenplay elements
- **Keyboard Shortcuts**: Tab and Enter keys for quick element switching
- **Custom File Format**: SDft (.sdft) format preserves all formatting information
- **Title Page Management**: Separate title page view with industry-standard formatting

### Screenplay Elements
- **Scene Headings**: INT./EXT. locations with automatic formatting
- **Action Lines**: Descriptive text with proper margins
- **Character Names**: Bold, uppercase formatting
- **Dialogue**: Properly indented speech
- **Parentheticals**: Italicized character directions
- **Transitions**: Right-aligned scene transitions
- **Shot Descriptions**: Camera direction formatting

### Management Tools
- **Character Manager**: Track and manage character names
- **Scene Manager**: Organize and navigate scene headings
- **SmartType Manager**: Auto-complete suggestions and settings
- **Auto-Detection**: Automatically identify elements from text

### Export Options
- **SDft Export**: Native format with full formatting preservation
- **PDF Export**: Industry-standard PDF formatting
- **FDX Export**: Final Draft XML format compatibility
- **Text Export**: Plain text with formatting

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd scriptdraft
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### Getting Started
1. Launch the application
2. Start typing your screenplay (begins with Scene Heading format)
3. Use Tab and Enter keys for automatic element switching
4. Use the left panel to manage characters and scenes
5. Use the right panel for SmartType settings and suggestions
6. Click the "Title Page" button in the toolbar to switch to title page view

### Automatic Formatting
The app automatically detects and formats screenplay elements as you type:

- **Scene Headings**: Automatically detected when starting with INT., EXT., INT/EXT., or I/E.
- **Character Names**: Automatically detected as all-caps names (up to 4 words)
- **Dialogue**: Automatically formatted after character names
- **Action Lines**: Default formatting for descriptive text
- **Transitions**: Automatically detected and right-aligned
- **Parentheticals**: Automatically detected when enclosed in parentheses

### Title Page Management
1. Click the "Title Page" button in the toolbar to switch to title page view
2. Enter the screenplay title, author name, and contact information
3. The title page is automatically formatted with industry-standard layout
4. Title page information is saved with the screenplay in SDft format
5. Click the "Title Page" button again to return to the screenplay editor

### Keyboard Shortcuts
- **Enter**: Create new line with automatic element detection
  - After Scene Heading → Action
  - After Character → Dialogue  
  - After Parenthetical → Dialogue
  - After Transition → Scene Heading
  - After Shot → Action
  - Default → Action
- **Tab**: Create character name line (indented at 4 inches)
  - Press Tab on empty line or Action line → Character formatting
  - Press Tab on Character line → Dialogue formatting
  - Press Tab on Dialogue line → Parenthetical formatting
  - Press Tab on Parenthetical line → Dialogue formatting
- **Ctrl+Space**: Trigger SmartType suggestions
- **Ctrl+S**: Save document
- **Ctrl+O**: Open document
- **Ctrl+Shift+F**: Auto-format document

### SmartType Features
- **Auto-complete**: Suggests character names, locations, and common terms
- **Character Suggestions**: Based on characters in your screenplay
- **Location Suggestions**: Extracted from scene headings
- **Common Terms**: INT., EXT., FADE, CUT, etc.
- **Configurable**: Enable/disable features in SmartType panel

### Element Types

#### Scene Heading
- Format: `INT. LOCATION - TIME`
- Example: `INT. COFFEE SHOP - DAY`
- Automatically formatted in bold, uppercase

#### Action
- Descriptive text describing what happens
- Normal formatting with proper margins
- Example: `John sits at the table, sipping his coffee.`

#### Character
- Character names in bold, uppercase
- Example: `JOHN`
- Automatically detected from all-caps text

#### Dialogue
- Character speech with proper indentation
- Example: `I can't believe this is happening.`

#### Parenthetical
- Character directions in italics
- Example: `(nervously)`

#### Transition
- Scene transitions, right-aligned
- Example: `FADE OUT`

### Managing Characters
1. Type character names in the editor (they'll be auto-detected)
2. Or manually add them in the Character Manager panel
3. Double-click characters to insert them at cursor position
4. Characters are automatically added to SmartType suggestions

### Managing Scenes
1. Scene headings are automatically detected from text
2. Or manually add them in the Scene Manager panel
3. Double-click scenes to insert them at cursor position
4. Locations are automatically extracted for SmartType

### Exporting
1. **SDft Export**: File → Save (default format)
   - Native ScriptDraft format
   - Preserves all formatting and element types
   - XML-based for compatibility

2. **PDF Export**: File → Export to PDF
   - Industry-standard formatting
   - Proper margins and spacing
   - Courier font

3. **FDX Export**: File → Export to FDX
   - Final Draft XML format
   - Compatible with Final Draft software
   - Preserves element types and formatting

## File Formats

### Supported Input
- ScriptDraft files (.sdft) - Native format with full formatting
- Plain text files (.txt)
- Final Draft XML files (.fdx)

### Supported Output
- ScriptDraft files (.sdft) - Native format with full formatting
- Plain text files (.txt)
- PDF files (.pdf)
- Final Draft XML files (.fdx)

### SDft Format
The SDft (ScriptDraft Format) is a custom XML format that preserves all formatting information:

```xml
<sdft:screenplay xmlns:sdft="http://scriptdraft.app/sdft" version="1.0">
  <sdft:metadata>
    <sdft:title>Screenplay Title</sdft:title>
    <sdft:author>Author Name</sdft:author>
    <sdft:contact_info>Contact Information</sdft:contact_info>
  </sdft:metadata>
  <sdft:content>
    <sdft:element type="Scene Heading">
      INT. LOCATION - TIME
      <sdft:formatting>
        <sdft:alignment>left</sdft:alignment>
        <sdft:character_format>
          <sdft:font_weight>700</sdft:font_weight>
          <sdft:font_capitalization>1</sdft:font_capitalization>
        </sdft:character_format>
      </sdft:formatting>
    </sdft:element>
  </sdft:content>
</sdft:screenplay>
```

## Technical Details

### Architecture
- **Main Application**: `main.py` - Main window and application logic
- **Screenplay Editor**: `screenplay_editor.py` - Core text editing with formatting
- **SmartType Manager**: `smarttype_manager.py` - Auto-complete functionality
- **SDft Manager**: `sdft_manager.py` - Custom file format handling
- **Title Page Manager**: `title_page_manager.py` - Title page creation and management
- **Export Manager**: `export_manager.py` - PDF and FDX export functionality
- **Character Manager**: `character_manager.py` - Character tracking
- **Scene Manager**: `scene_manager.py` - Scene heading management

### Dependencies
- **PyQt6**: Cross-platform GUI framework
- **reportlab**: PDF generation
- **lxml**: XML processing for FDX export
- **xml.etree.ElementTree**: SDft XML processing

### Platform Support
- Windows
- macOS
- Linux

## Development

### Project Structure
```
scriptdraft/
├── main.py                 # Main application entry point
├── screenplay_editor.py    # Core editor component
├── smarttype_manager.py    # SmartType auto-complete
├── sdft_manager.py         # Custom file format handling
├── title_page_manager.py   # Title page management
├── export_manager.py       # Export functionality
├── character_manager.py    # Character management
├── scene_manager.py        # Scene management
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── sample_screenplay.sdft # Sample SDft file
└── FDSample.fdx           # Sample Final Draft file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues, questions, or feature requests, please open an issue on the project repository.

## Roadmap

### Planned Features
- Title page generation
- Page numbering
- Revision tracking
- Collaboration features
- Cloud sync
- Mobile companion app
- Advanced formatting options
- Template library
- Statistics and analysis tools 