import streamlit as st
import os
from utils.doc_parser import extract_text_from_file
from utils.ai_helpers import get_document_summary, analyze_document_risks, ask_question_about_document, compare_contracts

st.set_page_config(page_title="LegalLens v2: GenAI Legal Assistant", page_icon="⚖️", layout="wide")

def main():
    st.title("⚖️ LegalLens v2: Your GenAI Legal Co-Pilot")
    st.markdown("Upload a contract, lease, or NDA, and let AI help you understand it in plain English, spot risks, or compare versions.")
    st.warning("**DISCLAIMER:** This tool uses Artificial Intelligence to provide general information and assistance. It is **NOT** a replacement for professional legal advice.", icon="⚠️")
    
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
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🚨 Risk Analyzer", "💬 Chat", "⚖️ Compare Contracts"])
        
        # Tab 1: Summary
        with tab1:
            st.subheader(f"Document Summary ({language})")
            if st.button("Generate Summary"):
                with st.spinner("Analyzing document..."):
                    summary = get_document_summary(st.session_state.document_text, language)
                    st.session_state.summary = summary
            if st.session_state.get("summary"):
                st.markdown(st.session_state.summary)

        # Tab 2: Risk Analyzer (Table & Negotiation)
        with tab2:
            st.subheader("Clause-by-Clause Risk Analysis")
            st.info("The AI will generate a structured table of risks and provide negotiation scripts.")
            if st.button("Analyze Risks"):
                with st.spinner("Scanning for risks..."):
                    risks = analyze_document_risks(st.session_state.document_text, language)
                    st.session_state.risks = risks
            if st.session_state.get("risks"):
                st.markdown(st.session_state.risks)

        # Tab 3: Q&A Chat
        with tab3:
            st.subheader("Chat with your Document")
            for message in st.session_state.get("chat_history", []):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            user_question = st.chat_input("E.g., Can I terminate this lease early?")
            if user_question:
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                with st.chat_message("user"):
                    st.markdown(user_question)
                
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        ai_response = ask_question_about_document(st.session_state.document_text, user_question, language)
                        st.markdown(ai_response)
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

        # Tab 4: Compare Contracts
        with tab4:
            st.subheader("Compare with a Second Version")
            st.write("Upload a second document (like an updated lease) to see what changed.")
            uploaded_file_2 = st.file_uploader("Upload Secondary Document (PDF/TXT)", type=['pdf', 'txt'], key="doc2")
            
            if uploaded_file_2:
                if st.button("Compare Documents"):
                    with st.spinner("Extracting text and comparing..."):
                        doc2_text = extract_text_from_file(uploaded_file_2)
                        comparison_result = compare_contracts(st.session_state.document_text, doc2_text, language)
                        st.markdown(comparison_result)
    else:
        st.info("👈 Please upload a primary document in the sidebar to get started.")

if __name__ == "__main__":
    main()
