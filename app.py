import streamlit as st
import os
from utils.doc_parser import extract_text_from_file
from utils.ai_helpers import (
    get_document_summary, analyze_document_risks, ask_question_about_document,
    compare_contracts, simulate_full_negotiation
)
from utils.simulation_view import get_office_simulation_html
import streamlit.components.v1 as components

st.set_page_config(
    page_title="LegalLens: AI Legal Co-Pilot & Simulator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN STYLING INJECTION (Glassmorphism, Gradients, Sleek Tabs) ---
MODERN_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
  
  html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
  }
  
  /* Modern Dark App Canvas */
  .stApp {
    background: radial-gradient(130% 120% at 50% 0%, #0f172a 0%, #030712 100%);
    color: #f8fafc;
  }
  
  /* Sidebar Polishing */
  [data-testid="stSidebar"] {
    background: #090d16 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
  }
  
  /* Glassmorphism Cards */
  .glass-card {
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.6);
    margin-bottom: 16px;
  }
  
  /* Pill Tab Navigation Overhaul */
  .stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background: rgba(15, 23, 42, 0.7) !important;
    padding: 6px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
  }
  
  .stTabs [data-baseweb="tab"] {
    height: 42px !important;
    border-radius: 8px !important;
    padding: 0 16px !important;
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: none !important;
    transition: all 0.2s ease !important;
  }
  
  .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
  }
  
  /* Modern Button Styling */
  .stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  }
  
  .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px -4px rgba(2, 132, 199, 0.45) !important;
  }
  
  /* Gradient Hero Header */
  .hero-title {
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    letter-spacing: -0.02em;
  }
  
  /* Custom badge */
  .badge-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
</style>
"""
st.markdown(MODERN_CSS, unsafe_allow_html=True)

# Sample Documents for One-Click Testing
SAMPLE_LEASE = """COMMERCIAL LEASE AGREEMENT
1. PARTIES: Landlord ("Acme Properties") and Tenant ("Nova Corp").
2. PREMISES & RENT: Suite 400, $3,500 payable monthly on the 1st day.
3. TERM & AUTOMATIC RENEWAL: 1-year term commencing October 1, 2026. This lease shall automatically renew for successive 3-year periods unless Tenant gives written notice 120 days prior to expiration.
4. INDEMNIFICATION: Tenant shall indemnify, defend, and hold harmless Landlord from any and all damages, liabilities, and claims whatsoever, without limitation.
5. TERMINATION PENALTY: In the event of early termination, Tenant shall immediately forfeit all deposits and pay an early exit penalty equal to six (6) months rent.
6. DISPUTE RESOLUTION: All disputes shall be resolved via binding arbitration in Wilmington, Delaware at Tenant's sole expense."""

SAMPLE_NDA = """MUTUAL NON-DISCLOSURE AGREEMENT
1. CONFIDENTIAL INFORMATION: Includes all trade secrets, source code, and customer data disclosed by Disclosing Party.
2. OBLIGATIONS: Receiving Party shall hold all information in strict confidence for a period of ten (10) years.
3. INJUNCTIVE RELIEF: Disclosing Party shall be entitled to immediate injunctive relief without the requirement of posting a bond.
4. NON-COMPETE RESTRICTION: Receiving Party agrees not to engage in any competing line of business in North America for three (3) years following signature.
5. LIQUIDATED DAMAGES: Breach of this agreement triggers an automatic liquidated damages payment of $250,000 without requirement of proving actual damages."""

# --- PERFORMANCE OPTIMIZED CACHING ---
@st.cache_data(show_spinner=False, max_entries=50)
def cached_document_summary(doc_text: str, target_lang: str) -> str:
    """Caches AI summaries to prevent redundant API calls and reduce latency."""
    return get_document_summary(doc_text, target_lang)


@st.cache_data(show_spinner=False, max_entries=50)
def cached_document_risks(doc_text: str, target_lang: str) -> str:
    """Caches AI risk assessments for instant sub-millisecond retrieval."""
    return analyze_document_risks(doc_text, target_lang)


@st.cache_data(show_spinner=False, max_entries=50)
def cached_contract_comparison(doc1: str, doc2: str, target_lang: str) -> str:
    """Caches contract version comparison diffs."""
    return compare_contracts(doc1, doc2, target_lang)


@st.cache_data(show_spinner=False, max_entries=20)
def cached_negotiation_simulation(doc_text: str, target_lang: str) -> tuple:
    """Caches 3-turn multi-agent simulation for instant playback."""
    return simulate_full_negotiation(doc_text, target_lang)


def main():
    # Initialize persistent state variables
    if "document_text" not in st.session_state:
        st.session_state.document_text = None
    if "active_doc_name" not in st.session_state:
        st.session_state.active_doc_name = None
    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "risks" not in st.session_state:
        st.session_state.risks = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "disclaimer_dismissed" not in st.session_state:
        st.session_state.disclaimer_dismissed = False

    # Header section with sleek gradient typography
    st.markdown("""
    <div style="margin-bottom: 18px;">
      <div class="badge-tag" style="background: rgba(2, 132, 199, 0.15); color: #38bdf8; border: 1px solid rgba(2, 132, 199, 0.3); margin-bottom: 8px;">
        ⚖️ Hack2Skill AI Hackathon • Legal Co-Pilot Edition
      </div>
      <h1 class="hero-title" style="font-size: 2.5rem; margin: 0;">LegalLens: AI Legal Co-Pilot & Simulator</h1>
      <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 6px;">
        Democratizing legal documents with plain-English simplification, risk discovery, and autonomous 16-bit multi-agent negotiation simulations.
      </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dismissible Disclaimer
    if not st.session_state.disclaimer_dismissed:
        col_disc, col_btn = st.columns([0.88, 0.12])
        with col_disc:
            st.warning(
                "**LEGAL NOTICE:** LegalLens provides general informational assistance and educational analysis powered by AI. "
                "It is **not** a law firm and does **not** provide legal advice. Always consult a licensed attorney for formal legal matters.",
                icon="⚠️"
            )
        with col_btn:
            if st.button("✕ Dismiss", key="btn_dismiss_disclaimer", help="Acknowledge and hide this banner"):
                st.session_state.disclaimer_dismissed = True
                st.rerun()

    # Sidebar Controls
    with st.sidebar:
        st.markdown("### 🌐 Global Settings")
        language = st.selectbox(
            "Select Response Language",
            ["English", "Spanish", "French", "Hindi", "German", "Mandarin", "Arabic", "Portuguese"],
            help="All AI summaries, tables, and simulations will be generated in this language."
        )

        st.markdown("### ♿ Accessibility")
        a11y_mode = st.toggle(
            "High-Contrast & Large Text",
            value=False,
            key="a11y_toggle",
            help="Enforces WCAG 2.1 AAA high-contrast colors and increased typography for accessibility."
        )
        if a11y_mode:
            st.markdown("""
            <style>
              .stApp { background: #000000 !important; color: #ffffff !important; }
              p, span, div, label { font-size: 1.05rem !important; color: #ffffff !important; }
              button, input, select, textarea { outline: 3px solid #facc15 !important; outline-offset: 2px !important; }
              .glass-card { background: #090d16 !important; border: 2px solid #ffffff !important; }
            </style>
            """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📄 Primary Document")
        
        has_active_doc = bool(st.session_state.document_text and st.session_state.active_doc_name)
        
        if has_active_doc:
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 12px; margin-bottom: 12px;">
              <div style="font-size: 11px; text-transform: uppercase; color: #10b981; font-weight: 700;">✅ Active Document</div>
              <div style="font-size: 13px; font-weight: 600; color: #f8fafc; margin-top: 4px; word-break: break-all;">{st.session_state.active_doc_name}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Upload Different Document", key="btn_reset_doc", use_container_width=True):
                st.session_state.document_text = None
                st.session_state.active_doc_name = None
                st.session_state.summary = None
                st.session_state.risks = None
                st.session_state.chat_history = []
                st.rerun()
        else:
            uploaded_file = st.file_uploader(
                "Upload Contract / Agreement",
                type=['pdf', 'txt'],
                key="primary_file_uploader",
                help="Supports searchable PDF and TXT documents up to 50 pages."
            )
            
            if uploaded_file is not None:
                with st.spinner("Extracting text from document..."):
                    extracted_text = extract_text_from_file(uploaded_file)
                    
                    if not extracted_text or extracted_text.startswith("Error"):
                        st.error(f"❌ Failed to parse document: {extracted_text}")
                    else:
                        st.session_state.document_text = extracted_text
                        st.session_state.active_doc_name = uploaded_file.name
                        st.session_state.summary = None
                        st.session_state.risks = None
                        st.session_state.chat_history = []
                        st.rerun()
            
            # Quick one-click demo loaders for instant testing
            st.markdown("<div style='margin-top: 14px; font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase;'>⚡ Or Test with Sample Demo</div>", unsafe_allow_html=True)
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                if st.button("Commercial Lease", key="demo_lease", use_container_width=True):
                    st.session_state.document_text = SAMPLE_LEASE
                    st.session_state.active_doc_name = "Sample_Commercial_Lease.txt"
                    st.session_state.summary = None
                    st.session_state.risks = None
                    st.session_state.chat_history = []
                    st.rerun()
            with col_d2:
                if st.button("Unilateral NDA", key="demo_nda", use_container_width=True):
                    st.session_state.document_text = SAMPLE_NDA
                    st.session_state.active_doc_name = "Sample_Unilateral_NDA.txt"
                    st.session_state.summary = None
                    st.session_state.risks = None
                    st.session_state.chat_history = []
                    st.rerun()

    # Check API key before proceeding
    if not os.environ.get("GEMINI_API_KEY"):
        st.error(
            "🚨 **Gemini API Key Missing!** Please ensure your `GEMINI_API_KEY` is set in the `.env` file in the project directory.",
            icon="🔒"
        )
        st.info("Example `.env` format:\n```text\nGEMINI_API_KEY=AIzaSy...\n```")
        return

    # If document is loaded in session, show full modern application
    if has_active_doc:
        st.markdown(f"""
        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px; font-size: 12px; color: #94a3b8;">
          <span>📄 Analyzing: <strong style="color: #f8fafc;">{st.session_state.active_doc_name}</strong></span>
          <span>•</span>
          <span>🌐 Language: <strong style="color: #38bdf8;">{language}</strong></span>
        </div>
        """, unsafe_allow_html=True)
        
        # Main Interface Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📝 Plain English Summary",
            "🚨 Clause Risk Analyzer",
            "🎭 2D Office & Negotiation Simulation",
            "💬 Interactive Q&A",
            "⚖️ Version Comparison"
        ])
        
        # --- TAB 1: SUMMARY ---
        with tab1:
            st.subheader(f"Plain English Summary ({language})")
            st.caption("Converts dense legal jargon into clear obligations, dates, and takeaways.")
            
            col_sum_action, _ = st.columns([0.3, 0.7])
            with col_sum_action:
                if st.button("✨ Generate Summary", type="primary", use_container_width=True, key="btn_gen_sum"):
                    with st.spinner("Analyzing document structure and obligations..."):
                        summary = cached_document_summary(st.session_state.document_text, language)
                        st.session_state.summary = summary
            
            if st.session_state.get("summary"):
                st.markdown(st.session_state.summary)
                st.download_button(
                    label="📥 Download Summary (Markdown)",
                    data=st.session_state.summary,
                    file_name="legallens_summary.md",
                    mime="text/markdown",
                    key="dl_summary",
                    help="Export the plain-English summary"
                )

        # --- TAB 2: RISK ANALYZER ---
        with tab2:
            st.subheader("Clause-by-Clause Risk & Red-Flag Analyzer")
            st.caption("Spots predatory clauses like auto-renewals, broad liability, and hidden termination penalties.")
            
            if st.button("🔍 Scan for Hidden Risks", type="primary", key="btn_gen_risk"):
                with st.spinner("Scanning for predatory terms and unfavorable clauses..."):
                    risks = cached_document_risks(st.session_state.document_text, language)
                    st.session_state.risks = risks
            
            if st.session_state.get("risks"):
                st.markdown(st.session_state.risks)
                
                st.download_button(
                    label="📥 Download Risk Report (Markdown)",
                    data=st.session_state.risks,
                    file_name="legallens_risk_report.md",
                    mime="text/markdown",
                    key="dl_risks"
                )

        # --- TAB 3: 2D OFFICE & NEGOTIATION SIMULATION ---
        with tab3:
            st.subheader("🎭 Interactive 2D Law Office Simulation")
            st.caption("Inspired by Stanford Generative Agents: Autonomous AI legal agents navigate the 16-bit law firm map to negotiate clauses live.")

            col_run_sim, _ = st.columns([0.35, 0.65])
            with col_run_sim:
                run_sim_btn = st.button("▶️ Launch 2D Agent Simulation", type="primary", use_container_width=True, key="btn_run_2d_sim")

            if run_sim_btn or "sim_msg1" in st.session_state:
                if run_sim_btn:
                    with st.spinner("AI agents are examining legal clauses and roleplaying negotiation..."):
                        m1, m2, m3 = cached_negotiation_simulation(st.session_state.document_text, language)
                        st.session_state.sim_msg1 = m1
                        st.session_state.sim_msg2 = m2
                        st.session_state.sim_msg3 = m3
                
                # Render the 2D Canvas Office Map
                components.html(
                    get_office_simulation_html(
                        st.session_state.sim_msg1,
                        st.session_state.sim_msg2,
                        st.session_state.sim_msg3
                    ),
                    height=640
                )
                
                # Full negotiation transcript
                with st.expander("📜 Full Strategic Negotiation Transcript", expanded=True):
                    st.markdown(f"**🧑‍⚖️ Alex (Your Legal Counsel):**\n\n{st.session_state.sim_msg1}")
                    st.markdown(f"**🕴️ Morgan (Opposing Counsel):**\n\n{st.session_state.sim_msg2}")
                    st.markdown(f"**🧑‍⚖️ Alex (Final Protective Terms):**\n\n{st.session_state.sim_msg3}")
            else:
                # Default live 2D canvas view
                components.html(get_office_simulation_html(), height=640)
                st.info("Click **'▶️ Launch 2D Agent Simulation'** above to generate arguments based on your uploaded document and watch the agents navigate and negotiate live on the map!")

        # --- TAB 4: CHAT Q&A ---
        with tab4:
            st.subheader("Chat with your Document")
            st.caption("Ask specific questions grounded strictly in the contents of your uploaded document.")
            
            for message in st.session_state.get("chat_history", []):
                avatar = "🧑‍💻" if message["role"] == "user" else "⚖️"
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

            user_question = st.chat_input("Ask anything (e.g. 'Can I terminate early?' or 'What are the penalties?')")
            if user_question:
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                with st.chat_message("user", avatar="🧑‍💻"):
                    st.markdown(user_question)
                
                with st.chat_message("assistant", avatar="⚖️"):
                    with st.spinner("Consulting document clauses..."):
                        ai_response = ask_question_about_document(st.session_state.document_text, user_question, language)
                        st.markdown(ai_response)
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

        # --- TAB 5: COMPARE CONTRACTS ---
        with tab5:
            st.subheader("Contract Version Comparison")
            st.caption("Upload an updated or counter-party version to detect additions, deletions, and subtle changes.")
            
            uploaded_file_2 = st.file_uploader(
                "Upload Secondary Version (PDF/TXT)",
                type=['pdf', 'txt'],
                key="doc2_uploader",
                help="Select the new draft or revised contract to compare against the primary one."
            )
            
            if uploaded_file_2 is not None:
                if st.button("⚖️ Compare Contract Versions", type="primary", key="btn_compare"):
                    with st.spinner("Extracting and comparing clause differences..."):
                        doc2_text = extract_text_from_file(uploaded_file_2)
                        if not doc2_text or doc2_text.startswith("Error"):
                            st.error(f"❌ Failed to parse secondary document: {doc2_text}")
                        else:
                            comparison_result = cached_contract_comparison(st.session_state.document_text, doc2_text, language)
                            st.markdown(comparison_result)
                            st.download_button(
                                label="📥 Download Comparison Report",
                                data=comparison_result,
                                file_name="legallens_comparison.md",
                                mime="text/markdown",
                                key="dl_compare"
                            )
            else:
                st.info("Upload a second document above to compare it against your primary document.")

    else:
        # Empty State Landing
        st.info("👈 **Get Started:** Upload a legal document (PDF or TXT) in the sidebar or click one of the quick demo buttons to begin.", icon="📂")
        
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-top: 20px;">
          <div class="glass-card">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">📝</div>
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">Simplify Complex Jargon</h3>
            <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5;">Translates confusing legalese into clear, actionable summaries with dates, financial commitments, and obligations.</p>
          </div>
          <div class="glass-card">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">🚨</div>
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">Spot Red Flags</h3>
            <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5;">Detects one-sided clauses, auto-renewals, and liability traps in a structured risk table with negotiation scripts.</p>
          </div>
          <div class="glass-card">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">🎭</div>
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">Negotiate Smarter</h3>
            <p style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5;">Runs live autonomous 16-bit agent simulations so you know exactly how to counter-propose before signing.</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
