from unittest.mock import MagicMock, patch
from utils.doc_parser import extract_text_from_file, MAX_PAGES

class MockUploadedFile:
    """Mock for Streamlit UploadedFile object."""
    def __init__(self, name: str, content_bytes: bytes):
        self.name = name
        self._content = content_bytes
        self.size = len(content_bytes)

    def getvalue(self) -> bytes:
        return self._content

def test_extract_txt_utf8():
    content = "Legal Clause: Tenant shall maintain property.".encode("utf-8")
    mock_file = MockUploadedFile("contract.txt", content)
    result = extract_text_from_file(mock_file)
    assert "Legal Clause: Tenant shall maintain property." in result

def test_extract_txt_latin1():
    content = "Payment amount: £1,200 annually.".encode("latin-1")
    mock_file = MockUploadedFile("terms.txt", content)
    result = extract_text_from_file(mock_file)
    assert "1,200" in result

def test_extract_none():
    assert extract_text_from_file(None) == ""

def test_extract_empty_name():
    mock_file = MockUploadedFile("", b"")
    assert extract_text_from_file(mock_file) == ""

def test_extract_unsupported_format():
    mock_file = MockUploadedFile("agreement.docx", b"data")
    result = extract_text_from_file(mock_file)
    assert "Unsupported file format" in result

@patch("pypdf.PdfReader")
def test_extract_pdf_success(mock_reader_cls):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page 1: Confidentiality clause."
    
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_reader_cls.return_value = mock_reader

    mock_file = MockUploadedFile("nda.pdf", b"%PDF-1.4...")
    result = extract_text_from_file(mock_file)
    assert "Page 1: Confidentiality clause." in result

@patch("pypdf.PdfReader")
def test_extract_pdf_zero_pages(mock_reader_cls):
    mock_reader = MagicMock()
    mock_reader.pages = []
    mock_reader_cls.return_value = mock_reader

    mock_file = MockUploadedFile("empty.pdf", b"%PDF-1.4...")
    result = extract_text_from_file(mock_file)
    assert "Error: The uploaded PDF has no pages." in result

@patch("pypdf.PdfReader")
def test_extract_pdf_truncation_guard(mock_reader_cls):
    # Simulate a PDF with 60 pages (> MAX_PAGES = 50)
    mock_pages = []
    for i in range(60):
        p = MagicMock()
        p.extract_text.return_value = f"Page {i} text."
        mock_pages.append(p)

    mock_reader = MagicMock()
    mock_reader.pages = mock_pages
    mock_reader_cls.return_value = mock_reader

    mock_file = MockUploadedFile("large_contract.pdf", b"%PDF-1.4...")
    result = extract_text_from_file(mock_file)
    assert "Page 0 text." in result
    assert f"[Note: Document was truncated to the first {MAX_PAGES} pages" in result

@patch("pypdf.PdfReader")
def test_extract_pdf_exception_handling(mock_reader_cls):
    mock_reader_cls.side_effect = Exception("Corrupted PDF stream")
    mock_file = MockUploadedFile("corrupted.pdf", b"bad bytes")
    result = extract_text_from_file(mock_file)
    assert "Error reading file: Corrupted PDF stream" in result
