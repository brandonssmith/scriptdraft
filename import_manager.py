"""
Import Manager
Handles import from FDX (Final Draft XML) format
"""

import re
from lxml import etree

class ImportManager:
    """Manages import functionality for different formats"""
    
    def __init__(self):
        pass
        
    def import_from_fdx(self, file_path):
        """Import screenplay content from FDX (Final Draft XML)"""
        try:
            # Parse the FDX file
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            # Extract content
            content_elem = root.find("Content")
            if content_elem is None:
                raise ValueError("No Content element found in FDX file")
                
            # Convert paragraphs to screenplay text
            screenplay_lines = []
            
            for paragraph in content_elem.findall("Paragraph"):
                paragraph_type = paragraph.get("Type", "")
                text_elem = paragraph.find("Text")
                
                if text_elem is not None and text_elem.text:
                    text = text_elem.text.strip()
                    if text:
                        # Format text based on paragraph type
                        formatted_text = self.format_fdx_text(text, paragraph_type)
                        screenplay_lines.append(formatted_text)
                        
            return "\n".join(screenplay_lines)
            
        except Exception as e:
            raise Exception(f"Error importing FDX file: {str(e)}")
            
    def format_fdx_text(self, text, paragraph_type):
        """Format text based on FDX paragraph type"""
        # Map FDX types to our formatting
        if paragraph_type == "Scene Heading":
            # Scene headings should be all caps
            return text.upper()
            
        elif paragraph_type == "Character":
            # Character names should be all caps
            return text.upper()
            
        elif paragraph_type == "Transition":
            # Transitions should be all caps
            return text.upper()
            
        elif paragraph_type == "Action":
            # Action lines - keep as is, but capitalize first letter of sentences
            return self.capitalize_sentences(text)
            
        elif paragraph_type == "Dialogue":
            # Dialogue - keep as is
            return text
            
        elif paragraph_type == "Parenthetical":
            # Parentheticals - keep as is
            return text
            
        elif paragraph_type == "Shot":
            # Shot descriptions should be all caps
            return text.upper()
            
        elif paragraph_type == "Title Page":
            # Skip title page content for now
            return ""
            
        else:
            # Default to action formatting
            return self.capitalize_sentences(text)
            
    def capitalize_sentences(self, text):
        """Capitalize the first letter of sentences in action text"""
        # Split into sentences and capitalize first letter
        sentences = re.split(r'([.!?]+)', text)
        capitalized_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i % 2 == 0:  # Even indices are sentence content
                if sentence.strip():
                    # Capitalize first letter
                    sentence = sentence.strip()
                    if sentence:
                        sentence = sentence[0].upper() + sentence[1:]
                capitalized_sentences.append(sentence)
            else:  # Odd indices are punctuation
                capitalized_sentences.append(sentence)
                
        return ''.join(capitalized_sentences)
        
    def detect_element_type_from_fdx(self, paragraph_type):
        """Map FDX paragraph type to our element type"""
        type_mapping = {
            "Scene Heading": "Scene Heading",
            "Action": "Action",
            "Character": "Character",
            "Dialogue": "Dialogue",
            "Parenthetical": "Parenthetical",
            "Transition": "Transition",
            "Shot": "Shot",
            "General": "Action"  # General often maps to Action
        }
        
        return type_mapping.get(paragraph_type, "Action") 