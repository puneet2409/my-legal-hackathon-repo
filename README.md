# LegalLens: GenAI Legal Assistant

## 📌 Problem Statement & Chosen Vertical
**Vertical:** Legal Information & Assistance
Legal documents are often filled with complex terminology ("legalese") that is difficult for the average person to understand. LegalLens is a GenAI-powered solution designed to democratize legal information. It helps users understand, analyze, and safely navigate legal documents (like contracts, NDAs, and leases) by translating them into plain English and highlighting potential risks. 

*Note: This tool provides information and assistance, not certified legal advice.*

## 🚀 Approach and Logic
We built LegalLens using a highly efficient and lightweight tech stack: **Python and Streamlit** for the frontend/backend, and the **Google Gemini API** for natural language understanding and document analysis. 

The application logic follows a clear pipeline:
1.  **Ingestion:** The user uploads a PDF or TXT file. The `utils/doc_parser.py` safely extracts the raw text.
2.  **Analysis (Gemini API):** The extracted text is passed to the Gemini model using highly structured system prompts in `utils/ai_helpers.py`.
    *   *Summarization:* Extracts the core purpose and key obligations.
    *   *Risk Analysis:* Specifically hunts for common predatory clauses (auto-renewals, hidden fees, extreme liability waivers).
3.  **Interaction:** A built-in chat interface allows users to ask ad-hoc questions about the document context, keeping state via Streamlit's session state.
4.  **Security & Compliance:** Explicit disclaimers are placed in the UI. No documents are permanently stored on a server (processed in memory), and API keys are strictly managed via environment variables (never committed to the repo).

## 💡 How the Solution Works
1.  **Clone the Repository** and navigate to the project folder.
2.  **Install Dependencies:** Run `pip install -r requirements.txt`.
3.  **Set up Environment Variables:** Create a `.env` file in the root directory and add your Google API key: `GEMINI_API_KEY=your_api_key_here`.
4.  **Run the App:** Execute `streamlit run app.py` in your terminal.
5.  **Use the App:**
    *   Upload a legal document using the sidebar.
    *   Read the generated "Plain English" summary.
    *   Review the "Risk Analysis" section for highlighted clauses.
    *   Use the Chat tab to ask specific questions like, *"Can they terminate this contract without notice?"*
6.  **Run Tests:** Execute `pytest tests/` to run unit tests and ensure the core extraction logic works perfectly.

## 🧠 Assumptions Made
*   Users have access to an internet connection to communicate with the Gemini API.
*   Uploaded documents are text-searchable (not scanned images requiring OCR, though Gemini can handle images natively, we optimized for text extraction speed and token limits in this prototype).
*   The primary language of the documents is English.
*   The user understands the disclaimer that this AI is a co-pilot, not a replacement for a licensed attorney.

## 🛠 Tech Stack
*   **Frontend/UI:** Streamlit
*   **AI/LLM:** Google Gemini API (`google-genai` SDK)
*   **PDF Parsing:** pypdf
*   **Testing:** Pytest

---
*Developed for the Hack2Skill AI Hackathon Challenge.*
