#!/usr/bin/env python3
"""
Универсальный обработчик документов с поддержкой Tesseract и EasyOCR.
Автоматически выбирает движок в зависимости от типа документа.
"""

import os
import sys
import pdfplumber
import pytesseract
from PIL import Image
import pdf2image
import cv2
import numpy as np
import easyocr

def is_scanned_pdf(pdf_path):
    """Проверяет, является ли PDF сканированным изображением (нет текстового слоя)."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    return False  # Есть текстовый слой
        return True
    except:
        return True  # В случае ошибки считаем сканированным

def extract_text_with_tesseract(image):
    """Извлекает текст с помощью Tesseract (с предобработкой)."""
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    processed = Image.fromarray(thresh)
    config = '--psm 6 -l rus+eng'
    text = pytesseract.image_to_string(processed, config=config)
    return text

def extract_text_with_easyocr(image):
    """Извлекает текст с помощью EasyOCR."""
    reader = easyocr.Reader(['ru', 'en'], gpu=False)
    img_np = np.array(image)
    result = reader.readtext(img_np, detail=0, paragraph=True)
    return "\n".join(result)

def process_pdf(pdf_path, use_easyocr_for_scanned=True):
    """Обрабатывает PDF, возвращает текст."""
    if not is_scanned_pdf(pdf_path):
        # Текстовый PDF: извлекаем напрямую
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
        return text.strip()
    else:
        # Сканированный PDF: конвертируем в изображения и применяем OCR
        images = pdf2image.convert_from_path(pdf_path)
        full_text = ""
        for i, img in enumerate(images):
            if use_easyocr_for_scanned:
                page_text = extract_text_with_easyocr(img)
            else:
                page_text = extract_text_with_tesseract(img)
            full_text += f"--- Страница {i+1} ---\n{page_text}\n\n"
        return full_text.strip()

def process_image(image_path):
    """Обрабатывает изображение (JPG, PNG и т.д.)."""
    img = Image.open(image_path)
    # Для изображений используем EasyOCR (лучше качество)
    return extract_text_with_easyocr(img)

def main():
    if len(sys.argv) < 2:
        print("Использование: document_processor_final.py <путь_к_файлу> [--tesseract]")
        print("  --tesseract : принудительно использовать Tesseract вместо EasyOCR")
        sys.exit(1)
    
    file_path = sys.argv[1]
    force_tesseract = '--tesseract' in sys.argv
    
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
        sys.exit(1)
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            text = process_pdf(file_path, use_easyocr_for_scanned=not force_tesseract)
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            if force_tesseract:
                img = Image.open(file_path)
                text = extract_text_with_tesseract(img)
            else:
                text = process_image(file_path)
        else:
            print(f"Неподдерживаемый формат: {ext}")
            sys.exit(1)
        
        print(text)
    except Exception as e:
        print(f"Ошибка обработки: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()