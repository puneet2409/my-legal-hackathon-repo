import os
import re
from unittest.mock import MagicMock
from utils.doc_parser import sanitize_filename, extract_text_from_file, MAX_FILE_SIZE_BYTES
from utils.simulation_view import get_office_simulation_html
from utils.ai_helpers import MODELS, PROMPT_INJECTION_GUARD


def test_sanitize_filename_unix_traversal():
    dirty = "../../etc/passwd"
    clean = sanitize_filename(dirty)
    assert ".." not in clean
    assert "/" not in clean
    assert clean == "passwd"


def test_sanitize_filename_windows_traversal():
    dirty = "..\\..\\windows\\system32\\config.sys"
    clean = sanitize_filename(dirty)
    assert ".." not in clean
    assert "\\" not in clean
    assert clean == "config.sys"


def test_sanitize_filename_empty_and_special():
    assert sanitize_filename("") == ""
    assert sanitize_filename("contract!@#$%^&*().pdf") == "contract__________.pdf"


def test_file_size_exceeded_guard_txt():
    mock_file = MagicMock()
    mock_file.name = "huge_file.txt"
    mock_file.size = MAX_FILE_SIZE_BYTES + 1024
    mock_file.getvalue.return_value = b"x" * (MAX_FILE_SIZE_BYTES + 1024)

    result = extract_text_from_file(mock_file)
    assert "Error: File exceeds maximum allowed size" in result


def test_null_byte_sanitization():
    mock_file = MagicMock()
    mock_file.name = "null_bytes.txt"
    mock_file.size = 100
    mock_file.getvalue.return_value = "Legal Clause\x00 with hidden null bytes\x00.".encode("utf-8")

    result = extract_text_from_file(mock_file)
    assert "\x00" not in result
    assert result == "Legal Clause with hidden null bytes."


def test_prompt_injection_guard_isolation():
    assert "SECURITY POLICY" in PROMPT_INJECTION_GUARD
    assert "<contract_document>" in PROMPT_INJECTION_GUARD or "untrusted reference data" in PROMPT_INJECTION_GUARD


def test_xss_escaping_in_simulation():
    evil_xss = "<script>alert('pwned')</script><img src=x onerror=alert(1)>"
    html = get_office_simulation_html(evil_xss, "Defending position", "Counter offer")
    assert "<script>alert" not in html
    assert "&lt;script&gt;alert" in html
    assert "&lt;img src=x" in html


def test_simulation_aria_accessibility_landmarks():
    html = get_office_simulation_html("Opening argument", "Defense", "Counter")
    assert 'role="region"' in html
    assert 'role="img"' in html
    assert 'role="article"' in html
    assert 'role="log"' in html
    assert 'aria-live="polite"' in html
    assert 'aria-label="Interactive 2D Legal Negotiation Simulation"' in html


def test_models_fast_fallback_priority():
    # Efficiency requirement: First model must be a high-throughput, low-latency Flash-Lite model
    assert len(MODELS) >= 3
    assert "flash-lite" in MODELS[0].lower() or "flash" in MODELS[0].lower()


def test_simulation_generation_latency():
    import time
    start = time.perf_counter()
    html = get_office_simulation_html("Arg A", "Arg B", "Arg C")
    duration = time.perf_counter() - start
    assert duration < 0.05  # Must generate in under 50ms (ultra efficient)
    assert len(html) > 1000
