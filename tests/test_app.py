import pytest
from unittest.mock import MagicMock, patch
import io
from utils.doc_parser import extract_text_from_file
from utils.ai_helpers import (
    is_transient_error,
    get_document_summary,
    analyze_document_risks,
    ask_question_about_document,
    compare_contracts
)

class MockUploadedFile:
    """Mock for Streamlit's UploadedFile object."""
    def __init__(self, name: str, content_bytes: bytes):
        self.name = name
        self._content = content_bytes
        self.size = len(content_bytes)

    def getvalue(self) -> bytes:
        return self._content

# --- Document Parser Tests ---

def test_extract_text_from_txt_utf8():
    mock_content = "Tenant shall pay rent of $1,500 monthly.".encode("utf-8")
    mock_file = MockUploadedFile(name="lease.txt", content_bytes=mock_content)
    extracted = extract_text_from_file(mock_file)
    assert "Tenant shall pay rent of $1,500 monthly." in extracted

def test_extract_text_from_txt_latin1():
    # Test encoding resilience
    mock_content = "Lease agreement with currency: £500".encode("latin-1")
    mock_file = MockUploadedFile(name="agreement.txt", content_bytes=mock_content)
    extracted = extract_text_from_file(mock_file)
    assert "500" in extracted

def test_extract_text_unsupported_format():
    mock_file = MockUploadedFile(name="document.docx", content_bytes=b"dummy docx")
    result = extract_text_from_file(mock_file)
    assert "Unsupported file format" in result

def test_extract_text_none_input():
    result = extract_text_from_file(None)
    assert result == ""

def test_extract_text_empty_file():
    mock_file = MockUploadedFile(name="", content_bytes=b"")
    result = extract_text_from_file(mock_file)
    assert result == ""

# --- AI Helper Logic & Error Classification Tests ---

def test_is_transient_error():
    assert is_transient_error(Exception("503 UNAVAILABLE: Model is currently experiencing high demand"))
    assert is_transient_error(Exception("429 Resource has been exhausted"))
    assert is_transient_error(Exception("Server connection timeout"))
    assert not is_transient_error(Exception("400 Invalid argument passed"))
    assert not is_transient_error(Exception("Authentication failed"))

@patch("utils.ai_helpers._generate_with_retry")
@patch.dict("os.environ", {"GEMINI_API_KEY": "fake_test_key"})
def test_get_document_summary_success(mock_generate):
    mock_generate.return_value = "### Summary\nThis is a standard NDA agreement."
    result = get_document_summary("Agreement between Party A and Party B", language="English")
    assert "This is a standard NDA agreement." in result
    mock_generate.assert_called_once()

@patch("utils.ai_helpers._generate_with_retry")
@patch.dict("os.environ", {"GEMINI_API_KEY": "fake_test_key"})
def test_analyze_document_risks_success(mock_generate):
    mock_generate.return_value = "| Auto-Renewal Clause | Unfair renewal terms | High |"
    result = analyze_document_risks("Auto renews after 1 year unless notice in 2 hours.", language="English")
    assert "Auto-Renewal" in result
    mock_generate.assert_called_once()

@patch("utils.ai_helpers._generate_with_retry")
@patch.dict("os.environ", {"GEMINI_API_KEY": "fake_test_key"})
def test_compare_contracts_success(mock_generate):
    mock_generate.return_value = "Document B added an arbitration clause."
    result = compare_contracts("Doc A text", "Doc B text with arbitration", language="English")
    assert "arbitration clause" in result
    mock_generate.assert_called_once()

@patch.dict("os.environ", {}, clear=True)
def test_ai_helpers_missing_key():
    # Tests that when GEMINI_API_KEY is missing, it returns a helpful error string without crashing
    result = get_document_summary("Some text", "English")
    assert "API key not configured" in result
