import os

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')

def extract_text_from_file(file_path):
    """Extract text from PDF, DOCX or image file"""
    if not file_path:
        return ""
    
    original_path = file_path
    
    # Handle relative paths - make them absolute
    if not os.path.isabs(file_path):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        uploads_folder = os.path.join(project_root, 'uploads')
        file_path = os.path.join(uploads_folder, os.path.basename(file_path))
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return ""
    
    ext = os.path.splitext(file_path)[1].lower()
    
    # Only process PDF and DOCX files - return message for images
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        print(f"Image file detected: {ext}. For text extraction, please use PDF or DOCX format.")
        return "[Image file uploaded - Text extraction not available for images. Please convert to PDF or DOCX for best results.]"
    
    try:
        if ext == '.pdf':
            return extract_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return extract_docx(file_path)
        else:
            print(f"Unsupported file type: {ext}")
            return ""
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""

def extract_image(file_path):
    """Extract text from image using OCR"""
    try:
        from PIL import Image
    except ImportError:
        print("PIL not installed. Cannot process images. Please convert image to PDF.")
        return "Image file detected. For best results, please upload a PDF or DOCX file."
    
    try:
        import pytesseract
    except ImportError:
        print("pytesseract not installed. Cannot extract text from images.")
        return "Image file detected. OCR not available. Please convert image to PDF."
    
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        if text and text.strip():
            return text
        print("No text found in image - image may not contain readable text")
        return "Image uploaded but no readable text found. Please ensure your resume contains text."
    except Exception as e:
        print(f"Failed to extract text from image: {e}")
        return "Could not read image file. Please convert to PDF format."

def extract_pdf(file_path):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as f:
            try:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    try:
                        text += page.extract_text() or ""
                    except Exception as page_err:
                        print(f"Error extracting page: {page_err}")
                        continue
            except Exception as read_err:
                print(f"PDF read error: {read_err}")
                return ""
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def extract_docx(file_path):
    """Extract text from DOCX file"""
    try:
        from docx import Document
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""
