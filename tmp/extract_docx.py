import zipfile
import xml.etree.ElementTree as ET
import os

def docx_to_txt(docx_path, txt_path):
    try:
        if not os.path.exists(docx_path):
            print(f"File not found: {docx_path}")
            return
        
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        # XML namespace tags in docx
        # Namespaces are usually prepended in braced format {url}tag
        text_runs = []
        # Find all paragraph elements
        for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            para_text = []
            # For each paragraph, find all text elements
            for run in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if run.text:
                    para_text.append(run.text)
            text_runs.append(''.join(para_text))
            
        full_text = '\n'.join(text_runs)
        
        # Ensure target dir exists
        os.makedirs(os.path.dirname(txt_path), exist_ok=True)
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"Successfully extracted {docx_path} to {txt_path} ({len(full_text)} chars)")
    except Exception as e:
        print(f"Error extracting {docx_path}: {e}")

# Paths
docx_files = [
    ("backend/rasa/Tugas akhir/BAB I.docx", "tmp/bab1.txt"),
    ("backend/rasa/Tugas akhir/BAB 2.docx", "tmp/bab2.txt"),
    ("backend/rasa/Tugas akhir/BAB 3.docx", "tmp/bab3.txt"),
    ("backend/rasa/Tugas akhir/BAB 4.docx", "tmp/bab4.txt")
]

for docx_p, txt_p in docx_files:
    docx_to_txt(docx_p, txt_p)
