#!/usr/bin/env python3
import easyocr
import pdf2image
import numpy as np
import sys

def extract_with_easyocr(pdf_path):
    reader = easyocr.Reader(['ru', 'en'], gpu=False)
    images = pdf2image.convert_from_path(pdf_path)
    full_text = ""
    for i, img in enumerate(images):
        img_np = np.array(img)
        result = reader.readtext(img_np, detail=0, paragraph=True)
        page_text = "\n".join(result)
        full_text += f"--- Страница {i+1} ---\n{page_text}\n\n"
    return full_text.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Укажите путь к PDF")
        sys.exit(1)
    pdf_path = sys.argv[1]
    text = extract_with_easyocr(pdf_path)
    print(text)