import pytest
from unittest.mock import MagicMock
from utils.doc_parser import extract_text_from_file
import io

class MockUploadedFile:
    """A simple mock for Streamlit's UploadedFile object."""
    def __init__(self, name, content_bytes):
        self.name = name
        self._content = content_bytes

    def getvalue(self):
        return self._content

def test_extract_text_from_txt():
    # Arrange
    mock_content = b"This is a sample legal contract."
    mock_file = MockUploadedFile(name="sample.txt", content_bytes=mock_content)
    
    # Act
    extracted_text = extract_text_from_file(mock_file)
    
    # Assert
    assert extracted_text == "This is a sample legal contract."

def test_extract_text_unsupported_format():
    # Arrange
    mock_file = MockUploadedFile(name="sample.jpg", content_bytes=b"fake image data")
    
    # Act
    result = extract_text_from_file(mock_file)
    
    # Assert
    assert "Unsupported file format" in result

def test_extract_text_none():
    # Act
    result = extract_text_from_file(None)
    
    # Assert
    assert result == ""
