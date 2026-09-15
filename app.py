import streamlit as st
import os
import time
from utils.doc_parser import extract_text_from_file
from utils.ai_helpers import (
    get_document_summary, analyze_document_risks, ask_question_about_document, 
    compare_contracts, agent_a_opening, agent_b_response, agent_a_counter
)
from utils.simulation_view import get_office_simulation_html
import streamlit.components.v1 as components

st.set_page_config(
    page_title="LegalLens: AI Legal Co-Pilot & Simulator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    st.title("⚖️ LegalLens: AI Legal Co-Pilot & Simulator")
    st.markdown("Democratizing legal documents with plain-English simplification, risk discovery, and autonomous negotiation simulations.")
    
    # Dismissible Disclaimer (State preserved so it never kicks user out)
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
        st.header("🌐 Global Settings")
        language = st.selectbox(
            "Select Response Language",
            ["English", "Spanish", "French", "Hindi", "German", "Mandarin", "Arabic", "Portuguese"],
            help="All AI summaries, tables, and simulations will be generated in this language."
        )
        
        st.divider()
        st.header("📄 Primary Document")
        
        # If document already loaded into session, keep it active and allow reuse!
        if st.session_state.document_text:
            st.success(f"📄 **Active Document:**\n\n`{st.session_state.active_doc_name}`")
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

    # Check API key before proceeding
    if not os.environ.get("GEMINI_API_KEY"):
        st.error(
            "🚨 **Gemini API Key Missing!** Please ensure your `GEMINI_API_KEY` is set in the `.env` file in the project directory.",
            icon="🔒"
        )
        st.info("Example `.env` format:\n```text\nGEMINI_API_KEY=AIzaSy...\n```")
        return

    # If document is loaded in session, show full application
    if st.session_state.document_text:
        st.caption(f"📁 Analyzing: **{st.session_state.active_doc_name}** | Language: **{language}**")
        
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
                if st.button("Generate Summary", type="primary", use_container_width=True, key="btn_gen_sum"):
                    with st.spinner("Analyzing document structure and obligations..."):
                        summary = get_document_summary(st.session_state.document_text, language)
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
            
            if st.button("Scan for Hidden Risks", type="primary", key="btn_gen_risk"):
                with st.spinner("Scanning for predatory terms and unfavorable clauses..."):
                    risks = analyze_document_risks(st.session_state.document_text, language)
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
            st.caption("Inspired by Generative Agents: Autonomous AI agents move across office rooms (Research Library, Conference Room, Opposing Desk) to negotiate terms live.")

            col_run_sim, _ = st.columns([0.35, 0.65])
            with col_run_sim:
                run_sim_btn = st.button("▶️ Launch 2D Agent Simulation", type="primary", use_container_width=True, key="btn_run_2d_sim")

            if run_sim_btn or "sim_msg1" in st.session_state:
                if run_sim_btn:
                    with st.spinner("AI agents are examining legal clauses and roleplaying negotiation..."):
                        m1 = agent_a_opening(st.session_state.document_text, language)
                        m2 = agent_b_response(st.session_state.document_text, m1, language)
                        m3 = agent_a_counter(st.session_state.document_text, m2, language)
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
                    height=600
                )
                
                # Full negotiation transcript
                with st.expander("📜 Full Strategic Negotiation Transcript", expanded=True):
                    st.markdown(f"**🧑‍⚖️ Alex (Your Legal Counsel):**\n\n{st.session_state.sim_msg1}")
                    st.markdown(f"**🕴️ Morgan (Opposing Counsel):**\n\n{st.session_state.sim_msg2}")
                    st.markdown(f"**🧑‍⚖️ Alex (Final Protective Terms):**\n\n{st.session_state.sim_msg3}")
            else:
                # Default live 2D canvas view
                components.html(get_office_simulation_html(), height=600)
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
                if st.button("Compare Contract Versions", type="primary", key="btn_compare"):
                    with st.spinner("Extracting and comparing clause differences..."):
                        doc2_text = extract_text_from_file(uploaded_file_2)
                        if not doc2_text or doc2_text.startswith("Error"):
                            st.error(f"❌ Failed to parse secondary document: {doc2_text}")
                        else:
                            comparison_result = compare_contracts(st.session_state.document_text, doc2_text, language)
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
        st.info("👈 **Get Started:** Upload a legal document (PDF or TXT) in the sidebar to begin your analysis.", icon="📂")
        
        st.markdown("### 🌟 What LegalLens Can Do:")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("#### 📝 Simplify Complex Jargon")
            st.write("Translates confusing legalese into clear, actionable summaries with dates and financial obligations.")
        with col_b:
            st.markdown("#### 🚨 Spot Red Flags")
            st.write("Detects one-sided clauses, auto-renewals, and liability traps in a structured risk table.")
        with col_c:
            st.markdown("#### 🎭 Negotiate Smarter")
            st.write("Runs live autonomous agent simulations so you know how to push back before signing.")

if __name__ == "__main__":
    main()
