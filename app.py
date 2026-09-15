import streamlit as st
import os
import time
from utils.doc_parser import extract_text_from_file
from utils.ai_helpers import (
    get_document_summary, analyze_document_risks, ask_question_about_document, 
    compare_contracts, agent_a_opening, agent_b_response, agent_a_counter
)

st.set_page_config(
    page_title="LegalLens: AI Legal Co-Pilot & Simulator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("⚖️ LegalLens: AI Legal Co-Pilot & Simulator")
    st.markdown("Democratizing legal documents with plain-English simplification, risk discovery, and autonomous negotiation simulations.")
    
    # Dismissible Disclaimer
    if not st.session_state.get("disclaimer_dismissed", False):
        col_disc, col_btn = st.columns([0.85, 0.15])
        with col_disc:
            st.warning(
                "**LEGAL NOTICE:** LegalLens provides general informational assistance and educational analysis powered by AI. "
                "It is **not** a law firm and does **not** provide legal advice. Always consult a licensed attorney for formal legal matters.",
                icon="⚠️"
            )
        with col_btn:
            if st.button("Dismiss", help="Acknowledge disclaimer and hide this banner"):
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
        uploaded_file = st.file_uploader(
            "Upload Contract / Agreement",
            type=['pdf', 'txt'],
            help="Supports searchable PDF and TXT documents up to 50 pages."
        )
        
        if uploaded_file is not None:
            st.caption(f"📁 **File:** `{uploaded_file.name}` ({round(uploaded_file.size / 1024, 1)} KB)")

    # Check API key before proceeding
    if not os.environ.get("GEMINI_API_KEY"):
        st.error(
            "🚨 **Gemini API Key Missing!** Please ensure your `GEMINI_API_KEY` is set in the `.env` file in the project directory.",
            icon="🔒"
        )
        st.info("Example `.env` format:\n```text\nGEMINI_API_KEY=AIzaSy...\n```")
        return

    # Document Extraction & State Management
    if uploaded_file is not None:
        if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            with st.spinner("Extracting text from primary document..."):
                extracted_text = extract_text_from_file(uploaded_file)
                
                # Check for extraction errors or empty results
                if not extracted_text or extracted_text.startswith("Error"):
                    st.error(f"❌ Failed to parse document: {extracted_text}")
                    st.session_state.document_text = None
                    return
                
                st.session_state.document_text = extracted_text
                st.session_state.last_uploaded_file = uploaded_file.name
                st.session_state.summary = None
                st.session_state.risks = None
                st.session_state.chat_history = []
                st.session_state.simulation_history = None

        if not st.session_state.get("document_text"):
            st.warning("Please upload a valid text or searchable PDF document to continue.")
            return

        # Main Interface Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Plain English Summary",
            "🚨 Clause Risk Analyzer",
            "💬 Interactive Q&A",
            "⚖️ Version Comparison"
        ])
        
        # --- TAB 1: SUMMARY ---
        with tab1:
            st.subheader(f"Plain English Summary ({language})")
            st.caption("Converts dense legal jargon into clear obligations, dates, and takeaways.")
            
            col_sum_action, _ = st.columns([0.3, 0.7])
            with col_sum_action:
                if st.button("Generate Summary", type="primary", use_container_width=True):
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
                    help="Export the plain-English summary"
                )

        # --- TAB 2: RISK ANALYZER & SIMULATION ---
        with tab2:
            st.subheader("Clause-by-Clause Risk & Red-Flag Analyzer")
            st.caption("Spots predatory clauses like auto-renewals, broad liability, and hidden termination penalties.")
            
            if st.button("Scan for Hidden Risks", type="primary"):
                with st.spinner("Scanning for predatory terms and unfavorable clauses..."):
                    risks = analyze_document_risks(st.session_state.document_text, language)
                    st.session_state.risks = risks
            
            if st.session_state.get("risks"):
                st.markdown(st.session_state.risks)
                
                st.download_button(
                    label="📥 Download Risk Report (Markdown)",
                    data=st.session_state.risks,
                    file_name="legallens_risk_report.md",
                    mime="text/markdown"
                )
                
                # --- INTEGRATED AI SIMULATOR ---
                st.divider()
                st.subheader("🎭 Autonomous Negotiation Simulation")
                st.info(
                    "Watch two AI agents roleplay a live negotiation on the problematic clauses detected above. "
                    "**Agent A** fights for your rights; **Agent B** defends the document.",
                    icon="🤖"
                )
                
                if st.button("Launch Live Agent Negotiation", help="Simulate back-and-forth negotiation arguments"):
                    # Step 1: Agent A Opening
                    with st.chat_message("user", avatar="🧑‍⚖️"):
                        with st.spinner("Your AI Lawyer is analyzing the clauses to form an argument..."):
                            msg1 = agent_a_opening(st.session_state.document_text, language)
                            st.markdown(f"**Your Legal Counsel:**\n\n{msg1}")
                    
                    time.sleep(1)
                    
                    # Step 2: Agent B Defense
                    with st.chat_message("assistant", avatar="🕴️"):
                        with st.spinner("Opposing Counsel is formulating a formal response..."):
                            msg2 = agent_b_response(st.session_state.document_text, msg1, language)
                            st.markdown(f"**Opposing Counsel:**\n\n{msg2}")
                    
                    time.sleep(1)
                    
                    # Step 3: Agent A Counter
                    with st.chat_message("user", avatar="🧑‍⚖️"):
                        with st.spinner("Your AI Lawyer is delivering a protective counter-offer..."):
                            msg3 = agent_a_counter(st.session_state.document_text, msg2, language)
                            st.markdown(f"**Your Legal Counsel (Final Counter):**\n\n{msg3}")
                            
                    st.success("✅ Simulation complete! You can use these strategic points when discussing this contract.")

        # --- TAB 3: CHAT Q&A ---
        with tab3:
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

        # --- TAB 4: COMPARE CONTRACTS ---
        with tab4:
            st.subheader("Contract Version Comparison")
            st.caption("Upload an updated or counter-party version to detect additions, deletions, and subtle changes.")
            
            uploaded_file_2 = st.file_uploader(
                "Upload Secondary Version (PDF/TXT)",
                type=['pdf', 'txt'],
                key="doc2_uploader",
                help="Select the new draft or revised contract to compare against the primary one."
            )
            
            if uploaded_file_2 is not None:
                if st.button("Compare Contract Versions", type="primary"):
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
                                mime="text/markdown"
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
