#!/usr/bin/env python3
"""
Обработчик PDF и изображений.
Извлекает текст из PDF (включая сканы через OCR) и изображений.
"""

import sys
import os
import tempfile
import json
import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import pdf2image
import cv2
import numpy as np

def extract_text_from_pdf(pdf_path, use_ocr=False):
    """Извлекает текст из PDF. Если use_ocr=True, применяет OCR к страницам-изображениям."""
    text = ""
    try:
        if use_ocr:
            # Конвертируем PDF в изображения
            images = pdf2image.convert_from_path(pdf_path)
            for i, img in enumerate(images):
                # Преобразуем PIL Image в OpenCV для предобработки
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                # Увеличиваем контраст (опционально)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                # Обратно в PIL
                img_processed = Image.fromarray(thresh)
                page_text = pytesseract.image_to_string(img_processed, lang='rus+eng')
                text += f"--- Страница {i+1} (OCR) ---\n{page_text}\n\n"
        else:
            # Пытаемся извлечь обычный текст
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"--- Страница {i+1} ---\n{page_text}\n\n"
                    else:
                        # Если текст не извлекся, возможно, это сканы — переключаемся на OCR
                        return extract_text_from_pdf(pdf_path, use_ocr=True)
    except Exception as e:
        return f"Ошибка при обработке PDF: {e}"
    return text.strip()

def extract_text_from_image(image_path):
    """Извлекает текст с изображения через OCR."""
    try:
        img = Image.open(image_path)
        # Предобработка: конвертируем в grayscale и увеличиваем контраст
        img = img.convert('L')
        img = img.point(lambda x: 0 if x < 128 else 255, '1')
        text = pytesseract.image_to_string(img, lang='rus+eng')
        return text.strip()
    except Exception as e:
        return f"Ошибка при обработке изображения: {e}"

def process_file(file_path):
    """Определяет тип файла и вызывает соответствующий обработчик."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        # Сначала пробуем без OCR, если текст не извлекся — с OCR
        text = extract_text_from_pdf(file_path, use_ocr=False)
        if not text or len(text) < 50:  # Если текста мало, возможно, это сканы
            text = extract_text_from_pdf(file_path, use_ocr=True)
        return {"type": "pdf", "text": text}
    elif ext in ('.jpg', '.jpeg', '.png', '.bmp', '.tiff'):
        text = extract_text_from_image(file_path)
        return {"type": "image", "text": text}
    else:
        return {"error": f"Неподдерживаемый формат файла: {ext}"}

if __name__ == "__main__":
    # Ожидаем путь к файлу как аргумент
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Не указан путь к файлу"}))
        sys.exit(1)
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(json.dumps({"error": f"Файл не найден: {file_path}"}))
        sys.exit(1)
    result = process_file(file_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))