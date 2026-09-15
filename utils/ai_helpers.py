import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else None
except Exception:
    client = None

MODEL_ID = 'gemini-3.8-flash'

def get_document_summary(document_text: str, language: str = "English") -> str:
    """
    Asks Gemini to summarize a legal document in plain language.
    """
    if not client:
        return "Error: Gemini API key not configured properly."
        
    prompt = f"""
    You are an expert legal assistant whose goal is to make legal documents accessible to everyday people.
    Please read the following legal document and provide a clear, plain-language summary. 
    
    IMPORTANT: You must provide your ENTIRE response in {language}.
    
    Focus on:
    1. The core purpose of the document.
    2. The main obligations of the parties involved.
    3. Key dates, durations, or financial commitments if present.
    
    Document Text:
    {document_text}
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"An error occurred during summarization: {str(e)}"

def analyze_document_risks(document_text: str, language: str = "English") -> str:
    """
    Asks Gemini to identify risks and output a structured Markdown table and negotiation advice.
    """
    if not client:
        return "Error: Gemini API key not configured properly."
        
    prompt = f"""
    You are an expert legal assistant reviewing a document for a client who is not a lawyer.
    Your goal is to protect the user by identifying "Red Flags" or potentially unfavorable clauses.
    
    IMPORTANT: You must provide your ENTIRE response in {language}.
    
    Scan the document and highlight any of the following if they exist:
    - Auto-renewal clauses
    - Hidden fees or penalties
    - Extreme liability waivers or indemnification clauses
    - Forced arbitration or unfair dispute resolution terms
    - Unusually long notice periods for termination
    
    Format your output strictly as follows:
    
    ### Clause-by-Clause Risk Analysis
    Create a Markdown table with the following columns:
    | Original Clause Snippet | Plain English Translation | Risk Level (High/Medium/Low) |
    
    ### Negotiation Suggestions
    For any clause rated 'High' or 'Medium' risk, provide a short, polite email snippet the user can use to negotiate or push back against that specific clause.
    
    If no major risks are found, state that the document appears standard, but remind them to still read carefully.
    
    Document Text:
    {document_text}
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"An error occurred during risk analysis: {str(e)}"

def ask_question_about_document(document_text: str, user_question: str, language: str = "English") -> str:
    """
    Allows the user to ask a specific question about the uploaded document.
    """
    if not client:
        return "Error: Gemini API key not configured properly."
        
    prompt = f"""
    You are a helpful legal assistant. The user has uploaded a legal document and has a specific question about it.
    Answer the user's question based ONLY on the provided document text. 
    If the answer is not in the document, politely state that the document does not cover that specific issue.
    Always remind the user at the end of your response that you are providing informational assistance, not formal legal advice.
    
    IMPORTANT: You must provide your ENTIRE response in {language}.
    
    User Question: {user_question}
    
    Document Text:
    {document_text}
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"An error occurred while answering the question: {str(e)}"

def compare_contracts(doc1_text: str, doc2_text: str, language: str = "English") -> str:
    """
    Compares two versions of a document to find additions, deletions, and modifications.
    """
    if not client:
        return "Error: Gemini API key not configured properly."
        
    prompt = f"""
    You are an expert legal assistant. The user has provided two versions of a legal document (Document A and Document B).
    Your task is to compare them and highlight the material differences.
    
    IMPORTANT: You must provide your ENTIRE response in {language}.
    
    Please structure your response as follows:
    1. **Summary of Changes:** A high-level overview of what changed (e.g., "The rent increased and a new pet fee was added.")
    2. **Key Additions:** What is in Document B that was NOT in Document A?
    3. **Key Deletions:** What was in Document A that was REMOVED in Document B?
    4. **Modified Clauses:** Which clauses were changed, and how does that impact the user?
    
    Document A (Original):
    {doc1_text}
    
    Document B (New/Modified):
    {doc2_text}
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"An error occurred during comparison: {str(e)}"
