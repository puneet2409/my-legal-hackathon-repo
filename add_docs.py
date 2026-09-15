import os

def prepend_docstring(filepath, docstring):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if not content.startswith('"""'):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(docstring + '\n\n' + content)

prepend_docstring('D:/my-legal-hackathon-repo/utils/ai_helpers.py', '\"\"\"AI integration helpers for Gemini API calls, handling retries, fallbacks, and prompts.\"\"\"')
prepend_docstring('D:/my-legal-hackathon-repo/utils/doc_parser.py', '\"\"\"Document parsing utilities for safe text extraction from PDFs and Text files.\"\"\"')
prepend_docstring('D:/my-legal-hackathon-repo/utils/simulation_view.py', '\"\"\"Simulation view rendering module for generating the 2D canvas HTML.\"\"\"')
prepend_docstring('D:/my-legal-hackathon-repo/app.py', '\"\"\"LegalLens main Streamlit application entry point.\"\"\"')
