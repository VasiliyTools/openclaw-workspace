#!/usr/bin/env python3
import cv2
import numpy as np
from PIL import Image
import pytesseract
import pdf2image
import sys

def preprocess_image(image):
    """Улучшает изображение для OCR."""
    # Конвертируем PIL в OpenCV
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # Переводим в grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Убираем шум с помощью медианного фильтра
    gray = cv2.medianBlur(gray, 3)
    # Адаптивный порог для улучшения контраста текста на фоне графика
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    # Морфологические операции для соединения разорванных символов
    kernel = np.ones((2,2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # Увеличиваем резкость
    thresh = cv2.erode(thresh, kernel, iterations=1)
    thresh = cv2.dilate(thresh, kernel, iterations=1)
    return Image.fromarray(thresh)

def extract_text_from_pdf_improved(pdf_path):
    """Извлекает текст из PDF с улучшенной предобработкой."""
    images = pdf2image.convert_from_path(pdf_path)
    full_text = ""
    for i, img in enumerate(images):
        processed = preprocess_image(img)
        text = pytesseract.image_to_string(processed, lang='rus+eng')
        full_text += f"--- Страница {i+1} ---\n{text}\n\n"
    return full_text.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Укажите путь к PDF")
        sys.exit(1)
    pdf_path = sys.argv[1]
    text = extract_text_from_pdf_improved(pdf_path)
    print(text)