import streamlit as st
import os
import time
from utils.doc_parser import extract_text_from_file
from utils.ai_helpers import (
    get_document_summary, analyze_document_risks, ask_question_about_document, 
    compare_contracts, agent_a_opening, agent_b_response, agent_a_counter
)

st.set_page_config(page_title="LegalLens v3: GenAI Legal Assistant", page_icon="⚖️", layout="wide")

def main():
    st.title("⚖️ LegalLens: AI Legal Co-Pilot & Simulator")
    st.markdown("Upload a contract to summarize it, spot risks, or watch autonomous AI agents negotiate it live.")
    st.warning("**DISCLAIMER:** This tool uses AI for informational assistance. It is **NOT** a replacement for professional legal advice.", icon="⚠️")
    
    # Sidebar
    st.sidebar.header("🌐 Settings")
    language = st.sidebar.selectbox("Select Language", ["English", "Spanish", "French", "Hindi", "German", "Mandarin"])
    
    st.sidebar.header("📄 1. Primary Document")
    uploaded_file = st.sidebar.file_uploader("Upload Main Document (PDF/TXT)", type=['pdf', 'txt'], key="doc1")
    
    if uploaded_file is not None:
        if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            with st.spinner("Extracting text from primary document..."):
                raw_text = extract_text_from_file(uploaded_file)
                st.session_state.document_text = raw_text
                st.session_state.last_uploaded_file = uploaded_file.name
                st.session_state.summary = None
                st.session_state.risks = None
                st.session_state.chat_history = []
        
        if not os.getenv("GEMINI_API_KEY"):
            st.error("🚨 API Key Missing! Please set GEMINI_API_KEY in your .env file.")
            return

        # UI Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🚨 Risk Analyzer", "💬 Chat", "⚖️ Compare"])
        
        with tab1:
            st.subheader(f"Document Summary ({language})")
            if st.button("Generate Summary"):
                with st.spinner("Analyzing document..."):
                    summary = get_document_summary(st.session_state.document_text, language)
                    st.session_state.summary = summary
            if st.session_state.get("summary"):
                st.markdown(st.session_state.summary)

        with tab2:
            st.subheader("Clause-by-Clause Risk Analysis")
            if st.button("Analyze Risks"):
                with st.spinner("Scanning for risks..."):
                    risks = analyze_document_risks(st.session_state.document_text, language)
                    st.session_state.risks = risks
            
            if st.session_state.get("risks"):
                st.markdown(st.session_state.risks)
                
                st.divider()
                st.subheader("🎭 Live Negotiation Simulation")
                st.info("Watch your AI Lawyer and Opposing Counsel debate the risks identified above in real-time.", icon="🤖")
                
                if st.button("Simulate Negotiation for these Risks"):
                    with st.chat_message("user", avatar="🧑‍⚖️"):
                        with st.spinner("Your AI Lawyer is aggressively analyzing the document..."):
                            msg1 = agent_a_opening(st.session_state.document_text, language)
                            st.markdown(f"**Your Lawyer:**\n\n{msg1}")
                    
                    time.sleep(1) # Artificial dramatic pause
                    
                    with st.chat_message("assistant", avatar="🕴️"):
                        with st.spinner("Opposing Counsel is formulating a defense..."):
                            msg2 = agent_b_response(st.session_state.document_text, msg1, language)
                            st.markdown(f"**Opposing Counsel:**\n\n{msg2}")
                    
                    time.sleep(1)
                    
                    with st.chat_message("user", avatar="🧑‍⚖️"):
                        with st.spinner("Your AI Lawyer is drafting a counter-offer..."):
                            msg3 = agent_a_counter(st.session_state.document_text, msg2, language)
                            st.markdown(f"**Your Lawyer:**\n\n{msg3}")
                            
                    st.success("Simulation Complete! You can use these arguments to push back in real life.")

        with tab3:
            st.subheader("Chat with your Document")
            for message in st.session_state.get("chat_history", []):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            user_question = st.chat_input("E.g., Can I terminate this lease early?")
            if user_question:
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                with st.chat_message("user"): st.markdown(user_question)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        ai_response = ask_question_about_document(st.session_state.document_text, user_question, language)
                        st.markdown(ai_response)
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

        with tab4:
            st.subheader("Compare with a Second Version")
            uploaded_file_2 = st.file_uploader("Upload Secondary Document (PDF/TXT)", type=['pdf', 'txt'], key="doc2")
            if uploaded_file_2 and st.button("Compare Documents"):
                with st.spinner("Extracting text and comparing..."):
                    doc2_text = extract_text_from_file(uploaded_file_2)
                    st.markdown(compare_contracts(st.session_state.document_text, doc2_text, language))
    else:
        st.info("👈 Please upload a primary document in the sidebar to get started.")

if __name__ == "__main__":
    main()
