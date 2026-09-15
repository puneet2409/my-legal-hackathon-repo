import os
from google import genai
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None
except Exception:
    client = None

MODEL_ID = 'gemini-3.6-flash'

def retry_on_503(e):
    # Only retry if it's a 503 Unavailable error
    return "503" in str(e) or "UNAVAILABLE" in str(e)

# Create a decorator we can reuse
auto_retry = retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(5)
)

@auto_retry
def _generate_with_retry(prompt: str) -> str:
    """Helper function to execute the API call with automatic retries."""
    return client.models.generate_content(model=MODEL_ID, contents=prompt).text

def get_document_summary(document_text: str, language: str = "English") -> str:
    if not client: return "Error: Gemini API key not configured properly."
    prompt = f"You are an expert legal assistant. Summarize this document in plain language. Respond ENTIRELY in {language}.\n\nFocus on: 1. Core purpose 2. Main obligations 3. Key dates/money.\n\nDoc: {document_text}"
    try: return _generate_with_retry(prompt)
    except Exception as e: return f"Error: {str(e)}"

def analyze_document_risks(document_text: str, language: str = "English") -> str:
    if not client: return "Error: Gemini API key not configured properly."
    prompt = f"You are an expert legal assistant. Respond ENTIRELY in {language}.\n\nFind Red Flags (auto-renewals, hidden fees, extreme waivers, forced arbitration). Format strictly as a Markdown table: | Original Clause Snippet | Plain English Translation | Risk Level (High/Medium/Low) |\n\nBelow the table, provide Negotiation Suggestions for High/Medium risks.\n\nDoc: {document_text}"
    try: return _generate_with_retry(prompt)
    except Exception as e: return f"Error: {str(e)}"

def ask_question_about_document(document_text: str, user_question: str, language: str = "English") -> str:
    if not client: return "Error: Gemini API key not configured properly."
    prompt = f"You are a legal assistant. Answer the user's question based ONLY on the document. Respond ENTIRELY in {language}.\n\nQuestion: {user_question}\nDoc: {document_text}"
    try: return _generate_with_retry(prompt)
    except Exception as e: return f"Error: {str(e)}"

def compare_contracts(doc1_text: str, doc2_text: str, language: str = "English") -> str:
    if not client: return "Error: Gemini API key not configured properly."
    prompt = f"Compare Document A and Document B. Respond ENTIRELY in {language}.\n\nStructure: 1. Summary of Changes 2. Key Additions 3. Key Deletions 4. Modified Clauses.\n\nDoc A: {doc1_text}\nDoc B: {doc2_text}"
    try: return _generate_with_retry(prompt)
    except Exception as e: return f"Error: {str(e)}"

# --- NEW SIMULATION AGENTS ---

def agent_a_opening(document_text: str, language: str = "English") -> str:
    if not client: return "Error"
    prompt = f"You are a fierce, highly competent AI lawyer representing the user. Read the document, find the most unfair or one-sided clause, and write a concise, persuasive 1-paragraph opening argument to the opposing counsel demanding it be changed. Be professional but firm. Respond ENTIRELY in {language}.\n\nDoc: {document_text}"
    try: return _generate_with_retry(prompt)
    except Exception: return "Agent A encountered an error."

def agent_b_response(document_text: str, agent_a_msg: str, language: str = "English") -> str:
    if not client: return "Error"
    prompt = f"You are the opposing counsel defending this document. The other lawyer just said: '{agent_a_msg}'. Write a concise, stubborn 1-paragraph response defending your client's clause, but offer a very slight, sneaky compromise. Be formal. Respond ENTIRELY in {language}."
    try: return _generate_with_retry(prompt)
    except Exception: return "Agent B encountered an error."

def agent_a_counter(document_text: str, agent_b_msg: str, language: str = "English") -> str:
    if not client: return "Error"
    prompt = f"You are a fierce AI lawyer representing the user. The opposing counsel just said: '{agent_b_msg}'. Write a final, aggressive 1-paragraph counter-offer protecting the user. Call out their sneaky compromise. Respond ENTIRELY in {language}."
    try: return _generate_with_retry(prompt)
    except Exception: return "Agent A encountered an error."
