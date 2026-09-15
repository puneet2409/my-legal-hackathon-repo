import pypdf
import io

MAX_PAGES = 50

def extract_text_from_file(uploaded_file) -> str:
    """
    Extracts text from an uploaded file (either PDF or TXT) safely.
    
    Args:
        uploaded_file: The Streamlit UploadedFile or file-like object.
        
    Returns:
        str: The extracted text, or an error/warning message if extraction fails.
    """
    if uploaded_file is None:
        return ""
        
    file_name = getattr(uploaded_file, "name", "")
    if not file_name:
        return ""
        
    file_type = file_name.split('.')[-1].lower()
    
    try:
        if file_type == 'txt':
            raw_bytes = uploaded_file.getvalue()
            # Handle UTF-8 with fallback to latin-1
            try:
                text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = raw_bytes.decode("latin-1", errors="replace")
            return text.strip()
            
        elif file_type == 'pdf':
            pdf_reader = pypdf.PdfReader(uploaded_file)
            total_pages = len(pdf_reader.pages)
            if total_pages == 0:
                return "Error: The uploaded PDF has no pages."
                
            text_parts = []
            pages_to_read = min(total_pages, MAX_PAGES)
            
            for page_num in range(pages_to_read):
                page = pdf_reader.pages[page_num]
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)
            
            if not text_parts:
                return "Error: Could not extract text. The PDF might be scanned or image-based."
                
            full_text = "\n\n".join(text_parts).strip()
            if total_pages > MAX_PAGES:
                full_text += f"\n\n[Note: Document was truncated to the first {MAX_PAGES} pages for performance.]"
                
            return full_text
            
        else:
            return f"Unsupported file format (.{file_type}). Please upload a .txt or .pdf file."
            
    except Exception as e:
        return f"Error reading file: {str(e)}"
