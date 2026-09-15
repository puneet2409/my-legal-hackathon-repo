import streamlit as st
import os
from utils.doc_parser import extract_text_from_file
from utils.ai_helpers import get_document_summary, analyze_document_risks, ask_question_about_document

# Must be the first Streamlit command
st.set_page_config(page_title="LegalLens: GenAI Legal Assistant", page_icon="⚖️", layout="wide")

def main():
    # Application Header
    st.title("⚖️ LegalLens: Your GenAI Legal Co-Pilot")
    st.markdown("""
    **Welcome!** Legal documents are often complex and hard to read. Upload a contract, lease, or NDA, and let AI help you understand it in plain English.
    """)
    
    # Security/Disclaimer - High Impact Criteria
    st.warning("**DISCLAIMER:** This tool uses Artificial Intelligence to provide general information and assistance. It is **NOT** a replacement for professional legal advice. Always consult a certified attorney for official legal matters.", icon="⚠️")
    
    # Sidebar for Document Upload
    st.sidebar.header("1. Upload Document")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF or TXT file", type=['pdf', 'txt'])
    
    if uploaded_file is not None:
        # Check if we need to re-parse (only parse when a new file is uploaded)
        if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            with st.spinner("Extracting text from document..."):
                raw_text = extract_text_from_file(uploaded_file)
                st.session_state.document_text = raw_text
                st.session_state.last_uploaded_file = uploaded_file.name
                st.session_state.summary = None
                st.session_state.risks = None
                st.session_state.chat_history = []
        
        # Ensure API Key is set before proceeding
        if not os.getenv("GEMINI_API_KEY"):
            st.error("🚨 API Key Missing! Please set the GEMINI_API_KEY in your .env file.")
            return

        # Main UI Tabs
        tab1, tab2, tab3 = st.tabs(["📝 Plain English Summary", "🚨 Risk Analysis", "💬 Ask a Question"])
        
        # Tab 1: Summary
        with tab1:
            st.subheader("Document Summary")
            if st.button("Generate Summary"):
                with st.spinner("Analyzing document..."):
                    summary = get_document_summary(st.session_state.document_text)
                    st.session_state.summary = summary
            
            if st.session_state.get("summary"):
                st.write(st.session_state.summary)

        # Tab 2: Risk Analysis
        with tab2:
            st.subheader("Potential Risks & Red Flags")
            st.info("The AI will scan for common predatory clauses like auto-renewals, hidden fees, or extreme liability waivers.")
            if st.button("Analyze Risks"):
                with st.spinner("Scanning for risks..."):
                    risks = analyze_document_risks(st.session_state.document_text)
                    st.session_state.risks = risks
            
            if st.session_state.get("risks"):
                st.write(st.session_state.risks)

        # Tab 3: Q&A Chat
        with tab3:
            st.subheader("Chat with your Document")
            st.write("Ask any specific question about the document's contents.")
            
            # Display chat history
            for message in st.session_state.get("chat_history", []):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Input field for new question
            user_question = st.chat_input("E.g., Can I terminate this lease early?")
            if user_question:
                # Add user message to state and display
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                with st.chat_message("user"):
                    st.markdown(user_question)
                
                # Get AI response
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        ai_response = ask_question_about_document(st.session_state.document_text, user_question)
                        st.markdown(ai_response)
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

    else:
        st.info("👈 Please upload a document in the sidebar to get started.")

if __name__ == "__main__":
    main()
