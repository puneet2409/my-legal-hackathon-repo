import os
from google import genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

# Always reload environment variables to catch runtime updates to .env
load_dotenv(override=True)

# Candidate models in preferred order
MODELS = ['gemini-3.6-flash', 'gemini-3.8-flash', 'gemini-3.7-flash']
CURRENT_MODEL = MODELS[0]

def get_client() -> genai.Client:
    """
    Returns an initialized Gemini Client using the GEMINI_API_KEY environment variable.
    Refreshes the key if .env was modified.
    """
    load_dotenv(override=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None

def is_transient_error(exception: BaseException) -> bool:
    """
    Checks whether an exception is transient (503, 429, timeout, network error)
    and should be retried.
    """
    err_str = str(exception).upper()
    transient_indicators = [
        "503", "UNAVAILABLE", "HIGH DEMAND", "429", "RESOURCE_EXHAUSTED",
        "RATE LIMIT", "TIMEOUT", "CONNECTION", "SERVERERROR"
    ]
    return any(indicator in err_str for indicator in transient_indicators)

@retry(
    retry=retry_if_exception(is_transient_error),
    wait=wait_exponential(multiplier=1.5, min=2, max=10),
    stop=stop_after_attempt(4)
)
def _generate_with_retry(prompt: str) -> str:
    """
    Executes an API call with automatic retry on transient errors and model fallback.
    """
    client = get_client()
    if not client:
        raise ValueError("Gemini API key is not configured or invalid.")

    # Try models in fallback order
    last_err = None
    for model_name in MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            # If it's a 404 (model not found), try next model immediately
            if "404" in str(e) or "NOT_FOUND" in str(e):
                continue
            # If transient, raise to let tenacity retry
            if is_transient_error(e):
                raise e
            # Other errors, break and return
            break

    if last_err:
        raise last_err
    return "Error: Unable to generate content from AI model."

def get_document_summary(document_text: str, language: str = "English") -> str:
    """
    Summarizes the legal document in clear, plain language.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return "Error: Gemini API key not configured properly. Please check your .env file."
        
    prompt = f"""
    You are an expert legal assistant. Summarize the following document in plain, accessible language.
    IMPORTANT: Respond ENTIRELY in {language}.
    
    Structure your summary as follows:
    1. **Overview & Purpose**: What kind of agreement is this and what is its goal?
    2. **Key Parties & Obligations**: Who is involved and what must each party do?
    3. **Important Dates & Financial Terms**: Notice periods, renewal terms, fees, and penalties.
    4. **Key Takeaways**: The 3 most critical points the reader must remember.
    
    Document Text:
    {document_text}
    """
    try:
        return _generate_with_retry(prompt)
    except Exception as e:
        return f"An error occurred during summarization: {str(e)}"

def analyze_document_risks(document_text: str, language: str = "English") -> str:
    """
    Analyzes legal risks and outputs a structured Markdown table and negotiation guidance.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return "Error: Gemini API key not configured properly. Please check your .env file."
        
    prompt = f"""
    You are an expert legal advisor protecting a non-lawyer consumer or small business.
    Scan this legal document for hidden traps, high risks, or unfair clauses.
    IMPORTANT: Respond ENTIRELY in {language}.
    
    Pay special attention to:
    - Automatic renewals or difficult termination clauses
    - Excessive fees, penalties, or liquidated damages
    - Broad indemnification or unilateral liability waivers
    - Forced arbitration or unfair dispute venue selections
    - Intellectual property or data ownership forfeitures
    
    Format your output strictly as:
    ### ⚠️ Clause-by-Clause Risk Assessment
    | Original Clause Excerpt | Plain English Meaning | Risk Level (High / Medium / Low) |
    | :--- | :--- | :--- |
    
    ### 🤝 Recommended Negotiation Strategy
    For each High or Medium risk item, provide a clear, polite alternative wording or email script the user can send to negotiate.
    
    Document Text:
    {document_text}
    """
    try:
        return _generate_with_retry(prompt)
    except Exception as e:
        return f"An error occurred during risk analysis: {str(e)}"

def ask_question_about_document(document_text: str, user_question: str, language: str = "English") -> str:
    """
    Answers user queries grounded strictly within the document.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return "Error: Gemini API key not configured properly. Please check your .env file."
        
    prompt = f"""
    You are an interactive legal assistant. Answer the user's question accurately using ONLY the provided document.
    If the document does not mention the answer, state clearly that it is not addressed in this agreement.
    IMPORTANT: Respond ENTIRELY in {language}.
    
    Question: {user_question}
    
    Document Text:
    {document_text}
    """
    try:
        return _generate_with_retry(prompt)
    except Exception as e:
        return f"An error occurred while answering your question: {str(e)}"

def compare_contracts(doc1_text: str, doc2_text: str, language: str = "English") -> str:
    """
    Compares two documents and highlights additions, deletions, and modifications.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return "Error: Gemini API key not configured properly. Please check your .env file."
        
    prompt = f"""
    You are an expert contract comparison analyst.
    Compare Document A (Original) and Document B (Modified/New Version).
    IMPORTANT: Respond ENTIRELY in {language}.
    
    Provide your analysis structured as:
    1. **Executive Summary of Differences**: High-level comparison.
    2. **Key Additions in Document B**: What was newly introduced?
    3. **Key Deletions from Document A**: What protections or clauses were removed?
    4. **Material Modifications**: How have existing terms shifted (e.g. price, duration, liability)?
    5. **Impact Assessment**: Is Document B more or less favorable to the user than Document A?
    
    Document A (Original):
    {doc1_text}
    
    Document B (Modified):
    {doc2_text}
    """
    try:
        return _generate_with_retry(prompt)
    except Exception as e:
        return f"An error occurred during document comparison: {str(e)}"

# --- AUTONOMOUS AGENT SIMULATION ---

def agent_a_opening(document_text: str, language: str = "English") -> str:
    """Agent A: User's assertive counsel demanding changes."""
    prompt = f"""
    You are an assertive, professional legal counsel representing the user.
    Identify the single most unfair, one-sided clause in this document and write a firm 1-paragraph opening negotiation argument to opposing counsel demanding its revision.
    IMPORTANT: Respond ENTIRELY in {language}.
    
    Document: {document_text}
    """
    try:
        return _generate_with_retry(prompt)
    except Exception as e:
        return f"Agent A encountered an error: {str(e)}"

def agent_b_response(document_text: str, agent_a_msg: str, language: str = "English") -> str:
    """Agent B: Opposing counsel defending the clause with a proposed compromise."""
    prompt = f"""
    You are opposing counsel defending the contract.
    The user's counsel just stated: '{agent_a_msg}'.
    Write a 1-paragraph formal defense of your client's position, but propose a slight counter-compromise.
    IMPORTANT: Respond ENTIRELY in {language}.
    """
    try:
        return _generate_with_retry(prompt)
    except Exception as e:
        return f"Agent B encountered an error: {str(e)}"

def agent_a_counter(document_text: str, agent_b_msg: str, language: str = "English") -> str:
    """Agent A: Counter-argument closing the negotiation with protective terms."""
    prompt = f"""
    You are the user's legal counsel.
    Opposing counsel replied: '{agent_b_msg}'.
    Write a final 1-paragraph counter-proposal that calls out any subtle risks in their compromise and locks down favorable terms for your client.
    IMPORTANT: Respond ENTIRELY in {language}.
    """
    try:
        return _generate_with_retry(prompt)
    except Exception as e:
        return f"Agent A encountered an error: {str(e)}"
