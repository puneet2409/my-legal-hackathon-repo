# ⚖️ LegalLens: AI Legal Co-Pilot & Autonomous Negotiation Simulator

## 📌 Problem Statement & Chosen Vertical
**Vertical:** Legal Information & Basic Assistance  
Legal information and contracts are notorious for complex terminology ("legalese"), dense structures, and hidden traps that are difficult to navigate without costly professional legal counsel. 

**LegalLens** is a modern, GenAI-powered legal co-pilot designed to democratize legal comprehension. It enables consumers, freelancers, and small businesses to:
1. **Demystify Complex Documents:** Translate contracts, leases, NDAs, and policies into clear, plain language with highlighted obligations and deadlines.
2. **Expose Hidden Risks & Red Flags:** Automatically spot predatory clauses (auto-renewals, unilateral liability waivers, termination penalties) in structured risk assessment matrices.
3. **Simulate Autonomous Multi-Agent Negotiations:** Watch two AI agents roleplay a live negotiation between user's counsel and opposing counsel to prepare counter-strategies before signing.
4. **Compare Contract Versions:** Identify additions, deletions, and subtle clause shifts between initial drafts and counter-party revisions.
5. **Multi-Language Accessibility:** Instant real-time legal translations across 8 global languages.

> **⚠️ Responsible AI Notice:** LegalLens provides general informational assistance and educational analysis. It does *not* provide formal legal advice and does *not* replace a licensed attorney.

---

## 🚀 Approach, Logic & Architecture
LegalLens is built using a lightweight, modular, and resilient architecture adhering strictly to hackathon performance and repository size rules (< 10 MB):

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Frontend                     │
│  [Plain English Summary] [Risk Table] [Q&A Chat] [Compare]  │
│          [🎭 Autonomous AI Negotiation Simulator]           │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
     ┌───────────────────┐           ┌───────────────────┐
     │ utils/doc_parser  │           │ utils/ai_helpers  │
     │  - pypdf parser   │           │  - Gemini API     │
     │  - UTF-8 fallback │           │  - Tenacity Retry │
     │  - 50-page guard  │           │  - Model Fallback │
     └───────────────────┘           └───────────────────┘
```

### 1. Robust Document Ingestion (`utils/doc_parser.py`)
- Safe extraction for PDF and TXT formats.
- Encoding resilience: Automatic fallback between UTF-8 and Latin-1.
- Page limit guard (up to 50 pages) to protect token budgets and execution speed.

### 2. Enterprise Resilience & Model Fallback (`utils/ai_helpers.py`)
- **Transient Error Shield:** Integrates `tenacity` exponential backoff (2s → 10s) specifically catching 503 high-demand, 429 rate-limit, and network errors.
- **Dynamic Key Reloading:** Automatically detects runtime changes in `.env` without requiring process restarts.
- **Model Fallback Chain:** Gracefully falls back across Gemini 3.6/3.8 Flash models if a specific model experiences regional saturation.

### 3. Privacy & Security By Design
- Zero permanent server storage: uploaded documents are parsed strictly in memory.
- API keys are isolated in `.env` and shielded by `.gitignore` to prevent secret leakage on public GitHub repositories.
- Prominently featured dismissible legal disclaimer to educate users.

---

## 💡 How the Solution Works (Local Setup & Run)

### Prerequisites
- Python 3.10+ installed
- Google AI Studio API Key ([Get one free here](https://aistudio.google.com/))

### Installation Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/puneet2409/my-legal-hackathon-repo.git
   cd my-legal-hackathon-repo
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure your API Key:**
   Create a `.env` file in the root directory:
   ```text
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   ```
4. **Launch the application:**
   ```bash
   streamlit run app.py
   ```
5. **Run the Automated Test Suite:**
   ```bash
   python -m pytest tests/ -v
   ```

---

## 🧪 Comprehensive Automated Testing
The project includes a robust test suite covering:
- Parsing UTF-8 and Latin-1 encoded text documents.
- Error handling for unsupported file extensions and empty payloads.
- Transient error classification (verifying 503/429 retry behavior).
- Mock-based unit tests for AI summarization, risk analysis, version comparison, and missing key handling.

Run tests anytime with:
```bash
python -m pytest tests/ -v
```

---

## 🧠 Assumptions Made
* **Searchable Text:** Uploaded PDFs contain digital text layers rather than scanned flat images.
* **Informational Purpose:** Users leverage the tool to understand concepts and prepare questions for legal professionals.
* **Connectivity:** Requires outbound internet access to interact with Google Gemini AI Studio endpoints.

---

## 🛠 Tech Stack
* **UI & Reactive Frontend:** Streamlit 1.38.0
* **Generative AI Platform:** Google Gemini API via `google-genai` SDK
* **Fault Tolerance & Resilience:** `tenacity` exponential backoff
* **Document Parsing Engine:** `pypdf`
* **Automated Unit Testing:** `pytest`

---
*Developed for the Hack2Skill AI Hackathon Challenge.*
