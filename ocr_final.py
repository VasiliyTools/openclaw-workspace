#!/usr/bin/env python3
"""
Улучшенный OCR на основе Tesseract с предобработкой.
"""

import cv2
import numpy as np
from PIL import Image
import pytesseract
import pdf2image
import sys
import re

def preprocess_image(image):
    """Улучшает изображение для OCR."""
    # Конвертируем PIL в OpenCV
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # Увеличиваем разрешение в 2 раза (улучшает чтение мелкого текста)
    height, width = img.shape[:2]
    img = cv2.resize(img, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
    # Переводим в grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Убираем шум медианным фильтром
    gray = cv2.medianBlur(gray, 3)
    # Адаптивная бинаризация
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    # Морфологическое закрытие для соединения разорванных символов
    kernel = np.ones((2,2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # Возвращаем PIL Image
    return Image.fromarray(thresh)

def correct_ocr_errors(text):
    """Исправление частых ошибок OCR."""
    replacements = {
        'РВЕ': 'PDF',
        'РОЕ': 'PDF',
        'РПЕ': 'PDF',
        'РDЕ': 'PDF',
        'РDФ': 'PDF',
        'B': 'В',
        'C': 'С',
        'P': 'Р',
        'M': 'М',
        'T': 'Т',
        'O': 'О',
        'A': 'А',
        'E': 'Е',
        'K': 'К',
        'X': 'Х',
        'y': 'у',
        'a': 'а',
        'e': 'е',
        'o': 'о',
        'c': 'с',
        'p': 'р',
        'x': 'х',
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text

def extract_text_from_pdf(pdf_path):
    """Извлекает текст из PDF с улучшенным OCR."""
    images = pdf2image.convert_from_path(pdf_path)
    full_text = ""
    for i, img in enumerate(images):
        processed = preprocess_image(img)
        # Используем PSM 6 (предполагаем единый блок текста) и языки русский+английский
        config = '--psm 6 -l rus+eng'
        text = pytesseract.image_to_string(processed, config=config)
        text = correct_ocr_errors(text)
        full_text += f"--- Страница {i+1} ---\n{text}\n\n"
    return full_text.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Укажите путь к PDF")
        sys.exit(1)
    pdf_path = sys.argv[1]
    text = extract_text_from_pdf(pdf_path)
    print(text)