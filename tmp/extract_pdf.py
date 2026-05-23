import os
import sys

def try_extract_pdf(pdf_path, txt_path):
    print(f"Trying to extract {pdf_path}...")
    
    # Try importing PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Success using PyMuPDF (fitz)!")
        return True
    except ImportError:
        print("fitz not available.")
    except Exception as e:
        print(f"fitz failed: {e}")
        
    # Try importing pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Success using pypdf!")
        return True
    except ImportError:
        print("pypdf not available.")
    except Exception as e:
        print(f"pypdf failed: {e}")

    # Try importing PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Success using PyPDF2!")
        return True
    except ImportError:
        print("PyPDF2 not available.")
    except Exception as e:
        print(f"PyPDF2 failed: {e}")

    # Try pdfplumber
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Success using pdfplumber!")
        return True
    except ImportError:
        print("pdfplumber not available.")
    except Exception as e:
        print(f"pdfplumber failed: {e}")

    print("No PDF extraction libraries available or extraction failed.")
    return False

pdf_path = "backend/rasa/Tugas akhir/PROPOSAL OPTIMASI PIPELINE.pdf"
txt_path = "tmp/proposal_text.txt"
try_extract_pdf(pdf_path, txt_path)
