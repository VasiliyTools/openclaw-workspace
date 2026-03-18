#!/usr/bin/env python3
"""
Генерация PDF из Markdown-текста.
Использует reportlab для создания простого PDF.
"""

import sys
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import re

def markdown_to_paragraphs(text, styles):
    """Преобразует Markdown-текст в список элементов reportlab."""
    elements = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Заголовки
        if line.startswith('###'):
            elements.append(Paragraph(line[3:].strip(), styles['Heading3']))
        elif line.startswith('##'):
            elements.append(Paragraph(line[2:].strip(), styles['Heading2']))
        elif line.startswith('#'):
            elements.append(Paragraph(line[1:].strip(), styles['Heading1']))
        # Маркированные списки
        elif line.startswith('- '):
            elements.append(Paragraph('• ' + line[2:], styles['Normal']))
        else:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 6))
    return elements

def create_pdf(content, output_path):
    """Создаёт PDF файл."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    # Добавляем свои стили
    styles.add(ParagraphStyle(name='Heading1', parent=styles['Heading1'],
                              fontSize=16, spaceAfter=12, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='Heading2', parent=styles['Heading2'],
                              fontSize=14, spaceAfter=8, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='Heading3', parent=styles['Heading3'],
                              fontSize=12, spaceAfter=6, textColor=colors.darkblue))
    
    elements = []
    # Заголовок
    elements.append(Paragraph("Отчёт Финансиста", styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Контент
    elements.extend(markdown_to_paragraphs(content, styles))
    
    doc.build(elements)
    print(f"PDF создан: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: generate_pdf.py <входной_файл.md> <выходной_файл.pdf>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if not os.path.exists(input_file):
        print(f"Файл не найден: {input_file}")
        sys.exit(1)
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    create_pdf(content, output_file)