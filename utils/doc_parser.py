import pypdf
import io

def extract_text_from_file(uploaded_file) -> str:
    """
    Extracts text from an uploaded file (either PDF or TXT).
    
    Args:
        uploaded_file: The Streamlit UploadedFile object.
        
    Returns:
        str: The extracted text, or an error message if extraction fails.
    """
    if uploaded_file is None:
        return ""
        
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_type == 'txt':
            # Read text file
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            return stringio.read()
            
        elif file_type == 'pdf':
            # Read PDF file
            pdf_reader = pypdf.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
            
        else:
            return "Unsupported file format. Please upload a .txt or .pdf file."
            
    except Exception as e:
        return f"Error reading file: {str(e)}"
