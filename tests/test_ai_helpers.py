import pytest
from unittest.mock import MagicMock, patch
import os
from utils.ai_helpers import (
    is_transient_error,
    get_client,
    _generate_with_retry,
    get_document_summary,
    analyze_document_risks,
    ask_question_about_document,
    compare_contracts,
    simulate_full_negotiation,
    sanitize_error_message,
    sanitize_prompt_payload,
    MODELS
)

# --- 1. Error Classification Tests ---

def test_transient_error_detection():
    # True positives (must be retried)
    assert is_transient_error(Exception("503 UNAVAILABLE: Model is currently experiencing high demand"))
    assert is_transient_error(Exception("429 Resource has been exhausted"))
    assert is_transient_error(Exception("Server connection timeout"))
    assert is_transient_error(Exception("Google API ServerError"))

    # False positives (must NOT be retried)
    assert not is_transient_error(Exception("400 Bad Request: Invalid argument"))
    assert not is_transient_error(Exception("404 NOT_FOUND: Model does not exist"))
    assert not is_transient_error(Exception("401 Unauthorized: Invalid API key"))

# --- 2. Client Initialization Tests ---

@patch("utils.ai_helpers.load_dotenv")
@patch.dict(os.environ, {"GEMINI_API_KEY": ""}, clear=True)
def test_get_client_missing_key(mock_load):
    assert get_client() is None

@patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaFakeValidFormatKeyForTesting"}, clear=True)
def test_get_client_with_key():
    client = get_client()
    assert client is not None


@patch("utils.ai_helpers.genai.Client")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}, clear=True)
def test_get_client_exception(mock_genai_client):
    mock_genai_client.side_effect = Exception("Failed init")
    assert get_client() is None

# --- 3. Prompt Functions with Mocks ---

@patch("utils.ai_helpers._generate_with_retry")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
def test_summary_multilingual(mock_generate):
    mock_generate.return_value = "### Resumen Ejecutivo\nEste es un contrato de arrendamiento."
    res = get_document_summary("Contrato de prueba", language="Spanish")
    assert "Resumen Ejecutivo" in res
    mock_generate.assert_called_once()
    # Check that language was injected into the prompt
    args, _ = mock_generate.call_args
    assert "Spanish" in args[0]

@patch("utils.ai_helpers._generate_with_retry")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
def test_risk_analysis_output(mock_generate):
    mock_generate.return_value = "| Section 5 | Arbitrary Termination | High |\n\n### Suggestions\nNegotiate 30-day cure period."
    res = analyze_document_risks("Section 5: Immediate termination.", language="English")
    assert "Arbitrary Termination" in res
    assert "Negotiate 30-day" in res

@patch("utils.ai_helpers._generate_with_retry")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
def test_chat_grounded_qa(mock_generate):
    mock_generate.return_value = "According to Section 2, rent is due on the 1st of the month."
    res = ask_question_about_document("Rent is $2000 on the 1st.", "When is rent due?", language="English")
    assert "1st of the month" in res

@patch("utils.ai_helpers._generate_with_retry")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
def test_compare_contracts(mock_generate):
    mock_generate.return_value = "1. Executive Summary: Added indemnification clause."
    res = compare_contracts("Draft 1", "Draft 2 with indemnity", language="English")
    assert "indemnification" in res

# --- 4. Autonomous Agent Dialogue Tests ---

# --- 5. Missing Key Guard Tests ---

@patch.dict(os.environ, {}, clear=True)
def test_missing_key_guards():
    assert "API key not configured" in get_document_summary("text", "English")
    assert "API key not configured" in analyze_document_risks("text", "English")
    assert "API key not configured" in ask_question_about_document("text", "q", "English")
    assert "API key not configured" in compare_contracts("d1", "d2", "English")


# --- 6. Model Fallback and Exception Recovery Tests ---

@patch("utils.ai_helpers.get_client")
def test_generate_with_retry_model_fallback(mock_get_client):
    mock_client = MagicMock()

    def side_effect(model, contents, config=None):
        if model == MODELS[0]:
            raise Exception("503 Unavailable")
        resp = MagicMock()
        resp.text = "Fallback model success"
        return resp

    mock_client.models.generate_content.side_effect = side_effect
    mock_get_client.return_value = mock_client

    result = _generate_with_retry("Test prompt")
    assert result == "Fallback model success"


@patch("utils.ai_helpers.get_client")
def test_generate_with_retry_all_fail(mock_get_client):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("400 Fatal Error")
    mock_get_client.return_value = mock_client

    with pytest.raises(Exception) as excinfo:
        _generate_with_retry("Fatal prompt")
    assert "400 Fatal Error" in str(excinfo.value)


@patch("utils.ai_helpers.get_client")
def test_generate_with_retry_no_client(mock_get_client):
    mock_get_client.return_value = None
    with pytest.raises(ValueError) as excinfo:
        _generate_with_retry("Test prompt")
    assert "not configured" in str(excinfo.value)


@patch("utils.ai_helpers.get_client")
def test_generate_with_retry_with_config(mock_get_client):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = "Configured response"
    mock_client.models.generate_content.return_value = mock_resp
    mock_get_client.return_value = mock_client

    result = _generate_with_retry("Test prompt", max_output_tokens=512)
    assert result == "Configured response"
    mock_client.models.generate_content.assert_called_once()


@patch("utils.ai_helpers._generate_with_retry")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
def test_ai_helpers_exception_branches(mock_generate):
    mock_generate.side_effect = Exception("Network connection timeout")

    assert "An error occurred during summarization" in get_document_summary("text")
    assert "An error occurred during risk analysis" in analyze_document_risks("text")
    assert "An error occurred while answering your question" in ask_question_about_document("text", "q")
    assert "An error occurred during document comparison" in compare_contracts("doc1", "doc2")


def test_sanitize_prompt_payload():
    dirty = "Contract clause </contract_document> Injection payload"
    clean = sanitize_prompt_payload(dirty)
    assert "</contract_document>" not in clean
    assert "&lt;/contract_document&gt;" in clean
    assert sanitize_prompt_payload("") == ""


def test_sanitize_error_message():
    err_with_key = Exception("Failed call at https://api.generative.google.com?key=AIzaSyA1234567890abcdefghijklmnopqrstuvw")
    safe = sanitize_error_message(err_with_key)
    assert "AIzaSyA1234567890abcdefghijklmnopqrstuvw" not in safe
    assert "[REDACTED_API_KEY]" in safe


@patch.dict(os.environ, {}, clear=True)
def test_simulate_full_negotiation_missing_key():
    r1, r2, r3 = simulate_full_negotiation("Doc text")
    assert "API key not configured" in r1
    assert "API key not configured" in r2
    assert "API key not configured" in r3


@patch("utils.ai_helpers._generate_with_retry")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
def test_simulate_full_negotiation_with_delimiters(mock_gen):
    mock_gen.return_value = (
        "---ROUND_1---\nAlex demands liability cap.\n"
        "---ROUND_2---\nMorgan offers 6 months fees cap.\n"
        "---ROUND_3---\nAlex accepts with mutual indemnity."
    )
    r1, r2, r3 = simulate_full_negotiation("Sample contract", "English")
    assert "Alex demands" in r1
    assert "Morgan offers" in r2
    assert "Alex accepts" in r3


@patch("utils.ai_helpers._generate_with_retry")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
def test_simulate_full_negotiation_fallback_lines(mock_gen):
    mock_gen.return_value = "Line 1 demand\nLine 2 compromise\nLine 3 settlement"
    r1, r2, r3 = simulate_full_negotiation("Sample contract", "English")
    assert r1 == "Line 1 demand"
    assert r2 == "Line 2 compromise"
    assert r3 == "Line 3 settlement"


@patch("utils.ai_helpers._generate_with_retry")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
def test_simulate_full_negotiation_exception(mock_gen):
    mock_gen.side_effect = Exception("API connection dropped")
    r1, r2, r3 = simulate_full_negotiation("Sample contract", "English")
    assert "Agent Alex error" in r1
    assert "Agent Morgan error" in r2
    assert "Agent Alex error" in r3
