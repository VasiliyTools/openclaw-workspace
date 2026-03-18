#!/usr/bin/env python3
import cv2
import numpy as np
from PIL import Image
import pytesseract
import pdf2image
import sys
import re

def preprocess_for_mixed_text(image):
    """Предобработка для смешанного русского/английского текста."""
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Увеличение резкости
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharp = cv2.filter2D(gray, -1, kernel)
    # Адаптивный порог
    thresh = cv2.adaptiveThreshold(sharp, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    # Удаление мелкого шума
    kernel = np.ones((1,1), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return Image.fromarray(thresh)

def correct_common_errors(text):
    """Исправление частых ошибок OCR."""
    replacements = {
        'РВЕ': 'PDF',
        'РОЕ': 'PDF',
        'РПЕ': 'PDF',
        'РDЕ': 'PDF',
        'РDФ': 'PDF',
        'сейчас': 'сейчас',
        'ЧТО': 'что',
        'ШТО': 'что',
        'B': 'В',  # латинская B -> кириллическая В
        'C': 'С',  # латинская C -> кириллическая С
        'P': 'Р',  # латинская P -> кириллическая Р
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

def extract_text_with_correction(pdf_path):
    images = pdf2image.convert_from_path(pdf_path)
    full_text = ""
    for i, img in enumerate(images):
        processed = preprocess_for_mixed_text(img)
        # Пробуем разные PSM
        config = '--psm 6 -l rus+eng'
        text = pytesseract.image_to_string(processed, config=config)
        text = correct_common_errors(text)
        full_text += f"--- Страница {i+1} ---\n{text}\n\n"
    return full_text.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Укажите путь к PDF")
        sys.exit(1)
    pdf_path = sys.argv[1]
    text = extract_text_with_correction(pdf_path)
    print(text)