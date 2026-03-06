from pypdf import PdfReader
from pdf2image import convert_from_path
import pytesseract


def extract_text_from_pdf(pdf_path):
    # First, try standard text extraction
    reader = PdfReader(pdf_path)
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    full_text = full_text.strip()
    
    # If no text was found, it's likely a scanned image PDF. Fallback to OCR.
    if not full_text:
        print(f"⚠ No text layer found in {pdf_path}. Running OCR (this may take a moment)...")
        try:
            images = convert_from_path(pdf_path)
            for img in images:
                full_text += pytesseract.image_to_string(img) + "\n"
        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")

    return full_text.strip()