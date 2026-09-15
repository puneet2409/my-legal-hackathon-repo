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
    agent_a_opening,
    agent_b_response,
    agent_a_counter,
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

@patch("utils.ai_helpers._generate_with_retry")
def test_agent_a_opening(mock_generate):
    mock_generate.return_value = "Section 4 imposes unilateral indemnification which is unfair."
    res = agent_a_opening("Contract text with section 4.", language="English")
    assert "unilateral indemnification" in res

@patch("utils.ai_helpers._generate_with_retry")
def test_agent_b_response(mock_generate):
    mock_generate.return_value = "Our client requires indemnity, but we offer a $10,000 liability cap."
    res = agent_b_response("Doc text", "Opposing argument", language="English")
    assert "liability cap" in res

@patch("utils.ai_helpers._generate_with_retry")
def test_agent_a_counter(mock_generate):
    mock_generate.return_value = "We accept the cap if mutual 30-day notice is guaranteed."
    res = agent_a_counter("Doc text", "Compromise offer", language="English")
    assert "30-day notice" in res

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
    # First model raises error, second model returns response
    first_resp = MagicMock(side_effect=Exception("503 Service Unavailable"))
    second_resp = MagicMock(text="Successful fallback response")

    def side_effect(model, contents):
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


@patch("utils.ai_helpers._generate_with_retry")
@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
def test_ai_helpers_exception_branches(mock_generate):
    mock_generate.side_effect = Exception("Network connection timeout")

    assert "An error occurred during summarization" in get_document_summary("text")
    assert "An error occurred during risk analysis" in analyze_document_risks("text")
    assert "An error occurred while answering your question" in ask_question_about_document("text", "q")
    assert "An error occurred during document comparison" in compare_contracts("doc1", "doc2")
    assert "Agent A encountered an error" in agent_a_opening("text")
    assert "Agent B encountered an error" in agent_b_response("text", "msg")
    assert "Agent A encountered an error" in agent_a_counter("text", "msg")
