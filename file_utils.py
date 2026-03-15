import pdfplumber
import docx
from PIL import Image
import pytesseract

def extract_text(file_path):

    text = ""

    try:

        if file_path.endswith(".pdf"):

            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            except:
                print("PDFPlumber failed → trying OCR")

                images = Image.open(file_path)
                text += pytesseract.image_to_string(images)

        elif file_path.endswith(".docx"):

            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text

        elif file_path.endswith((".jpg", ".png", ".jpeg")):

            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)

    except Exception as e:
        print("Extraction error:", e)

    return text