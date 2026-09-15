# pylint: disable=line-too-long,broad-exception-caught,too-many-locals,too-many-return-statements,too-many-branches,no-else-return
"""Document parsing utilities for safe text extraction from PDFs and Text files."""

import os
import re
import logging
from typing import Any
import pypdf

# Configure module-level logger
logger = logging.getLogger(__name__)

# Security & Performance Constraints
MAX_PAGES: int = 50
MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit to prevent Memory/DoS attacks
SUPPORTED_EXTENSIONS = {"pdf", "txt"}
RE_SAFE_FILENAME = re.compile(r"[^a-zA-Z0-9_.-]")


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to protect against path traversal and special character injection.

    Args:
        filename: Untrusted raw filename string.

    Returns:
        str: Clean basename stripped of path separators and unsafe characters.
    """
    if not filename:
        return ""
    # Strip directory path traversal sequences (both / and \)
    base = os.path.basename(filename.replace("\\", "/"))
    # Keep only safe alphanumeric characters, underscores, hyphens, and dots
    clean = RE_SAFE_FILENAME.sub("_", base)
    return clean.strip("._")


def extract_text_from_file(uploaded_file: Any) -> str:
    """
    Extracts text from an uploaded file (either PDF or TXT) safely.

    Implements:
      - File size bounds checking (<= 10MB)
      - Path traversal sanitization
      - Dual-encoding fallback (UTF-8 with Latin-1 failover)
      - Null byte stripping
      - Page count capping (<= 50 pages)

    Args:
        uploaded_file: Streamlit UploadedFile or file-like object with .name and .getvalue().

    Returns:
        str: Extracted document text, or a user-friendly error/warning message.
    """
    if uploaded_file is None:
        return ""

    raw_name = getattr(uploaded_file, "name", "")
    if not raw_name:
        return ""

    safe_name = sanitize_filename(raw_name)
    file_type = safe_name.split(".")[-1].lower() if "." in safe_name else ""

    if file_type not in SUPPORTED_EXTENSIONS:
        return f"Unsupported file format (.{file_type}). Please upload a .txt or .pdf file."

    try:
        # Check size if available
        file_size = getattr(uploaded_file, "size", None)
        if file_size is not None and file_size > MAX_FILE_SIZE_BYTES:
            logger.warning("Rejected file %s exceeding size limit: %d bytes", safe_name, file_size)
            return f"Error: File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."

        if file_type == "txt":
            raw_bytes = uploaded_file.getvalue()
            if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
                return f"Error: File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."

            # Decode UTF-8 with failover to Latin-1
            try:
                text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = raw_bytes.decode("latin-1", errors="replace")

            # Strip null bytes and sanitize whitespace
            cleaned_text = text.replace("\x00", "").strip()
            return cleaned_text

        elif file_type == "pdf":
            pdf_reader = pypdf.PdfReader(uploaded_file)
            total_pages = len(pdf_reader.pages)
            if total_pages == 0:
                return "Error: The uploaded PDF has no pages."

            text_parts = []
            pages_to_read = min(total_pages, MAX_PAGES)

            for page_num in range(pages_to_read):
                page = pdf_reader.pages[page_num]
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)

            if not text_parts:
                return "Error: Could not extract text. The PDF might be scanned or image-based."

            full_text = "\n\n".join(text_parts).replace("\x00", "").strip()
            if total_pages > MAX_PAGES:
                full_text += f"\n\n[Note: Document was truncated to the first {MAX_PAGES} pages for performance.]"

            return full_text

    except Exception as e:
        logger.error("Failed to parse file %s: %s", safe_name, str(e))
        return f"Error reading file: {str(e)}"

    return ""
